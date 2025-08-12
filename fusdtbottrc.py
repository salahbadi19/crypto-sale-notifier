import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

# تفعيل التسجيل
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# ⚙️ الإعدادات
ADMIN_ID = 8251525181
SUPPORT_USERNAME = "@ahmede726"
PROOFS_CHANNEL = "@flashusdt2000"

# 📦 الباقات
PACKS = [500, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000]
PRICE_PER_500 = 40  # 40 دولار لكل 500 وحدة

# 🔗 الروابط
WELCOME_VIDEO = "https://i.imgur.com/E98VDqh_lq.mp4"
PROMO_VIDEO = "https://i.imgur.com/kPG4d6B_lq.mp4"

# 💸 عنوان الدفع (يمكن تغييره من لوحة الإدارة)
PAYMENT_ADDRESS = "TAp2XpxaBddzH9H1sga4vNdAvSkBRoLEH4"
NETWORK_NAME = "TRON (TRC-20)"

# 📝 وصف العملات (عالمي)
DESCRIPTIONS = {
    "usdt_flash": (
        "🎯 <b>USDT Flash</b>\n\n"
        "• ✅ متوافقة مع منصات الخيارات والميتا ماسك\n"
        "• 🕒 الصلاحية: 90 يوماً من تاريخ الشراء\n"
        "• 🌐 تدعم شبكات: BSC، TRON، Ethereum\n"
        "• 💸 تُستخدم في:\n\n"
        "🚀 <b>IQ Option • Pocket Option • Quotex</b>\n"
        "💼 <b>Binance • Trust Wallet • MetaMask</b>"
    ),
    "bnb_flash": (
        "⚡ <b>BNB Flash</b>\n\n"
        "• ✅ مناسبة لدفع الرسوم والتحويلات\n"
        "• 🕒 الصلاحية: 90 يوماً من تاريخ الشراء\n"
        "• 🌐 تدعم شبكات: BSC، Polygon\n"
        "• 💸 تُستخدم في:\n\n"
        "📈 <b>IQ Option • Pocket Option • Quotex</b>\n"
        "💼 <b>Binance • Trust Wallet • MetaMask</b>"
    ),
    "usdtz_flash": (
        "💎 <b>USDT.Z Flash</b>\n\n"
        "• ✅ عملة مستقرة 1:1 مع الدولار\n"
        "• 🕒 الصلاحية: 90 يوماً من تاريخ الشراء\n"
        "• 🌐 تدعم شبكات: Polygon، Arbitrum\n"
        "• 💸 مثالية للتداول الآمن\n\n"
        "🔐 <b>IQ Option • Pocket Option • Quotex</b>\n"
        "💼 <b>Binance • Trust Wallet • MetaMask</b>"
    )
}

# 🛒 حالة المستخدم
user_states = {}

