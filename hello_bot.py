from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InputFile, BotCommand
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
    "veo3_ultra_bh": {"name": "Veo3 Ultra 25K cre BH 24H", "price":25555},
    "veo3_ultra_bh30d": {"name": "Veo3 Ultra 25K cre BH 30D", "price":200000},
    "Capcut_Pro": {"name": "Capcut Pro Team 35D Renew", "price":15000},
    "Fam_Ultra": {"name": "Fam Ultra Add 5 slot BH 3D", "price": 650000},
    "Fam_Ultra_bhf": {"name": "Fam Ultra Add 5 slot BHF 30D", "price":1200000 },
    "veo3_0k_bhf_1m": {"name": "Ultra Add Fam 0 credit BHF 1 tháng", "price": 250000},
    "veo3_ultra_bhf_1m": {"name": "Ultra Add Fam 5k credit BHF 1 tháng", "price": 300000},
    "veo3_25k_bhf_1m": {"name": "Ultra Add Fam 25K credit BHF 1 Tháng", "price": 680000},
    "veo3_0cre_12m": {"name": " Ultra Add Fam 0k cre/tháng BHF 1 NĂM", "price": 1500000},
    "veo3_bhf_12m": {"name": " Ultra Add Fam 6k cre/tháng BHF 1 NĂM", "price": 1900000},
    "cdk_gpt_go": {"name": "CDK CHATGPT Go 12M BH ACTIVE", "price": 70000},
    "cdk_gpt_plus_1m": {"name": "CDK CHATGPT PLUS 1M BH ACTIVE", "price": 35000},
}

