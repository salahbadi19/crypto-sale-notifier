# bot.py
# بوت USDT Flash - نسخة نهائية مع زر تأكيد التحويل
# الإصدار: v4.0 (محدث - لا يحذف الرسائل - توكن جديد)

import logging
import re
from typing import Dict, Any
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, constants
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes
)

# --------------------------
# 🧩 1) البيانات الثابتة
# --------------------------

BOT_TOKEN = "8448080764:AAFQqt_QCJroubj_0mwqZ-ZQh2fp6LSwQoE"  # ✅ التوكن الجديد
ADMIN_ID = 8251525181
SUPPORT_USERNAME = "ahmede726"
PROOFS_CHANNEL = "flashusdt2000"

# ✅ عنوان الدفع (يتم الدفع إليه)
PAYMENT_ADDRESS = "TAp2XpxaBddzH9H1sga4vNdAvSkBRoLEH4"
NETWORK_NAME = "TRON (TRC-20)"
PACKS = [500, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000]
PRICE_PER_500 = 40  # دولار

# 🪙 أسماء العملات
CURRENCIES = {
    "usdt_flash": "💵 USDT Flash",
    "bnb_flash": "🔶 BNB Flash",
    "usdtz_flash": "🔷 USDT.Z Flash",
}

# 🛠 طرق الاستلام
NETWORKS = {
    "binance": "💼 عبر معرف Binance",
    "erc20": "🌐 Ethereum (ERC-20)",
    "trc20": "🌀 TRON (TRC-20)",
}

# 📄 وصف العملات
DESCRIPTIONS = {
    "usdt_flash": "<b>💵 USDT Flash</b>\n\nخدمة فلاش فورية مع نسبة نجاح عالية.\nاختَر الباقة المناسبة واضغط <b>شراء الآن</b>.",
    "bnb_flash": "<b>🔶 BNB Flash</b>\n\nتنفيذ سريع ورسوم منخفضة.\nاختَر الباقة المناسبة واضغط <b>شراء الآن</b>.",
    "usdtz_flash": "<b>🔷 USDT.Z Flash</b>\n\nإصدار خاص بسرعات تحويل محسّنة.\nاختَر الباقة المناسبة واضغط <b>شراء الآن</b>.",
}

# --------------------------
# 🧠 حالة المستخدمين
# --------------------------
user_states: Dict[int, Dict[str, Any]] = {}
admin_waiting: Dict[int, str] = {}

# --------------------------
# 📜 التسجيل
# --------------------------
logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO
)
logger = logging.getLogger("flash-bot")

# --------------------------
# 🔧 وظائف مساعدة
# --------------------------

def get_full_name(update: Update) -> str:
    user = update.effective_user
    return f"{user.first_name or ''} {user.last_name or ''}".strip() or "مستخدم"

def get_username(update: Update) -> str:
    return f"@{update.effective_user.username}" if update.effective_user.username else "بدون_يوزر"

def create_keyboard(buttons: list, cols: int = 2) -> InlineKeyboardMarkup:
    keyboard = [buttons[i:i + cols] for i in range(0, len(buttons), cols)]
    return InlineKeyboardMarkup(keyboard)

# ❌ تم إزالة safe_delete_message تمامًا
# --------------------------
# طلب عرض خاص
# --------------------------
async def contact_support(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=(
            "💬 يمكنك التواصل معنا لطلب عرض خاص:\n"
            f"• الدعم الفني: @{SUPPORT_USERNAME}\n"
            "• ارسل لنا التفاصيل لنقوم بمساعدتك مباشرة."
        )
    )

