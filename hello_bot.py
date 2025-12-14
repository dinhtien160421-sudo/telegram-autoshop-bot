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
BOT_TOKEN = "8376460284:AAFhM_HmBDVST1lYyICYGjLUFm9Dqg6WTag"
ADMIN_CHAT_ID = 6164122466          # ID admin
PENDING_ORDERS = {}                 # đơn đang chờ duyệt
BANK_CODE = "sacombank"
BANK_ACCOUNT = "0842108959"
ADMIN_CONTACT = "Liên hệ Zalo: 0842108959"
USERS_FILE = "users.txt"            # nơi lưu danh sách user

# user đang được hỏi số lượng: user_id -> product_id
WAITING_QTY = {}
# ====================================


def add_user(chat_id: int):
    """Lưu chat_id vào users.txt nếu chưa có."""
    ids = set()

    # đọc các id hiện có (nếu file đã tồn tại)
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    ids.add(int(line))

    # thêm id mới nếu chưa có
    if chat_id not in ids:
        ids.add(chat_id)
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            for uid in ids:
                f.write(str(uid) + "\n")


# Danh sách sản phẩm
PRODUCTS = {
    "Canva_Edu": {
        "name": "Canva Edu 500 Slot BH 30D",
        "price": 70000,
    },
    "code_gpt": {
        "name": "CODE GPT PLUS",
        "price": 15000,
    },
    "gemini_edu": {
        "name": "GEMINI PRO EDU 1 NĂM BH Login 24h",
        "price": 45000,
    },
    "veo3_ultra": {
        "name": "GEMINI VEO3 ULTRA 45K CREDIT 30D",
        "price": 50000,
	},
    "gpt_plus_30d": {                       
        "name": "ACC GPT PLUS 30D",
        "price": 45000,	
    },
}

