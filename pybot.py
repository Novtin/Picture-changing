import cv2
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from PIL import Image


bot = Bot(token="5208126996:AAGgbK5tyQ6UtNAvV6I56Asct6adKbGEPMY", parse_mode=types.ParseMode.HTML)  # Объект бота
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)  # Диспетчер для бота
logging.basicConfig(level=logging.INFO)  # Включаем логирование, чтобы не пропустить важные сообщения

button_start1 = KeyboardButton('Чёрно-белый 🔳') # кнопка после старта
button_start2 = KeyboardButton('Пиксель - арт') # кнопка после старта

greet_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
greet_kb.add(button_start1, button_start2)


@dp.message_handler(commands=['start'])  # Команда старт
async def start(message: types.Message):
    await message.answer("Выберите стиль для изменения", reply_markup=greet_kb)


@dp.message_handler()  # Приём текста с клавы
async def next_start(message: types.Message, state: FSMContext):
    if message.text == 'Чёрно-белый 🔳':
        await message.answer("Загрузите фотографию", reply_markup=ReplyKeyboardRemove())
        await state.set_state('wb')
    if message.text == 'Пиксель - арт':
        await message.answer("Загрузите фотографию", reply_markup=ReplyKeyboardRemove())
        await state.set_state('pix')


@dp.message_handler(state='wb', content_types=['photo'])  # Функция стиля Ч-Б
async def send_photo(message: types.Message, state: FSMContext):
    await message.photo[-1].download('test.jpg')
    img_grey = cv2.imread('test.jpg', cv2.IMREAD_GRAYSCALE)
    color = 128
    img_binary = cv2.threshold(img_grey, color, 255, cv2.THRESH_BINARY)[1]
    cv2.imwrite('test_BaW.jpg', img_binary)
    photo = open('test_BaW.jpg', 'rb')
    await bot.send_photo(message.from_user.id, photo=photo, caption="Результат")
    await state.finish()


@dp.message_handler(state='pix', content_types=['photo'])
async def send_photo_pix(message: types.Message, state: FSMContext):  # Пикселизация фото
    await message.photo[-1].download('test.jpg')

    picture = Image.open('test.jpg')
    small_picture = picture.resize((128, 128), Image.BILINEAR)
    result_picture = small_picture.resize(picture.size, Image.NEAREST)
    result_picture.save('testPIX.jpg')
    photo = open('testPIX.jpg', 'rb')
    await bot.send_photo(message.from_user.id, photo=photo, caption="Результат")
    await state.finish()


if __name__ == "__main__":
    # Запуск бота
    executor.start_polling(dp, skip_updates=True)
