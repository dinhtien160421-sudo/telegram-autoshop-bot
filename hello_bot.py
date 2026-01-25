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

# ============= CẤU HÌNH =============
BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_CHAT_ID = 6164122466
PENDING_ORDERS = {}
BANK_CODE = "ACB"
BANK_ACCOUNT = "21812351"
ADMIN_CONTACT = "Liên hệ Zalo: 0842108959"
USERS_FILE = "users.txt"

# user đang được hỏi số lượng: user_id -> product_id
WAITING_QTY = {}
# ====================================


# ===== LƯU USER =====
def add_user(chat_id: int):
    ids = set()
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    ids.add(int(line))

    if chat_id not in ids:
        ids.add(chat_id)
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            for uid in ids:
                f.write(str(uid) + "\n")


# ===== SẢN PHẨM =====
PRODUCTS = {
    "code_gpt": {
        "name": "CODE GPT PLUS",
        "price": 15000,
    },
    "veo3_ultra_bh": {
        "name": "Veo3 Ultra 45K cre BH 4/2",
        "price": 75000,
    },
    "veo3_ultra_bhf": {
        "name": "Veo3 Ultra 45K cre BH 30D",
        "price": 130000,
    },
    "info_1": {
        "name": "Gia hạn GPT Plus – Capcut - Canva Ib",
        "price": 0,
    },
    "info_2": {
        "name": "Zalo: 0842.108.959 - Tele:@dtdt28",
        "price": 0,
    },
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
"leno@sneel61512.tahsdwssd.name.ng|dtdt0440",
"zixo@sneel61512.tahsdwssd.name.ng|dtdt0440",
"kavoa@sneel61512.tahsdwssd.name.ng|dtdt0440",
"rexo@sneel61512.tahsdwssd.name.ng|dtdt0440",
"biro@sneel61512.tahsdwssd.name.ng|dtdt0440",
"viro@sneel61512.tahsdwssd.name.ng|dtdt0440",
"nexo@sneel61512.tahsdwssd.name.ng|dtdt0440",
"zimo@sneel61512.tahsdwssd.name.ng|dtdt0440",
"laxo@sneel61512.tahsdwssd.name.ng|dtdt0440",
"nira@sneel61512.tahsdwssd.name.ng|dtdt0440",
"bexo@sneel61512.tahsdwssd.name.ng|dtdt0440",
"ximu@sneel61512.tahsdwssd.name.ng|dtdt0440",
"drax@sneel61512.tahsdwssd.name.ng|dtdt0440",
"meko@sneel61512.tahsdwssd.name.ng|dtdt0440",
"qor@sneel61512.tahsdwssd.name.ng|dtdt0440",
"vemi@sneel61512.tahsdwssd.name.ng|dtdt0440",
"nami@sneel61512.tahsdwssd.name.ng|dtdt0440",
"sijoee@sneel61512.tahsdwssd.name.ng|dtdt0440",
"aomo@sneel61512.tahsdwssd.name.ng|dtdt0440",
"ziom@sneel61512.tahsdwssd.name.ng|dtdt0440",
"poter@sneel61512.tahsdwssd.name.ng|dtdt0440",
"zine@sneel61512.tahsdwssd.name.ng|dtdt0440",
"emo@dtskoaa2oimae.shop|dtdt0440",
"zin@dtskoaa2oimae.shop|dtdt0440",
"tico@dtskoaa2oimae.shop|dtdt0440",
"zomi@dtskoaa2oimae.shop|dtdt0440",
"tim@dtskoaa2oimae.shop|dtdt0440",
"giru@dtskoaa2oimae.shop|dtdt0440",
"lope@dtskoaa2oimae.shop|dtdt0440",
"haie@dtskoaa2oimae.shop|dtdt0440",
"zine@dtskoaa2oimae.shop|dtdt0440",
"giee@dtskoaa2oimae.shop|dtdt0440",
"zora@dtskoaa2oimae.shop|dtdt0440",
"yexo@dtskoaa2oimae.shop|dtdt0440",
"wexo@dtskoaa2oimae.shop|dtdt0440",
"veko@dtskoaa2oimae.shop|dtdt0440",
"uxel@dtskoaa2oimae.shop|dtdt0440",
"tyn@dtskoaa2oimae.shop|dtdt0440",
    ],
    "veo3_ultra_bhf": [
"umea@dtskoaa2oimae.shop|dtdt0440",
"varn@dtskoaa2oimae.shop|dtdt0440",
"nirae@dtskoaa2oimae.shop|dtdt0440",
"mirok@dtskoaa2oimae.shop|dtdt0440",
"leto@dtskoaa2oimae.shop|dtdt0440",
"kora@dtskoaa2oimae.shop|dtdt0440",
"jexo@dtskoaa2oimae.shop|dtdt0440",
"ilya@dtskoaa2oimae.shop|dtdt0440",
"hemi@dtskoaa2oimae.shop|dtdt0440",
"garo@dtskoaa2oimae.shop|dtdt0440",
"sorae@dtskoaa2oimae.shop|dtdt0440",
"ryn@dtskoaa2oimae.shop|dtdt0440",
"qelo@dtskoaa2oimae.shop|dtdt0440",
"pryo@dtskoaa2oimae.shop|dtdt0440",
"orzo@dtskoaa2oimae.shop|dtdt0440",

    ],
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
                context.bot.send_message(
                    chat_id=uid,
                    text=message,
                    disable_web_page_preview=True
                )
                sent += 1
            except Exception:
                continue

    msg.reply_text(f"✅ Đã gửi cho khoảng {sent} người dùng.")


