from telebot import types
import telebot
import sqlite3
from config import BOT_TOKEN

bot = telebot.TeleBot(BOT_TOKEN)
title = ''
text = ''
cost = 0
searching = []
id_for_delete = None
place = ''


@bot.message_handler(commands=['start'])
def start(message):
    conn = sqlite3.connect('bot_db.sql')
    cur = conn.cursor()
    cur.execute(
        'CREATE TABLE IF NOT EXISTS adverts '
        '(id INTEGER PRIMARY KEY,'
        ' title varchar(50),'
        ' text varchar(200),'
        ' cost int,'
        ' username integer)')

    conn.commit()

    cur.execute(
        'CREATE TABLE IF NOT EXISTS events'
        '(id INTEGER PRIMARY KEY,'
        ' title varchar(50),'
        ' text varchar(200),'
        ' cost int,'
        ' place integer,'
        ' username integer)')

    conn.commit()
    cur.close()
    conn.close()

    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton('Поиск объявления')
    btn2 = types.KeyboardButton('Создание объявления')
    btn3 = types.KeyboardButton('Мои объявления')
    btn4 = types.KeyboardButton('Удалить объявление')
    btn5 = types.KeyboardButton('Изменить объявление')
    btn6 = types.KeyboardButton('Поиск мероприятия')
    btn7 = types.KeyboardButton('Создание мероприятия')
    btn8 = types.KeyboardButton('Мои мероприятия')
    btn9 = types.KeyboardButton('Удалить мероприятие')
    btn10 = types.KeyboardButton('Изменить мероприятие')
    markup.row(btn1, btn2, btn3, btn4, btn5)
    markup.row(btn6, btn7, btn8, btn9, btn10)

    bot.send_message(message.chat.id, f'Здравствуй, {message.from_user.first_name}!',
                     reply_markup=markup)


@bot.message_handler(content_types=['text'])
def text_message(message):
    if message.text == 'Поиск объявления':
        bot.send_message(message.chat.id, 'Введите поисковое слово')
        bot.register_next_step_handler(message, search)

    elif message.text == 'Создание объявления':
        bot.send_message(message.chat.id, 'Введите заголовок объявления')
        bot.register_next_step_handler(message, title_func)

    elif message.text == 'Мои объявления':
        conn = sqlite3.connect('bot_db.sql')
        cur = conn.cursor()
        a = cur.execute(f'SELECT * FROM adverts WHERE username =='
                        f' "{message.from_user.username}"').fetchall()
        cur.close()
        conn.close()

        if a:
            bot.send_message(message.chat.id, 'Ваши объявления')
            conn = sqlite3.connect('bot_db.sql')
            cur = conn.cursor()
            a = cur.execute(f'SELECT * FROM adverts WHERE username =='
                            f' "{message.from_user.username}"').fetchall()

            cur.close()
            conn.close()
            for i in a:
                bot.send_message(message.chat.id,
                                 f'{i[1]} \n{i[2]} \nЦена: {i[3]} \nId: {i[0]} \n'
                                 f' <a href="https://t.me/{i[-1]}">Перейти</a>',
                                 parse_mode="HTML")

        else:
            bot.send_message(message.chat.id, 'У вас ещё нет объявлений')

    elif message.text == 'Удалить объявление':
        bot.send_message(message.chat.id, 'Введите id объявления')
        bot.register_next_step_handler(message, delete)

    elif message.text == 'Изменить объявление':
        bot.send_message(message.chat.id, 'Введите id объявления')
        bot.register_next_step_handler(message, change)

    elif message.text == 'Поиск мероприятия':
        bot.send_message(message.chat.id, 'Введите поисковое слово')
        bot.register_next_step_handler(message, search_event)

    elif message.text == 'Создание мероприятия':
        bot.send_message(message.chat.id, 'Введите заголовок объявления')
        bot.register_next_step_handler(message, title_func_event)

    elif message.text == 'Мои мероприятия':
        conn = sqlite3.connect('bot_db.sql')
        cur = conn.cursor()
        a = cur.execute(f'SELECT * FROM events WHERE username =='
                        f' "{message.from_user.username}"').fetchall()
        cur.close()
        conn.close()

        if a:
            bot.send_message(message.chat.id, 'Ваши мероприятия')
            conn = sqlite3.connect('bot_db.sql')
            cur = conn.cursor()
            a = cur.execute(f'SELECT * FROM events WHERE username =='
                            f' "{message.from_user.username}"').fetchall()

            cur.close()
            conn.close()
            for i in a:
                bot.send_message(message.chat.id,
                                 f'{i[1]} \n{i[2]} \nЦена: {i[3]} \n'
                                 f'Место: {i[4]}'
                                 f'Id: {i[0]} \n'
                                 f' <a href="https://t.me/{i[-1]}">Перейти</a>',
                                 parse_mode="HTML")

        else:
            bot.send_message(message.chat.id, 'У вас ещё нет мероприятий')

    elif message.text == 'Удалить мероприятие':
        bot.send_message(message.chat.id, 'Введите id мероприятия')
        bot.register_next_step_handler(message, delete_event)

    elif message.text == 'Изменить мероприятие':
        bot.send_message(message.chat.id, 'Введите id мероприятия')
        bot.register_next_step_handler(message, change_event)


