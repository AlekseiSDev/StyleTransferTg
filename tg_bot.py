import telebot as tb
import config
import random
import model

Model = model.Model()
bot = tb.TeleBot(config.TOKEN)


@bot.message_handler(commands=['start'])
def welcome(message):
    """

    :param message:
    :return:
    """

    # приветствие и 1й пример
    msg = f"""Добро пожаловать, {message.from_user.first_name}!\nЯ - <b>{bot.get_me().first_name}</b>, бот, позволяющий каждому почувствовать себя художником. \n """
    bot.send_message(message.chat.id, msg, parse_mode='html')
    __send_photo(chat_id=message.chat.id, photo_path='data/examples/1.jpg',
                 msg="Смотри какие клевые штуки мы с тобой можем делать!")

    # keyboard
    markup = tb.types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1, item2 = tb.types.KeyboardButton("Кул, хочу также с моими фото!"), tb.types.KeyboardButton("Не, отстой")
    markup.add(item1, item2)
    bot.send_message(message.chat.id, "Ну че, похудожничаем чутка?", parse_mode='html', reply_markup=markup)


@bot.message_handler(content_types=['text'])
def handle_message(message):
    """
    handler of all messages
    :param message:
    :return:
    """
    if message.chat.type == 'private':
        # TODO: разные варианты диалога
        if message.text == 'Кул, хочу также с моими фото!':
            bot.send_message(message.chat.id, "Ща намутим, бро! Скинь свою фотку для обработки.")
            # TODO: отправить фотку
        elif message.text == 'Не, отстой':
            bot.send_message(message.chat.id, "Художника обидить каждый может!")
        else:
            bot.send_message(message.chat.id, 'Я и не знаю что ответить на такое..')


@bot.message_handler(content_types=['photo'])
def __handle_get_photo(message):
    if message.chat.type == 'private':
        # TODO: условия, что это после прошлого диалога
        msg_photo = message.photo
        photo_id = message.photo[1].file_id
        # file_info = bot.get_file(message.photo.file_id)
        file_info = bot.get_file(photo_id)
        downloaded_file = bot.download_file(file_info.file_path)
        # сохранение
        # TODO: не переписывать же каждый раз
        content_path = 'data/content/1.jpg'
        style_path = 'data/style/11.jpg'
        out_path = 'data/out/1.jpg'

        with open(content_path, 'wb') as new_file:
            new_file.write(downloaded_file)
        # ответ
        bot.send_message(message.chat.id, "Окей бро, обрабатываю!")

        Model.inference(content_path=content_path, style_path=style_path, out_path=out_path)
        bot.send_message(message.chat.id, "Смотри, что у нас вышло!")
        __send_photo(chat_id=message.chat.id, photo_path=out_path, msg="Кул?!")


def __send_photo(chat_id, msg, photo_path):
    ex_1 = open(photo_path, 'rb')
    bot.send_message(chat_id, msg)
    bot.send_photo(chat_id, photo=ex_1)


# TODO: шо это и нужно ли
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    try:
        if call.message:
            if call.data == 'good':
                bot.send_message(call.message.chat.id, 'Вот и отличненько 😊')
            elif call.data == 'bad':
                bot.send_message(call.message.chat.id, 'Бывает 😢')

            # remove inline buttons
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="😊 Как дела?",
                                  reply_markup=None)

            # show alert
            bot.answer_callback_query(callback_query_id=call.id, show_alert=False,
                                      text="ЭТО ТЕСТОВОЕ УВЕДОМЛЕНИЕ!!11")

    except Exception as e:
        print(repr(e))


# RUN
bot.polling(none_stop=True)
