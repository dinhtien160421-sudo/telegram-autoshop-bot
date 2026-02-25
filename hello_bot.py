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
USERS_FILE = "users.txt"

# user đang được hỏi số lượng: user_id -> product_id
WAITING_QTY = {}

# ĐƠN CHỜ THANH TOÁN (SePay sẽ gọi webhook để auto nhả)
# order_code -> {product_id, user_id, qty, amount}
PENDING_ORDERS = {}

# ===== SẢN PHẨM =====
PRODUCTS = {
    "veo3_pro_bh": {"name": "Veo3 Pro 25K cre BH 24H", "price": 50000},
    "canva_pro_1m": {"name": "Canva Pro 30D BHF", "price": 25000},
    "canva_pro_6m": {"name": "Canva Pro 6 THÁNG BHF", "price": 100000},
    "info_2": {"name": "Capcut Pro Team 30-35D BHF", "price": 18000},
    "info_3": {"name": "Capcut Pro Team 6 THÁNG BHF", "price": 90000},
    "info_4": {"name": "Zalo: 0842.108.959 - Tele:@dtdt28", "price": 0},
}

# ===== KHO =====
STOCK = {
    "veo3_pro_bh":[    
    "zedlrcgj7@sk.pmhveo.pro.vn|ThaoYenHiep@999",
"zedyicryz@sk.pmhveo.pro.vn|ThaoYenHiep@999",
"zedtupu1i@sk.pmhveo.pro.vn|ThaoYenHiep@999",
"zeda6vuco@sk.pmhveo.pro.vn|ThaoYenHiep@999",
"zedhouy66@sk.pmhveo.pro.vn|ThaoYenHiep@999",
"zedtnftrb@sk.pmhveo.pro.vn|ThaoYenHiep@999",
"zedr6m0n9@sk.pmhveo.pro.vn|ThaoYenHiep@999",
"zedctlbr7@sk.pmhveo.pro.vn|ThaoYenHiep@999",
"zed8t64x0@sk.pmhveo.pro.vn|ThaoYenHiep@999",
"zedt0jjs6@sk.pmhveo.pro.vn|ThaoYenHiep@999",
"zednp2awf@sk.pmhveo.pro.vn|ThaoYenHiep@999",
"zeds5sg7k@sk.pmhveo.pro.vn|ThaoYenHiep@999",
"zeduzker4@sk.pmhveo.pro.vn|ThaoYenHiep@999",
"zed97rmu0@sk.pmhveo.pro.vn|ThaoYenHiep@999",
"zeduxj769@sk.pmhveo.pro.vn|ThaoYenHiep@999",
"zedc99h0f@sk.pmhveo.pro.vn|ThaoYenHiep@999",
"zedyq3rmk@sk.pmhveo.pro.vn|ThaoYenHiep@999",
"zeduk69zm@sk.pmhveo.pro.vn|ThaoYenHiep@999",
"zed8msqhv@sk.pmhveo.pro.vn|ThaoYenHiep@999",
"zedcv0jr0@sk.pmhveo.pro.vn|ThaoYenHiep@999",
"zedlfs2x8@sk.pmhveo.pro.vn|ThaoYenHiep@999",
"zedzijcuf@sk.pmhveo.pro.vn|ThaoYenHiep@999",
"zedmjbimx@sk.pmhveo.pro.vn|ThaoYenHiep@999",
"zed6uebdy@sk.pmhveo.pro.vn|ThaoYenHiep@999",
"zedmb7yeg@sk.pmhveo.pro.vn|ThaoYenHiep@999",
"zedv5d7qw@sk.pmhveo.pro.vn|ThaoYenHiep@999",
"zedy2laz3@sk.pmhveo.pro.vn|ThaoYenHiep@999",
"zedsel9ib@sk.pmhveo.pro.vn|ThaoYenHiep@999",
"zedizbek0@sk.pmhveo.pro.vn|ThaoYenHiep@999",
"zed7df4z0@sk.pmhveo.pro.vn|ThaoYenHiep@999",
"zedoutz95@sk.pmhveo.pro.vn|ThaoYenHiep@999",
"zedg4i6nc@sk.pmhveo.pro.vn|ThaoYenHiep@999",
"zeduz1hn8@sk.pmhveo.pro.vn|ThaoYenHiep@999",
"zedx41bnq@sk.pmhveo.pro.vn|ThaoYenHiep@999",
"zedd8jpff@sk.pmhveo.pro.vn|ThaoYenHiep@999",
"zed9k6knt@sk.pmhveo.pro.vn|ThaoYenHiep@999",
"zed6sty8u@sk.pmhveo.pro.vn|ThaoYenHiep@999",
"zedxjrrzu@sk.pmhveo.pro.vn|ThaoYenHiep@999"

    ],
    
    "canva_pro_1m": [
    "nilsondh53coe@hotmail.com|dtdt2992",
    "mullins359lmuniz@hotmail.com|dtdt2992",
    "kariwalter88n@hotmail.com|dtdt2992",
    "meeksnqykane@hotmail.com|dtdt2992",
    "garvinisom2j1@hotmail.com|dtdt2992"
    ],
    "canva_pro_6m": [
    "givens1rhharp@hotmail.com|dtdt2992"
     ], 
    "info_2": [
    "mayra45@mmoninja.pics|123456",
    "rico25@oceanbreezehub.space|123456",
    "brandynf@happyzoomer.us|123456",
    "sheldond@tinybizhub.xyz|123456",
    "yessenia@greenbudgetstore.online|123456"
     ],
     "info_3": [
     "sjmrb44@abe26.tempdukviet.site|a123456",
     "svkfk88@abe18.tempdukviet.site|a123456"
     ],
    
    "info_4": ["IB"] * 0,
}

