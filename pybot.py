import cv2
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from PIL import Image, ImageDraw
from os import remove
import numpy as np
from ASCII import ArtConverter

bot = Bot(token="5208126996:AAGgbK5tyQ6UtNAvV6I56Asct6adKbGEPMY", parse_mode=types.ParseMode.HTML)  # Объект бота
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)  # Диспетчер для бота
logging.basicConfig(level=logging.INFO)  # Включаем логирование, чтобы не пропустить важные сообщения

button_start1 = KeyboardButton('Чёрно-белый 🔳')  # кнопка после старта
button_start2 = KeyboardButton('Пиксель - арт')  # кнопка после старта
button_start3 = KeyboardButton('Негатив')  # кнопка после старта
button_start4 = KeyboardButton('Оттенки серого')  # кнопка после старта
button_start5 = KeyboardButton('Мультяшный-max')  # кнопка после старта
button_start6 = KeyboardButton('Мультяшный-min')  # кнопка после старта
button_start7 = KeyboardButton('ASCII')  # кнопка после старта

greet_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
greet_kb.add(button_start1, button_start2, button_start3).add(button_start4, button_start5, button_start6) \
    .add(button_start7)


@dp.message_handler(commands=['start'])  # Команда старт для первого использования
async def command_start(message: types.Message, state: FSMContext):
    await message.answer("Начнём!")
    await start(message, state)


@dp.message_handler()  # Команда старт для повторных использований
async def start(message: types.Message, state: FSMContext):
    await message.answer("Выберите стиль для изменения", reply_markup=greet_kb)
    await state.set_state('enter')


@dp.message_handler(state='enter')  # Приём текста с клавы
async def next_start(message: types.Message, state: FSMContext):
    if message.text == 'Чёрно-белый 🔳':
        await message.answer("Загрузите фотографию", reply_markup=ReplyKeyboardRemove())
        await state.set_state('wb')
    elif message.text == 'Пиксель - арт':
        await message.answer("Загрузите фотографию", reply_markup=ReplyKeyboardRemove())
        await state.set_state('pix')
    elif message.text == 'Негатив':
        await message.answer("Загрузите фотографию", reply_markup=ReplyKeyboardRemove())
        await state.set_state('neg')
    elif message.text == 'Оттенки серого':
        await message.answer("Загрузите фотографию", reply_markup=ReplyKeyboardRemove())
        await state.set_state('gray')
    elif message.text == 'Мультяшный-max':
        await message.answer("Загрузите фотографию", reply_markup=ReplyKeyboardRemove())
        await state.set_state('cartoon-max')
    elif message.text == 'Мультяшный-min':
        await message.answer("Загрузите фотографию", reply_markup=ReplyKeyboardRemove())
        await state.set_state('cartoon-min')
    elif message.text == 'ASCII':
        await message.answer("Загрузите фотографию", reply_markup=ReplyKeyboardRemove())
        await state.set_state('ascii')


@dp.message_handler(state='wb', content_types=['photo'])  # Функция стиля Ч-Б
async def send_photo(message: types.Message, state: FSMContext):
    await message.photo[-1].download('static/images/test.jpg')
    img_grey = cv2.imread('static/images/test.jpg', cv2.IMREAD_GRAYSCALE)
    color = 128
    img_binary = cv2.threshold(img_grey, color, 255, cv2.THRESH_BINARY)[1]
    cv2.imwrite('test_BaW.jpg', img_binary)
    photo = open('test_BaW.jpg', 'rb')
    await bot.send_photo(message.from_user.id, photo=photo, caption="Результат")
    photo.close()
    remove('static/images/test.jpg')
    remove('test_BaW.jpg')
    await start(message, state)


@dp.message_handler(state='pix', content_types=['photo'])
async def send_photo_pix(message: types.Message, state: FSMContext):  # Пикселизация фото
    await message.photo[-1].download('static/images/test.jpg')

    picture = Image.open('static/images/test.jpg')
    small_picture = picture.resize((128, 128), Image.BILINEAR)
    result_picture = small_picture.resize(picture.size, Image.NEAREST)
    result_picture.save('testPIX.jpg')
    photo = open('testPIX.jpg', 'rb')
    await bot.send_photo(message.from_user.id, photo=photo, caption="Результат")
    photo.close()
    remove('static/images/test.jpg')
    remove('testPIX.jpg')
    await start(message, state)


@dp.message_handler(state='neg', content_types=['photo'])
async def send_photo_negative(message: types.Message, state: FSMContext):  # Наложение негатива на фото
    await message.photo[-1].download('static/images/test.jpg')
    image = Image.open('static/images/test.jpg')
    draw = ImageDraw.Draw(image)  # Создаем инструмент для рисования
    width = image.size[0]  # Ширина
    height = image.size[1]  # Высота
    pix = image.load()  # Выгружаем значения пикселей
    for i in range(width):
        for j in range(height):
            a = pix[i, j][0]
            b = pix[i, j][1]
            c = pix[i, j][2]
            draw.point((i, j), (255 - a, 255 - b, 255 - c))
    image.save('testNegative.jpg')
    del draw
    photo = open('testNegative.jpg', 'rb')
    await bot.send_photo(message.from_user.id, photo=photo, caption="Результат")
    photo.close()
    remove('static/images/test.jpg')
    remove('testNegative.jpg')
    await start(message, state)


