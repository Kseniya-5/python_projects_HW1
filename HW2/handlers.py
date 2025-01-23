from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, InputFile, FSInputFile
from aiogram.filters import Command
import matplotlib.pyplot as plt
from states import User
from config import API_W
from aiohttp import ClientSession
import re

router = Router()
users = {}
API_KEY = API_W


# Обработчик команды /start
@router.message(Command('start'))
async def cmd_start(message: Message):
    welcome_message = await message.reply(
        f'<b>️🏋️‍♀️Добро пожаловать! Я Ваш персональный фитнес-помощник.</b>🧘‍♀️\n'
        '\nВведите /help для того, чтобы узнать дополнительную информацию о моих функциях.\n\n'
        'Чтобы начать работать со мной создайте, пожалуйста, свой профиль.',
        parse_mode='HTML'
    )
    # Автоматически вызываем команду show_keyboard
    await show_keyboard(welcome_message)


# Обработчик команды /help
@router.message(Command('help'))
async def cmd_help(message: Message):
    help_message = await message.reply(
        '<u>Мои основные функции:</u>\n\n'
        '1. <b>Создать профиль</b> - Создание профиля пользователя.\n'
        '2. <b>Профиль</b> - Просмотр данных своего профиля.\n'
        '3. <b>Вода</b> - Сохраняет выпитое количество воды и показывает, сколько осталось до нормы.\n'
        '4. <b>Еда</b> - Сохраняет калорийность продукта.\n'
        '5. <b>Тренировка</b> - Фиксирует сожженные калории, учитывает расходы воды на тренировке.\n'
        '6. <b>Прогресс</b> - Показывает прогресс по воде и калориям.',
        parse_mode='HTML'
    )
    # Автоматически вызываем команду show_keyboard
    await show_keyboard(help_message)


# Обработчик команды /keyboard с инлайн-кнопками
async def show_keyboard(message: Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='Создать профиль 🍏', callback_data='profile'),
                InlineKeyboardButton(text='Профиль 🍎', callback_data='get_profile'),
            ],
            [
                InlineKeyboardButton(text='Вода 💧', callback_data='water'),
                InlineKeyboardButton(text='Еда 🍕', callback_data='food'),
            ],
            [
                InlineKeyboardButton(text='Тренировка 🤸‍♀️', callback_data='training'),
                InlineKeyboardButton(text='Прогресс 🏆', callback_data='progress')
            ]
        ]
    )
    await message.bot.edit_message_reply_markup(
        chat_id=message.chat.id,
        message_id=message.message_id,
        reply_markup=keyboard
    )


# Обработчик нажатий на инлайн-кнопки
@router.callback_query()
async def handle_callback(callback_query: CallbackQuery, state: FSMContext):
    if callback_query.data == 'profile':
        await start_profile(callback_query.message, state)
    elif callback_query.data == 'get_profile':
        await get_profile(callback_query.message, state)
    elif callback_query.data == 'water':
        await start_water(callback_query.message, state)
    elif callback_query.data == 'food':
        await callback_query.message.reply('Вы выбрали кнопку "Еда".')
    elif callback_query.data == 'training':
        await callback_query.message.reply('Вы выбрали кнопку "Тренировка".')
    elif callback_query.data == 'progress':
        await callback_query.message.reply('Вы выбрали кнопку "Прогресс".')
    else:
        await callback_query.message.answer("Неизвестная опция.")


###################################Profile##############################################
@router.message(Command('profile'))
async def start_profile(message: Message, state: FSMContext):
    await message.answer('<b><u>Вы выбрали кнопку "Создать профиль"</u></b>\n\n'
                         'Как Вас зовут?',
                         parse_mode='HTML')
    await state.set_state(User.name)


@router.message(User.name)
async def process_manual_name(message: Message, state: FSMContext):
    name = message.text.strip()
    if not name:
        await message.answer("Имя не может быть пустым. Пожалуйста, введите ваше имя:")
        return
    elif not re.match('^[A-Za-zА-Яа-яЁёs]+$', name):
        await message.answer('Имя должно содержать только буквы. Пожалуйста, введите ваше имя снова.')
        return
    await state.update_data(name=name)
    await message.answer('Сколько Вам лет?')
    await state.set_state(User.age)


@router.message(User.age)
async def process_age(message: Message, state: FSMContext):
    age = message.text.strip()
    # Проверка корректности возраста
    if not age.isdigit() or not (12 <= int(age) < 120):
        await message.answer('Пожалуйста, введите корректный возраст (число от 12 до 119):')
        return
    await state.update_data(age=int(age))
    await message.answer('Пожалуйста, укажите свой вес (в кг):')
    await state.set_state(User.weight)


