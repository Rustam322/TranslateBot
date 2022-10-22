from telebot import TeleBot
from configs import *
from telebot.types import Message
from googletrans import Translator
bot = TeleBot(TOKEN)
from keyboards import generate_languages

@bot.message_handler(commands=['start'])
def command_start(message: Message):
    chat_id = message.chat.id
    bot.send_message(chat_id, 'Привет')
    get_lang_src(message)

def get_lang_src(message: Message):
    chat_id = message.chat.id
    msg = bot.send_message(chat_id, 'Выберите язык', reply_markup=generate_languages())
    bot.register_next_step_handler(msg, get_dest)

def get_dest(message: Message):
    chat_id = message.chat.id
    src = message.text
    msg = bot.send_message(chat_id, 'Выберите язык2', reply_markup=generate_languages())
    bot.register_next_step_handler(msg, get_text, src)

def get_text(message: Message, src):
    chat_id = message.chat.id
    dest = message.text
    msg = bot.send_message(chat_id, 'Выберите текст')
    bot.register_next_step_handler(msg, translate_func, src, dest)

def translate_func(message: Message, src, dest):
    chat_id = message.chat.id
    text = message.text
    husan = Translator()
    tr_text = husan.translate(text=text, dest=get_key(dest), src=get_key(src)).text
    bot.send_message(chat_id, tr_text)




bot.polling(none_stop=True)