# --------------------------
# 📡 Handlers
# --------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    is_admin = user.id == ADMIN_ID

    buttons = [
        InlineKeyboardButton("🎁 عروضنا", callback_data="offers"),
        InlineKeyboardButton("💬 طلب خاص", callback_data="contact_support"),
        InlineKeyboardButton("📢 قناة الإثباتات", url="https://t.me/flashusdt2000"),
        InlineKeyboardButton("🛟 الدعم الفني", url="https://t.me/ahmede726")
    ]
    if is_admin:
        buttons.append(InlineKeyboardButton("🔐 لوحة الإدارة", callback_data="admin_panel"))

    reply_markup = create_keyboard(buttons, cols=2)

    caption = (
        "<b>👋 أهلاً بك في بوت العروض الخاصة</b>\n\n"
        "◀️ اختر من القائمة أدناه لعرض <b>🎁 عروضنا</b> أو تواصل مع <b>الدعم الفني</b>.\n"
        "🧾 في حال وجود أي استفسار لا تتردد بالتواصل."
    )

    # ✅ تم إزالة: await update.message.delete()
    # لن يحذف أي رسالة

    try:
        await context.bot.send_video(
            chat_id=user.id,
            video="https://i.imgur.com/E98VDqh.mp4",
            caption=caption,
            reply_markup=reply_markup,
            parse_mode=constants.ParseMode.HTML
        )
    except Exception:
        await context.bot.send_message(
            chat_id=user.id,
            text=caption,
            reply_markup=reply_markup,
            parse_mode=constants.ParseMode.HTML
        )

    if user.id not in user_states:
        user_states[user.id] = {"step": "idle"}

# --------------------------
# عرض العروض
# --------------------------

async def show_offers(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    buttons = [
        InlineKeyboardButton("💵 USDT Flash", callback_data="currency_usdt_flash"),
        InlineKeyboardButton("🔶 BNB Flash", callback_data="currency_bnb_flash"),
        InlineKeyboardButton("🔷 USDT.Z Flash", callback_data="currency_usdtz_flash"),
        InlineKeyboardButton("🔙 رجوع", callback_data="start")
    ]

    reply_markup = create_keyboard(buttons, cols=2)

    # ✅ تم إزالة: await query.delete_message()
    # سيبقى الزر "عرض العروض" كما هو

    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text="🎁 اختر العملة لعرض التفاصيل:",
        reply_markup=reply_markup
    )

async def show_currency_details(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    currency_key = query.data.split("_", 1)[1]

    if currency_key not in DESCRIPTIONS:
        await context.bot.send_message(query.message.chat_id, "⚠️ عملة غير معروفة.")
        return

    buttons = [
        InlineKeyboardButton("🛒 شراء الآن", callback_data=f"buy_{currency_key}"),
        InlineKeyboardButton("🔙 رجوع", callback_data="offers")
    ]
    reply_markup = create_keyboard(buttons, cols=2)

    try:
        await context.bot.send_video(
            chat_id=query.message.chat_id,
            video="https://i.imgur.com/kPG4d6B.mp4",
            caption=DESCRIPTIONS[currency_key],
            reply_markup=reply_markup,
            parse_mode=constants.ParseMode.HTML
        )
    except Exception:
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=DESCRIPTIONS[currency_key],
            reply_markup=reply_markup,
            parse_mode=constants.ParseMode.HTML
        )
    # ✅ تم إزالة: await query.delete_message()

# --------------------------
# تدفق الشراء
# --------------------------

