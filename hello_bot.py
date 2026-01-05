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
BOT_TOKEN = "8524709110:AAHWruvE7GOtTIk28-G--tgS1fthno0s2vM"
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
        "name": "Canva Edu 300 Slot BH 30D",
        "price": 70000,
    },
    "code_gpt": {
        "name": "CODE GPT PLUS",
        "price": 15000,
    },
    "veo3_ultra_30d": {
        "name": "VEO3 ULTRA 45K CREDIT BH 30D",
        "price": 50000,
    },
    "gpt_plus_30d": {
        "name": "ACC GPT PLUS 30D",
        "price": 35000,
	 },
}


# Kho hàng
STOCK = {
    "Canva_Edu": [ 
	"inge-lisev5555@hotmail.com|ResSb75L|bhzftzjqvb92@smvmail.com",
	"katulkajoa3569@hotmail.com|timeRais19|ewhgrtfy@smvmail.com",
    ],

    "code_gpt": [   
	"chatgpt.com/p/AUAX9NGJNJPYJ7HD",
	"chatgpt.com/p/EVLR9E9HVF7LMAPV",
	"chatgpt.com/p/GSZDVSEAC463JRVF",
	"chatgpt.com/p/HWWEFY6BVH2UANY2",
	

    ],

   "veo3_ultra_30d": [
"xenoa@ts.timball.cloud|dtdt4664"
"bex@glkzneder.tokyo|dtdt3443",
"ximo@glkzneder.tokyo|dtdt3443",
"tyn@glkzneder.tokyo|dtdt3443",
"salo@glkzneder.tokyo|dtdt3443",
"dex@glkzneder.tokyo|dtdt3443",
"zuvo@glkzneder.tokyo|dtdt3443",
"krel@glkzneder.tokyo|dtdt3443",
"ryn@glkzneder.tokyo|dtdt3443",
"laxo@glkzneder.tokyo|dtdt3443",
"vemi@glkzneder.tokyo|dtdt3443",
"qor@glkzneder.tokyo|dtdt3443",
"mixa@glkzneder.tokyo|dtdt3443",
"dirox@glkzneder.tokyo|dtdt3443",
"suni@glkzneder.tokyo|dtdt3443",
"xiroe@dtstorexmecae.click|dtdt3443",
"ravoa@dtstorexmecae.click|dtdt3443",
"kiroz@dtstorexmecae.click|dtdt3443",
"banu@dtstorexmecae.click|dtdt3443",
"vixo@dtstorexmecae.click|dtdt3443",
"tavoa@dtstorexmecae.click|dtdt3443",
"nemu@dtstorexmecae.click|dtdt3443",
"qaroa@dtstorexmecae.click|dtdt3443",
"lexo@dtstorexmecae.click|dtdt3443",
"mavu@dtstorexmecae.click|dtdt3443",
"ziroe@dtstorexmecae.click|dtdt3443",
"denu@dtstorexmecae.click|dtdt3443",
"rimoe@dtstorexmecae.click|dtdt3443",
"kexo@dtstorexmecae.click|dtdt3443",
"venu@dtstorexmecae.click|dtdt3443",
"naro@dtstorexmecae.click|dtdt3443",
"pexo@dtstorexmecae.click|dtdt3443",
"limo@dtstorexmecae.click|dtdt3443",
"zalo@dtstorexmecae.click|dtdt3443",
"xiru@dtstorexmecae.click|dtdt3443",
"viroa@dtstorexmecae.click|dtdt3443",
"renu@dtstorexmecae.click|dtdt3443",
"kavo@dtstorexmecae.click|dtdt3443",
"diroe@dtstorexmecae.click|dtdt3443",
"nima@dtstorexmecae.click|dtdt3443",
"zoru@dtstorexmecae.click|dtdt3443",
"qixo@dtstorexmecae.click|dtdt3443",
"mero@dtstorexmecae.click|dtdt3443",
"lenu@dtstorexmecae.click|dtdt3443",
"zynx@dtstorexmecae.click|dtdt3443",
"kavoe@dtstorexmecae.click|dtdt3443",
"rilod@dtstorexmecae.click|dtdt3443",
"lemu@dtstorexmecae.click|dtdt3443",
"vaxo@dtstorexmecae.click|dtdt3443",
"qrin@dtstorexmecae.click|dtdt3443",
"meko@dtstorexmecae.click|dtdt3443",
"davi@dtstorexmecae.click|dtdt3443",
"sixo@dtstorexmecae.click|dtdt3443",
"tavoe@dtstorexmecae.click|dtdt3443",
"xeno@dtstorexmecae.click|dtdt3443",
"brix@dtstorexmecae.click|dtdt3443",
"navo@dtstorexmecae.click|dtdt3443",
"liro@dtstorexmecae.click|dtdt3443",
"zexoe@dtstorexmecae.click|dtdt3443",
"kiro@dtstorexmecae.click|dtdt3443",
"ravo@dtstorexmecae.click|dtdt3443",
"vimo@dtstorexmecae.click|dtdt3443",
"qexo@dtstorexmecae.click|dtdt3443",
"mino@dtstorexmecae.click|dtdt3443",
"zavo@no.timball.cloud|dtdt3443",
"laxo@no.timball.cloud|dtdt3443",
"ahri@no.timball.cloud|dtdt3443",
"exo@no.timball.cloud|dtdt3443",
"dze@no.timball.cloud|dtdt3443",
"kexo@no.timball.cloud|dtdt3443",
"rimo@no.timball.cloud|dtdt3443",
"daxo@no.timball.cloud|dtdt3443",
"xiro@no.timball.cloud|dtdt3443",
"mavo@no.timball.cloud|dtdt3443",
"ziro@no.timball.cloud|dtdt3443",
"limo@no.timball.cloud|dtdt3443",
"qiro@no.timball.cloud|dtdt3443",
"niro@no.timball.cloud|dtdt3443",
"vexo@no.timball.cloud|dtdt3443",
"kavoa@no.timball.cloud|dtdt3443",
"rixo@no.timball.cloud|dtdt3443",
"savo@no.timball.cloud|dtdt3443",
"e@no.timball.cloud|dtdt3443",
"xavo@no.timball.cloud|dtdt3443",
"zimo@no.timball.cloud|dtdt3443",
"lirox@no.timball.cloud|dtdt3443",
"mixo@no.timball.cloud|dtdt3443",
"qavo@no.timball.cloud|dtdt3443",
"navoa@no.timball.cloud|dtdt3443",
"varo@no.timball.cloud|dtdt3443",
"kirox@no.timball.cloud|dtdt3443",
"rexo@no.timball.cloud|dtdt3443",
"diro@no.timball.cloud|dtdt3443",
"xilo@no.timball.cloud|dtdt3443",
"zaxo@no.timball.cloud|dtdt3443",
"lavo@no.timball.cloud|dtdt3443",
"miro@no.timball.cloud|dtdt3443",
"qexo@no.timball.cloud|dtdt3443",
"nilo@no.timball.cloud|dtdt3443",
"vixo@no.timball.cloud|dtdt3443",
"kiroa@no.timball.cloud|dtdt3443",
"ravoa@no.timball.cloud|dtdt3443",
"siro@no.timball.cloud|dtdt3443",
"xexo@no.timball.cloud|dtdt3443",
"zeno@no.timball.cloud|dtdt3443",
"liroa@no.timball.cloud|dtdt3443",
"mexo@no.timball.cloud|dtdt3443",
"qaxo@no.timball.cloud|dtdt3443",
"naxo@no.timball.cloud|dtdt3443",
"vino@no.timball.cloud|dtdt3443",
"kexoe@no.timball.cloud|dtdt3443",
"rino@no.timball.cloud|dtdt3443",
"dixo@no.timball.cloud|dtdt3443",
"xiroa@ta.syfar.cloud|dtdt3443",
"zirox@ta.syfar.cloud|dtdt3443",
"leno@ta.syfar.cloud|dtdt3443",
"mavoae@ta.syfar.cloud|dtdt3443",
"qino@ta.syfar.cloud|dtdt3443",
"nirox@ta.syfar.cloud|dtdt3443",
"vexoe@ta.syfar.cloud|dtdt3443",
"kavo@ta.syfar.cloud|dtdt3443",
"raxo@ta.syfar.cloud|dtdt3443",
"sixo@ta.syfar.cloud|dtdt3443",
"xavoa@ta.syfar.cloud|dtdt3443",
"zavoa@ta.syfar.cloud|dtdt3443",
"lixo@ta.syfar.cloud|dtdt3443",
"mirox@ta.syfar.cloud|dtdt3443",
"qiroa@ta.syfar.cloud|dtdt3443",
"nexo@ta.syfar.cloud|dtdt3443",
"varoa@ta.syfar.cloud|dtdt3443",
"kiro@ta.syfar.cloud|dtdt3443",
"rimo@ta.syfar.cloud|dtdt3443",
"dexo@ta.syfar.cloud|dtdt3443",
"xino@ta.syfar.cloud|dtdt3443",
"zixo@ta.syfar.cloud|dtdt3443",
"lavoa@ta.syfar.cloud|dtdt3443",
"mexo@ta.syfar.cloud|dtdt3443",
"qexo@ta.syfar.cloud|dtdt3443",
"navo@ta.syfar.cloud|dtdt3443",
"viroa@ta.syfar.cloud|dtdt3443",
"kexo@ta.syfar.cloud|dtdt3443",
"riloa@ta.syfar.cloud|dtdt3443",
"savoa@ta.syfar.cloud|dtdt3443",
"xiro@ta.syfar.cloud|dtdt3443",
"zaroe@ta.syfar.cloud|dtdt3443",
"limoae@ta.syfar.cloud|dtdt3443",
"mixo@ta.syfar.cloud|dtdt3443",
"niro@ta.syfar.cloud|dtdt3443",
"ziroa@ta.syfar.cloud|dtdt3443",
"kirox@ta.syfar.cloud|dtdt3443",
"ravo@ta.syfar.cloud|dtdt3443",
"diroa@ta.syfar.cloud|dtdt3443",
"karsy@hn.syfar.cloud|dtdt3443",
"luden@hn.syfar.cloud|dtdt3443",
"mepra@hn.syfar.cloud|dtdt3443",
"norel@hn.syfar.cloud|dtdt3443",
"otrix@hn.syfar.cloud|dtdt3443",
"palen@hn.syfar.cloud|dtdt3443",
"quera@hn.syfar.cloud|dtdt3443",
"ralco@hn.syfar.cloud|dtdt3443",
"senvy@hn.syfar.cloud|dtdt3443",
"tomene@hn.syfar.cloud|dtdt3443",
"udris@hn.syfar.cloud|dtdt3443",
"varel@hn.syfar.cloud|dtdt3443",
"wexly@hn.syfar.cloud|dtdt3443",
"yorin@hn.syfar.cloud|dtdt3443",
"zefra@hn.syfar.cloud|dtdt3443",
"amlor@hn.syfar.cloud|dtdt3443",
"brant@hn.syfar.cloud|dtdt3443",
"cevone@hn.syfar.cloud|dtdt3443",
"darek@hn.syfar.cloud|dtdt3443",
"elvio@hn.syfar.cloud|dtdt3443",
"faren@hn.syfar.cloud|dtdt3443",
"gomar@hn.syfar.cloud|dtdt3443",
"hilen@hn.syfar.cloud|dtdt3443",
"iroth@hn.syfar.cloud|dtdt3443",
"javen@hn.syfar.cloud|dtdt3443",
"kelor@hn.syfar.cloud|dtdt3443",
"lamis@hn.syfar.cloud|dtdt3443",
"moren@hn.syfar.cloud|dtdt3443",
"nisel@hn.syfar.cloud|dtdt3443",
"obran@hn.syfar.cloud|dtdt3443",
"pirel@hn.syfar.cloud|dtdt3443",
"qorin@hn.syfar.cloud|dtdt3443",
"rimus@hn.syfar.cloud|dtdt3443",
"selvo@hn.syfar.cloud|dtdt3443",
"trano@hn.syfar.cloud|dtdt3443",
"ulven@hn.syfar.cloud|dtdt3443",
"virex@hn.syfar.cloud|dtdt3443",
"worin@hn.syfar.cloud|dtdt3443",
"yelro@hn.syfar.cloud|dtdt3443",
"zanor@hn.syfar.cloud|dtdt3443",
"arvik@hn.syfar.cloud|dtdt3443",
"brelan@hn.syfar.cloud|dtdt3443",
"cordan@hn.syfar.cloud|dtdt3443",
"etran@hn.syfar.cloud|dtdt3443",
"fexar@hn.syfar.cloud|dtdt3443",
"galen@hn.syfar.cloud|dtdt3443",
"huxen@hn.syfar.cloud|dtdt3443",
"ivarn@hn.syfar.cloud|dtdt3443",
"jorel@hn.syfar.cloud|dtdt3443",
"ze@ts.timball.cloud|dtdt3443",



    ],
	
	"gpt_plus_30d": [
	
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