# 🚀 رسالة البدء
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    keyboard = [
        [InlineKeyboardButton("📌 قناة الإثباتات", url=f"https://t.me/{PROOFS_CHANNEL[1:]}")],
        [InlineKeyboardButton("🛠 الدعم الفني", url=f"https://t.me/{SUPPORT_USERNAME[1:]}")],
        [InlineKeyboardButton("🎁 عروضنا", callback_data="offers")],
        [InlineKeyboardButton("💬 طلب عرض خاص", callback_data="special_offer")]
    ]
    if user.id == ADMIN_ID:
        keyboard.append([InlineKeyboardButton("🔐 لوحة الإدارة", callback_data="admin_panel")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    welcome_text = (
        f"مرحباً {user.first_name}! 👋\n\n"
        "أهلاً بك في <b>بوت العملات الرقمية للخيارات الثنائية</b> 💎\n"
        "نقدم لك أفضل العملات لتشغيلها على منصات الخيارات!\n\n"
        "✅ تُستخدم على: IQ Option، Pocket Option، Quotex\n"
        "✅ متوافقة مع: Binance، Trust Wallet، MetaMask\n"
        "✅ صلاحية تصل إلى 90 يوماً\n\n"
        "اختر من القائمة أدناه 👇"
    )
    try:
        await update.message.reply_video(
            video=WELCOME_VIDEO,
            caption=welcome_text,
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
    except Exception as e:
        logger.error(f"فشل إرسال الفيديو الترحيبي: {e}")
        await update.message.reply_text("حدث خطأ، يرجى المحاولة لاحقاً.")

# 🔄 معالجة الأزرار
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    try:
        await query.answer()
    except:
        pass

    # --- عروضنا ---
    if query.data == "offers":
        keyboard = [
            [InlineKeyboardButton("💵 USDT Flash", callback_data="usdt_flash")],
            [InlineKeyboardButton("🔶 BNB Flash", callback_data="bnb_flash")],
            [InlineKeyboardButton("🔷 USDT.Z Flash", callback_data="usdtz_flash")],
            [InlineKeyboardButton("🔙 رجوع", callback_data="start")]
        ]
        try:
            await query.edit_message_caption("🎯 اختر العملة المناسبة:", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
        except:
            await query.message.reply_text("🎯 اختر العملة المناسبة:", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
            await query.message.delete()

    # --- عرض تفاصيل العملة ---
    elif query.data in ["usdt_flash", "bnb_flash", "usdtz_flash"]:
        currency = query.data
        try:
            await query.delete_message()
        except:
            pass
        await query.message.reply_video(
            video=PROMO_VIDEO,
            caption=DESCRIPTIONS[currency],
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🛒 شراء الآن", callback_data=f"buy_{currency}")],
                [InlineKeyboardButton("🔙 رجوع", callback_data="offers")]
            ]),
            parse_mode='HTML'
        )

    # --- شراء العملة ---
    elif query.data.startswith("buy_"):
        currency = query.data.replace("buy_", "")
        keyboard = []
        for i in range(0, len(PACKS), 2):
            row = [
                InlineKeyboardButton(f"{PACKS[i]} (>${PACKS[i]//500 * PRICE_PER_500})", callback_data=f"pack_{currency}_{PACKS[i]}")
            ]
            if i+1 < len(PACKS):
                row.append(InlineKeyboardButton(f"{PACKS[i+1]} (>${PACKS[i+1]//500 * PRICE_PER_500})", callback_data=f"pack_{currency}_{PACKS[i+1]}"))
            keyboard.append(row)
        keyboard.append([InlineKeyboardButton("🔙 رجوع", callback_data=currency)])
        try:
            await query.edit_message_caption(f"📦 اختر كمية {currency.upper()}:", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
        except:
            await query.message.reply_text(f"📦 اختر كمية {currency.upper()}:", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
            await query.message.delete()

    # --- اختيار الكمية ---
    elif query.data.startswith("pack_"):
        try:
            _, currency_amount = query.data.split("_", 1)
            currency, amount_str = currency_amount.rsplit("_", 1)
            amount = int(amount_str)
            total_price = (amount // 500) * PRICE_PER_500
            user_states[query.from_user.id] = {
                "step": "awaiting_wallet",
                "currency": currency,
                "amount": amount,
                "price": total_price,
                "user_name": query.from_user.full_name,
                "user_id": query.from_user.id,
                "username": f"@{query.from_user.username}" if query.from_user.username else "غير معروف"
            }

            keyboard = [
                [InlineKeyboardButton("💼 عبر معرف Binance", callback_data="method_binance")],
                [InlineKeyboardButton("🌐 Ethereum (ERC-20)", callback_data="method_erc20")],
                [InlineKeyboardButton("🌀 TRON (TRC-20)", callback_data="method_trc20")],
                [InlineKeyboardButton("🔙 رجوع", callback_data=f"buy_{currency}")]
            ]
            try:
                await query.edit_message_caption("📌 اختر طريقة استلام العملة:", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
            except:
                await query.message.reply_text("📌 اختر طريقة استلام العملة:", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
                await query.message.delete()

        except Exception as e:
            logger.error(f"Error in pack: {e}")
            await query.message.reply_text("❌ حدث خطأ داخلي.")

    # --- اختيار الطريقة ---
    elif query.data.startswith("method_"):
        method = query.data.replace("method_", "")
        user_states[query.from_user.id]["method"] = method
        prompts = {
            "binance": "💼 أرسل معرف Binance الخاص بك",
            "erc20": "🌐 أرسل عنوان محفظتك على Ethereum (ERC-20)",
            "trc20": "🌀 أرسل عنوان محفظتك على TRON (TRC-20)"
        }
        keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data=f"pack_{user_states[query.from_user.id]['currency']}_{user_states[query.from_user.id]['amount']}")]]
        try:
            await query.edit_message_text(prompts[method], reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
        except:
            await query.message.reply_text(prompts[method], reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
            await query.message.delete()

    # --- طلب عرض خاص ---
    elif query.data == "special_offer":
        keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="start")]]
        try:
            await query.edit_message_caption(
                f"📞 لطلب عرض خاص أو كميات كبيرة:\nتواصل مع الدعم: {SUPPORT_USERNAME}\nسيتم الرد عليك في أسرع وقت!",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='HTML'
            )
        except:
            await query.message.reply_text(
                f"📞 لطلب عرض خاص أو كميات كبيرة:\nتواصل مع الدعم: {SUPPORT_USERNAME}\nسيتم الرد عليك في أسرع وقت!",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='HTML'
            )
            await query.message.delete()

    # --- لوحة الإدارة ---
    elif query.data == "admin_panel" and query.from_user.id == ADMIN_ID:
        keyboard = [
            [InlineKeyboardButton("✏️ تعديل عنوان الدفع", callback_data="edit_payment")],
            [InlineKeyboardButton("📦 تعديل الباقات", callback_data="edit_packs")],
            [InlineKeyboardButton("📋 عرض الطلبات", callback_data="view_orders")],
            [InlineKeyboardButton("🔙 رجوع", callback_data="start")]
        ]
        try:
            await query.edit_message_caption("🔐 <b>لوحة الإدارة</b>", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
        except:
            await query.message.reply_text("🔐 <b>لوحة الإدارة</b>", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
            await query.message.delete()

    # --- تعديل عنوان الدفع ---
    elif query.data == "edit_payment" and query.from_user.id == ADMIN_ID:
        user_states[query.from_user.id] = {"step": "awaiting_payment_info"}
        keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="admin_panel")]]
        try:
            await query.edit_message_caption("📌 أرسل عنوان الدفع الجديد:", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
        except:
            await query.message.reply_text("📌 أرسل عنوان الدفع الجديد:", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
            await query.message.delete()

    # --- تعديل الباقات ---
    elif query.data == "edit_packs" and query.from_user.id == ADMIN_ID:
        user_states[query.from_user.id] = {"step": "awaiting_packs"}
        keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="admin_panel")]]
        try:
            await query.edit_message_caption("📌 أرسل الباقات الجديدة (مفصولة بفواصل):", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
        except:
            await query.message.reply_text("📌 أرسل الباقات الجديدة (مفصولة بفواصل):", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
            await query.message.delete()

    # --- عرض الطلبات ---
    elif query.data == "view_orders" and query.from_user.id == ADMIN_ID:
        pending_orders = {}
        for uid, data in user_states.items():
            if isinstance(data, dict) and data.get("step") == "pending":
                pending_orders[uid] = data

        if not pending_orders:
            msg = "📋 <b>الطلبات المعلقة</b>\n\n• لا توجد طلبات حالياً."
        else:
            msg = "📋 <b>الطلبات المعلقة:</b>\n\n"
            for uid, data in pending_orders.items():
                username = data.get("username", "غير معروف")
                full_name = data.get("user_name", "مستخدم")
                msg += (
                    f"👤 {full_name} ({username})\n"
                    f"🪙 {data['amount']} {data['currency'].upper()}\n"
                    f"💳 {data['method']}\n"
                    f"📤 <code>{data['wallet']}</code>\n"
                    f"💰 ${data['price']}\n"
                    f"✅ /confirm {uid}\n\n"
                )
        keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="admin_panel")]]
        try:
            await query.edit_message_caption(msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
        except:
            await query.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
            await query.message.delete()

    # --- رجوع للرئيسية ---
    elif query.data == "start":
        try:
            await query.edit_message_caption(
                "اختر من القائمة أدناه 👇",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("📌 قناة الإثباتات", url=f"https://t.me/{PROOFS_CHANNEL[1:]}")],
                    [InlineKeyboardButton("🛠 الدعم الفني", url=f"https://t.me/{SUPPORT_USERNAME[1:]}")],
                    [InlineKeyboardButton("🎁 عروضنا", callback_data="offers")],
                    [InlineKeyboardButton("💬 طلب عرض خاص", callback_data="special_offer")]
                ]),
                parse_mode='HTML'
            )
        except:
            await query.message.reply_text("اختر من القائمة أدناه 👇", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🎁 عروضنا", callback_data="offers")]]), parse_mode='HTML')
            await query.message.delete()

# 🔄 معالجة "تم الدفع"
async def paid_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    try:
        await query.answer()
    except:
        pass

    try:
        await query.edit_message_text(
            "📸 <b>من فضلك أرسل لقطة شاشة للتأكيد على الدفع</b>.\n\n"
            "تأكد من ظهور:\n"
            f"• العنوان: <code>{PAYMENT_ADDRESS}</code>\n"
            f"• الشبكة: {NETWORK_NAME}\n\n"
            "✅ سيتم التحقق من طلبك فوراً بعد الإرسال.",
            parse_mode='HTML'
        )
    except:
        try:
            await query.message.reply_text(
                "📸 <b>من فضلك أرسل لقطة شاشة للتأكيد على الدفع</b>.\n\n"
                "تأكد من ظهور:\n"
                f"• العنوان: <code>{PAYMENT_ADDRESS}</code>\n"
                f"• الشبكة: {NETWORK_NAME}\n\n"
                "✅ سيتم التحقق من طلبك فوراً بعد الإرسال.",
                parse_mode='HTML'
            )
        except:
            pass

# 📩 معالجة الرسائل
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global PAYMENT_ADDRESS

    user_id = update.effective_user.id
    state = user_states.get(user_id, {})

    # 🖋️ إدخال عنوان المحفظة
    if state.get("step") == "awaiting_wallet" and "method" in state:
        wallet = update.message.text
        user_states[user_id]["wallet"] = wallet
        currency = state["currency"]
        amount = state["amount"]
        price = state["price"]
        method = state["method"]
        full_name = state.get("user_name", "مستخدم")
        username = state.get("username", "غير معروف")

        # ✅ إشعار للإدارة مع اسم المستخدم
        try:
            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=(
                    f"📥 <b>طلب جديد</b>\n"
                    f"• المستخدم: {full_name} ({username})\n"
                    f"• العملة: {currency.upper()}\n"
                    f"• الكمية: {amount}\n"
                    f"• السعر: ${price}\n"
                    f"• الطريقة: {method}\n"
                    f"• العنوان: <code>{wallet}</code>"
                ),
                parse_mode='HTML'
            )
        except Exception as e:
            logger.error(f"فشل إرسال إشعار للإدارة: {e}")

        # عرض عنوان الدفع
        payment_text = (
            f"💸 <b>المبلغ المطلوب: ${price}</b>\n\n"
            f"📌 <b>أرسل الدفع إلى:</b>\n"
            f"<code>{PAYMENT_ADDRESS}</code>\n"
            f"🌐 <b>الشبكة:</b> {NETWORK_NAME}\n\n"
            f"✅ بعد التحويل، اضغط على زر <b>تم الدفع</b> أدناه.\n\n"
            f"⚠️ <b>مهم:</b> بعد الضغط على الزر، يجب أن ترسل <b>لقطة شاشة</b> للتأكيد على الدفع."
        )
        keyboard = [[InlineKeyboardButton("✅ تم الدفع", callback_data=f"paid_{currency}_{amount}")]]
        await update.message.reply_text(payment_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
        user_states[user_id]["step"] = "awaiting_payment_confirmation"

    # ✏️ تعديل عنوان الدفع من الأدمن
    elif state.get("step") == "awaiting_payment_info" and user_id == ADMIN_ID:
        PAYMENT_ADDRESS = update.message.text.strip()
        try:
            await update.message.reply_text(f"✅ تم تحديث عنوان الدفع إلى:\n<code>{PAYMENT_ADDRESS}</code>", parse_mode='HTML')
        except:
            await context.bot.send_message(ADMIN_ID, "✅ تم تحديث عنوان الدفع.")
        del user_states[user_id]

    # 📦 تعديل الباقات
    elif state.get("step") == "awaiting_packs" and user_id == ADMIN_ID:
        try:
            global PACKS
            PACKS = sorted([int(x.strip()) for x in update.message.text.split(",") if x.strip().isdigit()])
            await update.message.reply_text(f"✅ تم تحديث الباقات: {PACKS}", parse_mode='HTML')
            del user_states[user_id]
        except:
            await update.message.reply_text("❌ خطأ في التنسيق.")

    # 🖼️ استقبال لقطة شاشة بعد الضغط على "تم الدفع"
    elif state.get("step") == "awaiting_payment_confirmation" and update.message.photo:
        currency = state["currency"]
        amount = state["amount"]
        wallet = state["wallet"]
        method = state["method"]
        price = state["price"]
        full_name = state.get("user_name", "مستخدم")
        username = state.get("username", "غير معروف")

        # تحديث الحالة
        user_states[user_id]["step"] = "pending"
        user_states[user_id]["screenshot_msg_id"] = update.message.message_id

        # ✅ رسالة للمستخدم
        await update.message.reply_text(
            f"✅ <b>تم استلام الدفع بنجاح!</b>\n\n"
            f"📌 تفاصيل طلبك:\n"
            f"• الكمية: {amount} {currency.upper()}\n"
            f"• السعر: ${price}\n"
            f"• طريقة الاستلام: {method}\n"
            f"• العنوان: <code>{wallet}</code>\n\n"
            f"🚀 سيتم التحويل إليك خلال 5 دقائق.\n"
            f"تحياتنا، فريق الدعم الفني.",
            parse_mode='HTML'
        )

        # ✅ إشعار للإدارة
        try:
            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=(
                    f"📸 <b>تم استلام الدفع</b>\n"
                    f"• المستخدم: {full_name} ({username})\n"
                    f"• العملة: {currency}\n"
                    f"• الكمية: {amount}\n"
                    f"• السعر: ${price}\n"
                    f"• الطريقة: {method}\n"
                    f"• العنوان: <code>{wallet}</code>\n"
                    f"✅ /confirm {user_id}"
                ),
                parse_mode='HTML'
            )
            await context.bot.forward_message(ADMIN_ID, update.effective_chat.id, update.message.message_id)
        except Exception as e:
            logger.error(f"فشل إرسال إشعار الدفع: {e}")

    # ❌ إذا أرسل نصاً بدلاً من صورة
    elif state.get("step") == "awaiting_payment_confirmation" and update.message.text:
        await update.message.reply_text("⚠️ من فضلك أرسل <b>لقطة شاشة</b> للتأكيد، وليس رسالة نصية.", parse_mode='HTML')