async def show_packs(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    currency_key = query.data.split("_", 1)[1]

    buttons = []
    for amount in PACKS:
        price = (amount // 500) * PRICE_PER_500
        buttons.append(
            InlineKeyboardButton(
                f"{amount} — {price}$",
                callback_data=f"pack_{currency_key}_{amount}"
            )
        )
    buttons.append(InlineKeyboardButton("🔙 رجوع", callback_data=f"currency_{currency_key}"))

    reply_markup = create_keyboard(buttons, cols=2)

    # ✅ تم إزالة: await query.delete_message()

    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=f"🛒 <b>اختر الباقة</b>\n\nالسعر يُحسب تلقائيًا: كل 500 = <b>{PRICE_PER_500}$</b>",
        reply_markup=reply_markup,
        parse_mode=constants.ParseMode.HTML
    )

async def select_pack(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    match = re.match(r"pack_([a-zA-Z_]+)_(\d+)", query.data)
    if not match:
        await context.bot.send_message(query.message.chat_id, "❌ خطأ في الباقة.")
        return

    currency_key, amount_str = match.groups()
    amount = int(amount_str)
    price = (amount // 500) * PRICE_PER_500

    user = update.effective_user
    user_id = user.id

    user_states[user_id] = {
        "step": "awaiting_method",
        "currency": currency_key,
        "amount": amount,
        "price": price,
        "user_name": get_full_name(update),
        "username": get_username(update),
        "user_id": user_id
    }

    buttons = [
        InlineKeyboardButton("💼 عبر معرف Binance", callback_data="method_binance"),
        InlineKeyboardButton("🌐 Ethereum (ERC-20)", callback_data="method_erc20"),
        InlineKeyboardButton("🌀 TRON (TRC-20)", callback_data="method_trc20"),
        InlineKeyboardButton("🔙 رجوع", callback_data=f"buy_{currency_key}")
    ]

    reply_markup = create_keyboard(buttons, cols=2)

    # ✅ تم إزالة: await query.delete_message()

    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text="📥 <b>اختر طريقة الاستلام</b>",
        reply_markup=reply_markup,
        parse_mode=constants.ParseMode.HTML
    )

async def select_method(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    method_key = query.data.replace("method_", "")
    user_id = update.effective_user.id

    if user_id not in user_states or user_states[user_id]["step"] != "awaiting_method":
        await context.bot.send_message(query.message.chat_id, "⚠️ حدث خطأ. ابدأ من جديد.")
        return

    user_states[user_id]["method"] = method_key
    prompts = {
        "binance": "🔹 أرسل <b>معرّف Binance</b> الخاص بك.",
        "erc20": "🔹 أرسل <b>عنوان محفظة Ethereum (ERC-20)</b>.",
        "trc20": "🔹 أرسل <b>عنوان محفظة TRON (TRC-20)</b>."
    }

    # ✅ تم إزالة: await query.delete_message()

    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=prompts.get(method_key, "⚠️ طريقة غير معروفة."),
        parse_mode=constants.ParseMode.HTML
    )

    user_states[user_id]["step"] = "awaiting_wallet"

# --------------------------
# إدخال المحفظة وتعليمات الدفع
# --------------------------

async def handle_wallet_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    text = update.message.text.strip()

    if user_id not in user_states or user_states[user_id]["step"] != "awaiting_wallet":
        return

    user_states[user_id]["wallet"] = text
    state = user_states[user_id]

    payment_msg = (
        "💳 <b>تعليمات الدفع</b>\n\n"
        f"المبلغ المطلوب: <b>{state['price']}$</b>\n"
        f"عنوان الدفع: <code>{PAYMENT_ADDRESS}</code>\n"
        f"الشبكة: <b>{NETWORK_NAME}</b>\n\n"
        "⚠️ قبل إرسال الصورة، تأكد من إتمام التحويل إلى هذا العنوان.\n"
        "اضغط الزر أدناه بعد الدفع لإرسال لقطة شاشة."
    )

    keyboard = [[InlineKeyboardButton("✅ تم الدفع", callback_data=f"paid_{state['currency']}_{state['amount']}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        text=payment_msg,
        reply_markup=reply_markup,
        parse_mode=constants.ParseMode.HTML
    )

    user_states[user_id]["step"] = "awaiting_payment_confirmation"

    # ✅ تم إزالة رسالة "طلب جديد" للأدمن هنا

# --------------------------
# استلام لقطة الشاشة
# --------------------------

async def payment_done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    if user_id not in user_states or user_states[user_id]["step"] != "awaiting_payment_confirmation":
        await context.bot.send_message(query.message.chat_id, "الطلب غير موجود.")
        return

    # ✅ تم إزالة: await query.delete_message()

    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text="📸 من فضلك أرسل <b>لقطة شاشة</b> تُثبت عملية الدفع (يجب أن تظهر العنوان والشبكة والمبلغ).",
        parse_mode=constants.ParseMode.HTML
    )

async def handle_screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id

    if user_id not in user_states or user_states[user_id]["step"] != "awaiting_payment_confirmation":
        return

    if not update.message.photo:
        await update.message.reply_text("⚠️ من فضلك أرسل <b>صورة</b> (لقطة شاشة)، وليس رسالة نصية.", parse_mode=constants.ParseMode.HTML)
        return

    user_states[user_id]["step"] = "pending"
    user_states[user_id]["screenshot_msg_id"] = update.message.message_id

    # تأكيد للمستخدم
    state = user_states[user_id]
    await update.message.reply_text(
        f"✅ تم استلام لقطة الشاشة.\n"
        f"⏳ سيتم التحقق من طلبك خلال 5 دقائق.\n\n"
        f"📦 <b>تفاصيل الطلب:</b>\n"
        f"• العملة: {CURRENCIES.get(state['currency'])}\n"
        f"• الكمية: {state['amount']}\n"
        f"• الطريقة: {NETWORKS.get(state['method'])}\n"
        f"• العنوان: <code>{state['wallet']}</code>",
        parse_mode=constants.ParseMode.HTML
    )

    # === ✅ إرسال الصورة + التفاصيل + الزر للأدمن ===
    try:
        photo_file = await context.bot.get_file(update.message.photo[-1].file_id)

        admin_caption = (
            f"📥 <b>طلب معلق من:</b> {state['user_name']} (@{state['username']})\n"
            f"💱 <b>العملة:</b> {CURRENCIES.get(state['currency'])}\n"
            f"📦 <b>الكمية:</b> {state['amount']}\n"
            f"🏦 <b>العنوان:</b> <code>{state['wallet']}</code>\n"
            f"💰 <b>السعر:</b> {state['price']}$\n"
            f"👤 <b>ID:</b> {user_id}"
        )

        keyboard = [[InlineKeyboardButton("✅ تأكيد التحويل", callback_data=f"confirm_{user_id}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await context.bot.send_photo(
            chat_id=ADMIN_ID,
            photo=photo_file.file_path,
            caption=admin_caption,
            reply_markup=reply_markup,
            parse_mode=constants.ParseMode.HTML
        )
    except Exception as e:
        logger.error(f"فشل إرسال الصورة والتفاصيل للأدمن: {e}")
        try:
            fallback_msg = (
                f"⚠️ لم يتمكن البوت من إرسال الصورة.\n"
                f"طلب من: {state['user_name']} (@{state['username']})\n"
                f"العملة: {CURRENCIES.get(state['currency'])} | الكمية: {state['amount']}\n"
                f"العنوان: <code>{state['wallet']}</code>"
            )
            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=fallback_msg,
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅ تأكيد التحويل", callback_data=f"confirm_{user_id}")]]),
                parse_mode=constants.ParseMode.HTML
            )
        except:
            pass

# --------------------------
# ✅ تأكيد التحويل
# --------------------------

async def confirm_order_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    try:
        target_user_id = int(query.data.split("_", 1)[1])
    except:
        await query.edit_message_text("❌ خطأ في تحديد المستخدم.")
        return

    if target_user_id not in user_states or user_states[target_user_id]["step"] != "pending":
        await query.edit_message_text("❌ الطلب غير موجود أو تم تأكيده مسبقًا.")
        return

    state = user_states[target_user_id]
    currency_display = CURRENCIES.get(state["currency"], state["currency"])

    # ✅ رسالة تأكيد أولية للمستخدم
    try:
        await context.bot.send_message(
            chat_id=target_user_id,
            text=(
                "✅ <b>تم تأكيد طلبك!</b>\n\n"
                "جارٍ تحويل <b>{amount} {currency}</b> إلى عنوانك...\n"
                "سيصلك الرصيد خلال دقائق قليلة.\n\n"
                "شكرًا لثقتك بنا ❤️"
            ).format(amount=state['amount'], currency=currency_display.split()[1]),
            parse_mode=constants.ParseMode.HTML
        )
    except Exception as e:
        logger.error(f"فشل إرسال رسالة التأكيد للمستخدم {target_user_id}: {e}")

    user_states[target_user_id]["step"] = "completed"
    await query.edit_message_text(f"✅ تم التأكيد - {state['user_name']}")

# --------------------------
# لوحة الإدارة
# --------------------------

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if update.effective_user.id != ADMIN_ID:
        return

    keyboard = [
        [InlineKeyboardButton("✏️ تعديل عنوان الدفع", callback_data="edit_address")],
        [InlineKeyboardButton("📦 تعديل الباقات", callback_data="edit_packs")],
        [InlineKeyboardButton("📋 عرض الطلبات", callback_data="view_requests")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="start")]
    ]

    # ✅ تم إزالة: await query.delete_message()

    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text="🔐 <b>لوحة الإدارة</b>",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=constants.ParseMode.HTML
    )

async def edit_address_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    if update.effective_user.id != ADMIN_ID:
        return
    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text="✏️ أرسل الآن <b>عنوان الدفع الجديد</b> ليتم تحديثه.",
        parse_mode=constants.ParseMode.HTML
    )
    admin_waiting[ADMIN_ID] = "awaiting_payment_info"

async def edit_packs_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    if update.effective_user.id != ADMIN_ID:
        return
    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text="✏️ أرسل القيم كأرقام مفصولة بفواصل (مثال: 500,1000,1500).",
        parse_mode=constants.ParseMode.HTML
    )
    admin_waiting[ADMIN_ID] = "awaiting_packs"

