import os
from math import hypot
from telebot import types
import cv2


face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
chickesn_ori = cv2.imread('ch.png')
specs_ori = cv2.imread('glass.png')
clown_ori = cv2.imread('clown.png')
pig_ori = cv2.imread('pig.png')


selected_mask_type = None


def apply_mask_to_video(mask_type):
    global selected_mask_type
    selected_mask_type = mask_type


def apply_mask():
    video_capture = cv2.VideoCapture('user_video.mp4')

    fps = video_capture.get(cv2.CAP_PROP_FPS)
    frame_size = (int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH)), int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT)))

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video_writer = cv2.VideoWriter('output.mp4', fourcc, fps, frame_size)

    while True:
        ret, frame = video_capture.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        for (x, y, w, h) in faces:
            if h > 0 and w > 0:

                if selected_mask_type == 'glass':
                    # Glasses position on the nose
                    nose_symin = int(y + 1.5 * h / 5)
                    nose_symax = int(y + 2.5 * h / 5)
                    nose_sh = nose_symax - nose_symin

                    face_nose_roi_color = frame[nose_symin:nose_symax, x:x + w]
                    specs = cv2.resize(specs_ori, (w, nose_sh), interpolation=cv2.INTER_CUBIC)
                    specs_gray = cv2.cvtColor(specs, cv2.COLOR_BGR2GRAY)
                    _, mask = cv2.threshold(specs_gray, 25, 255, cv2.THRESH_BINARY_INV)

                    mask_inv = cv2.bitwise_not(mask)
                    face_nose_roi = cv2.bitwise_and(face_nose_roi_color, face_nose_roi_color, mask=mask_inv)
                    res = cv2.add(face_nose_roi, specs)
                    frame[nose_symin:nose_symax, x:x + w] = res

                elif selected_mask_type == 'clown':
                    # Clown mask position on the full face
                    face_symin = int(y - 0.5 * h / 5)
                    face_symax = int(y + 1.5 * h / 5)
                    face_sh = face_symax - face_symin

                    face_roi_color = frame[face_symin:face_symax, x:x + w]
                    clown = cv2.resize(clown_ori, (w, face_sh), interpolation=cv2.INTER_CUBIC)
                    clown_gray = cv2.cvtColor(clown, cv2.COLOR_BGR2GRAY)
                    _, mask = cv2.threshold(clown_gray, 25, 255, cv2.THRESH_BINARY_INV)

                    mask_inv = cv2.bitwise_not(mask)
                    face_roi = cv2.bitwise_and(face_roi_color, face_roi_color, mask=mask_inv)
                    res = cv2.add(face_roi, clown)
                    frame[face_symin:face_symax, x:x + w] = res

                elif selected_mask_type == 'chicken':
                    # Chicken mask position on the full face
                    face_symin = int(y - 0.5 * h / 5)
                    face_symax = int(y + 1.5 * h / 5)
                    face_sh = face_symax - face_symin

                    face_roi_color = frame[face_symin:face_symax, x:x + w]
                    chicken = cv2.resize(chickesn_ori, (w, face_sh), interpolation=cv2.INTER_CUBIC)
                    chicken_gray = cv2.cvtColor(chicken, cv2.COLOR_BGR2GRAY)
                    _, mask = cv2.threshold(chicken_gray, 25, 255, cv2.THRESH_BINARY_INV)

                    mask_inv = cv2.bitwise_not(mask)
                    face_roi = cv2.bitwise_and(face_roi_color, face_roi_color, mask=mask_inv)
                    res = cv2.add(face_roi, chicken)
                    frame[face_symin:face_symax, x:x + w] = res

                elif selected_mask_type == 'pig':
                    face_symin = int(y - 0.5 * h / 5)
                    face_symax = int(y + 1.5 * h / 5)
                    face_sh = face_symax - face_symin

                    face_roi_color = frame[face_symin:face_symax, x:x + w]
                    pig = cv2.resize(pig_ori, (w, face_sh), interpolation=cv2.INTER_CUBIC)
                    pig_gray = cv2.cvtColor(pig, cv2.COLOR_BGR2GRAY)
                    _, mask = cv2.threshold(pig_gray, 25, 255, cv2.THRESH_BINARY_INV)

                    mask_inv = cv2.bitwise_not(mask)
                    face_roi = cv2.bitwise_and(face_roi_color, face_roi_color, mask=mask_inv)
                    res = cv2.add(face_roi, pig)
                    frame[face_symin:face_symax, x:x + w] = res

        video_writer.write(frame)

    video_capture.release()
    video_writer.release()
    cv2.destroyAllWindows()


import webbrowser
import telebot
from db import *
from telebot import types
import os
import time

bot = telebot.TeleBot('7142673061:AAHwNCi3xPUswzUxt1_S3b0ZuNVC8ml4tvI')


@bot.message_handler(commands=['start'])
def starart_bot(message):
    first_message = f"<b>{message.from_user.first_name} </b>, привет!\nХочешь попробовать маски на видео в Telegram? \nТогда введи команду из предложенных и отправь видео"
    markup = types.InlineKeyboardMarkup()
    button_clown = types.InlineKeyboardButton(text='Маска клоуна', callback_data='clown')
    button_glass = types.InlineKeyboardButton(text='Маска очков', callback_data='glass')
    button_pig = types.InlineKeyboardButton(text='Маска свиньи', callback_data='pig')
    button_chicken = types.InlineKeyboardButton(text='Маска цыплёнка', callback_data='chicken')
    markup.add(button_clown, button_glass, button_pig, button_chicken)
    bot.send_message(message.chat.id, first_message, parse_mode='html', reply_markup=markup)


# Callback query handler
@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    mask_type = call.data
    apply_mask_to_video(mask_type)
    bot.send_message(call.message.chat.id,
                     f'Отправьте мне видео, и я добавлю маску {mask_type} и отправлю его вам обратно.')


# Video message handler
@bot.message_handler(content_types=['video'])
def handle_video(message):
    file_info = bot.get_file(message.video.file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    with open('user_video.mp4', 'wb') as f:
        f.write(downloaded_file)

    apply_mask()

    while not os.path.exists('output.mp4'):
        time.sleep(1)

    with open('output.mp4', 'rb') as f:
        bot.send_video(message.chat.id, f, caption='Отправляю готовое видео обратно')

    os.remove('output.mp4')


# Start polling
bot.polling()
