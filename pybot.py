#!venv/bin/python
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton

# Объект бота
bot = Bot(token="5208126996:AAGgbK5tyQ6UtNAvV6I56Asct6adKbGEPMY")
# Диспетчер для бота
dp = Dispatcher(bot)
# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)

# кнопка после старта
button_start = KeyboardButton('Чёрно-белый 🔳')

greet_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
greet_kb.add(button_start)

# Хэндлер на команду /test1


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer("Выберите стиль для изменения", reply_markup=greet_kb)


@dp.message_handler()
async def next_start(message: types.Message):
    if message.text == 'Чёрно-белый 🔳':
        await message.answer("Загрузите фотографию", reply_markup=ReplyKeyboardRemove())


@dp.message_handler(content_types=["photo"])
async def send_photo(message: types.Message):
    photo_id = message.photo[-1].file_id
    await bot.send_photo(message.from_user.id, photo_id, caption='Результат')


if __name__ == "__main__":
    # Запуск бота
    executor.start_polling(dp, skip_updates=True)