async def view_pending_requests(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    if update.effective_user.id != ADMIN_ID:
        return

    pending = [s for s in user_states.values() if s.get("step") == "pending"]
    if not pending:
        await context.bot.send_message(chat_id=query.message.chat_id, text="🟢 لا توجد طلبات معلقة.")
        return

    await context.bot.send_message(chat_id=query.message.chat_id, text="📋 الطلبات المعلقة:")

    for s in pending:
        msg = (
            f"👤 <b>العميل:</b> {s['user_name']} (@{s['username']})\n"
            f"💱 <b>العملة:</b> {CURRENCIES.get(s['currency'])}\n"
            f"📦 <b>الكمية:</b> {s['amount']}\n"
            f"🏦 <b>العنوان:</b> <code>{s['wallet']}</code>"
        )
        keyboard = [[InlineKeyboardButton("✅ تأكيد التحويل", callback_data=f"confirm_{s['user_id']}")]]
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=msg,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=constants.ParseMode.HTML
        )

# --------------------------
# معالجة الرسائل
# --------------------------

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id

    # فقط الأدمن يمكنه إدخال أوامر لوحة الإدارة
    if user_id == ADMIN_ID and ADMIN_ID in admin_waiting:
        action = admin_waiting[ADMIN_ID]
        if action == "awaiting_payment_info":
            global PAYMENT_ADDRESS
            PAYMENT_ADDRESS = update.message.text.strip()
            await update.message.reply_text("✅ تم تحديث عنوان الدفع بنجاح.")
            del admin_waiting[ADMIN_ID]
        elif action == "awaiting_packs":
            try:
                global PACKS
                PACKS = sorted(set(map(int, [x.strip() for x in update.message.text.split(",") if x.strip()])))
                await update.message.reply_text("✅ تم تحديث قائمة الباقات بنجاح.")
                del admin_waiting[ADMIN_ID]
            except:
                await update.message.reply_text("⚠️ صيغة غير صحيحة. جرّب مجددًا.")
        return

    # معالجة الرسائل فقط إذا كان المستخدم في تدفق شراء
    if user_id in user_states:
        if user_states[user_id]["step"] == "awaiting_wallet":
            await handle_wallet_input(update, context)
        elif user_states[user_id]["step"] == "awaiting_payment_confirmation":
            await handle_screenshot(update, context)

