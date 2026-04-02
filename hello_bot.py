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
    "veo3_ultra_bh": {"name": "Veo3 Ultra 25K cre BH 24H", "price":39999},
    "veo3_pro_bh": {"name": "Veo3 Pro 25K cre BH 24h", "price":22222},
    "grok_bhf": {"name": "Grok Super 30D BH Full", "price":44444},
    "Fam_Ultra": {"name": "Fam Ultra Add 5 slot BH 3D", "price": 700000},
    "veo3_0k_bhf_1m": {"name": "Ultra Add Fam 0 credit BHF 1 tháng", "price": 300000},
    "veo3_ultra_bhf_1m": {"name": "Ultra Add Fam 5k credit BHF 1 tháng", "price": 320000},
    "veo3_25k_bhf_1m": {"name": "Ultra Add Fam 25K credit BHF 1 Tháng", "price": 650000},
    "veo3_0cre_12m": {"name": " Ultra Add Fam 0k cre/tháng BHF 1 NĂM", "price": 1400000},
    "veo3_bhf_12m": {"name": " Ultra Add Fam 6k cre/tháng BHF 1 NĂM", "price": 1900000},
    "cdk_gpt_go": {"name": "CDK CHATGPT Go 12M BH ACTIVE", "price": 80000},
    "cdk_gpt_plus_1m": {"name": "CDK CHATGPT PLUS 1M BH ACTIVE", "price": 50000},
    "info_4": {"name": "Zalo: 0842.108.959 - Tele:@dtdt28", "price": 0},
}

# ===== KHO =====
STOCK = {
    "veo3_ultra_bh":[
"v25n2t4bh24h135@core-datastream-engine.onekintun.com|uoeHSN6661",
"v25n2t4bh24h136@core-datastream-engine.onekintun.com|tkgRXB3537",
"v25n2t4bh24h137@core-datastream-engine.onekintun.com|gxcYIL1649",
"v25n2t4bh24h138@core-datastream-engine.onekintun.com|rrqBKI2401",
"v25n2t4bh24h139@core-datastream-engine.onekintun.com|dtgIKC0087",
"v25n2t4bh24h13@core-datastream-engine.onekintun.com|jznYNW7576",
"v25n2t4bh24h140@core-datastream-engine.onekintun.com|fjaDIO5294",
"v25n2t4bh24h141@core-datastream-engine.onekintun.com|unpDNI8414",
"v25n2t4bh24h142@core-datastream-engine.onekintun.com|lvlTRM8281",
"v25n2t4bh24h143@core-datastream-engine.onekintun.com|xthVCN5683",
"v25n2t4bh24h144@core-datastream-engine.onekintun.com|ycpFQA4033",
"v25n2t4bh24h145@core-datastream-engine.onekintun.com|lriDGX8750",
"v25n2t4bh24h146@core-datastream-engine.onekintun.com|kqxFZM3717",
"v25n2t4bh24h147@core-datastream-engine.onekintun.com|zabDVK9822",
"v25n2t4bh24h148@core-datastream-engine.onekintun.com|bymRDF3715",
"v25n2t4bh24h149@core-datastream-engine.onekintun.com|uqhVRA4405",
"v25n2t4bh24h14@core-datastream-engine.onekintun.com|htpQJM4456",
"v25n2t4bh24h150@core-datastream-engine.onekintun.com|ptfSBX0797",
"v25n2t4bh24h151@core-datastream-engine.onekintun.com|athNKZ6446",
"v25n2t4bh24h152@core-datastream-engine.onekintun.com|cxjTTB3413",
"v25n2t4bh24h153@core-datastream-engine.onekintun.com|obgQHJ3173",
"v25n2t4bh24h154@core-datastream-engine.onekintun.com|tqsDNY8146",
"v25n2t4bh24h155@core-datastream-engine.onekintun.com|tspOLQ5457",
"v25n2t4bh24h156@core-datastream-engine.onekintun.com|ptsIQB6356",
"v25n2t4bh24h157@core-datastream-engine.onekintun.com|mitQIS4738",
"v25n2t4bh24h158@core-datastream-engine.onekintun.com|ebiHZE1053",
"v25n2t4bh24h159@core-datastream-engine.onekintun.com|nduBGL8415",
"v25n2t4bh24h50@eocuncloudservicehub.sbs|okkKSV4958",
"v25n2t4bh24h55@eocunnextservicehub.sbs|wpbZSH4986",
"v25n2t4bh24h59@eocunnextservicehub.sbs|rmkRWW8316",
"v25n2t4bh24h60@eocunnextservicehub.sbs|necDMJ8465",
"v25n2t4bh24h58@eocunnextservicehub.sbs|bryFCB2072",
"v25n2t4bh24h54@eocunnextservicehub.sbs|tqdHNH6757",
"v25n2t4bh24h5@eocunnextservicehub.sbs|wfaLYC6045",
"v25n2t4bh24h52@eocuncloudservicehub.sbs|wqvDMS8967",
"v25n2t4bh24h56@eocunnextservicehub.sbs|ljqTWL9714",
"v25n2t4bh24h62@eocuncloudservicehub.sbs|qhyPNN5225",
"v25n2t4bh24h63@eocuncloudservicehub.sbs|hmyZDY8262",
     ],    
    "veo3_pro_bh":[    
    ],
    "grok_bhf":[
"zunbeg@aq16.tempdukviet.click|Supergrok123@",
"neglow@mail29.capytumbum.online|Supergrok123@",
"bimmod@av11.tempdukviet.site|Supergrok123@",
"dakcen@aq23.tempdukviet.click|Supergrok123@",
"zoonas@mail39.capytumbum.online|Supergrok123@",
"remkaf@vip10.tempdukviet.click|Supergrok123@",
"vazsep@vip5.tempdukviet.click|Supergrok123@",
"norsav@mail30.capytumbum.online|Supergrok123@",
"kefkev@ahihi25.tempdukviet.site|Supergrok123@",
"kivgeg@av3.tempdukviet.site|Supergrok123@",
"bollae@aq11.tempdukviet.click|Supergrok123@",
"golkom@aq51.tempdukviet.click|Supergrok123@",
"zoffao@vip16.tempdukviet.click|Supergrok123@",
"fuetiw@vip3.tempdukviet.click|Supergrok123@",
     ],
    "Fam_Ultra":[
    ],
    "veo3_0k_bhf_1m": ["MANUAL"] * 0,
    "veo3_ultra_bhf_1m": ["MANUAL"] * 0,
    "veo3_25k_bhf_1m": ["MANUAL"] * 0,
    "veo3_0cre_12m": ["MANUAL"] * 5,
    "veo3_bhf_12m": ["MANUAL"] * 5,
     "cdk_gpt_go": [

     ],
     "cdk_gpt_plus_1m": [
"8C1B8093-F8C7-4E21-AA1A-47077EF2B5BE",
"99578654-8C0E-4F13-AB02-F47588A9374F",
"0D9114AC-D8F9-4FA8-9415-6298F39191F7",
"BFA5EE58-8E45-43C9-B205-C705226DD195",
"D2A03D57-A110-44C7-B5E6-90DD3F1120C0",

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