# ====== SEPAY WEBHOOK (AUTO NHẢ ĐƠN) ======
app = Flask(__name__)
TG_BOT = None


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
                    except:
                        pass

    if chat_id not in ids:
        ids.add(chat_id)
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            for uid in ids:
                f.write(str(uid) + "\n")


# ===== BROADCAST (ADMIN) =====
def broadcast(update, context):
    chat_id = update.effective_chat.id

    if chat_id != ADMIN_CHAT_ID:
        update.message.reply_text("❌ Bạn không có quyền dùng lệnh này.")
        return

    msg = update.message

    # Reply vào tin nhắn: lấy text hoặc caption (để reply ảnh/caption cũng gửi được)
    if msg.reply_to_message:
        message = msg.reply_to_message.text or msg.reply_to_message.caption
    else:
        # /broadcast <nội dung>
        if not context.args:
            msg.reply_text(
                "⚠ Dùng:\n"
                "- /broadcast nội_dung\n"
                "- Hoặc reply vào tin nhắn cần gửi rồi gõ /broadcast"
            )
            return
        message = msg.text.partition(" ")[2]

    if not message:
        msg.reply_text("⚠ Không lấy được nội dung tin nhắn để gửi (reply ảnh thì phải có caption).")
        return

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
                context.bot.send_message(
                    chat_id=uid,
                    text=message,
                    disable_web_page_preview=True
                )
                sent += 1
            except Exception:
                # user block bot / id lỗi / rate limit... bỏ qua
                continue

    msg.reply_text(f"✅ Đã gửi cho khoảng {sent} người dùng.")


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


def deliver_order_auto(code: str, pid: str, user_id: int, qty: int):
    """Nhả đơn + gửi file txt"""
    product = PRODUCTS[pid]

    if len(STOCK.get(pid, [])) < qty:
        TG_BOT.send_message(chat_id=user_id, text="⚠ Kho không đủ số lượng. Liên hệ admin.")
        return False

    accounts = [STOCK[pid].pop(0) for _ in range(qty)]
    codes_text = "\n".join(f"{i+1}. {acc}" for i, acc in enumerate(accounts))

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
        disable_web_page_preview=True
    )

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


