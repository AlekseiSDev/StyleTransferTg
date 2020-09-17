import telebot as tb
import config
from session import Session
import model
from datetime import datetime

Model = model.Model()
bot = tb.TeleBot(config.TOKEN)
# словарь сессий, ключ - id чата
bot.sessions = {}


@bot.message_handler(commands=['start'])
def welcome(message):
    """
    handler for start command/ print hello messages
    :param message: message obj
    """

    ses = Session(message.chat.id)
    bot.sessions[message.chat.id] = ses

    # приветствие и 1й пример
    msg = f"""Добро пожаловать, {message.from_user.first_name}!\nЯ - <b>{bot.get_me().first_name}</b>, 
бот, позволяющий каждому почувствовать себя художником. \n """
    bot.send_message(message.chat.id, msg, parse_mode='html')
    __send_photo(chat_id=message.chat.id, photo_path='data/examples/1.jpg',
                 msg="Смотри какие клевые штуки мы с тобой можем делать!")

    # keyboard
    markup = tb.types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1, item2, item3 = tb.types.KeyboardButton("Ок, го выберем стили для моего шедевра!"), \
                          tb.types.KeyboardButton("Загружу фотку, которую хочу превратить в шедевр!"), \
                          tb.types.KeyboardButton("Сделай мне красиво, бро!")
    markup.add(item1, item2, item3)
    bot.send_message(message.chat.id, "Ну че, похудожничаем чутка?", parse_mode='html', reply_markup=markup)


@bot.message_handler(content_types=['text'])
def handle_message(message):
    """
    handler of all messages except '/start'
    :param message:
    :return:
    """
    # get session
    ses = bot.sessions.get(message.chat.id, None)

    # if session is not started - ask for /start
    if ses is None:
        bot.send_message(message.chat.id, "Бро, мы незнакомы, предлагаю начать с команды /start!")

    # если сессия существует
    else:
        if message.chat.type == 'private':
            if message.text == 'Ок, го выберем стили для моего шедевра!':
                bot.send_message(message.chat.id, "Смотри, чё есть!")
                paths, msgs = [], []
                for i in range(1, 10):
                    paths.append(f'data/style/{i}.jpg')
                    msgs.append(f'#{i}')
                __send_photos(chat_id=message.chat.id, photo_paths=paths, msgs=msgs)

            elif message.text[0] == '#':
                try:
                    style_code = int(message.text[1:])
                    # TODO: проверка, что входит в заданный диапазон стилей
                    ses.style_img_path = f'{style_code}.jpg'
                    if ses.content_img_path is not None:
                        ses.state = 3
                        bot.send_message(message.chat.id, "Стиль выставлен, фотка есть, го творить!")
                    else:
                        ses.state = 2
                        bot.send_message(message.chat.id, "Стиль выставлен, можно грузить фотку!")
                except Exception:
                    bot.send_message(message.chat.id, "Я не понимаю, выбери плз стиль, написал #n, где n замени на число от 1 до 9!")

            elif message.text[:5] == 'size=':
                # получим число
                size = int(message.text[5:])
                ses.size = size
                bot.send_message(message.chat.id, "Размер выходной картинки выставлен, бро!")

            elif message.text == "Загружу фотку, которую хочу превратить в шедевр!":
                if ses.state == 0:
                    bot.send_message(message.chat.id, "Бро, сначала глянь на стили и выбери поинтересней!")
                elif ses.state == 1:
                    bot.send_message(message.chat.id, "Бро, я показывал тебе стили, выбери их, написав мне #1,"
                                                      "#2 или #3!")
                else:
                    bot.send_message(message.chat.id, "Ок, жду фотку!")

            elif message.text == "Сделай мне красиво, бро!":
                if ses.state != 3:
                    if ses.state == 0:
                        bot.send_message(message.chat.id, "Бро, сначала глянь на стили и выбери поинтересней!")
                    if ses.state == 1:
                        bot.send_message(message.chat.id, "Бро, я показывал тебе стили, выбери их, написав мне #1,"
                                                          "#2 или #3!")
                    if ses.state == 2:
                        bot.send_message(message.chat.id, "Бро, сначала загрузи годный материал для обработки!")
                else:
                    # ответ
                    content_path = f'data/content/{ses.content_img_path}'
                    style_path = f'data/style/{ses.style_img_path}'
                    out_path = f'data/out/{ses.content_img_path}'
                    # само тело ответа
                    bot.send_message(message.chat.id, "Окей бро, обрабатываю!")
                    Model.inference(content_path=content_path, style_path=style_path, out_path=out_path,
                                    imsize=ses.size)
                    bot.send_message(message.chat.id, "Смотри, что у нас вышло!")
                    __send_photo(chat_id=message.chat.id, photo_path=out_path, msg="Кул?!")
            else:
                bot.send_message(message.chat.id, 'Я и не знаю что ответить на такое.. Попробуй начать с /start')


@bot.message_handler(content_types=['photo'])
def __handle_get_photo(message):
    """
    handle user photo. if it's good state - download photo, if not - ask for another commands
    :param message:
    :return:
    """
    ses = bot.sessions.get(message.chat.id, None)
    if ses is None:
        bot.send_message(message.chat.id, "Бро, мы незнакомы, предлагаю начать с команды /start!")
        return

    if ses.state < 2:
        if ses.state == 0:
            bot.send_message(message.chat.id, "Бро, сначала глянь на стили и выбери поинтересней!")
        if ses.state == 1:
            bot.send_message(message.chat.id, "Бро, я показывал тебе стили, выбери их, написав мне #1,"
                                              "#2 или #3!")
    else:
        if message.chat.type == 'private':
            photo_id = message.photo[1].file_id
            file_info = bot.get_file(photo_id)
            downloaded_file = bot.download_file(file_info.file_path)
            # сохранение
            content_img = datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + '.jpg'
            content_path = f"data/content/{content_img}"
            with open(content_path, 'wb') as new_file:
                new_file.write(downloaded_file)
            ses.content_img_path = content_img
            ses.state = 3
            bot.send_message(message.chat.id, "Принято бро!")


def __send_photos(chat_id, photo_paths, msgs=None):
    """
    send list of photos to chat with cover messages
    :param chat_id: chat u want to send
    :param photo_paths: list, each = path to photo
    :param msgs: list, each = cover msg for photo at photo_paths
    :return:
    """
    if msgs is None:
        for i in range(0, len(photo_paths)):
            __send_photo(chat_id=chat_id, photo_path=photo_paths[i])
    else:
        for i in range(0, len(photo_paths)):
            __send_photo(chat_id=chat_id, msg=msgs[i], photo_path=photo_paths[i])


def __send_photo(chat_id, photo_path, msg=None):
    """
    :param chat_id: chat u want to send
    :param photo_path: path to photo
    :param msg: cover msg
    :return:
    """
    ex_1 = open(photo_path, 'rb')
    if msg is not None:
        bot.send_message(chat_id, msg)
    bot.send_photo(chat_id, photo=ex_1)


# RUN
bot.polling(none_stop=True)