@router.message(User.weight)
async def process_weight(message: Message, state: FSMContext):
    weight = message.text.strip()
    # Проверка корректности веса
    if not weight.isdigit() or not (30 <= float(weight) <= 500):
        await message.answer('Пожалуйста, введите корректный вес (число от 30 до 500):')
        return
    await state.update_data(weight=float(weight))
    await message.answer('Пожалуйста, укажите свой рост (в см):')
    await state.set_state(User.height)


@router.message(User.height)
async def process_height(message: Message, state: FSMContext):
    height = message.text.strip()
    # Проверка корректности роста
    if not height.isdigit() or not (120 <= float(height) <= 300):
        await message.answer('Пожалуйста, введите корректный рост (число от 120 до 300):')
        return
    await state.update_data(height=float(height))
    await message.answer('Сколько минут активности у вас в день?')
    await state.set_state(User.activity_level)


@router.message(User.activity_level)
async def process_activity_level(message: Message, state: FSMContext):
    activity_level = message.text.strip()
    if not activity_level.isdigit() or not (0 <= int(activity_level) <= 1440):
        await message.answer('Пожалуйста, введите корректное время (число от 0 до 1440):')
        return
    await state.update_data(activity_level=int(activity_level))
    await message.answer('В каком городе вы находитесь?\n'
                         '(Напишите, пожалуйста, на английском.)')
    await state.set_state(User.city)


@router.message(User.city)
async def process_city(message: Message, state: FSMContext):
    city = message.text.strip()
    if not re.match('^[A-Za-zs]+$', city):
        await message.answer(
            'Город должен содержать только буквы на английском языке. Пожалуйста, введите корректное название города.')
        return
    await state.update_data(city=city)
    await message.answer('Какова ваша цель калорий?\n'
                         '(Введите "по умолчанию", чтобы я посчитал калории за Вас)')
    await state.set_state(User.calorie_goal)


async def calculate_calories(data):
    weight = float(data.get("weight", 0))
    height = float(data.get("height", 0))
    age = int(data.get("age", 0))
    activity_level = int(data.get("activity_level", 0))

    # Расчет калорий по формуле
    calories = 10 * weight + 6.25 * height - 5 * age
    # Добавляем уровень активности
    if activity_level < 30:
        calories += 200
    elif activity_level < 60:
        calories += 300
    else:
        calories += 400

    return calories


async def display_user_data(data, calorie_goal, goal_type, message):
    data = await message.answer(f'<b>Ваши данные:</b>\n\n'
                                f'Имя: {data.get("name")}\n'
                                f'Возраст: {data.get("age")} лет\n'
                                f'Вес: {data.get("weight")} кг\n'
                                f'Рост: {data.get("height")} см\n'
                                f'Уровень активности: {data.get("activity_level")} минут в день\n'
                                f'Город: {data.get("city")}\n'
                                f'Цель калорий: {calorie_goal} ккал ({goal_type})', parse_mode='HTML')
    # Возврат в главное меню
    await show_keyboard(data)


@router.message(User.calorie_goal)
async def process_calorie_goal(message: Message, state: FSMContext):
    data = await state.get_data()
    if message.text.lower() == "по умолчанию":
        calories = await calculate_calories(data)
        await state.update_data(custom_calorie_goal=float(calories))
        await display_user_data(data, calories, "по умолчанию", message)
    else:
        custom_calorie_goal = message.text.strip()
        if not custom_calorie_goal.isdigit() or not (800 <= int(custom_calorie_goal) <= 6000):
            await message.answer('Пожалуйста, введите корректное значение калорий (от 800 до 6000):')
            return
        await state.update_data(custom_calorie_goal=float(custom_calorie_goal))
        await display_user_data(data, message.text, "задано вручную", message)


