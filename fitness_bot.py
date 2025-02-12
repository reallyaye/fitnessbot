import os
import json
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from telegram import Update, ReplyKeyboardMarkup, InputFile
from telegram.constants import ParseMode
from telegram.ext import (ApplicationBuilder, CommandHandler, ContextTypes,
                          MessageHandler, filters, ConversationHandler)

# Замените на ваш токен Telegram-бота
TOKEN = '7858845011:AAH_BUqpdwRoMgyQTeDoiqfsVK2KzyJNLwQ'

# Файлы для хранения данных
PROGRESS_FILE = "progress_data.json"
WORKOUT_FILE = "workout_data.json"

# Глобальные словари для хранения данных
progress_data = {}
workout_data = {}

# Определение состояний для ConversationHandler
AWAITING_PROGRESS, AWAITING_CALORIE_INPUT, AWAITING_TRAINING_LEVEL, AWAITING_TRAINING_GOAL, AWAITING_TRAINING_DAYS = range(5)

############################################
# Функции загрузки и сохранения данных
############################################
def load_progress_data():
    global progress_data
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
            progress_data = json.load(f)
    else:
        progress_data = {}

def save_progress_data():
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(progress_data, f, ensure_ascii=False, indent=4)

def load_workout_data():
    global workout_data
    if os.path.exists(WORKOUT_FILE):
        with open(WORKOUT_FILE, "r", encoding="utf-8") as f:
            workout_data = json.load(f)
    else:
        workout_data = {}

def save_workout_data():
    with open(WORKOUT_FILE, "w", encoding="utf-8") as f:
        json.dump(workout_data, f, ensure_ascii=False, indent=4)

load_progress_data()
load_workout_data()

############################################
# Функция генерации персонализированного плана тренировок
############################################
def generate_training_plan(level, goal, days):
    plan = f"**Персонализированный план тренировок**\n\n"
    plan += f"Уровень подготовки: {level}\n"
    plan += f"Цель: {goal}\n"
    plan += f"Тренировок в неделю: {days}\n\n"
    plan += "Программа разработана с учетом ваших целей и уровня подготовки.\n\n"
    
    if goal.lower() in ['набор массы', 'набор']:
        if days == '2':
            plan += "**2 тренировки в неделю (Полное тело):**\n"
            plan += "- Приседания: 3 подхода x 10-12 повторений\n"
            plan += "- Жим лежа: 3 подхода x 10-12 повторений\n"
            plan += "- Становая тяга: 3 подхода x 8-10 повторений\n"
            plan += "- Подтягивания: 3 подхода x максимум повторений\n"
        elif days == '3':
            plan += "**3 тренировки в неделю (Push / Pull / Legs):**\n"
            plan += "**Push (Грудь, Плечи, Трицепс):**\n"
            plan += "• Жим лежа: 4 подхода x 8-10 повторений\n"
            plan += "• Жим гантелей на наклонной скамье: 3 подхода x 10-12 повторений\n"
            plan += "• Разведения гантелей: 3 подхода x 12-15 повторений\n\n"
            plan += "**Pull (Спина, Бицепс):**\n"
            plan += "• Тяга штанги в наклоне: 4 подхода x 8-10 повторений\n"
            plan += "• Тяга вертикального блока: 3 подхода x 10-12 повторений\n"
            plan += "• Подтягивания: 3 подхода x максимум повторений\n\n"
            plan += "**Legs (Ноги):**\n"
            plan += "• Приседания: 4 подхода x 8-10 повторений\n"
            plan += "• Выпады: 3 подхода x 10-12 повторений\n"
            plan += "• Сгибания ног в тренажере: 3 подхода x 12-15 повторений\n"
        else:
            plan += "План не найден для указанного количества тренировок."
    elif goal.lower() in ['сушка', 'сушка жиросжигание']:
        plan += "**Программа для сушки:**\n"
        plan += "- Выполняйте кардио упражнения и силовые тренировки с большим числом повторений.\n"
        plan += "- Придерживайтесь дефицита калорий.\n"
    elif goal.lower() in ['силовые тренировки', 'сила']:
        plan += "**План для силовых тренировок:**\n"
        plan += "- Выполняйте базовые упражнения с тяжелыми весами (приседания, жим, тяга).\n"
    elif goal.lower() in ['выносливость', 'кардио']:
        plan += "**План для выносливости (кардио):**\n"
        plan += "- Выполняйте длительные кардио-сессии, интервальный бег или велотренажер.\n"
    else:
        plan += "Цель не распознана. Выберите: Набор массы, Сушка, Силовые тренировки, Выносливость."
    
    # Текст кнопки должен совпадать точно
    plan += "\n\nПосле завершения тренировки нажмите кнопку **✅ Завершить тренировку**, чтобы зафиксировать выполнение."
    return plan

