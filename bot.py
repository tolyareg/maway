from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
import telegram.error, asyncio, re, random

# region: authorize
TOKEN = "7586702932:AAGVWtuX7b7Eo2XnSo9WlxrqYNXy2rkMw2s"
TARGET_CHANNEL_ID = -1002447905522
# endregion

# region: FAQ question and answer
FAQ_RESPONSES = {
    "Корпоративные клиенты": f"Вопрос: 💼 Корпоративные клиенты\n\nКомпания MAWAY Travel оказывает услуги по организации и сопровождению деловых поездок. Мы обеспечиваем надежное качество, заботимся о комфорте клиентов во время путешествий, помогаем оптимизировать затраты на деловые поездки и выездные корпоративные мероприятия.",
    "Когда и как я получу документы на тур": f"Вопрос: 📅 Когда и как я получу документы на тур\n\nПосле того, как ваш тур забронирован – вам на почту придет подтверждение от вашего персонального менеджера . Первый документ, который вы получаете, когда приобретаете тур – это договор, в котором прописаны основные параметры тура (программа путешествия), а также порядок взаимоотношений между туристом и оператором. В случае, когда подбор тура и бронирование происходит он-лайн, договор заключается автоматически по факту внесения оплаты за тур и предоставляется по запросу туриста.\n2. Вы получаете полный пакет документов для поездки: электронный билет, ваучер на проживание и трансфер, приглашение и документы для визы (в случае необходимости), детальную программу с таймингом в течение трех дней после окончательной оплаты путешествия (не позднее, чем за 30 дней до начала отдыха)",
    "Возможно ли изменение цены тура": f"Вопрос: 💰 Возможно ли изменение цены тура\n\nДа, в неоплаченной части тура",
    "Могу ли я отменить тур и как происходит возврат денежных средств": f"Вопрос: 📝 Могу ли я отменить тур\n\nДа, подробные условия по каждому направлению указываются в договоре",
    "Защита персональных данных": f"Вопрос: 🔒 Защита персональных данных\n\nВ целях выполнения договорных обязательств для организации вашего тура нам могут понадобятся ваши паспортные данные, а также информация о ваших диетических предпочтениях и медицинских ограничениях.\nВ этих рамках защита Ваших персональных данных является основополагающей задачей компании",
}
# endregion

# navigation through the context menu
DIRECTION_NAMES = {
    "0": "🏖️ Пляжный отдых",
    "1": "🏔️ Приключения в горах",
    "2": "🚢 Круизы",
    "3": "🏛️ Экскурсионные туры",
    "4": "🇷🇺 Путешествия по России",
    "5": "🎁 Специальные предложения с ранним бронированием",
    "6": "🔥 Специальное предложение с горящими турами",
}

VISA_NAMES = {
    "0": "🇺🇸🇬🇧 США и Великобритания",
    "1": "🇪🇺 Шенген",
    "2": "🇮🇳🇱🇰🇻🇳 Индия, Шри-Ланка, Вьетнам",
    "3": "🇧🇬🇷🇴 Болгария и Румыния",
}
VISA_TEXT = {
    "0": "Вы выбрали: 🇺🇸🇬🇧 США и Великобритания\n\nСрок оформления документов 3-5 дней, срок ожидания собеседования - от 1 месяца, результат сразу в день собеседования, иногда может быть административная проверка до 14 дней\nВыберите пожалуйста удобный вариант для связи с вами",
    "1": "Вы выбрали: 🇪🇺 Шенген\n\nСрок оформления документов 3-5 дней, срок ожидания собеседования - от 1 месяца, результат сразу в день собеседования, иногда может быть административная проверка до 14 дней\nВыберите пожалуйста удобный вариант для связи с вами",
    "2": "Вы выбрали: 🇮🇳🇱🇰🇻🇳 Индия, Шри-Ланка, Вьетнам\n\nСрок оформления документов 3-5 дней, срок ожидания собеседования - от 1 месяца, результат сразу в день собеседования, иногда может быть административная проверка до 14 дней\nВыберите пожалуйста удобный вариант для связи с вами",
    "3": "Вы выбрали: 🇧🇬🇷🇴 Болгария и Румыния\n\nСрок оформления документов 3-5 дней, срок ожидания собеседования - от 1 месяца, результат сразу в день собеседования, иногда может быть административная проверка до 14 дней\nВыберите пожалуйста удобный вариант для связи с вами",
}
# --------------------
# --------------------

