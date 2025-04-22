import json

import telebot
import webbrowser
from telebot import types
import sqlite3
import requests

bot = telebot.TeleBot('7739999442:AAEFDlwffuDSWJyRXoETemqa152TFsEs-qw') #connect to my bot
name = None
API = '5428a3d1c311cf25fb43d976b97abd7a'


@bot.message_handler(commands=['start'])
def welcome(message):
         bot.send_message(message.chat.id, f'<em>Hello, {message.from_user.first_name}</em>!', parse_mode='HTML') #prints hello with users name
         markup = types.ReplyKeyboardMarkup() #some ready options for testing
         btn1 = types.KeyboardButton('Open website')
         btn2 = types.KeyboardButton('Delete')
         btn3 = types.KeyboardButton('Change')
         markup.add(btn1)
         markup.row(btn2, btn3) #make a style for buttons
         with open('photo.png', 'rb') as photo: #also send a photo after welcome
            bot.send_photo(message.chat.id, photo, reply_markup=markup)
         bot.send_message(message.chat.id, "Choose the option:", reply_markup=markup)



@bot.message_handler(commands=['music'])
def send_music(message):
    music = open('music.mp3', 'rb') #open music file as a voice message
    bot.send_voice(message.chat.id, music)


@bot.message_handler(commands=['login'])
def log_in(message):
    conn = sqlite3.connect('telkiras.sql')
    cur = conn.cursor()

    cur.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, name VARCHAR(10), pass VARCHAR(10))')
    conn.commit()
    cur.close()
    conn.close()

    bot.send_message(message.chat.id, "Hello, let's log in you! Enter your name")
    bot.register_next_step_handler(message, user_name)

def user_name(message):
    global name
    name = message.text.strip()
    bot.send_message(message.chat.id, "Enter your password")
    bot.register_next_step_handler(message, user_pass)

def user_pass(message):
    password = message.text.strip()
    conn = sqlite3.connect('telkiras.sql')
    cur = conn.cursor()

    cur.execute('INSERT INTO users (name, pass) VALUES(?, ?)', (name, password))
    conn.commit()
    cur.close()
    conn.close()

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('The list of users', callback_data='users'))
    bot.send_message(message.chat.id, "User is registered.", reply_markup=markup)

@bot.callback_query_handler(func=lambda call:True)
def callback(call):
    if call.data == 'users':
        conn = sqlite3.connect('telkiras.sql')
        cur = conn.cursor()

        cur.execute('SELECT * FROM users')
        users = cur.fetchall()

        info = ''
        for el in users:
            info += f'Name: {el[1]}, Password: {el[2]}\n'

        cur.close()
        conn.close()

        bot.send_message(call.message.chat.id, info)
    elif call.data == 'delete':
        bot.delete_message(call.message.chat.id, call.message.message_id - 1)  # delete photo
        bot.send_message(call.message.chat.id, 'The photo is deleted')
    elif call.data == 'change':
        bot.edit_message_text('changing photo', call.message.chat.id, call.message.message_id)  # just send a message


@bot.message_handler(commands=['clean'])
def clear_users(message):
    conn = sqlite3.connect('telkiras.sql')
    cur = conn.cursor()

    cur.execute('DELETE FROM users')
    conn.commit()

    count = cur.rowcount

    cur.close()
    conn.close()

    bot.send_message(message.chat.id, f"{count} user(s) deleted from list.")

@bot.message_handler()
def answers(message): #answering
    if message.text == 'Open website':
     bot.send_message(message.chat.id, 'The website is open')
    elif message.text == 'Delete':
        bot.send_message(message.chat.id, 'The message is deleted')
    elif message.text == 'Change':
        bot.send_message(message.chat.id, 'The message is changed')
    elif message.text.lower() == 'id':
        bot.reply_to(message, f'ID: {message.from_user.id}')
    elif message.text == '/site':
        webbrowser.open('https://stackoverflow.com/')
    elif message.text == '/help':
        bot.send_message(message.chat.id, 'How can I help you?')
    elif message.text.lower() == 'bye':
        bot.send_message(message.chat.id, f'<em>Bye, {message.from_user.first_name}</em>!', parse_mode='HTML')
    elif message.text.lower() == 'hello' or message.text.lower() == 'hi':
        bot.send_message(message.chat.id, f'<em>Hello, {message.from_user.first_name}</em>!', parse_mode='HTML')
    elif message.text.lower() == 'weather':
        bot.send_message(message.chat.id, 'Enter your city: ')
        bot.register_next_step_handler(message, current_weather)
    else:
        bot.send_message(message.chat.id, 'Sorry, I don\'t understand.')

def current_weather(message):
    city = message.text.strip().lower()
    res = requests.get(f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API}&units=metric')
    if res.status_code == 200:
        data = json.loads(res.text)
        temp = data["main"]["temp"]
        bot.reply_to(message, f'The current weather is: {temp}')

        image = 'img.png' if temp <= 5.5 else 'img_1.png'
        file = open('./' + image, 'rb')
        bot.send_photo(message.chat.id, file)
    else:
        bot.reply_to(message, 'The city is not exist')



@bot.message_handler(content_types=['photo'])
def get_photo(message):
    markup = types.InlineKeyboardMarkup() #give some options after you send a photo
    btn1 = types.InlineKeyboardButton('Go to search', url='https://google.com')
    markup.row(btn1)
    btn2 = types.InlineKeyboardButton('Delete photo', callback_data='delete')
    btn3 = types.InlineKeyboardButton('Change photo', callback_data='change')
    markup.row(btn2, btn3)
    bot.reply_to(message, 'Nice photo!', reply_markup=markup) #reply to a photo before options


bot.polling(non_stop=True)