############################################
# Функция фиксации завершения тренировки
############################################
async def complete_workout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    session_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if user_id not in workout_data:
        workout_data[user_id] = []
    workout_data[user_id].append({
        'date': session_date,
        'status': 'completed'
    })
    save_workout_data()
    await update.message.reply_text("Отлично! Тренировка завершена и зафиксирована.")
    await back_to_main_menu(update, context)
    return ConversationHandler.END

############################################
# Функция возврата в главное меню
############################################
async def back_to_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ['📋 План тренировок', '🍎 Питание'],
        ['📊 Прогресс', '❓ FAQ']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Ты вернулся в главное меню. Выбери, что тебе нужно:", reply_markup=reply_markup)

############################################
# Обработчики для команд /start и /help
############################################
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ['📋 План тренировок', '🍎 Питание'],
        ['📊 Прогресс', '❓ FAQ']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Привет! Я фитнес-бот. Выбери, что тебе нужно:", reply_markup=reply_markup)
    return ConversationHandler.END

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "📚 Команды бота:\n"
        "/start - Начало работы с ботом\n"
        "/help - Список команд и помощь\n"
        "📋 План тренировок\n"
        "🍎 Питание\n"
        "📊 Прогресс\n"
        "❓ FAQ\n"
    )
    await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)

############################################
# Обработчики для работы с прогрессом
############################################
async def add_progress(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Введите вашу запись прогресса (например, вес или повторения) или отправьте фото.\nНажмите '🔙 Назад' для отмены."
    )
    return AWAITING_PROGRESS

async def handle_progress(update: Update, context: ContextTypes.DEFAULT_TYPE):
    record_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    user_key = str(update.message.from_user.id)
    if user_key not in progress_data:
        progress_data[user_key] = []
    if update.message.photo:
        photo = update.message.photo[-1]
        caption = update.message.caption or ''
        progress_data[user_key].append({
            'type': 'photo',
            'file_id': photo.file_id,
            'caption': caption,
            'date': record_date
        })
        save_progress_data()
        await update.message.reply_text("Фото прогресса сохранено!")
    elif update.message.text:
        if update.message.text == '🔙 Назад':
            await back_to_main_menu(update, context)
            return ConversationHandler.END
        else:
            progress_data[user_key].append({
                'type': 'text',
                'text': update.message.text,
                'date': record_date
            })
            save_progress_data()
            await update.message.reply_text("Запись прогресса сохранена!")
    return ConversationHandler.END

