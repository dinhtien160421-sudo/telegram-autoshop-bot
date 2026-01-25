from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    Filters,
)

import random
import string
import urllib.parse
from io import BytesIO
import os

from flask import Flask, request, jsonify
import threading
import re


# ============= CẤU HÌNH =============
BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_CHAT_ID = 6164122466

BANK_CODE = "ACB"
BANK_ACCOUNT = "21812351"
ADMIN_CONTACT = "Liên hệ Zalo: 0842108959"
USERS_FILE = "users.txt"

# Lưu đơn chờ thanh toán: order_code -> {product_id, user_id, qty, amount, delivered}
PENDING_ORDERS = {}
PENDING_LOCK = threading.Lock()

# user đang được hỏi số lượng: user_id -> product_id
WAITING_QTY = {}

# Bot instance dùng trong webhook
TG_BOT = None

# Flask app
app = Flask(__name__)

# Regex tìm mã ORDxxxxxxxxxx trong nội dung bank
ORDER_REGEX = re.compile(r"(ORD\d{10})")


# ===== LƯU USER =====
def add_user(chat_id: int):
    ids = set()
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        ids.add(int(line))
                    except Exception:
                        pass

    if chat_id not in ids:
        ids.add(chat_id)
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            for uid in ids:
                f.write(str(uid) + "\n")


# ===== SẢN PHẨM =====
PRODUCTS = {
    "code_gpt": {"name": "CODE GPT PLUS", "price": 15000},
    "veo3_ultra_bh": {"name": "Veo3 Ultra 45K cre BH 4/2", "price": 75000},
    "veo3_ultra_bhf": {"name": "Veo3 Ultra 45K cre BH 30D", "price": 130000},
    "info_1": {"name": "Gia hạn GPT Plus – Capcut - Canva Ib", "price": 0},
    "info_2": {"name": "Zalo: 0842.108.959 - Tele:@dtdt28", "price": 0},
}


# ===== KHO =====
STOCK = {
    "code_gpt": [
        "https://chatgpt.com/?promoCode=536RM3DD9SXGDFZN",
        "https://chatgpt.com/?promoCode=CRQ6PVLRAN7SHC5B",
        "https://chatgpt.com/?promoCode=DWMX97LJ5ZQAAR44",
        "https://chatgpt.com/?promoCode=A4PS7DCKX97JACPW",
        "https://chatgpt.com/?promoCode=252GYT9HLMR9PXWP",
        "https://chatgpt.com/?promoCode=E8GW6MC9YVMZ8NDP",
    ],
    "veo3_ultra_bh": [],
    "veo3_ultra_bhf": [],
    "info_1": ["IB"] * 0,
    "info_2": ["IB"] * 0,
}


# ===== HÀM PHỤ =====
def gen_order_code():
    return "ORD" + "".join(random.choices(string.digits, k=10))


def build_vietqr_url(amount, content):
    content_encoded = urllib.parse.quote(content)
    return (
        f"https://img.vietqr.io/image/"
        f"{BANK_CODE}-{BANK_ACCOUNT}-compact2.png"
        f"?amount={amount}&addInfo={content_encoded}"
    )


def deliver_order_auto(code: str, pid: str, user_id: int, qty: int) -> bool:
    """
    Nhả đơn + gửi txt file.
    Trả True nếu giao thành công.
    """
    product = PRODUCTS[pid]

    # Check kho
    if len(STOCK.get(pid, [])) < qty:
        TG_BOT.send_message(
            chat_id=user_id,
            text="⚠️ Đã nhận thanh toán nhưng kho không đủ số lượng. Vui lòng liên hệ admin.",
        )
        TG_BOT.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=f"⚠️ Kho không đủ để auto giao cho đơn {code} (pid={pid}, qty={qty}).",
        )
        return False

    # Lấy hàng
    accounts = [STOCK[pid].pop(0) for _ in range(qty)]
    codes_text = "\n".join(f"{i+1}. {acc}" for i, acc in enumerate(accounts))

    # Gửi tin nhắn cho khách
    detail = (
        f"✅ Đơn `{code}`\n"
        f"🎁 Sản phẩm: *{product['name']}*\n"
        f"📦 Số lượng: *{qty}*\n\n"
        f"{codes_text}\n\n"
        "Cảm ơn bạn đã mua hàng!"
    )

    TG_BOT.send_message(
        chat_id=user_id,
        text=detail,
        parse_mode="Markdown",
        disable_web_page_preview=True,
    )

    # Gửi file .txt
    txt = (
        f"Đơn hàng: {code}\n"
        f"Sản phẩm: {product['name']}\n"
        f"Số lượng: {qty}\n"
        f"Tài khoản/Mã:\n{codes_text}\n"
    ).encode("utf-8")

    f = BytesIO(txt)
    f.name = f"{code}.txt"

    TG_BOT.send_document(
        chat_id=user_id,
        document=InputFile(f),
        filename=f.name,
        caption="📄 File Notepad chứa tài khoản/mã.",
    )

    return True