@app.route("/bank-webhook", methods=["POST"])
def sepay_webhook():
    data = request.get_json(force=True, silent=True) or {}
    print("\n==== SEPAY PAYLOAD ====")
    print(data, flush=True)

    # chỉ nhận tiền vào
    if str(data.get("transferType", "")).lower() != "in":
        return jsonify({"ok": True, "ignored": "not_in"}), 200

    content = str(data.get("content", ""))
    amount = int(data.get("transferAmount", 0) or 0)

    # tìm ORDxxxxxxxxxx trong nội dung chuyển khoản
    m = re.search(r"(ORD\d{10})", content)
    if not m:
        return jsonify({"ok": True, "ignored": "no_ord"}), 200

    code = m.group(1)
    print(f"Tìm thấy đơn: {code}", flush=True)

    order = PENDING_ORDERS.get(code)
    if not order:
        print(f"Không có đơn chờ: {code}", flush=True)
        return jsonify({"ok": True, "ignored": "order_not_found"}), 200

    pid = order["product_id"]
    user_id = int(order["user_id"])
    qty = int(order.get("qty", 1))
    expected = int(order.get("amount", PRODUCTS[pid]["price"] * qty))

    if amount < expected:
        TG_BOT.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=f"⚠ Đơn `{code}` thiếu tiền: {amount:,}đ / {expected:,}đ".replace(",", "."),
            parse_mode="Markdown"
        )
        return jsonify({"ok": True, "ignored": "insufficient"}), 200

    # tránh nhả trùng: pop trước
    PENDING_ORDERS.pop(code, None)

    ok = deliver_order_auto(code, pid, user_id, qty)
    if ok:
        TG_BOT.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=f"🤖 AUTO NHẢ `{code}` — đã giao {qty} cho `{user_id}`",
            parse_mode="Markdown"
        )
    else:
        # nếu fail thì đưa lại vào pending
        PENDING_ORDERS[code] = order

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


# ===== XỬ LÝ NÚT =====
def handle_buttons(update, context):
    query = update.callback_query
    data = query.data
    query.answer()

    # lưu user luôn cho chắc
    add_user(query.from_user.id)

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
            "👉 Nhập số nguyên, ví dụ: 1, 2, 3 ...",
            parse_mode="Markdown",
        )
        return


# ===== NHẬP SỐ LƯỢNG =====
def handle_quantity(update, context):
    user_id = update.effective_user.id
    add_user(user_id)

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

    # ✅ LƯU ĐƠN CHỜ THANH TOÁN NGAY → SePay bank xong auto nhả
    PENDING_ORDERS[order_code] = {
        "product_id": pid,
        "user_id": user_id,
        "qty": qty,
        "amount": amount,
    }
    print(f"[ORDER] Pending saved: {order_code} user={user_id} pid={pid} qty={qty} amount={amount}", flush=True)

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
        "✅ Chuyển đúng nội dung *ORD* là hệ thống *tự giao hàng* (không cần bấm gì thêm)."
    ).replace(",", ".")

    update.message.reply_text(info, parse_mode="Markdown")

    caption = (
        f"◼️ Quét QR để thanh toán {amount:,}đ\n"
        f"Nội dung: {order_code}"
    ).replace(",", ".")

    update.message.reply_photo(photo=qr_url, caption=caption)


# ===== MAIN =====
def main():
    global TG_BOT

    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN is missing. Hãy export BOT_TOKEN hoặc set trong .env")

    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    # gán bot cho webhook dùng
    TG_BOT = updater.bot

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("menu", start))
    dp.add_handler(CommandHandler("broadcast", broadcast))  # ✅ THÊM LẠI BROADCAST
    dp.add_handler(CallbackQueryHandler(handle_buttons))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_quantity))

    # chạy webhook sepay trong thread (CÙNG PROCESS với bot)
    def run_webhook():
        app.run(host="0.0.0.0", port=8080, threaded=True)

    threading.Thread(target=run_webhook, daemon=True).start()

    print("BOT ĐANG CHẠY...")
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