@dp.message_handler(state='gray', content_types=['photo'])
async def send_photo_gray(message: types.Message, state: FSMContext):  # Серый фильтр на фото
    await message.photo[-1].download('static/images/test.jpg')
    image = Image.open('static/images/test.jpg')
    draw = ImageDraw.Draw(image)  # Создаем инструмент для рисования
    width = image.size[0]  # Ширина
    height = image.size[1]  # Высота
    pix = image.load()  # Выгружаем значения пикселей
    for i in range(width):
        for j in range(height):
            a = pix[i, j][0]
            b = pix[i, j][1]
            c = pix[i, j][2]
            s = (a + b + c) // 3
            draw.point((i, j), (s, s, s))
    image.save('testGray.jpg')
    del draw
    photo = open('testGray.jpg', 'rb')
    await bot.send_photo(message.from_user.id, photo=photo, caption="Результат")
    photo.close()
    remove('static/images/test.jpg')
    remove('testGray.jpg')
    await start(message, state)


@dp.message_handler(state='cartoon-max', content_types=['photo'])
async def send_photo_cartoon_max(message: types.Message, state: FSMContext):  # Мультяшный стиль с контрастом
    await message.photo[-1].download('static/images/test.jpg')
    img = cv2.imread('static/images/test.jpg')
    # Применение размытия по Гаусу
    img_gb = cv2.GaussianBlur(img, (7, 7), 0)
    # Применение блюра
    img_mb = cv2.medianBlur(img_gb, 1)
    # Применение двустороннего фильтра
    img_bf = cv2.bilateralFilter(img_mb, 5, 80, 80)

    # Использование фильтра Лапласа для обнаружение краев
    img_lp_im = cv2.Laplacian(img, cv2.CV_8U, ksize=5)
    img_lp_gb = cv2.Laplacian(img_gb, cv2.CV_8U, ksize=5)
    img_lp_mb = cv2.Laplacian(img_mb, cv2.CV_8U, ksize=5)
    img_lp_al = cv2.Laplacian(img_bf, cv2.CV_8U, ksize=5)

    # Применим пороговое значение (Otsu)
    # Конвертируем фото в серый фильтр
    img_lp_im_grey = cv2.cvtColor(img_lp_im, cv2.COLOR_BGR2GRAY)
    img_lp_gb_grey = cv2.cvtColor(img_lp_gb, cv2.COLOR_BGR2GRAY)
    img_lp_mb_grey = cv2.cvtColor(img_lp_mb, cv2.COLOR_BGR2GRAY)
    img_lp_al_grey = cv2.cvtColor(img_lp_al, cv2.COLOR_BGR2GRAY)

    # Убираем лишние шумы
    blur_im = cv2.GaussianBlur(img_lp_im_grey, (5, 5), 0)
    blur_gb = cv2.GaussianBlur(img_lp_gb_grey, (5, 5), 0)
    blur_mb = cv2.GaussianBlur(img_lp_mb_grey, (5, 5), 0)
    blur_al = cv2.GaussianBlur(img_lp_al_grey, (5, 5), 0)

    # Добавляем (Otsu)
    _, tresh_im = cv2.threshold(blur_im, 245, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    _, tresh_gb = cv2.threshold(blur_gb, 245, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    _, tresh_mb = cv2.threshold(blur_mb, 245, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    _, tresh_al = cv2.threshold(blur_al, 245, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    inverted_Bilateral = cv2.subtract(255, tresh_al)
    # Уменьшение цвета исходного изображения
    div = 64
    img_bins = img // div * div + div // 2
    # Изменение формы изображения
    img_reshaped = img.reshape((-1, 3))
    # Конвертируем в np.float32
    img_reshaped = np.float32(img_reshaped)
    # Установка критерия Kmeans
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    # Применим Kmeans
    _, label, center = cv2.kmeans(img_reshaped, 8, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
    # Конвертируем из черного в np.int8
    center = np.uint8(center)
    # Преобразуем изображение маски обратно в цвет
    inverted_Bilateral = cv2.cvtColor(inverted_Bilateral, cv2.COLOR_GRAY2RGB)
    # Объединим изображение края и привязанное изображение
    cartoon_Bilateral = cv2.bitwise_and(inverted_Bilateral, img_bins)
    cv2.imwrite('testCARTOONMAX.jpg', cartoon_Bilateral)
    photo = open('testCARTOONMAX.jpg', 'rb')
    await bot.send_photo(message.from_user.id, photo=photo, caption="Результат")
    photo.close()
    remove('static/images/test.jpg')
    remove('testCARTOONMAX.jpg')
    await start(message, state)


@dp.message_handler(state='cartoon-min', content_types=['photo'])
async def send_photo_cartoon_min(message: types.Message, state: FSMContext):  # Мультяшный стиль без
    await message.photo[-1].download('static/images/test.jpg')
    img = cv2.imread('static/images/test.jpg')
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img = cv2.medianBlur(img, 5)
    img = cv2.GaussianBlur(img, (7, 7), 0)
    # Использование адаптивного порога в качестве маски
    edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 9)
    color = cv2.bilateralFilter(img, 9, 200, 200)
    # Наложжение мультяшного стиля
    cartoon = cv2.bitwise_and(color, color, mask=edges)
    cv2.imwrite('testCARTOONMIN.jpg', cartoon)
    photo = open('testCARTOONMIN.jpg', 'rb')
    await bot.send_photo(message.from_user.id, photo=photo, caption="Результат")
    photo.close()
    remove('static/images/test.jpg')
    remove('testCARTOONMIN.jpg')
    await start(message, state)


@dp.message_handler(state='ascii', content_types=['photo'])
async def send_photo_ascii(message: types.Message, state: FSMContext):  # ASCII стиль
    await message.photo[-1].download('static/images/test.jpg')
    img = ArtConverter()
    img.run()
    photo = open('static/images/test.jpg', 'rb')
    await bot.send_photo(message.from_user.id, photo=photo, caption="Результат")
    photo.close()
    del img
    remove('static/images/test.jpg')
    await start(message, state)


if __name__ == "__main__":
    # Запуск бота
    executor.start_polling(dp, skip_updates=True)
