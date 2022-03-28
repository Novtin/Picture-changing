#!venv/bin/python
import logging
import cv2
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.filters.state import StatesGroup, State
from PIL import Image


class Status(StatesGroup):
    F1 = State()


bot = Bot(token="5208126996:AAGgbK5tyQ6UtNAvV6I56Asct6adKbGEPMY")  # Объект бота
dp = Dispatcher(bot)  # Диспетчер для бота
logging.basicConfig(level=logging.INFO)  # Включаем логирование, чтобы не пропустить важные сообщения

button_start = KeyboardButton('Чёрно-белый 🔳')  # кнопка после старта

greet_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
greet_kb.add(button_start)


@dp.message_handler(commands=['start'], state=None)  # Команда старт
async def start(message: types.Message):
    await message.answer("Выберите стиль для изменения", reply_markup=greet_kb)


# @dp.message_handler(state=Status.F1)  # Черно-белый фильтр
# async def send_photo(message: types.Message):
#     if message.content_type == 'photo':
#         await message.photo[-1].download('test.jpg')
#
#         img_grey = cv2.imread('test.jpg', cv2.IMREAD_GRAYSCALE)
#         color = 128
#         img_binary = cv2.threshold(img_grey, color, 255, cv2.THRESH_BINARY)[1]
#         cv2.imwrite('test_BaW.jpg', img_binary)
#
#         photo = open('test_BaW.jpg', 'rb')
#         await bot.send_photo(message.from_user.id, photo=photo, caption="Результат")
#     else:
#         await message.answer('ops')


@dp.message_handler()
async def send_photo_pix(message: types.Message):  # Пикселизация фото
    await message.photo[-1].download('test.jpg')

    picture = Image.open('test.jpg')
    small_picture = picture.resize((128, 128), Image.BILINEAR)
    result_picture = small_picture.resize(picture.size, Image.NEAREST)
    result_picture.save('testPIX.jpg')
    photo = open('testPIX.jpg', 'rb')
    await bot.send_photo(message.from_user.id, photo=photo, caption="Результат")


@dp.message_handler(state=None)  # Функция стиля
async def next_start(message: types.Message):
    if message.text == 'Чёрно-белый 🔳':
        await message.answer("Загрузите фотографию", reply_markup=ReplyKeyboardRemove())
        await Status.first()


if __name__ == "__main__":
    # Запуск бота
    executor.start_polling(dp, skip_updates=True)
