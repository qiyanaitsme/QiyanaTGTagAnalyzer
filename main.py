import telebot
from telebot import types

bot = telebot.TeleBot('сюда токен бота')

def analyze_nickname(nickname):
    info = {}
    for char in nickname:
        if char.isalnum():
            char_description = describe_letter(char)
            info[char] = char_description
    return info

def describe_letter(letter):
    descriptions = {
        'a': 'а (эй) английская строчная буква',
        'b': 'б (би) английская строчная буква',
        'c': 'с (си) английская строчная буква',
        'd': 'д (ди) английская строчная буква',
        'e': 'и (и) английская строчная буква',
        'f': 'эф (еф) английская строчная буква',
        'g': 'джи (ги) английская строчная буква',
        'h': 'эйч (эйч) английская строчная буква',
        'i': 'ай (ай) английская строчная буква',
        'j': 'джей (джей) английская строчная буква',
        'k': 'кей (кей) английская строчная буква',
        'l': 'эл (эл) английская строчная буква',
        'm': 'эм (эм) английская строчная буква',
        'n': 'эн (эн) английская строчная буква',
        'o': 'о (оу) английская строчная буква',
        'p': 'пи (пи) английская строчная буква',
        'q': 'кью (кью) английская строчная буква',
        'r': 'ар (ар) английская строчная буква',
        's': 'эс (эс) английская строчная буква',
        't': 'ти (ти) английская строчная буква',
        'u': 'ю (ю) английская строчная буква',
        'v': 'ви (ви) английская строчная буква',
        'w': 'дабл ю (дабл ю) английская строчная буква',
        'x': 'экс (экс) английская строчная буква',
        'y': 'вай (вай) английская строчная буква',
        'z': 'зед (зед) английская строчная буква',
        '0': 'ноль (ноль) цифра',
        '1': 'один (один) цифра',
        '2': 'два (два) цифра',
        '3': 'три (три) цифра',
        '4': 'четыре (четыре) цифра',
        '5': 'пять (пять) цифра',
        '6': 'шесть (шесть) цифра',
        '7': 'семь (семь) цифра',
        '8': 'восемь (восемь) цифра',
        '9': 'девять (девять) цифра',
    }
    return descriptions.get(letter.lower(), f'{letter} (неизвестный символ)')

def generate_tags(nickname):
    tags = [
        ''.join([char.lower() if char.isalpha() else '' for char in nickname]),
        ''.join([char.upper() if char.isalpha() else '' for char in nickname])
    ]
    return tags

def find_common_part(nickname1, nickname2):
    min_length = min(len(nickname1), len(nickname2))
    common_part = ""

    for i in range(min_length):
        if nickname1[i] == nickname2[i]:
            common_part += nickname1[i]
        else:
            break

    return common_part

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item = types.KeyboardButton("Анализ ника")
    markup.add(item)
    bot.send_message(message.chat.id, "Здравствуйте! Введите ник(и), который(ые) хотите проверить на наличие разных букв и цифр. Разделяйте ники запятыми или пробелами.", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def analyze_nicknames(message):
    if message.text == "Анализ ника":
        bot.reply_to(message, "Введите ник, который хотите проанализировать.")
        bot.register_next_step_handler(message, process_nickname)
    else:
        bot.reply_to(message, "Используйте кнопку 'Анализ ника' для анализа никнейма.")

def process_nickname(message):
    nicknames = message.text.split(', ') if ', ' in message.text else message.text.split()
    
    results = []
    for nickname in nicknames:
        analysis = analyze_nickname(nickname)
        if analysis:
            result = f"{nickname}:\n"
            for char, char_description in analysis.items():
                result += f"{char} - ({char_description})\n"
            tags = generate_tags(nickname)
            result += f"Варианты написания. Убедитесь какой ник правильный и только тогда отправляйте деньги.: {' '.join(tags)}"
            results.append(result)
        else:
            results.append(f"{nickname} не содержит английских букв и цифр. Точно тег телеграмма ввел?")
    
    response = "\n\n".join(results)
    bot.reply_to(message, response)

bot.polling()
