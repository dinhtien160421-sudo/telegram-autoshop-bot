from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
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
    "capcut":     {"name": "Capcut Pro Team 27D",            "price": 25000},
    "Canva_Edu":  {"name": "Canva Edu 500 Slot BH 30D",      "price": 70000},
    "code_gpt":   {"name": "CODE GPT PLUS",                  "price": 12000},
    "gemini_edu": {"name": "GEMINI PRO EDU 1 NĂM BH Login 24h",    "price": 45000},
    "veo3_ultra": {"name": "GEMINI VEO3 ULTRA 45K CREDIT 30D",   "price": 50000},
}

# Kho hàng
STOCK = {
    "capcut": [
        
    ],
    
    "Canva_Edu": [
        "nonibonetti8660@hotmail.com|37892MTr|M.C550_BAY.0.U.-Cj506SrReqrbNV5qxWuseop86KkESB84064132lNzZnrBrg2Zw11gbo1DJwJNotc6RUy2LqwsC27YFSbnjduddvYaPfJDOhlPcgTLX9sUwjiSze2YLQYLpREUhjekPS1RGAG0GiKu1!6nvFx*8ydcVqAcg7aUmhfTET4EWZo7K41WfQD7Q7rLncrh0RctKB7RPHnbJNlYw3aM6u7M4Tz*S2M7GCPNwSwSH3nX73vEFUuOLqLaG0OHRHbjETOn0PbQQvsNg0HKYJZdK6UGyPiIfFOlwrqFM1FT9XnJDpEYArLh5LuHBJou5I0AzerQMzHZs57MJZM6Y9NuGRoJgFm2PUvMCRrKgkway*r1*b5EquZE9juH03DJE1RXr57MhWW2ar5JLrzX913bjZnKOLXB*Jd55b6Ls9moYVE3BkolwJc|9e5f94bc-e8a4-4e73-b8be-63364c29d753|hjwws8jtw2m@smvmail.com",
    ],

    "code_gpt": [               
        "chatgpt.com/p/A72Q9HRT766X9HS2",
        "chatgpt.com/p/GC4LEU62HYXNDS3W",
        "chatgpt.com/p/73GG4U9QAR3ZZ6W4",
        "chatgpt.com/p/NQC3TNJMD6JRMGCB",
        "chatgpt.com/p/26VQ38KAAXJ4QBFE",
        "chatgpt.com/p/MJYQ7QN4R5LTVPUH",
        "chatgpt.com/p/SRTM89HSEPVTUXZ8",
        "chatgpt.com/p/6D46XBSSU34ECL2Q",
        "chatgpt.com/p/JK8UX652TL3MFV6P",
    ],

    "gemini_edu": [
        "bhoa26808@gmail.com|thanhngan@22|2pob ktda o6xq kh66 gkby tmmd gfsr oojh",
            
     ],

    "veo3_ultra": [    
        "ztkim2@napos.dpdns.org|dtdt2525",
        "rinke1@napos.dpdns.org|Mj*8jQBADBJL5eN=",
        "lindt2@napos.dpdns.org|EZ9CMhY<RCA<2uB&",
        "htyuw1@napos.dpdns.org|5ddaFj2j>5db8mT&",
        "znxmz1@napos.dpdns.org|AADFHKRZqqVF6nU%",
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

        # Hết hàng
        if len(STOCK[pid]) == 0:
            query.message.reply_text(
                f"❌ Sản phẩm *{product['name']}* đã hết hàng.",
                parse_mode="Markdown",
            )
            return

        # Tạo mã đơn và lưu tạm
        order_code = gen_order_code()
        context.user_data["order"] = (pid, order_code)

        amount = product["price"]
        qr_url = build_vietqr_url(amount, order_code)

        # Tin 1: Thông tin đơn
        info = (
            f"✅ Đã tạo đơn *{order_code}*\n"
            f"Số tiền: *{amount:,}đ*\n\n"
            "🏦 Thông tin chuyển khoản\n"
            "Vui lòng QUÉT MÃ QR ở tin nhắn tiếp theo để thanh toán.\n\n"
            f"📌 Nội dung: *{order_code}*\n\n"
            "Sau khi chuyển khoản xong, bấm *Tôi đã chuyển tiền*."
        ).replace(",", ".")

        keyboard = [
            [InlineKeyboardButton("✅ Tôi đã chuyển tiền", callback_data="confirm")],
            [InlineKeyboardButton("❌ Hủy đơn", callback_data="cancel")],
        ]

        query.message.reply_text(
            info,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

        # Tin 2: QR
        caption = (
            f"◼️ Quét QR để thanh toán {amount:,}đ\n"
            f"Nội dung: {order_code}"
        ).replace(",", ".")

        query.message.reply_photo(photo=qr_url, caption=caption)
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

        pid, code = context.user_data["order"]
        product = PRODUCTS[pid]
        user_id = query.message.chat_id

        # Lưu đơn vào danh sách CHỜ DUYỆT
        PENDING_ORDERS[code] = {
            "product_id": pid,
            "user_id": user_id,
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
            f"User ID: `{user_id}`\n\n"
            "Vui lòng mở app ngân hàng để kiểm tra.\n"
            "Nếu đã nhận tiền, bấm *Duyệt* để bot tự gửi tài khoản/mã cho khách."
        )

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
        product = PRODUCTS[pid]

        # Kiểm tra kho
        if len(STOCK[pid]) == 0:
            context.bot.send_message(
                chat_id=user_id,
                text="⚠ Xin lỗi, kho đã hết hàng. Vui lòng liên hệ admin để được xử lý.",
            )
            query.message.reply_text("❌ Duyệt thất bại: kho đã hết hàng.")
            return

        # Lấy tài khoản / code đầu tiên
        account = STOCK[pid].pop(0)

        # Tin nhắn gửi cho KHÁCH
        detail = (
            f"✅ Đơn `{code}`\n"
            f"🎁 Sản phẩm: *{product['name']}*\n\n"
            f"`{account}`\n\n"
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
            f"Tài khoản/Mã:\n{account}\n"
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
        query.message.reply_text(f"✅ Đã duyệt và giao hàng cho user {user_id}.")
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


# ===== MAIN =====

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("menu", menu))
    dp.add_handler(CommandHandler("broadcast", broadcast))   # lệnh gửi tin hàng loạt
    dp.add_handler(CallbackQueryHandler(handle_buttons))

    print("BOT ĐANG CHẠY...")
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
