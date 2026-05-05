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
    "Veo3_45K": {"name": "Veo3 Ultra 45K cre - Dùng được Antigravity - BH 7D", "price":120000},
    "Veo3_bhf": {"name": "Veo3 Ultra 25K cre BH30D", "price":200000},
    "Capcut_Pro": {"name": "Capcut Pro Team 35D Renew", "price":15000},
    "Fam_Ultra": {"name": "Fam Google Ultra Add 5 slot BH 3D", "price":900000},
    "Fam_Ultra_bhf": {"name": "Fam Google Ultra Add 5 slot BHF 30D", "price":1800000},
    "veo3_0k_bhf_1m": {"name": "Ultra Add Fam 0 credit BHF 1 tháng", "price": 300000},
    "veo3_ultra_bhf_1m": {"name": "Ultra Add Fam 5k credit BHF 1 tháng", "price": 350000},
    "veo3_25k_bhf_1m": {"name": "Ultra Add Fam 25K credit BHF 1 Tháng", "price": 750000},
    "veo3_0cre_12m": {"name": " Ultra Add Fam 0k cre/tháng BHF 1 NĂM", "price": 1500000},
    "veo3_bhf_12m": {"name": " Ultra Add Fam 6k cre/tháng BHF 1 NĂM", "price": 1900000},
}

# ===== KHO =====
STOCK = {
    "veo3_ultra_bh":[
    "s4524h24h857@mubanima16.sbs|zghMUL5962",
"s4524h24h851@mubanima16.sbs|sjcTRB0609",
"s4524h24h852@mubanima16.sbs|ipvUYX5414",
"s4524h24h853@mubanima16.sbs|jlePVM3883",
"s4524h24h855@mubanima16.sbs|cqkUWU2635",
"s4524h24h854@mubanima16.sbs|rcxFOX7055",
"s4524h24h850@mubanima16.sbs|eunTZS5688",
"s4524h24h856@mubanima16.sbs|gxvGHC1387",
"s4524h24h882@mubanima16.sbs|menRPL3120",
"s4524h24h867@mubanima16.sbs|glyZEH6340",
"s4524h24h886@mubanima16.sbs|zspCKN6363",
"s4524h24h880@mubanima16.sbs|jrtUZI4815",
"s4524h24h865@mubanima16.sbs|jhsLVY3063",
"s4524h24h884@mubanima16.sbs|oupQTC7397",
"s4524h24h858@mubanima16.sbs|ehdSEN2260",
"s4524h24h869@mubanima16.sbs|nauQCI9309",
"s4524h24h888@mubanima16.sbs|cwtXUF7414",
"s4524h24h88@mubanima16.sbs|odbLEO9738",
"s4524h24h891@mubanima16.sbs|nvnXVD7419",
"s4524h24h892@mubanima16.sbs|itxCNE4746",
"s4524h24h85@mubanima16.sbs|novVNA7448",
"s4524h24h870@mubanima16.sbs|xogHTW5444",
"s4524h24h893@mubanima16.sbs|ofeRWH9243",
"s4524h24h895@mubanima16.sbs|yqlXKV8413",
"s4524h24h872@mubanima16.sbs|orqQYU7720",
"s4524h24h896@mubanima16.sbs|fewMLU1915",
"s4524h24h87@mubanima16.sbs|zbyZKL8452",
"s4524h24h864@mubanima16.sbs|kxgNLU8841",
"s4524h24h881@mubanima16.sbs|nztXFE3826",
"s4524h24h873@mubanima16.sbs|kywXQT1263",
"s4524h24h861@mubanima16.sbs|hgfRII5597",
"s4524h24h875@mubanima16.sbs|itcTDX6958",
"s4524h24h883@mubanima16.sbs|copBEV6457",
"s4524h24h866@mubanima16.sbs|ritBYS5549",
"s4524h24h885@mubanima16.sbs|dgvCPE4701",
"s4524h24h887@mubanima16.sbs|jnfZAD0462",
"s4524h24h868@mubanima16.sbs|fzkYZL3525",
"s4524h24h889@mubanima16.sbs|josPHZ8379",
"s4524h24h859@mubanima16.sbs|hceJJC6519",
"s4524h24h890@mubanima16.sbs|eheLUB9539",
"s4524h24h86@mubanima16.sbs|iloORK2432",
"s4524h24h876@mubanima16.sbs|edkCOI8542",
"s4524h24h894@mubanima16.sbs|qpeCLN7200",
"s4524h24h871@mubanima16.sbs|pboXOT6829",
"s4524h24h860@mubanima16.sbs|wobWQF6381",
"s4524h24h862@mubanima16.sbs|vexOMW9783",
"s4524h24h877@mubanima16.sbs|mvsPYY0592",
"s4524h24h878@mubanima16.sbs|xajIIV1859",
"s4524h24h863@mubanima16.sbs|tpzRRV5314",
"s4524h24h879@mubanima16.sbs|chbZOU0269",
    ],
    "Veo3_45K":[
    ],
    "Veo3_bhf":[
    ],
    "Capcut_Pro":[
"s109aw@sd.webmail.fit|123456",
"tsz36o@veomatrix25k.io.vn|123456",
"yw1649@veo325kcredit.io.vn|123456",
"0u16cw@anversa.com.co|123456",
"ut105e@trungmetax.com|123456",
    ],
    "Fam_Ultra":[
    ],
    "Fam_Ultra_bhf":[
    ],
    "veo3_0k_bhf_1m": ["MANUAL"] * 0,
    "veo3_ultra_bhf_1m": ["MANUAL"] * 0,
    "veo3_25k_bhf_1m": ["MANUAL"] * 0,
    "veo3_0cre_12m": ["MANUAL"] * 5,
    "veo3_bhf_12m": ["MANUAL"] * 5,
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
     # ===== LƯU Ý RIÊNG CHO GROK =====
    grok_note = ""
    if pid == "Grok":
        grok_note = (
        "\n\n📌 LƯU Ý KHI SỬ DỤNG GROK:\n\n"
        "- Không thay đổi mail\n"
        "- Không login X\n"
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