async def view_progress(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_key = str(update.message.from_user.id)
    records = progress_data.get(user_key, [])
    if not records:
        await update.message.reply_text("Записей прогресса не найдено.")
    else:
        for record in records:
            if record['type'] == 'text':
                msg = f"{record['date']} - {record['text']}"
                await update.message.reply_text(msg)
            elif record['type'] == 'photo':
                caption = record.get('caption', '')
                full_caption = f"Дата: {record['date']}\n{caption}" if caption else f"Дата: {record['date']}"
                await update.message.reply_photo(photo=record['file_id'], caption=full_caption)

async def plot_progress(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_key = str(update.message.from_user.id)
    records = progress_data.get(user_key, [])
    numeric_records = [record for record in records 
                       if record['type'] == 'text' and record['text'].strip().split()[0].replace('.', '', 1).isdigit()]
    if not numeric_records:
        await update.message.reply_text("Недостаточно данных для построения графика.")
        return
    dates = [datetime.strptime(record['date'], "%Y-%m-%d %H:%M:%S") for record in numeric_records]
    values = [float(record['text'].strip().split()[0]) for record in numeric_records]
    plt.figure(figsize=(10, 5))
    plt.plot(dates, values, marker='o')
    plt.title("Прогресс")
    plt.xlabel("Дата")
    plt.ylabel("Значение")
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()
    plot_filename = "progress_plot.png"
    plt.savefig(plot_filename)
    plt.close()
    with open(plot_filename, "rb") as photo_file:
        await update.message.reply_photo(photo=InputFile(photo_file))
    os.remove(plot_filename)

async def delete_progress(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_key = str(update.message.from_user.id)
    if user_key in progress_data and progress_data[user_key]:
        progress_data[user_key] = []
        save_progress_data()
        await update.message.reply_text("Все записи прогресса удалены.")
    else:
        await update.message.reply_text("Записей для удаления не найдено.")

############################################
# Функции для калькулятора калорий
############################################
async def start_calorie_calculator(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Введите ваши данные в формате:\n"
        "пол, возраст, вес (кг), рост (см), уровень активности\n\n"
        "Пример: M, 25, 70, 175, 1.55\nНажмите '🔙 Назад' для отмены."
    )
    return AWAITING_CALORIE_INPUT

async def handle_calorie_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == '🔙 Назад':
        await back_to_main_menu(update, context)
        return ConversationHandler.END
    try:
        parts = text.split(',')
        if len(parts) != 5:
            raise ValueError
        gender, age, weight, height, activity = [p.strip() for p in parts]
        age = int(age)
        weight = float(weight)
        height = float(height)
        activity = float(activity)
        if gender.lower() in ['m', 'male', 'м', 'муж']:
            bmr = 10 * weight + 6.25 * height - 5 * age + 5
        elif gender.lower() in ['f', 'female', 'ж', 'жен']:
            bmr = 10 * weight + 6.25 * height - 5 * age - 161
        else:
            await update.message.reply_text("Неверное значение пола. Введите 'M' или 'F'.")
            return AWAITING_CALORIE_INPUT
        daily_calories = bmr * activity
        await update.message.reply_text(
            f"Ваш базальный метаболизм (BMR): {bmr:.2f} ккал\nДневная норма калорий: {daily_calories:.2f} ккал"
        )
        return ConversationHandler.END
    except Exception as e:
        await update.message.reply_text(
            "Неверный формат данных. Введите данные в формате:\n"
            "пол, возраст, вес (кг), рост (см), уровень активности\nПример: M, 25, 70, 175, 1.55"
        )
        return AWAITING_CALORIE_INPUT

############################################
# Функции для персонализированного плана тренировок
############################################
async def start_personalized_plan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [['Начинающий', 'Средний', 'Продвинутый'], ['🔙 Назад']]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Выберите ваш уровень подготовки:", reply_markup=reply_markup)
    return AWAITING_TRAINING_LEVEL

async def handle_training_level(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == '🔙 Назад':
        await back_to_main_menu(update, context)
        return ConversationHandler.END
    context.user_data['training_level'] = update.message.text
    keyboard = [['Набор массы', 'Сушка'], ['Силовые тренировки', 'Выносливость'], ['🔙 Назад']]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Выберите вашу цель:", reply_markup=reply_markup)
    return AWAITING_TRAINING_GOAL

async def handle_training_goal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == '🔙 Назад':
        await back_to_main_menu(update, context)
        return ConversationHandler.END
    context.user_data['training_goal'] = update.message.text
    keyboard = [['2', '3', '4', '5', '6'], ['🔙 Назад']]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Сколько тренировок в неделю вы планируете?", reply_markup=reply_markup)
    return AWAITING_TRAINING_DAYS

async def handle_training_days(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == '🔙 Назад':
        await back_to_main_menu(update, context)
        return ConversationHandler.END
    context.user_data['training_days'] = update.message.text
    level = context.user_data.get('training_level', '')
    goal = context.user_data.get('training_goal', '')
    days = update.message.text
    plan_text = generate_training_plan(level, goal, days)
    # Очищаем временные данные
    context.user_data.pop('training_level', None)
    context.user_data.pop('training_goal', None)
    context.user_data.pop('training_days', None)
    # Создаем клавиатуру с кнопкой завершения тренировки
    finish_keyboard = ReplyKeyboardMarkup([['✅ Завершить тренировку']], resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text(plan_text, parse_mode=ParseMode.MARKDOWN, reply_markup=finish_keyboard)
    return ConversationHandler.END

############################################
# Общий обработчик для всех сообщений
############################################
async def handle_all_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
    text = update.message.text
    # Если нажата кнопка завершения тренировки, фиксируем её и возвращаем в главное меню
    if text == '✅ Завершить тренировку':
        await complete_workout(update, context)
        return
    # Обработка команд из основного меню
    if text == '📋 План тренировок':
        goals = [['🏋️ Набор массы'], ['🔥 Сушка'], ['💪 Силовые тренировки'], ['Персонализированный план'], ['🔙 Назад']]
        reply_markup = ReplyKeyboardMarkup(goals, resize_keyboard=True)
        await update.message.reply_text("Выберите программу тренировок:", reply_markup=reply_markup)
    elif text == '🏋️ Набор массы':
        mass_plan = (
            "План тренировок для набора массы\n\n"
            "День 1 (Грудь и трицепс):\n"
            "- Жим лёжа: 4 подхода x 8-10 повторений\n"
            "- Разведения гантелей: 3 подхода x 10-12 повторений\n\n"
            "День 2 (Спина и бицепс):\n"
            "- Тяга штанги: 4 подхода x 8-10 повторений\n"
            "- Подтягивания: 3 подхода x максимум повторений\n\n"
            "День 3 (Ноги и плечи):\n"
            "- Приседания: 5 подходов x 8-10 повторений\n"
            "- Жим ногами: 4 подхода x 10-12 повторений\n\n"
            "После завершения тренировки нажмите '✅ Завершить тренировку'."
        )
        await update.message.reply_text(mass_plan)
    elif text == '🔥 Сушка':
        cut_plan = (
            "План тренировок для сушки\n\n"
            "День 1 (Круговая тренировка):\n"
            "- Бёрпи: 4x15\n"
            "- Прыжки на месте: 4x30 секунд\n\n"
            "День 2 (Силовая тренировка):\n"
            "- Приседания: 4x10-12\n"
            "- Отжимания: 4x15\n\n"
            "После завершения тренировки нажмите '✅ Завершить тренировку'."
        )
        await update.message.reply_text(cut_plan)
    elif text == '💪 Силовые тренировки':
        strength_plan = (
            "План для силовых тренировок\n\n"
            "День 1:\n"
            "- Приседания: 4x5-6\n"
            "- Жим лёжа: 4x5-6\n"
            "- Становая тяга: 4x5\n\n"
            "День 2:\n"
            "- Жим стоя: 4x5-6\n"
            "- Подтягивания: 3x максимум повторений\n\n"
            "После завершения тренировки нажмите '✅ Завершить тренировку'."
        )
        await update.message.reply_text(strength_plan)
    elif text == 'Персонализированный план':
        await start_personalized_plan(update, context)
    elif text == '🍎 Питание':
        nutrition_keyboard = [['Калькулятор калорий', 'Показать рекомендации'], ['🔙 Назад']]
        reply_markup = ReplyKeyboardMarkup(nutrition_keyboard, resize_keyboard=True)
        await update.message.reply_text("Выберите действие по питанию:", reply_markup=reply_markup)
    elif text == 'Показать рекомендации':
        nutrition_guide = (
            "Руководство по питанию:\n"
            "• Для набора массы – профицит калорий, достаточное количество белка и углеводов.\n"
            "• Для сушки – дефицит калорий, повышенное потребление белка, умеренные углеводы.\n"
            "• Силовые тренировки – баланс макроэлементов и восстановление.\n"
            "• Пейте достаточно воды и не забывайте про витамины!"
        )
        await update.message.reply_text(nutrition_guide)
    elif text == 'Калькулятор калорий':
        await start_calorie_calculator(update, context)
    elif text == '📊 Прогресс':
        progress_options = [
            ['➕ Добавить запись', '📈 Просмотреть прогресс'],
            ['📊 Построить график', '🗑️ Удалить прогресс'],
            ['🔙 Назад']
        ]
        reply_markup = ReplyKeyboardMarkup(progress_options, resize_keyboard=True)
        await update.message.reply_text("Выберите действие для отслеживания прогресса:", reply_markup=reply_markup)
    elif text == '📈 Просмотреть прогресс':
        await view_progress(update, context)
    elif text == '📊 Построить график':
        await plot_progress(update, context)
    elif text == '🗑️ Удалить прогресс':
        await delete_progress(update, context)
    elif text == '🔙 Назад':
        await back_to_main_menu(update, context)
    else:
        await update.message.reply_text("Я тебя не понял. Попробуй снова.")

############################################
# Регистрация обработчиков
############################################
progress_conv_handler = ConversationHandler(
    entry_points=[MessageHandler(filters.Regex('➕ Добавить запись'), add_progress)],
    states={
        AWAITING_PROGRESS: [MessageHandler(filters.TEXT | filters.PHOTO, handle_progress)]
    },
    fallbacks=[MessageHandler(filters.Regex('🔙 Назад'), back_to_main_menu)]
)

calorie_conv_handler = ConversationHandler(
    entry_points=[MessageHandler(filters.Regex('Калькулятор калорий'), start_calorie_calculator)],
    states={
        AWAITING_CALORIE_INPUT: [MessageHandler(filters.TEXT, handle_calorie_input)]
    },
    fallbacks=[MessageHandler(filters.Regex('🔙 Назад'), back_to_main_menu)]
)

training_plan_conv_handler = ConversationHandler(
    entry_points=[MessageHandler(filters.Regex('Персонализированный план'), start_personalized_plan)],
    states={
        AWAITING_TRAINING_LEVEL: [MessageHandler(filters.TEXT, handle_training_level)],
        AWAITING_TRAINING_GOAL: [MessageHandler(filters.TEXT, handle_training_goal)],
        AWAITING_TRAINING_DAYS: [MessageHandler(filters.TEXT, handle_training_days)]
    },
    fallbacks=[MessageHandler(filters.Regex('🔙 Назад'), back_to_main_menu)]
)

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler('start', start_command))
app.add_handler(CommandHandler('help', help_command))
app.add_handler(progress_conv_handler)
app.add_handler(calorie_conv_handler)
app.add_handler(training_plan_conv_handler)
app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, handle_all_messages))

# (Опционально) Если у вас есть функция send_weekly_report, можно запланировать еженедельную рассылку:
# app.job_queue.run_repeating(send_weekly_report, interval=604800, first=604800)

print("Бот запущен!")
app.run_polling()