# ====== SEPAY WEBHOOK (AUTO NHẢ ĐƠN) ======
@app.route("/bank-webhook", methods=["POST"])
def sepay_webhook():
    data = request.get_json(force=True, silent=True) or {}
    print("\n==== SEPAY PAYLOAD ====")
    print(data, flush=True)

    # Chỉ nhận tiền vào
    if str(data.get("transferType", "")).lower() != "in":
        return jsonify({"ok": True, "ignored": "not_in"}), 200

    content = str(data.get("content") or data.get("description") or "")
    amount = int(data.get("transferAmount", 0) or 0)

    m = ORDER_REGEX.search(content)
    if not m:
        print("[SEPAY] No ORD found in content/description.", flush=True)
        return jsonify({"ok": True, "ignored": "no_ord"}), 200

    code = m.group(1)
    print(f"[SEPAY] Found code={code} amount={amount}", flush=True)

    with PENDING_LOCK:
        order = PENDING_ORDERS.get(code)

    if not order:
        print(f"[SEPAY] No pending order for: {code}", flush=True)
        return jsonify({"ok": True, "ignored": "order_not_found"}), 200

    # Chống gọi trùng
    with PENDING_LOCK:
        if order.get("delivered"):
            print(f"[SEPAY] Already delivered: {code}", flush=True)
            return jsonify({"ok": True, "ignored": "already_delivered"}), 200

    pid = order["product_id"]
    user_id = order["user_id"]
    qty = int(order.get("qty", 1))
    expected = int(order.get("amount", PRODUCTS[pid]["price"] * qty))

    if amount < expected:
        # Báo admin nếu thiếu tiền
        TG_BOT.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=f"⚠ Đơn `{code}` thiếu tiền: {amount:,}đ / {expected:,}đ".replace(",", "."),
            parse_mode="Markdown",
        )
        print(f"[SEPAY] Insufficient: got={amount} expected={expected}", flush=True)
        return jsonify({"ok": True, "ignored": "insufficient"}), 200

    # Đánh dấu delivered trước để chống trùng
    with PENDING_LOCK:
        PENDING_ORDERS[code]["delivered"] = True

    ok = deliver_order_auto(code, pid, user_id, qty)

    if ok:
        with PENDING_LOCK:
            PENDING_ORDERS.pop(code, None)

        TG_BOT.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=f"🤖 AUTO NHẢ `{code}` — đã giao {qty} tài khoản cho `{user_id}`",
            parse_mode="Markdown",
        )
        print(f"[SEPAY] Delivered OK: {code}", flush=True)

    return jsonify({"ok": True}), 200


