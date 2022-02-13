import DbHelper
import telebot
from consts import ConstsString

from dotenv import load_dotenv
import os
from pathlib import Path
load_dotenv()
env_path = Path('.')/'.env'
load_dotenv(dotenv_path=env_path)

# Создаем экземпляр бота
bot = telebot.TeleBot(os.getenv("TOKEN"))


def check_rate(user_money):
    rating_money = 0
    if user_money <= 100:
        rating_money = 1
    elif user_money <= 200:
        rating_money = 2
    elif user_money <= 300:
        rating_money = 3
    elif user_money <= 400:
        rating_money = 4
    elif user_money <= 500:
        rating_money = 5
    else:
        rating_money = 5
    return rating_money

# Функция, обрабатывающая команду /start
@bot.message_handler(commands=["start"])
def start(m, res=False):
   bot.send_message(m.chat.id, ConstsString.meeting_text())

# Получение сообщений от юзера
@bot.message_handler(content_types=["text"])
def handle_text(message):
    user_money = message.text
    user_id = (message.from_user.id)
    user_fn = (message.from_user.first_name)
    user_lastn = (message.from_user.last_name)
    user_name = (message.from_user.username)


    print("Сообщение получено ")
    print("Имя " + str(user_fn) + " Фамилия " + str(user_lastn))
    print("С именем пользователя " + str(user_name))
    print("Захотел похавать на сумму " + str(user_money))
    print(' ')
    if user_money.isdigit():
        user_money = int(user_money)

        rating_money = check_rate(user_money) # Вычислим рейтинг исходя из бюджета юзера
        print(user_money)

        if user_money >= 50:
            found_name = DbHelper.DbRequests.dishes_request(rating_money)
            markup_reply = telebot.types.InlineKeyboardMarkup(row_width=2)
            str_message = ConstsString.opportunity_dishes()

            # keyboard = Keyboa.

            for i in range(len(found_name)):
                str_message = str_message + str(found_name[i][0])
                item_yes = telebot.types.InlineKeyboardButton(text=str(found_name[i][0]),callback_data=str(found_name[i][0]))
                markup_reply.add(item_yes)

            bot.send_message(message.chat.id, ConstsString.chose_recipe(), reply_markup=markup_reply)
        else:
            bot.send_message(message.from_user.id,ConstsString.low_money())
    else:
        bot.send_message(message.from_user.id, ConstsString.wrong_message())

@bot.callback_query_handler(func= lambda call: True)
def answer(call):
    choosen_dishes = call.data

    found_ph_id = DbHelper.DbRequests.photo_id_reques(choosen_dishes)

    choosen_dishes_id = found_ph_id[0][1]

    found_cost_time = DbHelper.DbRequests.cost_time_reques(choosen_dishes)

    rating_cost = int(found_cost_time[0][0])
    rating_time = int(found_cost_time[0][1])

    star_cost = 'Цена '
    star_time = 'Время '

    for i in range(rating_cost):
        star_cost = star_cost + "⭐️"

    for i in range(rating_time):
        star_time = star_time + "⭐️"

    answer_1 = DbHelper.DbRequests.ingr_name_request(choosen_dishes_id)
    str_message = choosen_dishes + '\n' + star_cost + '\n' + star_time + ConstsString.ingredients()
    for i in range(len(answer_1)):
        str_message = str_message + '✔️' + answer_1[i][0] + '\t' + str(answer_1[i][1]) + ' ' + str(answer_1[i][2]) + '\n'
    bot.send_photo(call.from_user.id,photo=found_ph_id[0][0],caption = str_message)

    check_list_button = []
    for i in range(len(answer_1)-6):
        check_list_button.append(answer_1[i][0])
        print(check_list_button[i])

    bot.answer_callback_query(callback_query_id=call.id)

#Запускаем бота
bot.polling(none_stop=True, interval=0)