# --------------------------
# معالج الأخطاء
# --------------------------

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error("Error: %s\n%s", context.error, context.error.__traceback__)
    if isinstance(update, Update) and update.effective_chat:
        try:
            await context.bot.send_message(update.effective_chat.id, "⚠️ حدث خطأ داخلي. تم الإبلاغ.")
        except:
            pass

# --------------------------
# 🚀 تشغيل البوت
# --------------------------

def main() -> None:
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(start, pattern="^start$"))
    application.add_handler(CallbackQueryHandler(show_offers, pattern="^offers$"))
    application.add_handler(CallbackQueryHandler(show_currency_details, pattern=r"^currency_"))
    application.add_handler(CallbackQueryHandler(show_packs, pattern=r"^buy_"))
    application.add_handler(CallbackQueryHandler(select_pack, pattern=r"^pack_"))
    application.add_handler(CallbackQueryHandler(select_method, pattern=r"^method_"))
    application.add_handler(CallbackQueryHandler(payment_done, pattern=r"^paid_"))
    application.add_handler(CallbackQueryHandler(admin_panel, pattern="^admin_panel$"))
    application.add_handler(CallbackQueryHandler(edit_address_prompt, pattern="^edit_address$"))
    application.add_handler(CallbackQueryHandler(edit_packs_prompt, pattern="^edit_packs$"))
    application.add_handler(CallbackQueryHandler(view_pending_requests, pattern="^view_requests$"))
    application.add_handler(CallbackQueryHandler(confirm_order_callback, pattern=r"^confirm_\d+$"))
    application.add_handler(CallbackQueryHandler(contact_support, pattern="^contact_support$"))

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.PHOTO, handle_screenshot))

    application.add_error_handler(error_handler)

    logger.info("🚀 البوت يعمل. الأدمن: %s", ADMIN_ID)
    application.run_polling()

if __name__ == "__main__":
    main()