@router.message(Command('get_profile'))
async def get_profile(message: Message, state: FSMContext):
    data = await state.get_data()  # Получаем данные состояния
    if not data.get('name'):
        p = await message.answer('<b><u>Вы выбрали кнопку "Профиль"</u></b>\n\n'
                                 '<b>Ваш профиль пуст.</b> Для просмотра нужно сначала создать профиль.',
                                 parse_mode='HTML')
    else:
        p = await message.answer(
            '<b><u>Вы выбрали кнопку "Профиль"</u></b>\n\n'
            f'<b>Ваши данные:</b>\n\n'
            f'Имя: {data.get("name")}\n'
            f'Возраст: {data.get("age")} лет\n'
            f'Вес: {data.get("weight")} кг\n'
            f'Рост: {data.get("height")} см\n'
            f'Уровень активности: {data.get("activity_level")} минут в день\n'
            f'Город: {data.get("city")}\n'
            f'Цель калорий: {data.get("custom_calorie_goal")} ккал\n'
            f'Количество выпитой воды: {data.get("logged_water", "Не указано")} мл\n'
            f'Количество полученных калорий: {data.get("logged_calories", "Не указано")}\n'
            f'Количество сожженных калорий: {data.get("burned_calories", "Не указано")}',
            parse_mode='HTML'
        )
    # Возврат в главное меню
    await show_keyboard(p)


###################################Water##############################################
# Функция для получения погоды по API из дз1
async def fetch_temperature(session, city):
    params = {'q': city, 'appid': API_KEY, 'units': 'metric', 'lang': 'ru'}
    async with session.get('https://api.openweathermap.org/data/2.5/weather', params=params) as response:
        if response.status == 200:
            data = await response.json()
            return data['main']['temp']
        else:
            print(f"Ошибка при запросе для города {city}: {response.status}")
            return None


async def get_temperature(city):
    async with ClientSession() as session:
        return await fetch_temperature(session, city)


@router.message(Command('water'))
async def start_water(message: Message, state: FSMContext):
    data = await state.get_data()  # Получаем данные состояния
    if not data.get('name'):
        p = await message.answer('<b><u>Вы выбрали кнопку "Вода"</u></b>\n\n'
                                 '<b>Ваш профиль пуст.</b> Сначала нужно создать профиль.',
                                 parse_mode='HTML')
        # Возврат в главное меню
        await show_keyboard(p)
    else:
        await message.answer('<b><u>Вы выбрали кнопку "Вода"</u></b>\n\n'
                             'Сколько воды (в мл) Вы уже выпили сегодня?',
                             parse_mode='HTML')
        await state.set_state(User.logged_water)


async def calculate_water_goal(message: Message, data):
    weight = float(data.get('weight', 0))
    activity = int(data.get('activity', 0))
    city = data.get('city', '')
    logged_water = float(data.get('logged_water', 0))

    # Расчет базовой нормы воды
    base_water_intake = weight * 30  # в мл
    additional_water = 0

    # Учитываем активность
    if activity > 0:
        additional_water += (activity // 30) * 500  # 500 мл за каждые 30 минут

    # Получаем текущую температуру
    current_temp = await get_temperature(city) if city else None
    if current_temp is not None and current_temp > 25:
        additional_water += 500  # если температура больше 25°C, добавляем 500 мл
    if current_temp is not None and current_temp > 30:
        additional_water += 500  # дополнительно за жаркую погоду

    # Полная норма
    total_water_goal = base_water_intake + additional_water
    # Остаток до нормы
    remaining_water = total_water_goal - logged_water
    return current_temp, total_water_goal, remaining_water


def plot_water_intake(message, logged_water, total_water_goal):
    # Данные для графика
    categories = ['Выпитая вода', 'Необходимая норма']
    values = [int(logged_water), int(total_water_goal)]
    colors = ['blue', 'orange']

    # Создаем график
    fig, ax = plt.subplots()
    bars = ax.bar(categories, values, color=colors)  # тут

    # Подписи над столбиками
    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, yval, round(yval, 2), ha='center', va='bottom')

    # Заголовок и метки
    ax.set_title('Потребление воды в день')
    ax.set_ylabel('Объем (мл)')

    # Сохраняем график во временный файл
    plt.savefig('water_intake.jpg')
    plt.close()


@router.message(User.logged_water)
async def process_logged_water(message: Message, state: FSMContext):
    logged_water = message.text.strip()
    # Проверка корректности возраста
    if not logged_water.isdigit() or not (0 <= float(logged_water) <= 5000):
        await message.answer('Пожалуйста, введите корректное значение выпитой воды (от 0 до 5000) мл.')
        return
    await state.update_data(logged_water=float(logged_water))
    data = await state.get_data()
    current_temp, total_water_goal, remaining_water = await calculate_water_goal(message, data)
    plot_water_intake(message, logged_water, total_water_goal)
    photo = await message.answer_photo(photo=FSInputFile('water_intake.jpg', filename='График воды'),
                               caption=f'Вы выпили {logged_water} мл из необходимых {int(total_water_goal)} мл воды.\n'
                                       f'Осталось еще {int(remaining_water)} мл до выполнения нормы.')
    await show_keyboard(photo)
###################################Food##############################################