def delete(message):
    conn = sqlite3.connect('bot_db.sql')
    cur = conn.cursor()

    a = cur.execute(f'SELECT username FROM adverts WHERE id =='
                    f' "{message.text}"').fetchone()
    if a:
        if a[0] == message.from_user.username:
            cur.execute(f'DELETE FROM adverts WHERE id =='
                        f'"{message.text}"')
            conn.commit()
            bot.send_message(message.chat.id, 'Объявление удалено')

        else:
            bot.send_message(message.chat.id, 'Эта не ваша статья')
    else:
        bot.send_message(message.chat.id, 'Эта не ваше объявление')

    cur.close()
    conn.close()


def change(message):
    global title, text, cost
    conn = sqlite3.connect('bot_db.sql')
    cur = conn.cursor()
    a = cur.execute(f'SELECT * FROM adverts WHERE id =='
                    f' "{message.text}"').fetchone()
    if a:
        if a[4] == message.from_user.username:
            bot.send_message(message.chat.id, 'Выберите что изменить:\n'
                                              'Введите заголовок, текст или цена')

            a = cur.execute(f'SELECT * FROM adverts WHERE id =='
                            f' "{message.text}"').fetchone()

            title = a[1]
            text = a[2]
            cost = a[3]

            cur.execute(f'DELETE FROM adverts WHERE id =='
                        f' "{message.text}"')
            conn.commit()

            bot.register_next_step_handler(message, change_change)
        else:
            bot.send_message(message.chat.id, 'Эта не ваше объявление')
    else:
        bot.send_message(message.chat.id, 'По такому id ничего не найдено')


def change_change(message):
    if message.text.lower() == 'заголовок':
        bot.send_message(message.chat.id, 'Введите новый заголовок')
        bot.register_next_step_handler(message, change_title)

    elif message.text.lower() == 'текст':
        bot.send_message(message.chat.id, 'Введите новый текст')
        bot.register_next_step_handler(message, change_text)

    elif message.text.lower() == 'цена':
        bot.send_message(message.chat.id, 'Введите новую цену')
        bot.register_next_step_handler(message, change_cost)


def change_title(message):
    conn = sqlite3.connect('bot_db.sql')
    cur = conn.cursor()

    cur.execute(
        f'INSERT INTO adverts (title, text, cost, username) '
        f'VALUES ("%s", "%s", "%s", "%s")'
        % (message.text, text, cost, message.from_user.username))

    conn.commit()

    cur.close()
    conn.close()
    bot.send_message(message.chat.id, 'Заголовок изменён')


def change_text(message):
    conn = sqlite3.connect('bot_db.sql')
    cur = conn.cursor()

    cur.execute(
        f'INSERT INTO adverts (title, text, cost, username) '
        f'VALUES ("%s", "%s", "%s", "%s")'
        % (title, message.text, cost, message.from_user.username))

    conn.commit()

    cur.close()
    conn.close()
    bot.send_message(message.chat.id, 'Текст изменён')


