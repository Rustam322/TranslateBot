from aiogram import Bot, Dispatcher, executor
# Bot - класс бота, объект которого мы создадим
# Dispatcher - следит за ботом
# executor - запуск и зацикливание бота
from aiogram.types import Message, ReplyKeyboardRemove
from configs import TOKEN, get_key
# Из диспетчера вытащим адрес на локальное хранилище(оперативку)
from aiogram.dispatcher import FSMContext
from aiogram.utils.markdown import link
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from keyboards import generate_languages
from googletrans import Translator
import sqlite3

storage = MemoryStorage()  # Открываем локальное хранилище
bot = Bot(token=TOKEN, parse_mode='HTML')


dp = Dispatcher(bot, storage=storage)


class GetLanguages(StatesGroup):
    src = State() # Язык с которого перевести
    dest = State() # Язык на который перевести
    text = State() # Текст который надо перевести


@dp.message_handler(commands=['start', 'history'])
async def command_start(message: Message):
    if message.text == '/start':

        await message.answer(f'Здравствуйте <a href="https://ru.stackoverflow.com/questions/1206919/%D0%92%D0%BD%D0%B5%D0%B4%D1%80%D0%B5%D0%BD%D0%B8%D0%B5-%D1%81%D1%81%D1%8B%D0%BB%D0%BA%D0%B8-%D0%B2-%D1%81%D0%BE%D0%BE%D0%B1%D1%89%D0%B5%D0%BD%D0%B8%D0%B5-telegram-bot">{message.from_user.full_name}</a>, я тестовый бот переводчик')
        await message.answer(f'''@{message.from_user.username}''')
        # Ща будет вопрос
        await start_lang(message)
    if message.text == '/history':
        await get_history(message)


async def get_history(message: Message):
    chat_id = message.chat.id
    db = sqlite3.connect('bot.db')
    cursor = db.cursor()
    cursor.execute('''
    SELECT src, dest, original_text, translated_text FROM translate
    WHERE telegram_id = ?;
    ''', (str(chat_id), ))
    result = cursor.fetchall()[::-1] # [(src, dest, o, t), ()]
    db.close()
    for src, dest, original_text, translated_text in result[:10]:
        await message.answer(f'''Вы переводили с {src}
На {dest}
Текст: {original_text}
Бот перевел: {translated_text}
Для перевода нажмите /start''')


async def start_lang(message: Message, state=None):
    await GetLanguages.src.set() # Начинаем вопрос
    await message.answer('Укажите язык с которого хотите перевести',
                         reply_markup=generate_languages())

@dp.message_handler(content_types=['text'], state=GetLanguages.src) #Ловим ответ на 1 вопрос
async def get_src_ask_dest(message: Message, state: FSMContext):
    if message.text in ['/start', '/history']:
        await command_start(message)
    else:
        async with state.proxy() as data: # Открываем оперативку как data
            data['src'] = message.text
        #await GetLanguages.dest.set()
        await GetLanguages.next()
        await message.answer('Выберите язык на который хотите перевести: ',
                             reply_markup=generate_languages())

# Отловить ответ на 2 вопрос и сохранить в оперативку

@dp.message_handler(content_types=['text'], state=GetLanguages.dest)
async def get_dest_ask_text(message:Message, state: FSMContext):
    if message.text in ['/start', '/history']:
        await command_start(message)
    else:
        async with state.proxy() as data:
            data['dest'] = message.text

        await GetLanguages.next()
        await message.answer('Введите текст, который хотите перевести: ',
                             reply_markup=ReplyKeyboardRemove())

@dp.message_handler(content_types=['text'], state=GetLanguages.text)
async def get_text_translate(message: Message, state: FSMContext):
    if message.text in ['/start', '/history']:
        await command_start(message)
    else:
        async with state.proxy() as data:
            data['text'] = message.text
        src = data['src']
        dest = data['dest']
        text = data['text']
        await message.answer(f'{src}, {dest}, {text}')
        husan = Translator()
        translated_text = husan.translate(text=text, dest=get_key(dest), src=get_key(src)).text
        await message.answer(translated_text)
        db = sqlite3.connect('bot.db')
        cursor = db.cursor()
        cursor.execute('''
        INSERT INTO translate(telegram_id, src, dest, original_text, translated_text)
        VALUES (?,?,?,?,?)
        ''', (message.chat.id, src, dest, text, translated_text))
        db.commit()
        db.close()
        await state.finish()
        await start_lang(message)



executor.start_polling(dp)