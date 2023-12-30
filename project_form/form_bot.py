from telebot import *
from data_base import *
from question import Question

token = "6815594086:AAFmwexlJBjfNt8xinJKVhUz2613ND2opX0"
bot = TeleBot(token=token)

questions_list = ["Ты подвижный Камень?", "Как относишься к собратьям?", "Ты бы хотел стать человеком?"]
task_list = [["Канешн", "Сам такой", "Я камень"], ["Я потерял их в детстве...", "Я не КАМЕНЬЬЬ", "Положительно"],
             ["НЕТ", "Я и так человек", "Я КАМЕНЬЬЬ"]]
score_list = [2, 0, 3]


def markup_create(question):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for i in range(len(question.task)):
        markup.add(types.KeyboardButton(question.task[i]))
    return markup


def question_create_from_class(message, date):
    question = Question(questions_list[date["users"][message.chat.username]["index"]],
                        task_list[date["users"][message.chat.username]["index"]])
    return question


@bot.message_handler(commands=["start"])
def start(message):
    start_json_file(message)
    write_in_json_file_default_arg(message, "index", 0)
    write_in_json_file_default_arg(message, "score", 0)
    date = open_json_file_and_write()
    question = question_create_from_class(message, date)
    markup = markup_create(question)
    bot.send_message(chat_id=message.chat.id, text="Опрос на сколько ты Камень:", reply_markup=markup)
    msg = bot.reply_to(message, f"Первый вопрос:\n{question.question}")
    bot.register_next_step_handler(message, processing_user_response)


def processing_user_response(message):
    date = open_json_file_and_write()
    question = question_create_from_class(message, date)
    if message.text in question.task:
        date["users"][message.chat.username]["score"] += score_list[question.task.index(message.text)]
        date["users"][message.chat.username]["index"] += 1
        bot.send_message(chat_id=message.chat.id,
                         text="Ответ принят!",
                         reply_markup=types.ReplyKeyboardRemove())
        save_json_file_and_write(date)
    else:
        bot.send_message(chat_id=message.chat.id,
                         text="Вы написали фуфню, переходим к след. вопросу",
                         reply_markup=types.ReplyKeyboardRemove())
        date["users"][message.chat.username]["index"] += 1
        save_json_file_and_write(date)
    if date["users"][message.chat.username]["index"] == len(questions_list):
        bot.send_message(chat_id=message.chat.id,
                         text=f"Вы камень на: {round(date['users'][message.chat.username]['score'] / 9, 2) * 100}%")
        msg = bot.reply_to(message, "Напишите свой отзыв о данной анкете")
        bot.register_next_step_handler(msg, recording_reviews)
    else:
        question = question_create_from_class(message, date)
        markup = markup_create(question)
        bot.send_message(chat_id=message.chat.id, text="Следующий вопрос:", reply_markup=markup)
        msg = bot.reply_to(message, text=question.question)
        bot.register_next_step_handler(msg, processing_user_response)


def recording_reviews(message):
    write_in_json_file_default_arg(message, "reviews", message.text)
    bot.send_message(chat_id=message.chat.id,
                     text=f"Спасибо за отзыв!")
    bot.send_message(chat_id=message.chat.id,
                     text=f"Вы можете попробовать снова по команде /start")


@bot.message_handler(content_types=['text'])
def incorrect_input(message):
    bot.send_message(chat_id=message.chat.id,
                     text=f"Пройдите опрос по команде: /start")


bot.polling()