def change_cost(message):
    conn = sqlite3.connect('bot_db.sql')
    cur = conn.cursor()

    cur.execute(
        f'INSERT INTO adverts (title, text, cost, username) '
        f'VALUES ("%s", "%s", "%s", "%s")'
        % (title, text, message.text, message.from_user.username))

    conn.commit()

    cur.close()
    conn.close()
    bot.send_message(message.chat.id, 'Цена изменёна')


def title_func(message):
    global title
    if len(message.text) > 50:
        title = message.text[:49]

    else:
        title = message.text

    bot.send_message(message.chat.id, 'Введите текст')
    bot.register_next_step_handler(message, text_func)


def text_func(message):
    global text
    if len(message.text) > 50:
        text = message.text[:49]

    else:
        text = message.text

    bot.send_message(message.chat.id, 'Введите цену')
    bot.register_next_step_handler(message, cost_func)


def cost_func(message):
    try:
        int(message.text)

    except:
        bot.send_message(message.chat.id, 'Неверный тип данных')
        bot.register_next_step_handler(message, cost_func)
        return None

    cost = int(message.text)

    conn = sqlite3.connect('bot_db.sql')
    cur = conn.cursor()
    cur.execute(
        f'INSERT INTO adverts (title, text, cost, username) '
        f'VALUES ("%s", "%s", "%s", "%s")'
        % (title, text, cost, message.from_user.username))
    conn.commit()
    cur.close()
    conn.close()
    bot.send_message(message.chat.id, f'Объявление добавлено')


def search(message):
    global searching
    conn = sqlite3.connect('bot_db.sql')
    cur = conn.cursor()
    a = cur.execute(f'SELECT * FROM adverts WHERE title LIKE "%{message.text}%"').fetchall()

    cur.close()
    conn.close()
    for i in a:
        bot.send_message(message.chat.id, f'{i[1]}\n{i[2]}\n'
                                          f'Цена: {i[3]} \n '
                                          f'<a href="https://t.me/{i[-1]}">Написать</a>',
                         parse_mode="HTML")


def title_func_event(message):
    global title
    if len(message.text) > 50:
        title = message.text[:49]

    else:
        title = message.text

    bot.send_message(message.chat.id, 'Введите текст')
    bot.register_next_step_handler(message, text_func_event)


def text_func_event(message):
    global text
    if len(message.text) > 50:
        text = message.text[:49]

    else:
        text = message.text

    bot.send_message(message.chat.id, 'Введите цену')
    bot.register_next_step_handler(message, cost_func_event)


def cost_func_event(message):
    global cost
    try:
        int(message.text)

    except:
        bot.send_message(message.chat.id, 'Неверный тип данных')
        bot.register_next_step_handler(message, cost_func)
        return None

    cost = int(message.text)

    bot.send_message(message.chat.id, 'Введите место')
    bot.register_next_step_handler(message, place_func_event)


def place_func_event(message):
    conn = sqlite3.connect('bot_db.sql')
    cur = conn.cursor()

    cur.execute(
        f'INSERT INTO events (title, text, cost, place, username) '
        f'VALUES ("%s", "%s", "%s", "%s", "%s")'
        % (title, text, cost, message.text, message.from_user.username))

    conn.commit()

    cur.close()
    conn.close()
    bot.send_message(message.chat.id, f'Мероприятие добавлено')


def search_event(message):
    global searching
    conn = sqlite3.connect('bot_db.sql')
    cur = conn.cursor()
    a = cur.execute(f'SELECT * FROM events WHERE title LIKE "%{message.text}%"').fetchall()

    cur.close()
    conn.close()
    for i in a:
        bot.send_message(message.chat.id, f'{i[1]}\n'
                                          f'{i[2]}\n'
                                          f'Цена: {i[3]} \n'
                                          f'Время и дата: {i[4]}' 
                                          f'<a href="https://t.me/{i[-1]}">Написать</a>',
                         parse_mode="HTML")


