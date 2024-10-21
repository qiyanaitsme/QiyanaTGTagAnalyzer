import json
import logging
from pathlib import Path
from typing import Dict, List
from collections import Counter

import telebot
from telebot import types

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

config_path = Path('config.json')
with config_path.open('r', encoding='utf-8') as config_file:
    config = json.load(config_file)

bot = telebot.TeleBot(config['bot_token'])

USER_DATA_PATH = Path('user_data.json')


def load_descriptions() -> Dict[str, str]:
    """Загрузка описаний символов из JSON файла."""
    descriptions_path = Path('descriptions.json')
    with descriptions_path.open('r', encoding='utf-8') as desc_file:
        return json.load(desc_file)

DESCRIPTIONS = load_descriptions()

def load_user_data() -> Dict:
    """Загрузка данных пользователей."""
    if USER_DATA_PATH.exists():
        with USER_DATA_PATH.open('r') as f:
            return json.load(f)
    return {}

def save_user_data(data: Dict) -> None:
    """Сохранение данных пользователей."""
    with USER_DATA_PATH.open('w') as f:
        json.dump(data, f)

def analyze_nickname(nickname: str) -> Dict[str, str]:
    """Анализ никнейма и возврат информации о каждом символе."""
    return {char: DESCRIPTIONS.get(char.lower(), f'{char} (неизвестный символ)')
            for char in nickname if char.isalnum()}

def generate_tags(nickname: str) -> List[str]:
    """Генерация вариантов написания никнейма."""
    return [''.join(char.lower() if char.isalpha() else '' for char in nickname),
            ''.join(char.upper() if char.isalpha() else '' for char in nickname)]

def find_common_part(nickname1: str, nickname2: str) -> str:
    """Поиск общей части двух никнеймов."""
    return ''.join(char1 for char1, char2 in zip(nickname1, nickname2) if char1 == char2)

def create_keyboard() -> types.ReplyKeyboardMarkup:
    """Создание клавиатуры с кнопками."""
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton("Анализ ника"))
    keyboard.add(types.KeyboardButton("Моя статистика"))
    keyboard.add(types.KeyboardButton("Популярные символы"))
    return keyboard

@bot.message_handler(commands=['start'])
def start(message: types.Message) -> None:
    """Обработчик команды /start."""
    keyboard = create_keyboard()
    bot.send_message(message.chat.id, config['welcome_message'], reply_markup=keyboard)

@bot.message_handler(func=lambda message: True)
def handle_messages(message: types.Message) -> None:
    """Основной обработчик сообщений."""
    if message.text == "Анализ ника":
        bot.reply_to(message, "Введите ник, который хотите проанализировать.")
        bot.register_next_step_handler(message, process_nickname)
    elif message.text == "Моя статистика":
        show_user_statistics(message)
    elif message.text == "Популярные символы":
        show_popular_symbols(message)
    else:
        keyboard = create_keyboard()
        bot.reply_to(message, "Пожалуйста, используйте кнопки для взаимодействия с ботом.", reply_markup=keyboard)

def process_nickname(message: types.Message) -> None:
    """Обработка введенного никнейма."""
    nicknames = message.text.split(', ') if ', ' in message.text else message.text.split()
    results = []

    user_data = load_user_data()
    user_id = str(message.from_user.id)
    if user_id not in user_data:
        user_data[user_id] = {"analyzed_count": 0, "symbols": []}

    user_data[user_id]["analyzed_count"] += len(nicknames)

    for nickname in nicknames:
        analysis = analyze_nickname(nickname)
        if analysis:
            result = [f"{nickname}:"]
            result.extend(f"{char} - ({desc})" for char, desc in analysis.items())
            tags = generate_tags(nickname)
            result.append(f"Варианты написания: {' '.join(tags)}")
            results.append('\n'.join(result))
            user_data[user_id]["symbols"].extend(list(nickname.lower()))
        else:
            results.append(f"{nickname} не содержит английских букв и цифр. Проверьте правильность ввода.")

    save_user_data(user_data)

    response = "\n\n".join(results)
    keyboard = create_keyboard()
    bot.reply_to(message, response, reply_markup=keyboard)

def show_user_statistics(message: types.Message) -> None:
    """Показать статистику использования для пользователя."""
    user_data = load_user_data()
    user_id = str(message.from_user.id)
    if user_id in user_data:
        analyzed_count = user_data[user_id]["analyzed_count"]
        response = f"Вы проанализировали {analyzed_count} никнейм(ов)."
    else:
        response = "Вы еще не анализировали никнеймы."
    keyboard = create_keyboard()
    bot.reply_to(message, response, reply_markup=keyboard)

def show_popular_symbols(message: types.Message) -> None:
    """Показать самые популярные символы среди всех пользователей."""
    user_data = load_user_data()
    all_symbols = []
    for user in user_data.values():
        all_symbols.extend(user["symbols"])

    symbol_counts = Counter(all_symbols)
    top_symbols = symbol_counts.most_common(10)

    response = "Топ-10 самых популярных символов:\n"
    for symbol, count in top_symbols:
        response += f"{symbol}: {count}\n"

    keyboard = create_keyboard()
    bot.reply_to(message, response, reply_markup=keyboard)

if __name__ == '__main__':
    logger.info("Бот запущен")
    bot.polling(none_stop=True)
