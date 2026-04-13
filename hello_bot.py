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
    "veo3_ultra_bh": {"name": "Veo3 Ultra 25K cre BH 24H", "price":22222},
    "veo3_ultra_bh30d": {"name": "Veo3 Ultra 25K cre BH 30D", "price":200000},
    "grok_bhf": {"name": "Grok Super 30D BH Full", "price":99999},
    "Fam_Ultra": {"name": "Fam Ultra Add 5 slot BH 3D", "price": 750000},
    "veo3_0k_bhf_1m": {"name": "Ultra Add Fam 0 credit BHF 1 tháng", "price": 275000},
    "veo3_ultra_bhf_1m": {"name": "Ultra Add Fam 5k credit BHF 1 tháng", "price": 300000},
    "veo3_25k_bhf_1m": {"name": "Ultra Add Fam 25K credit BHF 1 Tháng", "price": 680000},
    "veo3_0cre_12m": {"name": " Ultra Add Fam 0k cre/tháng BHF 1 NĂM", "price": 1500000},
    "veo3_bhf_12m": {"name": " Ultra Add Fam 6k cre/tháng BHF 1 NĂM", "price": 1900000},
    "cdk_gpt_go": {"name": "CDK CHATGPT Go 12M BH ACTIVE", "price": 80000},
    "cdk_gpt_plus_1m": {"name": "CDK CHATGPT PLUS 1M BH ACTIVE", "price": 50000},
    "info_4": {"name": "Zalo: 0842.108.959 - Tele:@dtdt28", "price": 0},
}