# ===== KHO =====
STOCK = {
    "veo3_ultra_bh":[
"s21424h519@dzmbczvmttahdljm.sbs|luaRSA1523",
"s21424h51@dzmbczvmttahdljm.sbs|vhgULO8286",
"s21424h522@dzmbczvmttahdljm.sbs|rbtXDX9003",
"s21424h523@dzmbczvmttahdljm.sbs|sbtUHM2497",
"s21424h524@dzmbczvmttahdljm.sbs|ejsKJD3749",
"s21424h520@dzmbczvmttahdljm.sbs|ukeQHF4114",
"s21424h526@dzmbczvmttahdljm.sbs|vpdIGV1719",
"s21424h527@dzmbczvmttahdljm.sbs|lylLQN1417",
"s21424h528@dzmbczvmttahdljm.sbs|zexDVA7181",
"s21424h529@dzmbczvmttahdljm.sbs|pxhWMJ5247",
"s21424h52@dzmbczvmttahdljm.sbs|eaeLJG6592",
"s21424h530@dzmbczvmttahdljm.sbs|ucdYHN2931",
"s21424h525@dzmbczvmttahdljm.sbs|nfvJID9034",
"s21424h491@dzmbczvmttahdljm.sbs|uatVYD4947",
"s21424h493@dzmbczvmttahdljm.sbs|tcuIKO6861",
"s21424h495@dzmbczvmttahdljm.sbs|pxlBOC7982",
"s21424h497@dzmbczvmttahdljm.sbs|mnqSPG3519",
"s21424h498@dzmbczvmttahdljm.sbs|vkbBLL8631",
"s21424h499@dzmbczvmttahdljm.sbs|beaBXY8104",
"s21424h4@dzmbczvmttahdljm.sbs|lpnXWP7855",
"s21424h501@dzmbczvmttahdljm.sbs|fjzQZJ4932",
    ],
    "veo3_ultra_bh30d":[
    ],
    "Capcut_Pro":[
    ],
    "Fam_Ultra":[
"echitu65@gmail.com|LUlO922016QITip|echitu655595@hotmail.com|rquz svx3 wng3 t7dp 6jcx 3hqq a5yr bq5g",
"MalloIbrar805@gmail.com|rzrqzcghoz7|waistphoto3yr@hotmail.com|d337 wfnz lmpn aslg bov2 7kww 3o7x voia",
"FigueroaJames169@gmail.com|yzhbmsq7tk|elbislacsam8@hotmail.com|ai54 qvyp w4cs dsf3 qmql xoxm ek7i jqfo",
"
    ],
    "Fam_Ultra_bhf":[
"DivasBoles915@gmail.com|hnxycarev|hirelcadeeyz@outlook.com|kydi rxuv tnlg vbqe 3qxu 4htu zals lnys",
"HickelKellywood@gmail.com|8mlgorual|jyrwaakrabah@hotmail.com|aacjait5zofi5vqbqfk2nrpiow7i3hpt",
    ],
    "veo3_0k_bhf_1m": ["MANUAL"] * 20,
    "veo3_ultra_bhf_1m": ["MANUAL"] * 5,
    "veo3_25k_bhf_1m": ["MANUAL"] * 0,
    "veo3_0cre_12m": ["MANUAL"] * 5,
    "veo3_bhf_12m": ["MANUAL"] * 5,
     "cdk_gpt_go": [   
"81A60435-77D9-40FD-B86F-F3CA915EF323",
"DDF31F41-5188-4093-A529-E1C79393C1AB",
     ],
     "cdk_gpt_plus_1m": [

     ],
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


import threading
import time

# ===== HÀM GỬI RIÊNG (CHẠY NỀN) =====
def _send_broadcast_task(message, type_msg, photo, context):
    sent = 0

    with open(USERS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            try:
                uid = int(line)

                if type_msg == "text":
                    context.bot.send_message(
                        chat_id=uid,
                        text=message,
                        disable_web_page_preview=True
                    )

                elif type_msg == "photo":
                    context.bot.send_photo(
                        chat_id=uid,
                        photo=photo,
                        caption=message
                    )

                sent += 1
                time.sleep(0.03)  # chống spam

            except:
                continue

    print(f"[Broadcast] Sent: {sent}")

# ===== BROADCAST (ADMIN) =====
def broadcast(update, context):
    chat_id = update.effective_chat.id

    if chat_id != ADMIN_CHAT_ID:
        update.message.reply_text("❌ Bạn không có quyền dùng lệnh này.")
        return

    msg = update.message

    # ===== Reply hoặc nhập nội dung =====
    if msg.reply_to_message:
        r = msg.reply_to_message

        if r.text:
            message = r.text
            type_msg = "text"

        elif r.photo:
            message = r.caption or ""
            photo = r.photo[-1].file_id
            type_msg = "photo"

        else:
            msg.reply_text("⚠ Không hỗ trợ định dạng này.")
            return

    else:
        if not context.args:
            msg.reply_text(
                "⚠ Dùng:\n"
                "- /broadcast nội_dung\n"
                "- Hoặc reply vào tin nhắn cần gửi rồi gõ /broadcast"
            )
            return

        message = msg.text.partition(" ")[2]
        type_msg = "text"

    if type_msg == "text" and not message:
        msg.reply_text("⚠ Không lấy được nội dung.")
        return

    if not os.path.exists(USERS_FILE):
        msg.reply_text("Chưa có user nào trong danh sách.")
        return

    # 🚀 CHẠY NỀN
    threading.Thread(
        target=_send_broadcast_task,
        args=(message, type_msg, photo if type_msg == "photo" else None, context),
        daemon=True
    ).start()

    msg.reply_text("🚀 Đang gửi broadcast, bot vẫn hoạt động bình thường!")

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

    # ===== SẢN PHẨM NÂNG CẤP THỦ CÔNG =====
    if pid in ["veo3_0k_bhf_1m", "veo3_ultra_bhf_1m", "veo3_15k_bhf_1m", "veo3_25k_bhf_1m", "veo3_bhf_12m"]:
        detail = (
            f"✅ Đơn `{code}`\n"
            f"🎁 Sản phẩm: {product['name']}\n"
            f"📦 Số lượng: {qty}\n\n"
            "📌 Vui lòng gửi mã đơn này qua Telegram để được nâng cấp tài khoản.\n"
            "👉 Telegram: @dtdt28\n\n"
            "🚀 Quyền lợi nổi bật:\n"
            "• Tạo video Fast 3.1 Lower không tốn credit\n"
            "• Dung lượng 6TB Google Drive\n"
            "• Truy cập Antigravity Ultra\n"
            "• Toàn bộ các quyền lợi cao cấp khác của Gemini\n\n"
            "📢 LƯU Ý: NẾU DÙNG QUÁ CREDIT SẼ BỊ KICK KHỎI FARM VÀ KHÔNG HOÀN TIỀN\n\n"
            "Cảm ơn bạn đã mua hàng!"
        )

        TG_BOT.send_message(
            chat_id=user_id,
            text=detail,
            parse_mode="Markdown",
            disable_web_page_preview=True
        )
        return True

    # ===== SẢN PHẨM TỰ ĐỘNG (CÓ STOCK) =====
    if len(STOCK.get(pid, [])) < qty:
        TG_BOT.send_message(
            chat_id=user_id,
            text="⚠ Kho không đủ số lượng. Liên hệ admin."
        )
        return False

    accounts = [STOCK[pid].pop(0) for _ in range(qty)]
    codes_text = "\n".join(f"{i+1}. {acc}" for i, acc in enumerate(accounts))

    # Hướng dẫn riêng cho CDK
    extra_guide = ""
    if pid in ["cdk_gpt_plus_1m", "cdk_gpt_go"]:
        extra_guide = "\n\n🌐 Website sử dụng CDK: https://nuoitao.com\n"

    # Note riêng cho Fam Ultra
    fam_ultra_note = ""
    if pid in ["Fam_Ultra", "Fam_Ultra_bhf"]:
        fam_ultra_note = (
            "\n\n📌 Lưu ý khi mua fam Google Ultra 5 slot:\n"
            "- Mn chú ý chỉ change 2FA thôi là không ai back lại được rồi, lúc gửi mình cũng change trước 1 lần rồi. Nếu muốn change pass hãy đợi khoảng 24h ạ!\n"
            "- Hạn chế đăng nhập trên nhiều ip khác nhau nhé.\n"
        )
    capcut_note = ""
    if pid == "Capcut_Pro_Team_35D":
        capcut_note = (
        "\n\n⚠️ LƯU Ý KHI SỬ DỤNG:\n\n"
        "- Hàng 35D renew là dạng auto gia hạn sau 7 ngày.\n"
        "- Sau khi hết 7 ngày bên em sẽ cho tool tự động gia hạn tiếp đến khi đủ 35 ngày.\n"
        "- AE KHÔNG được thay đổi email hay mật khẩu để bên em còn gia hạn.\n"
        "-Nếu không sẽ không gia hạn đầy đủ.\n\n"
        "- Không tự ý rời khỏi không gian team, hay out team.\n"
        )
    detail = (
        f"✅ Đơn `{code}`\n"
        f"🎁 Sản phẩm: *{product['name']}*\n"
        f"📦 Số lượng: *{qty}*\n\n"
        f"{codes_text}"
        f"{extra_guide}"
        f"{fam_ultra_note}"
        f"{capcut_note}\n"
        "Cảm ơn bạn đã mua hàng!"
)

    TG_BOT.send_message(
        chat_id=user_id,
        text=detail,
        parse_mode="Markdown",
        disable_web_page_preview=True
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
def support(update, context):
    text = (
        "📞 Hỗ trợ nhanh:\n\n"
        "✈️ Telegram: Mn cần hỗ trợ liên hệ Admin @dtdt28"
    )
    update.message.reply_text(text)


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

    # ===== MENU COMMAND =====
    commands = [
        BotCommand("start", "Xem danh sách sản phẩm"),
        BotCommand("support", "Liên hệ admin"),
    ]
    updater.bot.set_my_commands(commands)

    # ===== HANDLER =====
    dp.add_handler(CommandHandler("support", support))
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("menu", start))
    dp.add_handler(CommandHandler("broadcast", broadcast))
    dp.add_handler(CallbackQueryHandler(handle_buttons))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_quantity))

    # ===== WEBHOOK THREAD =====
    def run_webhook():
        app.run(host="0.0.0.0", port=8080, threaded=True)

    threading.Thread(target=run_webhook, daemon=True).start()

    print("BOT ĐANG CHẠY...")
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