# ===== START + MENU =====
def start(update, context):
    chat_id = update.effective_chat.id
    add_user(chat_id)

    keyboard = []
    for pid, info in PRODUCTS.items():
        stock_count = len(STOCK.get(pid, []))
        status = f"(còn {stock_count})" if stock_count > 0 else "(hết hàng)"
        btn = f"{info['name']} - {info['price']:,}đ {status}".replace(",", ".")
        keyboard.append([InlineKeyboardButton(btn, callback_data=f"buy_{pid}")])

    update.message.reply_text(
        "🛍 *Danh sách sản phẩm* – chọn bên dưới 👇",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


# ===== BROADCAST ADMIN =====
def broadcast(update, context):
    chat_id = update.effective_chat.id
    if chat_id != ADMIN_CHAT_ID:
        update.message.reply_text("❌ Bạn không có quyền dùng lệnh này.")
        return

    msg = update.message

    if msg.reply_to_message and msg.reply_to_message.text:
        message = msg.reply_to_message.text
    else:
        if not context.args:
            msg.reply_text(
                "⚠ Dùng:\n"
                "- /broadcast nội_dung\n"
                "- Hoặc reply vào tin nhắn cần gửi rồi gõ /broadcast"
            )
            return
        message = msg.text.partition(" ")[2]

    if not os.path.exists(USERS_FILE):
        msg.reply_text("Chưa có user nào trong danh sách.")
        return

    sent = 0
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                uid = int(line)
                context.bot.send_message(chat_id=uid, text=message, disable_web_page_preview=True)
                sent += 1
            except Exception:
                continue

    msg.reply_text(f"✅ Đã gửi cho khoảng {sent} người dùng.")


# ===== XỬ LÝ NÚT =====
def handle_buttons(update, context):
    query = update.callback_query
    data = query.data
    query.answer()

    # Chọn sản phẩm
    if data.startswith("buy_"):
        pid = data.replace("buy_", "")
        product = PRODUCTS[pid]
        user_id = query.from_user.id

        stock_count = len(STOCK.get(pid, []))
        if stock_count == 0:
            query.message.reply_text(
                f"❌ Sản phẩm *{product['name']}* đã hết hàng.",
                parse_mode="Markdown",
            )
            return

        WAITING_QTY[user_id] = pid

        query.message.reply_text(
            f"Bạn muốn mua bao nhiêu *{product['name']}*?\n"
            f"(còn *{stock_count}*)\n"
            f"Đơn giá: *{product['price']:,}đ* / 1 tài khoản.\n\n"
            "👉 Vui lòng nhập một số nguyên, ví dụ: 1, 2, 3 ...",
            parse_mode="Markdown",
        )
        return

    # Khách bấm "Tôi đã chuyển tiền" (chỉ để trấn an, không duyệt tay)
    if data == "confirm":
        query.message.reply_text(
            "✅ Đã ghi nhận. Nếu bạn chuyển đúng *nội dung ORD*, hệ thống sẽ tự giao hàng sau ít phút.\n"
            "Nếu quá lâu chưa nhận được, vui lòng inbox admin.",
            parse_mode="Markdown",
        )
        return

    # Hủy đơn: xóa pending theo order trong context.user_data nếu có
    if data == "cancel":
        if "order" in context.user_data:
            pid, code, qty, amount = context.user_data["order"]
            with PENDING_LOCK:
                PENDING_ORDERS.pop(code, None)
            context.user_data.clear()

        query.message.reply_text("❌ Bạn đã hủy đơn.")
        return


# ===== NHẬP SỐ LƯỢNG =====
def handle_quantity(update, context):
    user_id = update.effective_user.id
    text = update.message.text.strip()

    if user_id not in WAITING_QTY:
        return

    pid = WAITING_QTY[user_id]
    product = PRODUCTS[pid]

    try:
        qty = int(text)
    except ValueError:
        update.message.reply_text("⚠ Vui lòng nhập số nguyên (1, 2, 3 ...)")
        return

    if qty <= 0:
        update.message.reply_text("⚠ Số lượng phải lớn hơn 0.")
        return

    stock_list = STOCK.get(pid, [])
    if len(stock_list) < qty:
        update.message.reply_text(f"⚠ Kho chỉ còn {len(stock_list)} tài khoản.")
        return

    amount = product["price"] * qty
    order_code = gen_order_code()

    # Lưu order vào context để nút Hủy xóa đúng
    context.user_data["order"] = (pid, order_code, qty, amount)

    # ✅ LƯU ĐƠN CHỜ THANH TOÁN NGAY (SePay bank xong auto nhả)
    with PENDING_LOCK:
        PENDING_ORDERS[order_code] = {
            "product_id": pid,
            "user_id": user_id,
            "qty": qty,
            "amount": amount,
            "delivered": False,
        }

    print(
        f"[ORDER] Pending saved: {order_code} user={user_id} pid={pid} qty={qty} amount={amount}",
        flush=True
    )

    WAITING_QTY.pop(user_id, None)

    qr_url = build_vietqr_url(amount, order_code)

    info = (
        f"✅ Đã tạo đơn *{order_code}*\n"
        f"Sản phẩm: *{product['name']}*\n"
        f"Số lượng: *{qty}*\n"
        f"Đơn giá: *{product['price']:,}đ*\n"
        f"Tổng tiền: *{amount:,}đ*\n\n"
        "🏦 Quét QR ở tin nhắn tiếp theo để thanh toán.\n"
        f"📌 Nội dung chuyển khoản: *{order_code}*\n\n"
        "Sau khi chuyển xong, bấm *Tôi đã chuyển tiền* (hoặc cứ để hệ thống tự xử lý)."
    ).replace(",", ".")

    keyboard = [
        [InlineKeyboardButton("✅ Tôi đã chuyển tiền", callback_data="confirm")],
        [InlineKeyboardButton("❌ Hủy đơn", callback_data="cancel")],
    ]

    update.message.reply_text(
        info,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

    caption = (f"◼️ Quét QR để thanh toán {amount:,}đ\nNội dung: {order_code}").replace(",", ".")
    update.message.reply_photo(photo=qr_url, caption=caption)


# ===== MAIN =====
def main():
    global TG_BOT

    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN is missing. Hãy export BOT_TOKEN hoặc set trong .env rồi source .env")

    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    # Gán bot cho webhook dùng
    TG_BOT = updater.bot

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("menu", start))
    dp.add_handler(CommandHandler("broadcast", broadcast))
    dp.add_handler(CallbackQueryHandler(handle_buttons))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_quantity))

    # Chạy Flask webhook trong thread
    def run_webhook():
        app.run(host="0.0.0.0", port=8080)

    threading.Thread(target=run_webhook, daemon=True).start()

    print("BOT ĐANG CHẠY...")
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
