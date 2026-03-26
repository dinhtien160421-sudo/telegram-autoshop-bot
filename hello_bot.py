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
    "veo3_ultra_bh": {"name": "Veo3 Ultra 25K cre BH 24H", "price":50000},
    "veo3_ultra_3D": {"name": "Veo3 Ultra 25K cre BH Hết Tháng ", "price":80000},
    "veo3_pro_bh": {"name": "Veo3 Pro 25K cre BH 24h", "price":22222},
    "grok_bhf": {"name": "Grok Super 30D BH Full", "price": 65000},
    "veo3_0k_bhf_1m": {"name": "Ultra Add Fam 0 credit BHF 1 tháng", "price": 300000},
    "veo3_ultra_bhf_1m": {"name": "Ultra Add Fam 5k credit BHF 1 tháng", "price": 320000},
    "veo3_15k_bhf_1m": {"name": "Ultra Add Fam 15k credit BHF 1 tháng", "price":440000},
    "veo3_25k_bhf_1m": {"name": "Ultra Add Fam 25K credit BHF 1 Tháng", "price": 550000},
    "veo3_bhf_12m": {"name": " Ultra Add Fam 6k cre/tháng BHF 1 NĂM", "price": 2000000},
    "cdk_gpt_go": {"name": "CDK CHATGPT Go 12M BH ACTIVE", "price": 80000},
    "cdk_gpt_plus_1m": {"name": "CDK CHATGPT PLUS 1M BH ACTIVE", "price": 50000},
    "info_4": {"name": "Zalo: 0842.108.959 - Tele:@dtdt28", "price": 0},
}