# ===== KHO =====
STOCK = {
    "veo3_ultra_bh":[
    "s1324h1290@klaoappapooa99n.sbs|ewiVUY1017"
"s1324h1292@klaoappapooa99n.sbs|kagUNE9863"
"s1324h1293@klaoappapooa99n.sbs|yqeGDS5001"
"s1324h1294@klaoappapooa99n.sbs|tuuHEM8373"
"s1324h1295@klaoappapooa99n.sbs|vbqNQT9264"
"s1324h1296@klaoappapooa99n.sbs|gdjFWL3220"
"s1324h1297@klaoappapooa99n.sbs|mbrLGZ3873"
"s1324h1298@klaoappapooa99n.sbs|vuoYFT9998"
"s1324h1299@klaoappapooa99n.sbs|smoHTQ0597"
"s1324h129@klaoappapooa99n.sbs|oqqHLV6929"
"s1324h12@klaoappapooa99n.sbs|vcqWQC3945"
"s1324h1300@klaoappapooa99n.sbs|xbtTEL0113"
"s1324h1301@klaoappapooa99n.sbs|drrNPI2169"
"s1324h1302@klaoappapooa99n.sbs|fgsDWQ1944"
"s1324h1303@klaoappapooa99n.sbs|joeSNL3901"
"s1324h1305@klaoappapooa99n.sbs|jlnYET1649"
"s1324h1306@klaoappapooa99n.sbs|caaRNC3244"
"s1324h1307@klaoappapooa99n.sbs|rysNQI8218"
"s1324h1308@klaoappapooa99n.sbs|ruxKOT8352"
"s1324h1309@klaoappapooa99n.sbs|wkjHBS1695"
"s1324h130@klaoappapooa99n.sbs|jbeWIF8261"
"s1324h1310@klaoappapooa99n.sbs|ogxMYS4053"
"s1324h1312@klaoappapooa99n.sbs|npzGFH5169"
"s1324h1313@klaoappapooa99n.sbs|cozSJQ2468"
"s1324h1314@klaoappapooa99n.sbs|xfhXQF1838"
"s1324h1315@klaoappapooa99n.sbs|hevPQP9814"
"s1324h1316@klaoappapooa99n.sbs|fnkLBJ3800"
"s1324h1317@klaoappapooa99n.sbs|pqsJGX9530"
"s1324h1318@klaoappapooa99n.sbs|eugVTT7087"
"s1324h181@klaoappapooa99n.sbs|gsjOKK7979",
"s1324h182@klaoappapooa99n.sbs|pfgNLT8469",
"s1324h183@klaoappapooa99n.sbs|yraDYE6980",
"s1324h184@klaoappapooa99n.sbs|wevJKP9088",
    ],
    "veo3_ultra_bh30d":[
    "s13bhf263@4corrineajohnsona.asia|vuoZXX3348",
"s13bhf264@4corrineajohnsona.asia|tziQPO8996",
"s13bhf265@4corrineajohnsona.asia|nwqVMM9535",
"s13bhf266@4corrineajohnsona.asia|nmaPPN1824",
"s13bhf267@4corrineajohnsona.asia|xdqYPV0647",
    ],
    "grok_bhf":[
"arunita.casanova0@outlook.com|SuperGrok1234@",
"argos.danvas34@outlook.com|SuperGrok1234@",
"kuzela_likam7@outlook.com|SuperGrok1234@",
"oeckler_brefort5@outlook.com|SuperGrok1234@",
"vajnar.moldes70@outlook.com|SuperGrok1234@",
"konecy.kseniya65@outlook.com|SuperGrok1234@",
"lenit.islami69@outlook.com|SuperGrok1234@",
"felch_virano9@outlook.com|SuperGrok1234@",
"mizyal_juiyao31@outlook.com|SuperGrok1234@",
"rapacki.loyson17@outlook.com|SuperGrok1234@",
"waltchspanola@outlook.com|SuperGrok1234@",
"crena.healim4@outlook.com|SuperGrok1234@",
"getrige.deton8@outlook.com|SuperGrok1234@",
"dalkys.strey8@outlook.com|SuperGrok1234@",
"cicurel_tamehau1@outlook.com|SuperGrok1234@",
     ],
    "Fam_Ultra":[
"InostrazaMerklin@gmail.com|ans45e3awvf|rellkhlokp@outlook.com|7fwd mjor czop 3ph6 mujn 5wbb w4yj f4cw|",
"CeraoLangtry@gmail.com|p1irqokpmx|emh872gz1jr59xt1t0us@anhnhat.online|xynt mzzd deah xuer 2prq sesw 7yqg heu3|",
    ],
    "veo3_0k_bhf_1m": ["MANUAL"] * 5,
    "veo3_ultra_bhf_1m": ["MANUAL"] * 5,
    "veo3_25k_bhf_1m": ["MANUAL"] * 0,
    "veo3_0cre_12m": ["MANUAL"] * 5,
    "veo3_bhf_12m": ["MANUAL"] * 5,
     "cdk_gpt_go": [   
"026926B4-5F44-4A24-8D0F-D27533284012",
"81A60435-77D9-40FD-B86F-F3CA915EF323",
"DDF31F41-5188-4093-A529-E1C79393C1AB",
     ],
     "cdk_gpt_plus_1m": [
"4224D4B7-03B9-4697-A6C7-FF74FA8DFD34",
"9403C29C-AC3A-4AB3-9EF3-9DAACA2C8F85",
"4EE7E443-9325-4DE3-B551-26BFD44D9E3F",
"DAB98FFE-1216-4EAA-B602-74BFEADAD450",
"69F1A10C-3B8C-4F75-90D7-CBDD11BD6C81",
"EEC2A1B1-E0F6-49D8-84BE-6BB2020D0F11",
"E35BA3FC-C750-44A5-8160-A02A6A53D015",
"CEFDDC9C-927F-4DBB-B1D2-12DDA155DFDE",
"7D562521-21DC-4684-8189-028CF9BB6AE3",
"DB126BE2-19AD-4BBD-A72F-D025CBB0E835",
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
    if pid == "Fam_Ultra":
        fam_ultra_note = (
            "\n\n📌 Lưu ý khi mua fam Google Ultra 5 slot:\n"
            "- Chỉ login IP US để ngâm và add family (vì đây là Gmail US nên mọi người fake IP sang US để hạn chế bị diss mail).\n"
            "- Trước khi gửi mình sẽ xóa HSTT + đổi 2FA + đá device - hỗ trợ từ A-Z, mn chỉ việc add mail vào là dùng được.\n"
            "- Mn chú ý chỉ change 2FA thôi là không ai back lại được rồi, lúc gửi mình cũng change trước 1 lần rồi.\n"
            "- Gmail ai có người nấy giữ nha ^^ Nếu khó quá mình vẫn sẽ hỗ trợ, tùy trường hợp.\n"
        )

    detail = (
        f"✅ Đơn `{code}`\n"
        f"🎁 Sản phẩm: *{product['name']}*\n"
        f"📦 Số lượng: *{qty}*\n\n"
        f"{codes_text}"
        f"{extra_guide}"
        f"{fam_ultra_note}\n"
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
