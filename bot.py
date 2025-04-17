import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import InlineKeyboardBuilder

import os
API_TOKEN = os.getenv("API_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Флаг приветствия
user_started = set()

# Состояния анкеты
class Form(StatesGroup):
    greeting = State()
    parent_name = State()
    child_name = State()
    child_age = State()
    child_class = State()
    child_shift = State()
    english_level = State()
    phone = State()
    branch = State()
    confirm = State()
    correcting = State()

user_data = {}

branches = ["Ул Авроры 17/2", "Ул Революционая,78", "Ул Баландина 2а", "Онлайн-школа"]

fields_map = {
    "Имя Родителя": ("parent_name", "Как к Вам можно обращаться?"),
    "Телефон": ("phone", "Укажите свой номер телефона, по которому мы вышлем подходящее расписание."),
    "Филиал": ("branch", "В каком филиале Вам удобнее заниматься?"),
    "Имя ребенка": ("child_name", "Укажите имя и фамилию ребенка."),
    "Возраст ребенка": ("child_age", "Укажите возраст ребенка"),
    "Класс ребенка": ("child_class", "Скажите, пожалуйста, в каком классе Ваш ребенок?"),
    "Смена ребенка": ("child_shift", "В какую смену учится ребенок?"),
}

def branch_keyboard():
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=b)] for b in branches],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return kb

@dp.message()
async def start(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if user_id not in user_started:
        user_started.add(user_id)
        await state.set_state(Form.parent_name)
        await message.answer(
            "Здравствуйте! С Вами на связи бот-помощник Языкового центра Smart+ \n\n"
            "Smart+ это: \n"
            "- Оксфордская программа, лицензия министерства образования; \n"
            "- Рождественской фестиваль, Театральный фестиваль на сцене университета для всех родителей ;\n"
            "- Государственный сертификат о получении уровня владения языком, торжественное вручение на сцене университета;\n"
            "- Встречи с иностранцами в разговорных клубах каждый месяц\n"
            "- Свой выездной  полилингвальный приключенческий лагерь Гринхил на всех каникулах"
        )
        await asyncio.sleep(1)
        await message.answer("Как к Вам можно обращаться?")
    else:
        current_state = await state.get_state()
        if not current_state:
            await state.set_state(Form.parent_name)
            await message.answer("Как к Вам можно обращаться?")
        else:
            await dp.feed_update(bot, message)

@dp.message(Form.parent_name)
async def get_parent_name(message: types.Message, state: FSMContext):
    user_data[message.from_user.id] = {"parent_name": message.text}
    await state.set_state(Form.child_name)
    await message.answer("Укажите имя и фамилию ребенка.")

@dp.message(Form.child_name)
async def get_child_name(message: types.Message, state: FSMContext):
    user_data[message.from_user.id]["child_name"] = message.text
    await state.set_state(Form.child_age)
    await message.answer("Укажите возраст ребенка")

@dp.message(Form.child_age)
async def get_child_age(message: types.Message, state: FSMContext):
    user_data[message.from_user.id]["child_age"] = message.text
    await state.set_state(Form.child_class)
    await message.answer("Скажите, пожалуйста, в каком классе Ваш ребенок?")

@dp.message(Form.child_class)
async def get_child_class(message: types.Message, state: FSMContext):
    user_data[message.from_user.id]["child_class"] = message.text
    await state.set_state(Form.child_shift)
    await message.answer("В какую смену учится ребенок?")

@dp.message(Form.child_shift)
async def get_child_shift(message: types.Message, state: FSMContext):
    user_data[message.from_user.id]["child_shift"] = message.text
    await state.set_state(Form.english_level)
    await message.answer("Как обстоят дела с английским языком? Изучали ли до этого дополнительно? Какая оценка в школе?")

@dp.message(Form.english_level)
async def get_english_level(message: types.Message, state: FSMContext):
    user_data[message.from_user.id]["english_level"] = message.text
    await state.set_state(Form.phone)
    await message.answer("Укажите свой номер телефона, по которому мы вышлем подходящее расписание.")

@dp.message(Form.phone)
async def get_phone(message: types.Message, state: FSMContext):
    user_data[message.from_user.id]["phone"] = message.text
    await state.set_state(Form.branch)
    await message.answer("В каком филиале Вам удобнее заниматься?", reply_markup=branch_keyboard())

@dp.message(Form.branch)
async def get_branch(message: types.Message, state: FSMContext):
    user_data[message.from_user.id]["branch"] = message.text
    await state.set_state(Form.confirm)
    await message.answer("Спасибо за информацию, давайте сверим все введенные Вами данные для исключения возможных опечаток.")
    await send_summary(message)

async def send_summary(message):
    data = user_data[message.from_user.id]
    summary = (
        f"Имя родителя: {data['parent_name']}\n"
        f"Телефон родителя: {data['phone']}\n"
        f"Филиал: {data['branch']}\n"
        f"Имя и фамилия ребенка: {data['child_name']}\n"
        f"Возраст ребенка: {data['child_age']}\n"
        f"Класс ребенка: {data['child_class']}\n"
        f"Смена ребенка: {data['child_shift']}"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Да, все верно!", callback_data="confirm_yes")],
        [InlineKeyboardButton(text="Нет, есть ошибка", callback_data="confirm_no")]
    ])
    await message.answer(summary)
    await message.answer("Все верно?", reply_markup=kb)

@dp.callback_query(lambda c: c.data == "confirm_yes")
async def confirmed(callback: types.CallbackQuery, state: FSMContext):
    data = user_data[callback.from_user.id]
    text = (
        f"Имя родителя: {data['parent_name']}\n"
        f"Телефон родителя: {data['phone']}\n"
        f"Филиал: {data['branch']}\n"
        f"Имя и фамилия ребенка: {data['child_name']}\n"
        f"Возраст ребенка: {data['child_age']}\n"
        f"Класс ребенка: {data['child_class']}\n"
        f"Смена ребенка: {data['child_shift']}\n"
        f"Познания в области Английского языка: {data['english_level']}"
    )
    await bot.send_message(ADMIN_ID, text)
    await callback.message.answer("Спасибо! Ваша анкета отправлена.")
    await state.clear()

@dp.callback_query(lambda c: c.data == "confirm_no")
async def correction(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(Form.correcting)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=field, callback_data=f"fix_{field}")] for field in fields_map
    ])
    await callback.message.answer("Пожалуйста укажите где была совершена ошибка", reply_markup=kb)

@dp.callback_query(lambda c: c.data.startswith("fix_"))
async def fix_field(callback: types.CallbackQuery, state: FSMContext):
    field_label = callback.data[4:]
    state_name, question = fields_map[field_label]
    await state.update_data(fix_field=state_name)
    await callback.message.answer(question)

@dp.message(Form.correcting)
async def save_correction(message: types.Message, state: FSMContext):
    fix = await state.get_data()
    field = fix["fix_field"]
    user_data[message.from_user.id][field] = message.text
    await message.answer("Хорошо, я исправил выбранные Вами данные!")
    await send_summary(message)

# Запуск
if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    asyncio.run(dp.start_polling(bot))