# ===== XỬ LÝ NÚT =====
def handle_buttons(update, context):
    query = update.callback_query
    data = query.data
    query.answer()

    # ===== CHỌN SẢN PHẨM =====
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

    # ===== HỦY =====
    if data == "cancel":
        context.user_data.clear()
        query.message.reply_text("❌ Bạn đã hủy đơn.")
        return

    # ===== XÁC NHẬN CHUYỂN TIỀN =====
    if data == "confirm":
        if "order" not in context.user_data:
            query.message.reply_text("⚠️ Không tìm thấy đơn đang chờ.")
            return

        pid, code, qty, amount = context.user_data["order"]
        product = PRODUCTS[pid]
        user_id = query.message.chat_id

        PENDING_ORDERS[code] = {
            "product_id": pid,
            "user_id": user_id,
            "qty": qty,
        }

        query.message.reply_text(
            "🤖 Cảm ơn bạn! Hệ thống đã nhận yêu cầu.\n"
            "Admin sẽ kiểm tra thanh toán và gửi tài khoản/mã cho bạn sau ít phút."
        )

        admin_text = (
            "🔔 *KHÁCH BÁO ĐÃ CHUYỂN TIỀN*\n\n"
            f"Đơn: `{code}`\n"
            f"Sản phẩm: *{product['name']}*\n"
            f"Số lượng: *{qty}*\n"
            f"Tổng tiền: *{amount:,}đ*\n"
            f"User ID: `{user_id}`\n\n"
            "Nếu đã nhận tiền, bấm *Duyệt* để bot gửi tài khoản cho khách."
        ).replace(",", ".")

        admin_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"✅ Duyệt {code}", callback_data=f"approve_{code}")],
            [InlineKeyboardButton(f"❌ Từ chối {code}", callback_data=f"reject_{code}")],
        ])

        context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=admin_text,
            parse_mode="Markdown",
            reply_markup=admin_keyboard,
        )

        context.user_data.clear()
        return

        # ===== ADMIN BẤM DUYỆT ĐƠN =====
    if data.startswith("approve_"):
        code = data.replace("approve_", "")
        order = PENDING_ORDERS.pop(code, None)

        if not order:
            query.message.reply_text(f"⚠️ Không tìm thấy đơn {code} trong hàng chờ.")
            return

        pid = order["product_id"]
        user_id = order["user_id"]
        qty = order.get("qty", 1)
        product = PRODUCTS[pid]

        # Kiểm tra kho đủ số lượng không
        if len(STOCK.get(pid, [])) < qty:
            context.bot.send_message(
                chat_id=user_id,
                text="⚠ Xin lỗi, kho hiện không đủ số lượng bạn đặt. "
                     "Vui lòng liên hệ admin để được xử lý.",
            )
            query.message.reply_text(
                f"❌ Duyệt thất bại: kho chỉ còn {len(STOCK.get(pid, []))} tài khoản."
            )
            return

        # Lấy ra qty tài khoản từ kho
        accounts = [STOCK[pid].pop(0) for _ in range(qty)]
        codes_text = "\n".join(f"{i + 1}. {acc}" for i, acc in enumerate(accounts))

        # Tin nhắn gửi cho KHÁCH
        detail = (
            f"✅ Đơn `{code}`\n"
            f"🎁 Sản phẩm: *{product['name']}*\n"
            f"📦 Số lượng: *{qty}*\n\n"
            f"{codes_text}\n\n"
            "Cảm ơn bạn đã mua hàng!"
        )

        context.bot.send_message(
            chat_id=user_id,
            text=detail,
            parse_mode="Markdown",
        )

        # ===== GỬI FILE TXT (NOTEPAD) =====
        txt = (
            f"Đơn hàng: {code}\n"
            f"Sản phẩm: {product['name']}\n"
            f"Số lượng: {qty}\n"
            f"Tài khoản/Mã:\n{codes_text}\n"
        ).encode("utf-8")

        f = BytesIO(txt)
        f.name = f"{code}.txt"

        context.bot.send_document(
            chat_id=user_id,
            document=InputFile(f),
            filename=f.name,
            caption="📄 File Notepad chứa tài khoản/mã.",
        )

        # Báo lại cho admin
        query.message.reply_text(
            f"✅ Đã duyệt và giao {qty} tài khoản cho user {user_id}."
        )
        return

        
        return

    # ===== ADMIN TỪ CHỐI =====
    if data.startswith("reject_"):
        code = data.replace("reject_", "")
        order = PENDING_ORDERS.pop(code, None)

        if not order:
            query.message.reply_text(f"⚠️ Không tìm thấy đơn {code}.")
            return

        user_id = order["user_id"]

        context.bot.send_message(
            chat_id=user_id,
            text=(
                f"❌ Đơn `{code}` đã bị từ chối.\n"
                "Nếu bạn đã chuyển tiền, vui lòng liên hệ admin."
            ),
            parse_mode="Markdown",
        )

        query.message.reply_text(f"❌ Đã từ chối đơn {code}.")
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
        update.message.reply_text(
            f"⚠ Kho chỉ còn {len(stock_list)} tài khoản."
        )
        return

    amount = product["price"] * qty
    order_code = gen_order_code()

    context.user_data["order"] = (pid, order_code, qty, amount)
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
        "Sau khi chuyển xong, bấm *Tôi đã chuyển tiền*."
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

    caption = (
        f"◼️ Quét QR để thanh toán {amount:,}đ\n"
        f"Nội dung: {order_code}"
    ).replace(",", ".")

    update.message.reply_photo(photo=qr_url, caption=caption)


# ===== MAIN =====
def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("menu", start))
    dp.add_handler(CommandHandler("broadcast", broadcast))
    dp.add_handler(CallbackQueryHandler(handle_buttons))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_quantity))

    print("BOT ĐANG CHẠY...")
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
