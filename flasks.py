from flask import Flask, render_template, request, url_for
from werkzeug.datastructures import FileStorage
import cv2
from PIL import Image, ImageDraw
import numpy as np
from ASCII import ArtConverter


app = Flask(__name__)
menu = [{"name": "Чёрно-белый", "url": "wb"},
        {"name": "Пиксель - арт", "url": "pix"},
        {"name": "Негатив", "url": "neg"},
        {"name": "Оттенки серого", "url": "grey"},
        {"name": "Мультяшный-max", "url": "cartoon-max"},
        {"name": "Мультяшный-min", "url": "cartoon-min"},
        {"name": "ASCII", "url": "ascii"}]


@app.route("/")
def main_page():
    return render_template('main.html', menu=menu)


@app.route("/wb", methods=['POST', 'GET'])
def wb():
    if request.method == 'POST':
        picture: FileStorage = request.files.to_dict()['picture']
        picture.save('static/images/test.jpg')
        img_grey = cv2.imread('static/images/test.jpg', cv2.IMREAD_GRAYSCALE)
        color = 128
        img_binary = cv2.threshold(img_grey, color, 255, cv2.THRESH_BINARY)[1]
        cv2.imwrite('static/images/test.jpg', img_binary)
    return render_template('style.html', name=url_for("wb"))


@app.route("/pix", methods=['POST', 'GET'])
def pixel():
    if request.method == 'POST':
        picture: FileStorage = request.files.to_dict()['picture']
        picture.save('static/images/test.jpg')
        picture = Image.open('static/images/test.jpg')
        small_picture = picture.resize((128, 128), Image.BILINEAR)
        result_picture = small_picture.resize(picture.size, Image.NEAREST)
        result_picture.save('static/images/test.jpg')
    return render_template('style.html', name=url_for("pixel"))


@app.route("/neg", methods=['POST', 'GET'])
def neg():
    if request.method == 'POST':
        picture: FileStorage = request.files.to_dict()['picture']
        picture.save('static/images/test.jpg')
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
        image.save('static/images/test.jpg')
        del draw
    return render_template('style.html', name=url_for("neg"))


@app.route("/grey", methods=['POST', 'GET'])
def grey():
    if request.method == 'POST':
        picture: FileStorage = request.files.to_dict()['picture']
        picture.save('static/images/test.jpg')
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
        image.save('static/images/test.jpg')
        del draw
    return render_template('style.html', name=url_for("grey"))


@app.route("/cartoon-max", methods=['POST', 'GET'])
def cartoon_max():
    if request.method == 'POST':
        picture: FileStorage = request.files.to_dict()['picture']
        picture.save('static/images/test.jpg')
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
        cv2.imwrite('static/images/test.jpg', cartoon_Bilateral)
    return render_template('style.html', name=url_for("cartoon_max"))


@app.route("/cartoon-min", methods=['POST', 'GET'])
def cartoon_min():
    if request.method == 'POST':
        picture: FileStorage = request.files.to_dict()['picture']
        picture.save('static/images/test.jpg')
        img = cv2.imread('static/images/test.jpg')
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img = cv2.medianBlur(img, 5)
        img = cv2.GaussianBlur(img, (7, 7), 0)
        # Использование адаптивного порога в качестве маски
        edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 9)
        color = cv2.bilateralFilter(img, 9, 200, 200)
        # Наложжение мультяшного стиля
        cartoon = cv2.bitwise_and(color, color, mask=edges)
        cv2.imwrite('static/images/test.jpg', cartoon)
    return render_template('style.html', name=url_for("cartoon_min"))


@app.route("/ascii", methods=['POST', 'GET'])
def ascii_style():
    if request.method == 'POST':
        picture: FileStorage = request.files.to_dict()['picture']
        picture.save('static/images/test.jpg')
        img = ArtConverter()
        img.run()
        del img
    return render_template('style.html', name=url_for("ascii_style"))


if __name__ == "__main__":
    app.run(debug=True)