def change_event(message):
    global title, text, cost, time
    conn = sqlite3.connect('bot_db.sql')
    cur = conn.cursor()
    a = cur.execute(f'SELECT * FROM events WHERE id =='
                    f' "{message.text}"').fetchone()
    if a:
        if a[4] == message.from_user.username:
            bot.send_message(message.chat.id, 'Выберите что изменить:\n'
                                              'Введите заголовок, текст или цена')

            a = cur.execute(f'SELECT * FROM events WHERE id =='
                            f' "{message.text}"').fetchone()

            title = a[1]
            text = a[2]
            cost = a[3]
            time = a[4]

            cur.execute(f'DELETE FROM events WHERE id =='
                        f' "{message.text}"')
            conn.commit()

            bot.register_next_step_handler(message, change_change)
        else:
            bot.send_message(message.chat.id, 'Эта не ваше объявление')
    else:
        bot.send_message(message.chat.id, 'По такому id ничего не найдено')


def change_change_event(message):
    if message.text.lower() == 'заголовок':
        bot.send_message(message.chat.id, 'Введите новый заголовок')
        bot.register_next_step_handler(message, change_title)

    elif message.text.lower() == 'текст':
        bot.send_message(message.chat.id, 'Введите новый текст')
        bot.register_next_step_handler(message, change_text)

    elif message.text.lower() == 'цена':
        bot.send_message(message.chat.id, 'Введите новую цену')
        bot.register_next_step_handler(message, change_cost)


def change_title_event(message):
    conn = sqlite3.connect('bot_db.sql')
    cur = conn.cursor()

    cur.execute(
        f'INSERT INTO events (title, text, cost, username) '
        f'VALUES ("%s", "%s", "%s", "%s")'
        % (message.text, text, cost, message.from_user.username))

    conn.commit()

    cur.close()
    conn.close()
    bot.send_message(message.chat.id, 'Заголовок изменён')


def change_text_event(message):
    conn = sqlite3.connect('bot_db.sql')
    cur = conn.cursor()

    cur.execute(
        f'INSERT INTO events (title, text, cost, place, username) '
        f'VALUES ("%s", "%s", "%s", "%s", "%s")'
        % (title, message.text, cost, place, message.from_user.username))

    conn.commit()

    cur.close()
    conn.close()
    bot.send_message(message.chat.id, 'Текст изменён')


def change_cost_event(message):
    conn = sqlite3.connect('bot_db.sql')
    cur = conn.cursor()

    cur.execute(
        f'INSERT INTO events (title, text, cost, place, username) '
        f'VALUES ("%s", "%s", "%s", "%s", "%s")'
        % (title, text, message.text, place, message.from_user.username))

    conn.commit()

    cur.close()
    conn.close()
    bot.send_message(message.chat.id, 'Цена изменёна')


def change_place_event(message):
    conn = sqlite3.connect('bot_db.sql')
    cur = conn.cursor()

    cur.execute(
        f'INSERT INTO events (title, text, cost, place, username) '
        f'VALUES ("%s", "%s", "%s", "%s", "%s")'
        % (title, text, cost, message.text, message.from_user.username))

    conn.commit()

    cur.close()
    conn.close()
    bot.send_message(message.chat.id, 'Место изменено')


def delete_event(message):
    conn = sqlite3.connect('bot_db.sql')
    cur = conn.cursor()

    a = cur.execute(f'SELECT username FROM events WHERE id =='
                    f' "{message.text}"').fetchone()
    if a:
        if a[0] == message.from_user.username:
            cur.execute(f'DELETE FROM events WHERE id =='
                        f'"{message.text}"')
            conn.commit()
            bot.send_message(message.chat.id, 'Мероприятие удалено')

        else:
            bot.send_message(message.chat.id, 'Это не ваше мероприятие')
    else:
        bot.send_message(message.chat.id, 'Это не ваше мероприятие')

    cur.close()
    conn.close()


bot.polling(none_stop=True)