# ===== KHO =====
STOCK = {
    "veo3_ultra_bh":[
    "v25n26t3bh24h52@weboradataplatformsystem.sbs|irxCMP1269",
"v25n26t3bh24h53@weboradataplatformsystem.sbs|nhfQBU4028",
"v25n26t3bh24h54@weboradataplatformsystem.sbs|cytPPJ5160",
"v25n26t3bh24h55@weboradataplatformsystem.sbs|ocbKZN5005",
"v25n26t3bh24h56@weboradataplatformsystem.sbs|crsJWK1664",
"v25n26t3bh24h57@weboradataplatformsystem.sbs|ujsPHS1450",
"v25n26t3bh24h58@weboradataplatformsystem.sbs|nihKDT8066",
"v25n26t3bh24h59@weboradataplatformsystem.sbs|wniZPR5081",
"v25n26t3bh24h5@weboradataplatformsystem.sbs|pxcAXN1858",
"v25n26t3bh24h60@weboradataplatformsystem.sbs|yfrOMN5240",
"v25n26t3bh24h61@weboradataplatformsystem.sbs|ybnTZR0047",
"v25n26t3bh24h62@weboradataplatformsystem.sbs|hzwNZY1174",
"v25n26t3bh24h63@weboradataplatformsystem.sbs|ndaZGC1645",
"v25n26t3bh24h64@weboradataplatformsystem.sbs|xtgSEB4096",
"v25n26t3bh24h65@weboradataplatformsystem.sbs|cqnMKJ0776",
"v25n26t3bh24h66@weboradataplatformsystem.sbs|yxiMET3645",
"v25n26t3bh24h67@weboradataplatformsystem.sbs|amvFPL8005",
"v25n26t3bh24h68@weboradataplatformsystem.sbs|dlqVGR6628",
"v25n26t3bh24h69@weboradataplatformsystem.sbs|jelWVH8957",
"v25n26t3bh24h6@weboradataplatformsystem.sbs|hzkFRN1908",
"v25n26t3bh24h70@weboradataplatformsystem.sbs|ulzUYX0634",
"v25n26t3bh24h71@weboradataplatformsystem.sbs|zegGFY5257",
"v25n26t3bh24h72@weboradataplatformsystem.sbs|pdjNAW5806",
"v25n26t3bh24h73@weboradataplatformsystem.sbs|casUZE7316",
"v25n26t3bh24h74@weboradataplatformsystem.sbs|crxOAS6236",
"v25n26t3bh24h75@weboradataplatformsystem.sbs|ssmBMD5133",
"v25n26t3bh24h76@weboradataplatformsystem.sbs|sinZVW5852",
"v25n26t3bh24h77@weboradataplatformsystem.sbs|gayKOB8740",
"v25n26t3bh24h78@weboradataplatformsystem.sbs|vfaLPV0634",
"v25n26t3bh24h79@weboradataplatformsystem.sbs|phyEFK7073",
"v25n26t3bh24h7@weboradataplatformsystem.sbs|hilLWY1668",
"v25n26t3bh24h80@weboradataplatformsystem.sbs|xzlWGP4426",
"v25n26t3bh24h81@weboradataplatformsystem.sbs|atoOLF9082",
"v25n26t3bh24h82@weboradataplatformsystem.sbs|vkzWKL8329",
"v25n26t3bh24h83@weboradataplatformsystem.sbs|peyBAJ2102",
"v25n26t3bh24h84@weboradataplatformsystem.sbs|taaQBO1911",
"v25n26t3bh24h85@weboradataplatformsystem.sbs|aroXHM5169",
"v25n26t3bh24h86@weboradataplatformsystem.sbs|hfjZFX0678",
"v25n26t3bh24h87@weboradataplatformsystem.sbs|hwuSAY9365",
"v25n26t3bh24h88@weboradataplatformsystem.sbs|iftDYM6923",
"v25n26t3bh24h89@weboradataplatformsystem.sbs|kgiNYR7488",
"v25n26t3bh24h90@weboradataplatformsystem.sbs|nbdZBH4313",
"v25n26t3bh24h92@weboradataplatformsystem.sbs|tckGOM3004",
"v25n26t3bh24h93@weboradataplatformsystem.sbs|qncFTP8545",
"v25n26t3bh24h94@weboradataplatformsystem.sbs|wvyNNC5176",
"v25n26t3bh24h95@weboradataplatformsystem.sbs|bpjZKR1918",
"v25n26t3bh24h97@weboradataplatformsystem.sbs|bwySXX1932",
    ],
     "veo3_ultra_3D":[
    "z27@dalahary.click | %YE&9qF<",
"andrzejultra883083@ded.tunmoravelixlta.com|Tvm152011@",
"vainoultra334205@ded.tunmoravelixlta.com|Tvm152011@",
"matteoultra119109@ded.tunmoravelixlta.com|Tvm152011@",
"knutultra119182@ded.tunmoravelixlta.com|Tvm152011@",
"eemilultra334249@ded.tunmoravelixlta.com|Tvm152011@",
"roopeultra334266@ded.tunmoravelixlta.com|Tvm152011@",
"krzysztofultra883082@ded.tunmoravelixlta.com|Tvm152011@",
     ],    
    "veo3_pro_bh":[    
"zedue6qlu@quseravonextalimiroq.sbs|MeoXinh@999",
"zedusjtzz@quseravonextalimiroq.sbs|MeoXinh@999",
"zedutcx4j@quseravonextalimiroq.sbs|MeoXinh@999",
    ],
    "grok_bhf":[
     ],
    "veo3_0k_bhf_1m": ["MANUAL"] * 0,
    "veo3_ultra_bhf_1m": ["MANUAL"] * 0,
    "veo3_15k_bhf_1m": ["MANUAL"] * 0,
    "veo3_25k_bhf_1m": ["MANUAL"] * 0,
    "veo3_bhf_12m": ["MANUAL"] * 5,
     "cdk_gpt_go": [
"64B906C8-1AA7-4A25-BE27-045889591B86",
     ],
     "cdk_gpt_plus_1m": [
"DE3584E4-681F-4C0B-B65C-8F4BB66B1ABD",
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
    if pid in [ "veo3_0k_bhf_1m","veo3_ultra_bhf_1m","veo3_15k_bhf_1m", "veo3_25k_bhf_1m","veo3_bhf_12m"]:
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

    detail = (
        f"✅ Đơn `{code}`\n"
        f"🎁 Sản phẩm: *{product['name']}*\n"
        f"📦 Số lượng: *{qty}*\n\n"
        f"{codes_text}"
        f"{extra_guide}\n"
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
