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
    "veo3_ultra_bh": [
        "sam@dto22aomcee.top|dtdt4994",
"ray@dto22aomcee.top|dtdt4994",
"lee@dto22aomcee.top|dtdt4994",
"sky@dto22aomcee.top|dtdt4994",
"ash@dto22aomcee.top|dtdt4994",
"kai@dto22aomcee.top|dtdt4994",
"jay@dto22aomcee.top|dtdt4994",
"max@dto22aomcee.top|dtdt4994",
"neo@dto22aomcee.top|dtdt0880",
"lux@dto22aomcee.top|dtdt0880",
"zen@dto22aomcee.top|dtdt0880",
"eli@dto22aomcee.top|dtdt0880",
"ren@dto22aomcee.top|dtdt0880",
"rio@dto22aomcee.top|dtdt0880",
"sol@dto22aomcee.top|dtdt0880",
"ari@dto22aomcee.top|dtdt0880",
"nova@dto22aomcee.top|dtdt0880",
"quinn@dto22aomcee.top|dtdt0880",
"blake@dto22aomcee.top|dtdt0880",
"casey@dto22aomcee.top|dtdt0880",
"jordan@dto22aomcee.top|dtdt0880",
"taylor@dto22aomcee.top|dtdt0880",
"morgan@dto22aomcee.top|dtdt0880",
"reese@dto22aomcee.top|dtdt0880",
"rowan@dto22aomcee.top|dtdt0880",
"parker@dto22aomcee.top|dtdt0880",
"logan@dto22aomcee.top|dtdt0880",
"avery@dto22aomcee.top|dtdt0880",
"sage@dto22aomcee.top|dtdt0880",
"drew@dto22aomcee.top|dtdt0880",
"lane@dto22aomcee.top|dtdt0880",
"finn@dto22aomcee.top|dtdt0880",
"jules@dto22aomcee.top|dtdt0880",
"scout@dto22aomcee.top|dtdt0880",
"river@dto22aomcee.top|dtdt0880",
"dakota@dto22aomcee.top|dtdt0880",
"cameron@dto22aomcee.top|dtdt0880",
"rory@dto22aomcee.top|dtdt0880",
"charlie@dto22aomcee.top|dtdt0880",
"xako@dto22aomcee.top|dtdt0880",
"zimin@dto22aomcee.top|dtdt0880",
"linka@dto22aomcee.top|dtdt0880",
"atem@dto22aomcee.top|dtdt0880",
"nin@dto22aomcee.top|dtdt0880",
"gum@dto22aomcee.top|dtdt0880",
"halie@dto22aomcee.top|dtdt0880",
"mfie@dto22aomcee.top|dtdt0880",
    ],
    "veo3_ultra_bhf": [
        "gnxwulk@apojwwlssoo22a.shop|dtdt0880",
"jzsguml@apojwwlssoo22a.shop|dtdt0880",
"tntjxqp@apojwwlssoo22a.shop|dtdt0880",
"onppxig@apojwwlssoo22a.shop|dtdt0880",
"wdofwzl@apojwwlssoo22a.shop|dtdt0880",
"xxugpyd@apojwwlssoo22a.shop|dtdt0880",
"lmynjaz@apojwwlssoo22a.shop|dtdt0880",
"xiegyig@apojwwlssoo22a.shop|dtdt0880",
"rfpweqq@apojwwlssoo22a.shop|dtdt0880",
"nbtsxdi@apojwwlssoo22a.shop|dtdt0880",
"wviwwcg@apojwwlssoo22a.shop|dtdt0880",
"dpitlwf@apojwwlssoo22a.shop|dtdt0880",
"inqnaxt@apojwwlssoo22a.shop|dtdt0880",
"mzbdtmr@apojwwlssoo22a.shop|dtdt0880",
"krqizwf@apojwwlssoo22a.shop|dtdt0880",
"voexirq@apojwwlssoo22a.shop|dtdt0880",
"gmzwrws@apojwwlssoo22a.shop|dtdt0880",
"pyryyof@apojwwlssoo22a.shop|dtdt0880",
"qmqfuaz@apojwwlssoo22a.shop|dtdt0880",
"advotjc@apojwwlssoo22a.shop|dtdt0880",
"ajpmiek@apojwwlssoo22a.shop|dtdt0880",
"wcqiypi@apojwwlssoo22a.shop|dtdt0880",
"owfbaoi@apojwwlssoo22a.shop|dtdt0880",
"ikhnwhm@apojwwlssoo22a.shop|dtdt0880",
"latubhf@apojwwlssoo22a.shop|dtdt0880",
"uzdcsyi@apojwwlssoo22a.shop|dtdt0880",
"gtdmehy@apojwwlssoo22a.shop|dtdt0880",
"usvdobw@apojwwlssoo22a.shop|dtdt0880",
"vmbwltn@apojwwlssoo22a.shop|dtdt0880",
"rezcasp@apojwwlssoo22a.shop|dtdt0880",
"givadvs@apojwwlssoo22a.shop|dtdt0880",
"alcoejq@apojwwlssoo22a.shop|dtdt0880",
"rquromo@apojwwlssoo22a.shop|dtdt0880",
"pgwmqjt@apojwwlssoo22a.shop|dtdt0880",
"voxhklm@apojwwlssoo22a.shop|dtdt0880",
"zqxcgnd@apojwwlssoo22a.shop|dtdt0880",
"rtwxvio@apojwwlssoo22a.shop|dtdt0880",
"gmjzqte@apojwwlssoo22a.shop|dtdt0880",
"hbvgtku@apojwwlssoo22a.shop|dtdt0880",
"fqqbbiw@apojwwlssoo22a.shop|dtdt0880",
"uyzkfow@apojwwlssoo22a.shop|dtdt0880",
"biqmcwe@apojwwlssoo22a.shop|dtdt0880",
"ogdynyp@apojwwlssoo22a.shop|dtdt0880",
"povhigs@apojwwlssoo22a.shop|dtdt0880",
"sqkezhv@apojwwlssoo22a.shop|dtdt0880"
""enatlqo@apojwwlssoo22a.shop|dtdt0880",
"tohscwq@apojwwlssoo22a.shop|dtdt0880",
"usnoqfv@apojwwlssoo22a.shop|dtdt0880",
"himoe@apojwwlssoo22a.shop|dtdt0880",

    ],
    "info_1": ["IB"] * 0,
    "info_2": ["IB"] * 0,
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