# region: showing sections
async def show_direction_options(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton(DIRECTION_NAMES["0"], callback_data="direction_0")],
        [InlineKeyboardButton(DIRECTION_NAMES["1"], callback_data="direction_1")],
        [InlineKeyboardButton(DIRECTION_NAMES["2"], callback_data="direction_2")],
        [InlineKeyboardButton(DIRECTION_NAMES["3"], callback_data="direction_3")],
        [InlineKeyboardButton(DIRECTION_NAMES["4"], callback_data="direction_4")],
        [InlineKeyboardButton(DIRECTION_NAMES["5"], callback_data="direction_5")],
        [InlineKeyboardButton(DIRECTION_NAMES["6"], callback_data="direction_6")],
        [InlineKeyboardButton("🔙 Назад", callback_data="back")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await send_message_or_reply(
        update,
        context,
        "🧭 Куда отправимся на этот раз?\n🗺️ Выберите направление!",
        reply_markup=reply_markup,
    )


async def show_visa_options(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton(VISA_NAMES["0"], callback_data="visa_0")],
        [InlineKeyboardButton(VISA_NAMES["1"], callback_data="visa_1")],
        [InlineKeyboardButton(VISA_NAMES["2"], callback_data="visa_2")],
        [InlineKeyboardButton(VISA_NAMES["3"], callback_data="visa_3")],
        [InlineKeyboardButton("🔙 Назад", callback_data="back")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await send_message_or_reply(
        update,
        context,
        "🛂 Какие страны ждут вас? 🌍\n🔍 Выберите визу!",
        reply_markup=reply_markup,
    )


# endregion

# --------------------
# --------------------

# region: keyboard data (can be adjusted as needed)
def get_form_keyboard(form_type):
    keyboard = []
    if form_type == "direction":
        keyboard = [
            [InlineKeyboardButton(DIRECTION_NAMES["0"], callback_data="direction_0")],
            [InlineKeyboardButton(DIRECTION_NAMES["1"], callback_data="direction_1")],
            [InlineKeyboardButton(DIRECTION_NAMES["2"], callback_data="direction_2")],
            [InlineKeyboardButton(DIRECTION_NAMES["3"], callback_data="direction_3")],
            [InlineKeyboardButton(DIRECTION_NAMES["4"], callback_data="direction_4")],
            [InlineKeyboardButton(DIRECTION_NAMES["5"], callback_data="direction_5")],
            [InlineKeyboardButton(DIRECTION_NAMES["6"], callback_data="direction_6")],
        ]

    if form_type == "visa":
        keyboard = [
            [InlineKeyboardButton(VISA_NAMES["0"], callback_data="visa_0")],
            [InlineKeyboardButton(VISA_NAMES["1"], callback_data="visa_1")],
            [InlineKeyboardButton(VISA_NAMES["2"], callback_data="visa_2")],
            [InlineKeyboardButton(VISA_NAMES["3"], callback_data="visa_3")],
        ]

    keyboard.append(
        [InlineKeyboardButton("Вернуться к главное меню", callback_data="back")]
    )
    return InlineKeyboardMarkup(keyboard)


# endregion

# region: menu cache
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    form_index = int(query.data.split("_")[1])

    history = context.user_data.get("history", [])
    history.append(form_index)
    context.user_data["history"] = history
    context.user_data["current_form"] = form_index
    # Reset form_step when going to a new main menu
    context.user_data["form_step"] = None

    if form_index == 0:
        await show_direction_options(update, context)

    elif form_index == 1:
        await show_visa_options(update, context)

    elif form_index == 2:
        await show_faq_options(update, context)


# endregion

# region: validation functions
def find_phone_number(text):
    phone_regex = (
        r"(?<!\S)(?:\+?\d{1,3})?[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,3}[-.\s]?\d{1,4}(?!\S)"
    )
    potential_numbers = re.findall(phone_regex, text)

    valid_numbers = [
        num for num in potential_numbers if "@" not in num and len(num) >= 7
    ]
    return valid_numbers[0] if valid_numbers else None


def find_email(text):
    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zAZ0-9.-]+\.[a-zA-Z]{2,}"
    match = re.search(email_pattern, text)
    return match.group() if match else None


# endregion

# region: Form steps
async def send_message_or_reply(
    update: Update, context: ContextTypes.DEFAULT_TYPE, text: str, reply_markup=None
):
    if update.message:
        await update.message.reply_text(text, reply_markup=reply_markup)
    elif update.callback_query:
        try:
            if (
                update.callback_query.message.text == text
                and update.callback_query.message.reply_markup == reply_markup
            ):
                await update.callback_query.message.reply_text(
                    text, reply_markup=reply_markup
                )
            else:
                await update.callback_query.edit_message_text(
                    text, reply_markup=reply_markup
                )
        except telegram.error.BadRequest as e:
            if "Message to edit not found" in str(e):
                print("Message to edit not found, sending a new message.")
                await update.callback_query.message.reply_text(
                    text, reply_markup=reply_markup
                )
            elif "Query is too old" in str(e):
                print("Query is too old, ignoring.")
            else:
                print(f"An unexpected BadRequest error occurred: {e}")


async def ask_contact_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_message_or_reply(update, context, "Как к вам можно обращаться?")
    context.user_data.setdefault("history", []).append("contact_name")


async def ask_contact_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_message_or_reply(
        update, context, "Ваш номер телефона, E-mail, Имя пользователя в соц. сетях:"
    )
    context.user_data.setdefault("history", []).append("contact_info")


async def ask_contact_method(update: Update, context: ContextTypes.DEFAULT_TYPE):
    current_direction = context.user_data.get("direction_name")

    keyboard = [
        [InlineKeyboardButton("📱 Telegram", callback_data="contact_method_0")],
        [InlineKeyboardButton("💬 WhatsApp", callback_data="contact_method_1")],
        [InlineKeyboardButton("👤 VK", callback_data="contact_method_2")],
        [InlineKeyboardButton("📧 E-Mail", callback_data="contact_method_3")],
        [InlineKeyboardButton("📞 Любой", callback_data="contact_method_4")],
        [InlineKeyboardButton("🔙 Назад", callback_data="back")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if (current_direction == DIRECTION_NAMES["5"]):
        await send_message_or_reply(
            update,
            context,
            "Вы выбрали: 🎁 Специальные предложения с ранним бронированием\n\n📲 Какой способ для связи вам ближе?",
            reply_markup=reply_markup,
        )
    elif (current_direction == DIRECTION_NAMES["6"]):
        await send_message_or_reply(
            update,
            context,
            "Вы выбрали: 🔥 Специальное предложение с горящими турами\n\n📲 Какой способ для связи вам ближе?",
            reply_markup=reply_markup,
        )

    context.user_data.setdefault("history", []).append("contact_method")


async def ask_visa_duration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    visa_name = context.user_data.get("visa_name")
    visa_index = list(VISA_NAMES.values()).index(visa_name)
    text = VISA_TEXT.get(str(visa_index))

    keyboard = [
        [InlineKeyboardButton("📱 Telegram", callback_data="contact_method_0")],
        [InlineKeyboardButton("💬 WhatsApp", callback_data="contact_method_1")],
        [InlineKeyboardButton("👤 VK", callback_data="contact_method_2")],
        [InlineKeyboardButton("📧 E-Mail", callback_data="contact_method_3")],
        [InlineKeyboardButton("📞 Любой", callback_data="contact_method_4")],
        [InlineKeyboardButton("🔙 Назад", callback_data="back")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await send_message_or_reply(update, context, f"{text}", reply_markup=reply_markup)
    context.user_data.setdefault("history", []).append("visa_duration")


async def ask_direction_duration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    current_direction = context.user_data.get("direction_name")
    keyboard = []

    if current_direction == DIRECTION_NAMES["0"]:
        keyboard = [
            [InlineKeyboardButton("🌙 до 7 ночей", callback_data="duration_0")],
            [InlineKeyboardButton("🌙🌙 до 10 ночей", callback_data="duration_1")],
            [InlineKeyboardButton("🌙🌙🌙 до 14 ночей", callback_data="duration_2")],
            [InlineKeyboardButton("🌙🌙🌙+ от 14 ночей", callback_data="duration_3")],
            [InlineKeyboardButton("🔙 Назад", callback_data="back")],
        ]
    elif current_direction == DIRECTION_NAMES["2"]:
        keyboard = [
            [InlineKeyboardButton("🌙🌙 до 14 ночей", callback_data="duration_2")],
            [InlineKeyboardButton("🌙🌙🌙+ от 14 ночей", callback_data="duration_3")],
            [InlineKeyboardButton("🔙 Назад", callback_data="back")],
        ]
    elif (
        current_direction == DIRECTION_NAMES["3"]
        or current_direction == DIRECTION_NAMES["4"]
    ):
        keyboard = [
            [InlineKeyboardButton("🏙️ до 3 ночей", callback_data="duration_0")],
            [InlineKeyboardButton("🌆 до 7 ночей", callback_data="duration_1")],
            [InlineKeyboardButton("🌇 до 10 ночей", callback_data="duration_2")],
            [InlineKeyboardButton("🌃 от 10 ночей", callback_data="duration_3")],
            [InlineKeyboardButton("🔙 Назад", callback_data="back")],
        ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    if current_direction == DIRECTION_NAMES["0"]:
        await send_message_or_reply(
            update,
            context,
            "Вы выбрали: 🏖️ Пляжный отдых\n\n⏳ Сколько времени выделить на отдых?\n✏️ Выберите желаемую продолжительность:",
            reply_markup=reply_markup,
        )
    elif current_direction == DIRECTION_NAMES["2"]:
        await send_message_or_reply(
            update,
            context,
            "Вы выбрали: 🚢 Круизы\n\n⏳ Сколько времени выделить на отдых?\n✏️ Выберите желаемую продолжительность:",
            reply_markup=reply_markup,
        )
    elif (current_direction == DIRECTION_NAMES["3"]):
        await send_message_or_reply(
            update,
            context,
            "Вы выбрали: 🏛️ Экскурсионные туры\n\n⏳ Сколько времени выделить на отдых?\n✏️ Выберите желаемую продолжительность:",
            reply_markup=reply_markup,
        )
    elif (current_direction == DIRECTION_NAMES["4"]):
        await send_message_or_reply(
            update,
            context,
            "Вы выбрали: 🇷🇺 Путешествия по России\n\n⏳ Сколько времени выделить на отдых?\n✏️ Выберите желаемую продолжительность:",
            reply_markup=reply_markup,
        )

    context.user_data.setdefault("history", []).append("direction_duration")


async def ask_direction_participants(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    keyboard = [
        [InlineKeyboardButton("1-2 человека", callback_data="participants_0")],
        [InlineKeyboardButton("до 4 человек", callback_data="participants_1")],
        [InlineKeyboardButton("от 4 человек", callback_data="participants_2")],
        [InlineKeyboardButton("🔙 Назад", callback_data="back")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await send_message_or_reply(
        update, context, "Состав участников путешествия:", reply_markup=reply_markup
    )
    context.user_data.setdefault("history", []).append("direction_participants")


async def ask_direction_children(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_message_or_reply(
        update, context, "Если вы берете с собой детей, укажите их кол-во и возраст:"
    )
    context.user_data.setdefault("history", []).append("direction_children")


async def ask_direction_budget(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = []
    current_direction = context.user_data.get("direction_name")
    if (
        current_direction == DIRECTION_NAMES["0"]
        or current_direction == DIRECTION_NAMES["4"]
    ):
        keyboard = [
            [InlineKeyboardButton("до 150 000", callback_data="budget_0")],
            [InlineKeyboardButton("до 250 000", callback_data="budget_1")],
            [InlineKeyboardButton("до 500 000", callback_data="budget_2")],
            [InlineKeyboardButton("от 500 000", callback_data="budget_3")],
            [InlineKeyboardButton("🔙 Назад", callback_data="back")],
        ]
    elif current_direction == DIRECTION_NAMES["2"]:
        keyboard = [
            [InlineKeyboardButton("до 250 000", callback_data="budget_1")],
            [InlineKeyboardButton("до 500 000", callback_data="budget_2")],
            [InlineKeyboardButton("от 500 000", callback_data="budget_3")],
            [InlineKeyboardButton("🔙 Назад", callback_data="back")],
        ]
    elif current_direction == DIRECTION_NAMES["3"]:
        keyboard = [
            [InlineKeyboardButton("до 100 000", callback_data="budget_0")],
            [InlineKeyboardButton("до 200 000", callback_data="budget_1")],
            [InlineKeyboardButton("до 400 000", callback_data="budget_2")],
            [InlineKeyboardButton("от 400 000", callback_data="budget_3")],
            [InlineKeyboardButton("🔙 Назад", callback_data="back")],
        ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await send_message_or_reply(
        update, context, "Желаемые границы бюджета:", reply_markup=reply_markup
    )
    context.user_data.setdefault("history", []).append("direction_budget")


async def ask_direction_travel_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = []
    current_direction = context.user_data.get("direction_name")
    if (
        current_direction == DIRECTION_NAMES["0"]
        or current_direction == DIRECTION_NAMES["3"]
        or current_direction == DIRECTION_NAMES["4"]
    ):
        keyboard = [
            [InlineKeyboardButton("до 4 часов", callback_data="travel_time_0")],
            [InlineKeyboardButton("до 9 часов", callback_data="travel_time_1")],
            [
                InlineKeyboardButton(
                    "Ради лучшего отпуска готов на все!", callback_data="travel_time_2"
                )
            ],
            [InlineKeyboardButton("🔙 Назад", callback_data="back")],
        ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await send_message_or_reply(
        update,
        context,
        "Количество времени в пути к отдыху мечты:",
        reply_markup=reply_markup,
    )
    context.user_data.setdefault("history", []).append("direction_travel_time")


async def ask_direction_preferences(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_message_or_reply(
        update,
        context,
        "Особые пожелания (по проживанию, питанию, виду из номера и т.д.):",
    )
    context.user_data.setdefault("history", []).append("direction_preferences")


async def ask_direction_extreme(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🚶 Прогулки", callback_data="extreme_0")],
        [InlineKeyboardButton("🗺️ Экскурсии", callback_data="extreme_1")],
        [InlineKeyboardButton("🪢 Восхождения", callback_data="extreme_2")],
        [InlineKeyboardButton("🔙 Назад", callback_data="back")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await send_message_or_reply(
        update,
        context,
        "Вы выбрали: 🏔️ Приключения в горах\n\n🧗 Какой уровень приключений по душе?",
        reply_markup=reply_markup,
    )
    context.user_data.setdefault("history", []).append("direction_extreme")


async def ask_direction_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🇷🇺 Россия", callback_data="type_0")],
        [InlineKeyboardButton("🌏 Зарубежный тур", callback_data="type_1")],
        [InlineKeyboardButton("🔙 Назад", callback_data="back")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await send_message_or_reply(
        update,
        context,
        "🗺️ Куда бы вы хотели отправиться?\n🧭 Выберите тур:",
        reply_markup=reply_markup,
    )
    context.user_data.setdefault("history", []).append("direction_type")


async def show_faq_options(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("💼 Корпоративные клиенты", callback_data="faq_0")],
        [
            InlineKeyboardButton(
                "📅 Когда и как я получу документы на тур", callback_data="faq_1"
            )
        ],
        [
            InlineKeyboardButton(
                "💰 Возможно ли изменение цены тура", callback_data="faq_2"
            )
        ],
        [InlineKeyboardButton("📝 Могу ли я отменить тур", callback_data="faq_3")],
        [InlineKeyboardButton("🔒 Защита персональных данных", callback_data="faq_4")],
        [InlineKeyboardButton("🔙 Назад", callback_data="back")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await send_message_or_reply(
        update,
        context,
        "ℹ️  Нужна помощь или информация? 🤔\n💡Выберите один из вопросов:",
        reply_markup=reply_markup,
    )


async def process_contact_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["contact_name"] = update.message.text
    await ask_contact_info(update, context)


async def process_contact_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    phone_number = find_phone_number(user_message)
    email = find_email(user_message)

    if phone_number:
        context.user_data["phone_number"] = phone_number

    if email:
        context.user_data["email"] = email

    if not phone_number and not email:
        await update.message.reply_text(
            "Пожалуйста, укажите хотя бы один контакт: номер телефона в формате +7 (XXX) XXX-XX-XX или email в формате example@mail.com."
        )
        return

    context.user_data["contact_info"] = update.message.text
    if context.user_data["current_form"] == 1:
        await send_application(update, context)
    elif context.user_data["current_form"] == 0:
        current_direction = context.user_data.get("direction_name")
        if (
            current_direction == DIRECTION_NAMES["5"]
            or current_direction == DIRECTION_NAMES["6"]
        ):
            await send_application(update, context)
        else:
            await ask_contact_method(update, context)


async def process_contact_method(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact_method = update.callback_query.data.split("_")[2]
    if contact_method == "0":
        context.user_data["contact_method"] = "Telegram"
    elif contact_method == "1":
        context.user_data["contact_method"] = "WhatsApp"
    elif contact_method == "2":
        context.user_data["contact_method"] = "VK"
    elif contact_method == "3":
        context.user_data["contact_method"] = "E-Mail"
    elif contact_method == "4":
        context.user_data["contact_method"] = "Любой"

    if context.user_data["current_form"] == 1:
        await ask_contact_name(update, context)
    elif context.user_data["current_form"] == 0:
        current_direction = context.user_data.get("direction_name")
        if (
            current_direction == DIRECTION_NAMES["5"]
            or current_direction == DIRECTION_NAMES["6"]
        ):
            await ask_contact_name(update, context)
        else:
            await send_application(update, context)


async def process_visa_duration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["visa_duration"] = update.message.text
    await ask_contact_name(update, context)


async def process_direction_duration(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    duration = update.callback_query.data.split("_")[1]

    if duration == "0":
        context.user_data["direction_duration"] = "до 3 ночей"
    elif duration == "1":
        context.user_data["direction_duration"] = "до 7 ночей"
    elif duration == "2":
        context.user_data["direction_duration"] = "до 10 ночей"
    elif duration == "3":
        context.user_data["direction_duration"] = "от 10 ночей"

    await ask_direction_participants(update, context)


async def process_direction_participants(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    participants = update.callback_query.data.split("_")[1]

    if participants == "0":
        context.user_data["direction_participants"] = "1-2 человека"
    elif participants == "1":
        context.user_data["direction_participants"] = "до 4 человек"
    elif participants == "2":
        context.user_data["direction_participants"] = "от 4 человек"

    await ask_direction_children(update, context)


async def process_direction_children(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    context.user_data["direction_children"] = update.message.text
    current_direction = context.user_data.get("direction_name")

    if (
        current_direction == DIRECTION_NAMES["0"]
        or current_direction == DIRECTION_NAMES["2"]
        or current_direction == DIRECTION_NAMES["3"]
        or current_direction == DIRECTION_NAMES["4"]
    ):
        await ask_direction_budget(update, context)
    elif current_direction == DIRECTION_NAMES["1"]:
        await ask_direction_preferences(update, context)


async def process_direction_budget(update: Update, context: ContextTypes.DEFAULT_TYPE):
    budget = update.callback_query.data.split("_")[1]

    if budget == "0":
        context.user_data["direction_budget"] = "до 100 000"
    elif budget == "1":
        context.user_data["direction_budget"] = "до 200 000"
    elif budget == "2":
        context.user_data["direction_budget"] = "до 400 000"
    elif budget == "3":
        context.user_data["direction_budget"] = "от 400 000"

    current_direction = context.user_data.get("direction_name")

    if (
        current_direction == DIRECTION_NAMES["0"]
        or current_direction == DIRECTION_NAMES["4"]
    ):
        await ask_direction_travel_time(update, context)
    elif current_direction == DIRECTION_NAMES["1"]:
        await ask_direction_preferences(update, context)
    elif current_direction == DIRECTION_NAMES["2"]:
        await ask_direction_preferences(update, context)
    elif current_direction == DIRECTION_NAMES["3"]:
        await ask_direction_travel_time(update, context)
    elif (
        current_direction == DIRECTION_NAMES["5"]
        or current_direction == DIRECTION_NAMES["6"]
    ):
        await ask_contact_name(update, context)


async def process_direction_travel_time(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    travel_time = update.callback_query.data.split("_")[2]
    if travel_time == "0":
        context.user_data["direction_travel_time"] = "до 4 часов"
    elif travel_time == "1":
        context.user_data["direction_travel_time"] = "до 9 часов"
    elif travel_time == "2":
        context.user_data[
            "direction_travel_time"
        ] = "Ради лучшего отпуска готов на все!"
    await ask_direction_preferences(update, context)


async def process_direction_preferences(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    context.user_data["direction_preferences"] = update.message.text
    await ask_contact_name(update, context)


async def process_direction_extreme(update: Update, context: ContextTypes.DEFAULT_TYPE):
    extreme = update.callback_query.data.split("_")[1]
    if extreme == "0":
        context.user_data["direction_extreme"] = "прогулки"
    elif extreme == "1":
        context.user_data["direction_extreme"] = "экскурсии"
    elif extreme == "2":
        context.user_data["direction_extreme"] = "восхождения"

    await ask_direction_participants(update, context)


async def process_direction_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    direction_type = update.callback_query.data.split("_")[1]
    if direction_type == "0":
        context.user_data["direction_type"] = "Россия"
    elif direction_type == "1":
        context.user_data["direction_type"] = "Зарубежный тур"
    await ask_direction_travel_time(update, context)


# endregion

# region: sending a message to a group
async def send_application(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = (
        update.message.from_user if update.message else update.callback_query.from_user
    )
    user_profile_link = f"@{user.username}" if user.username else f"ID: {user.id}"

    current_form = context.user_data.get("current_form")

    contact_info = ""

    if context.user_data.get("phone_number"):
        contact_info += f"\n*Phone:* {context.user_data.get('phone_number')}"

    if context.user_data.get("email"):
        contact_info += f"\n*Email:* {context.user_data.get('email')}"

    if current_form == 1:
        visa_name = context.user_data.get("visa_name", "Неизвестная виза")
        message_to_send = (
            f"Новая заявка на визу *{visa_name}* от {user_profile_link}:\n"
            f"{contact_info}\n\n"
        )
        if context.user_data.get("contact_name"):
            message_to_send += f"*Имя:* {context.user_data.get('contact_name')}\n"
        # if context.user_data.get("contact_info"):
        # message_to_send +=  f"*Контакт:* {context.user_data.get('contact_info')}\n"
        if context.user_data.get("contact_method"):
            message_to_send += f"*Связь:* {context.user_data.get('contact_method')}\n"
        if context.user_data.get("visa_duration"):
            message_to_send += f"*Срок визы:* {context.user_data.get('visa_duration')}"

    elif current_form == 0:
        direction_name = context.user_data.get(
            "direction_name", "Неизвестное направление"
        )
        message_to_send = (
            f"Новая заявка на направление *{direction_name}* от {user_profile_link}:\n"
            f"{contact_info}\n\n"
        )
        if context.user_data.get("contact_name"):
            message_to_send += f"*Имя:* {context.user_data.get('contact_name')}\n"
        if context.user_data.get("contact_method"):
            message_to_send += f"*Связь:* {context.user_data.get('contact_method')}\n"
        if context.user_data.get("direction_duration"):
            message_to_send += (
                f"*Продолжительность:* {context.user_data.get('direction_duration')}\n"
            )
        if context.user_data.get("direction_participants"):
            message_to_send += (
                f"*Участники:* {context.user_data.get('direction_participants')}\n"
            )
        if context.user_data.get("direction_children"):
            message_to_send += (
                f"*Дети:* {context.user_data.get('direction_children')}\n"
            )
        if context.user_data.get("direction_budget"):
            message_to_send += (
                f"*Бюджет:* {context.user_data.get('direction_budget')}\n"
            )
        if context.user_data.get("direction_travel_time"):
            message_to_send += (
                f"*Время в пути:* {context.user_data.get('direction_travel_time')}\n"
            )
        if context.user_data.get("direction_extreme"):
            message_to_send += (
                f"*Уровень экстрима:* {context.user_data.get('direction_extreme')}\n"
            )
        if context.user_data.get("direction_type"):
            message_to_send += (
                f"*Тип тура:* {context.user_data.get('direction_type')}\n"
            )
        if context.user_data.get("direction_preferences"):
            message_to_send += (
                f"*Предпочтения:* {context.user_data.get('direction_preferences')}\n"
            )

    try:
        await context.bot.send_message(
            chat_id=TARGET_CHANNEL_ID, text=message_to_send, parse_mode="Markdown"
        )
        if update.callback_query:
            thank_you_messages = [
                "🎉 Спасибо за обращение! Мы скоро свяжемся с вами! ✨",
                "🚀 Заявка принята! Менеджер уже обрабатывает ваше путешествие 🗺️",
                "✅ Ваша заявка у нас! Ожидайте звонка от нашего менеджера 📞",
                "Ваше обращение принято! Скоро с вами свяжется персональный менеджер! 😉",
                "Мы ценим ваш интерес к приключениям! Ожидайте новостей от нашей команды! 🧭",
            ]
            random_message = random.choice(thank_you_messages)
            await update.callback_query.edit_message_text(
                random_message, reply_markup=None
            )
        elif update.message:
            thank_you_messages = [
                "🎉 Спасибо за обращение! Мы скоро свяжемся с вами! ✨",
                "🚀 Заявка принята! Менеджер уже обрабатывает ваше путешествие 🗺️",
                "✅ Ваша заявка у нас! Ожидайте звонка от нашего менеджера 📞",
                "Ваше обращение принято! Скоро с вами свяжется персональный менеджер! 😉",
                "Мы ценим ваш интерес к приключениям! Ожидайте новостей от нашей команды! 🧭",
            ]
            random_message = random.choice(thank_you_messages)
            await update.message.reply_text(random_message)

        await asyncio.sleep(6)  # Задержка в 1 секунду
        await display_main_menu(update, context)

    except Exception as error:
        await send_message_or_reply(
            update,
            context,
            "Ошибка при отправке данных. Пожалуйста, попробуйте еще раз.",
        )
        print(f"Error sending message: {error}")
        return

    context.user_data.clear()


async def display_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton(
                "✨ Оставить заявку на Волшебное путешествие", callback_data="form_0"
            )
        ],
        [InlineKeyboardButton("✈️ Визы - Открой мир!", callback_data="form_1")],
        [InlineKeyboardButton("❓ FAQ - Ответы на вопросы", callback_data="form_2")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    text = (
        "🌍 MAWAY Travel — Прикоснись к мечте.\n"
        "        Открой мир незабываемых приключений! ✈️"
    )

    if update.message:
        await update.message.reply_text(text, reply_markup=reply_markup)
    elif update.callback_query:
        try:
            await update.callback_query.edit_message_text(
                text, reply_markup=reply_markup
            )
        except telegram.error.BadRequest as e:
            if "Message to edit not found" in str(e):
                print("Message to edit not found, sending a new message.")
                await update.callback_query.message.reply_text(
                    text, reply_markup=reply_markup
                )
            elif "Query is too old" in str(e):
                print("Query is too old, ignoring.")
            else:
                print(f"An unexpected BadRequest error occurred: {e}")


# endregion

# region: Message handler
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    current_form = context.user_data.get("current_form")
    form_step = context.user_data.get("form_step")
    if context.user_data.get("history"):
        form_step = context.user_data.get("history")[-1]
    else:
        form_step = None
    if current_form == 2:
        await send_message_or_reply(
            update, context, "Вы не можете заполнять форму в разделе FAQ."
        )
        await display_main_menu(update, context)
        return

    if current_form is None:
        await send_message_or_reply(
            update, context, "Выберите форму из доступных вариантов."
        )
        await display_main_menu(update, context)
        return

    if form_step == "contact_name":
        await process_contact_name(update, context)
    elif form_step == "contact_info":
        await process_contact_info(update, context)
    elif form_step == "contact_method":
        await process_contact_method(update, context)
    elif form_step == "visa_duration":
        await process_visa_duration(update, context)
    elif form_step == "direction_children":
        await process_direction_children(update, context)
    elif form_step == "direction_budget":
        await process_direction_budget(update, context)
    elif form_step == "direction_travel_time":
        await process_direction_travel_time(update, context)
    elif form_step == "direction_preferences":
        await process_direction_preferences(update, context)
    elif form_step == "direction_extreme":
        await process_direction_extreme(update, context)
    elif form_step == "direction_type":
        await process_direction_type(update, context)
    else:
        await send_message_or_reply(
            update, context, "Пожалуйста, следуйте инструкциям бота."
        )


# endregion

# --------------------
# --------------------

# region: updating subcategories
async def direction_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    direction = query.data.split("_")[1]
    direction_name = DIRECTION_NAMES.get(direction, "Неизвестное направление")

    context.user_data["direction_name"] = direction_name
    context.user_data["current_form"] = 0
    context.user_data["form_step"] = None

    if direction_name == DIRECTION_NAMES["1"]:
        await ask_direction_extreme(update, context)
    elif (
        direction_name == DIRECTION_NAMES["5"] or direction_name == DIRECTION_NAMES["6"]
    ):
        await ask_contact_method(update, context)
    else:
        await ask_direction_duration(update, context)


async def visa_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    visa = query.data.split("_")[1]
    visa_name = VISA_NAMES.get(visa, "Неизвестная виза")

    context.user_data["visa_name"] = visa_name
    context.user_data["current_form"] = 1
    await ask_visa_duration(update, context)


# endregion

# --------------------
# --------------------

# region: answers to the faq
async def show_faq_options(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("💼 Корпоративные клиенты", callback_data="faq_0")],
        [
            InlineKeyboardButton(
                "📅 Когда и как я получу документы на тур", callback_data="faq_1"
            )
        ],
        [
            InlineKeyboardButton(
                "💰 Возможно ли изменение цены тура", callback_data="faq_2"
            )
        ],
        [InlineKeyboardButton("📝 Могу ли я отменить тур", callback_data="faq_3")],
        [InlineKeyboardButton("🔒 Защита персональных данных", callback_data="faq_4")],
        [InlineKeyboardButton("🔙 Назад", callback_data="back")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await send_message_or_reply(
        update,
        context,
        "ℹ️  Нужна помощь или информация? 🤔\n💡Выберите один из вопросов:",
        reply_markup=reply_markup,
    )


# endregion

# --------------------
# --------------------


async def back_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    history = context.user_data.get("history", [])
    if len(history) <= 1:
        await display_main_menu(update, context)
        return

    history.pop()
    previous_step_info = history[-1]
    context.user_data["history"] = history

    if isinstance(previous_step_info, int) and previous_step_info in [0, 1, 2]:
        await display_main_menu(update, context)
        return

    form_step = previous_step_info
    if form_step == "contact_name":
        await ask_contact_name(update, context)
    elif form_step == "contact_info":
        await ask_contact_info(update, context)
    elif form_step == "contact_method":
        if context.user_data.get("current_form") == 1:
            await show_visa_options(update, context)
        else:
            await ask_contact_method(update, context)
    elif form_step == "visa_duration":
        await ask_visa_duration(update, context)
    elif form_step == "direction_children":
        await ask_direction_children(update, context)
    elif form_step == "direction_budget":
        await ask_direction_budget(update, context)
    elif form_step == "direction_travel_time":
        await ask_direction_travel_time(update, context)
    elif form_step == "direction_preferences":
        await ask_direction_preferences(update, context)
    elif form_step == "direction_extreme":
        await ask_direction_extreme(update, context)
    elif form_step == "direction_type":
        await ask_direction_type(update, context)


# endregion


async def faq_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    try:
        await query.answer()
    except telegram.error.BadRequest as e:
        if "Query is too old" in str(e):
            print("Query is too old, ignoring.")
            return
        else:
            print(f"An unexpected BadRequest error occurred: {e}")

    faq_index = int(query.data.split("_")[1])
    faq_question = list(FAQ_RESPONSES.keys())[faq_index]
    faq_response = FAQ_RESPONSES[faq_question]

    keyboard = [
        [InlineKeyboardButton("Вернуться к вопросам FAQ", callback_data="form_2")],
        [InlineKeyboardButton("Вернуться в главное меню", callback_data="back")],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await send_message_or_reply(
        update, context, f"{faq_response}", reply_markup=reply_markup
    )


# --------------------
# --------------------

# region: callbacks
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await display_main_menu(update, context)


if __name__ == "__main__":
    application = Application.builder().token(TOKEN).build()

    # ---------------------

    application.add_handler(MessageHandler(filters.COMMAND, start))
    application.add_handler(CallbackQueryHandler(button_handler, pattern="^form_\\d$"))
    application.add_handler(
        CallbackQueryHandler(direction_handler, pattern="^direction_\\d$")
    )
    application.add_handler(CallbackQueryHandler(visa_handler, pattern="^visa_\\d$"))
    application.add_handler(CallbackQueryHandler(faq_handler, pattern="^faq_\\d$"))

    application.add_handler(CallbackQueryHandler(back_handler, pattern="^back$"))

    # ---------------------

    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler)
    )
    application.add_handler(
        CallbackQueryHandler(process_direction_duration, pattern="^duration_\\d$")
    )
    application.add_handler(
        CallbackQueryHandler(
            process_direction_participants, pattern="^participants_\\d$"
        )
    )
    application.add_handler(
        CallbackQueryHandler(process_direction_budget, pattern="^budget_\\d$")
    )
    application.add_handler(
        CallbackQueryHandler(process_direction_travel_time, pattern="^travel_time_\\d$")
    )
    application.add_handler(
        CallbackQueryHandler(process_direction_extreme, pattern="^extreme_\\d$")
    )
    application.add_handler(
        CallbackQueryHandler(process_contact_method, pattern="^contact_method_\\d$")
    )
    application.add_handler(
        CallbackQueryHandler(process_direction_type, pattern="^type_\\d$")
    )
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler)
    )

    # ---------------------

    application.run_polling()
# endregion