# 🛠 أمر تأكيد التحويل
async def confirm_transfer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        try:
            await update.message.reply_text("❌ ليس لديك صلاحية.", parse_mode='HTML')
        except:
            pass
        return
    if not context.args:
        try:
            await update.message.reply_text("❌ استخدم: /confirm <user_id>", parse_mode='HTML')
        except:
            pass
        return
    try:
        user_id = int(context.args[0])
    except ValueError:
        try:
            await update.message.reply_text("❌ المعرف يجب أن يكون رقماً.", parse_mode='HTML')
        except:
            pass
        return

    state = user_states.get(user_id)
    if not state or state.get("step") != "pending":
        try:
            await update.message.reply_text("❌ الطلب غير موجود أو تم معالجته.", parse_mode='HTML')
        except:
            pass
        return

    currency = state["currency"]
    amount = state["amount"]
    wallet = state["wallet"]
    method = state["method"]
    full_name = state.get("user_name", "مستخدم")

    try:
        await context.bot.send_message(
            chat_id=user_id,
            text=(
                f"🎉 <b>تم التحويل بنجاح!</b>\n\n"
                f"🚀 تم تحويل <b>{amount} {currency.upper()}</b> إلى:\n"
                f"• الطريقة: {method}\n"
                f"• العنوان: <code>{wallet}</code>\n\n"
                f"نشكرك على ثقتك بنا!\n\n"
                f"📞 للدعم: {SUPPORT_USERNAME}"
            ),
            parse_mode='HTML'
        )
        try:
            await update.message.reply_text(f"✅ تم التحويل إلى المستخدم {full_name} (ID: {user_id}).", parse_mode='HTML')
        except:
            pass
        user_states[user_id]["step"] = "completed"
    except Exception as e:
        error_msg = str(e).lower()
        if "blocked" in error_msg or "not found" in error_msg:
            try:
                await update.message.reply_text(f"❌ المستخدم {user_id} قد حظر البوت أو لم يبدأه.", parse_mode='HTML')
            except:
                pass
        else:
            try:
                await update.message.reply_text(f"❌ خطأ: {e}", parse_mode='HTML')
            except:
                pass

# 🛠 معالج الأخطاء
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"حدث خطأ: {context.error}")

# 🏁 تشغيل البوت
if __name__ == '__main__':
    application = Application.builder().token("7615078495:AAE7eWpFiQ4ix5QQmZuekMiLEYqZPBtt0Xg").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(CallbackQueryHandler(paid_handler, pattern=r"^paid_"))
    application.add_handler(CommandHandler("confirm", confirm_transfer))
    application.add_handler(MessageHandler(filters.PHOTO, message_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    application.add_error_handler(error_handler)

    print("✅ البوت يعمل الآن...")
    application.run_polling()