# Kho hàng
STOCK = {
    "Canva_Edu": [
	"aerobikwa7643@hotmail.comcom|dOlL35h0|M.C533_SN1.0.U.-Ch8ZkhMHcRFhzUDWNQK!P3iDW1v1efsqFQ3LN2s*SJk0BG9e1PYWayzF0LZIYoP35PCLOWyTPJDYCr1lfZat4CepUWdk1BbJLhMOhk!J!TRTii*CMYFxjO*SpggIz9WRBsDvYWuTKQwSSXvydqUT4PqFnPxPGVfUpT0EJWL2x0NF25dLfb!0hwOAWce8DPEE53TLJ0NvsdXLvyKkjGmhvgNEGB8sCQzZ!S3SChAUy4UbduAw!j8BYnj6kMxewe0QkjRZVkBVNY9UAsiwQC7mplKjs7q5j8MEUyRGdZF0fztXJ1O11!H0MOmvo*0rNv7p2WEyrSVYfEwUZnf0f2DCbeZB7bEqPQe6jw5ZGdbr7xC4!cOBXh7MX!mYKCHv2Ms4CP9Ap1aqYTEZacxQDQSnitlXvNbwLKsrMn1m2Hvee6MKIahhjDdcu02j3oM!LpjByw$$|9e5f94bc-e8a4-4e73-b8be-63364c29d753|jajedxq5owk7@smvmail.com",	
        
    ],

    "code_gpt": [   
	"https://chatgpt.com/p/JU85JZDD4Y4R7TF4",
	"https://chatgpt.com/p/NSRZJYAQVR3QTFCB",
	"https://chatgpt.com/p/K6QKAQ3NZL32KRVC",
	"https://chatgpt.com/p/8KQSL7JQKCMXU2JL",
	"https://chatgpt.com/p/UN75QXSFQ753STG9",
    ],

    "gemini_edu": [
        # thêm hàng ở đây
    ],

    "veo3_ultra": [
	"dikomb@vivobooknet.com|dtdt0330",
	"vzezb@vivobooknet.com|dtdt0330",
	"xizop@vivobooknet.com|dtdt0330",
	"ezearl@vivobooknet.com|dtdt0330",
	"vrzez@vivobooknet.com|dtdt0330",

    ],
	
	"gpt_plus_30d": [
	"georgialippiapws@crispfeather.boats|111111111111|K7GSIGESBET6JJXUFOHFV632L4IXR5BY",
	"samuelsignorini4849@crispfeather.boats|111111111111|T6Q74GQBJVAKLOOAAW6QWCCT5UZD6LEI",
	],
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


# ===== LỆNH START + MENU =====


def start(update, context):
    chat_id = update.effective_chat.id
    add_user(chat_id)   # lưu người dùng vào users.txt

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


def menu(update, context):
    # cho tiện, /menu gọi lại /start
    return start(update, context)


# ===== LỆNH GỬI TIN TOÀN BỘ USER =====


def broadcast(update, context):
    chat_id = update.effective_chat.id

    # chỉ cho ADMIN dùng
    if chat_id != ADMIN_CHAT_ID:
        update.message.reply_text("❌ Bạn không có quyền dùng lệnh này.")
        return

    # lấy nội dung sau /broadcast
    if not context.args:
        update.message.reply_text("⚠ Dùng: /broadcast nội_dung_cần_gửi")
        return

    message = " ".join(context.args)

    # đọc danh sách user từ file
    if not os.path.exists(USERS_FILE):
        update.message.reply_text("Chưa có user nào trong danh sách.")
        return

    sent = 0
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                uid = int(line)
                context.bot.send_message(chat_id=uid, text=message)
                sent += 1
            except Exception:
                # user block bot hoặc lỗi khác thì bỏ qua
                continue

    update.message.reply_text(f"✅ Đã gửi cho khoảng {sent} người dùng.")


# ===== XỬ LÝ NÚT =====


def handle_buttons(update, context):
    query = update.callback_query
    data = query.data
    query.answer()

    # ===== Người dùng chọn sản phẩm =====
    if data.startswith("buy_"):
        pid = data.replace("buy_", "")
        product = PRODUCTS[pid]
        user_id = query.from_user.id

        # Hết hàng
        if len(STOCK.get(pid, [])) == 0:
            query.message.reply_text(
                f"❌ Sản phẩm *{product['name']}* đã hết hàng.",
                parse_mode="Markdown",
            )
            return

        # Ghi nhớ sản phẩm, chuẩn bị hỏi số lượng
        WAITING_QTY[user_id] = pid

        query.message.reply_text(
            f"Bạn muốn mua bao nhiêu *{product['name']}*?\n"
            f"Đơn giá: *{product['price']:,}đ* / 1 tài khoản.\n\n"
            "👉 Vui lòng nhập một số nguyên, ví dụ: 1, 2, 3 ...",
            parse_mode="Markdown",
        )
        return

    # ===== Hủy đơn =====
    if data == "cancel":
        context.user_data.clear()
        query.message.reply_text("❌ Bạn đã hủy đơn.")
        return

    # ===== KHÁCH BẤM "TÔI ĐÃ CHUYỂN TIỀN" =====
    if data == "confirm":
        if "order" not in context.user_data:
            query.message.reply_text("⚠️ Không tìm thấy đơn đang chờ.")
            return

        pid, code, qty, amount = context.user_data["order"]
        product = PRODUCTS[pid]
        user_id = query.message.chat_id

        # Lưu đơn vào danh sách CHỜ DUYỆT, kèm số lượng
        PENDING_ORDERS[code] = {
            "product_id": pid,
            "user_id": user_id,
            "qty": qty,
        }

        # Báo cho KHÁCH
        query.message.reply_text(
            "🤖 Cảm ơn bạn! Hệ thống đã nhận yêu cầu.\n"
            "Admin sẽ kiểm tra thanh toán và gửi tài khoản/mã cho bạn sau ít phút."
        )

        # Gửi cho ADMIN kèm nút DUYỆT / TỪ CHỐI
        admin_text = (
            "🔔 *KHÁCH BÁO ĐÃ CHUYỂN TIỀN*\n\n"
            f"Đơn: `{code}`\n"
            f"Sản phẩm: *{product['name']}*\n"
            f"Số lượng: *{qty}*\n"
            f"Tổng tiền: *{amount:,}đ*\n"
            f"User ID: `{user_id}`\n\n"
            "Vui lòng mở app ngân hàng để kiểm tra.\n"
            "Nếu đã nhận tiền, bấm *Duyệt* để bot tự gửi tài khoản/mã cho khách."
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

        # File txt gửi kèm
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

    # ===== ADMIN BẤM TỪ CHỐI ĐƠN =====
    if data.startswith("reject_"):
        code = data.replace("reject_", "")
        order = PENDING_ORDERS.pop(code, None)

        if not order:
            query.message.reply_text(f"⚠️ Không tìm thấy đơn {code} trong hàng chờ.")
            return

        user_id = order["user_id"]

        context.bot.send_message(
            chat_id=user_id,
            text=(
                f"❌ Đơn `{code}` đã bị từ chối.\n"
                "Nếu bạn đã chuyển tiền, vui lòng liên hệ admin để được hỗ trợ."
            ),
            parse_mode="Markdown",
        )

        query.message.reply_text(f"❌ Đã từ chối đơn {code}.")
        return


# ===== XỬ LÝ TEXT – NHẬP SỐ LƯỢNG =====


def handle_quantity(update, context):
    """Nhận tin nhắn text của user, nếu user đang trong WAITING_QTY thì coi là nhập số lượng."""
    user = update.effective_user
    user_id = user.id
    text = update.message.text.strip()

    # Nếu user không trong trạng thái chờ nhập số lượng thì bỏ qua
    if user_id not in WAITING_QTY:
        return

    pid = WAITING_QTY[user_id]
    product = PRODUCTS[pid]

    # cố gắng parse số lượng
    try:
        qty = int(text)
    except ValueError:
        update.message.reply_text(
            "⚠ Vui lòng nhập một *số nguyên* (1, 2, 3 ...)",
            parse_mode="Markdown",
        )
        return

    if qty <= 0:
        update.message.reply_text("⚠ Số lượng phải lớn hơn 0.")
        return

    # kiểm tra kho
    stock_list = STOCK.get(pid, [])
    if len(stock_list) < qty:
        update.message.reply_text(
            f"⚠ Kho hiện chỉ còn *{len(stock_list)}* tài khoản, không đủ {qty}. "
            "Bạn hãy nhập lại số lượng nhỏ hơn nha.",
            parse_mode="Markdown",
        )
        return

    # Tính tổng tiền
    amount = product["price"] * qty
    order_code = gen_order_code()

    # Lưu vào user_data để khi bấm 'Tôi đã chuyển tiền' còn biết pid/qty/amount
    context.user_data["order"] = (pid, order_code, qty, amount)

    # Sau khi tạo đơn thì không cần chờ số lượng nữa
    WAITING_QTY.pop(user_id, None)

    qr_url = build_vietqr_url(amount, order_code)

    info = (
        f"✅ Đã tạo đơn *{order_code}*\n"
        f"Sản phẩm: *{product['name']}*\n"
        f"Số lượng: *{qty}*\n"
        f"Đơn giá: *{product['price']:,}đ*\n"
        f"Tổng tiền: *{amount:,}đ*\n\n"
        "🏦 Thông tin chuyển khoản\n"
        "Vui lòng QUÉT MÃ QR ở tin nhắn tiếp theo để thanh toán.\n\n"
        f"📌 Nội dung: *{order_code}*\n\n"
        "Sau khi chuyển khoản xong, bấm *Tôi đã chuyển tiền*."
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
    dp.add_handler(CommandHandler("menu", menu))
    dp.add_handler(CommandHandler("broadcast", broadcast))   # lệnh gửi tin hàng loạt
    dp.add_handler(CallbackQueryHandler(handle_buttons))

    # Nhận tin nhắn text (không phải lệnh) để xử lý số lượng mua
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_quantity))

    print("BOT ĐANG CHẠY...")
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
