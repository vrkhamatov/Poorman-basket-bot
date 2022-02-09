import psycopg2
import telebot
from consts import ConstsString

from config import host,user,password, db_name, TOKEN
# Создаем экземпляр бота
bot = telebot.TeleBot(TOKEN)
connection = psycopg2.connect(
        host = host,
        user = user,
        password = password,
        database = db_name
)

def check_rate(user_money):
    rating_money = 0
    if user_money <= 200:
        rating_money = 1
    elif user_money <= 300:
        rating_money = 2
    elif user_money <= 400:
        rating_money = 3
    elif user_money <= 500:
        rating_money = 4
    elif user_money <= 800:
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
    print(user_money)
    if user_money.isdigit():
        user_money = int(user_money)

        rating_money = check_rate(user_money) # Вычислим рейтинг исходя из бюджета юзера
        print(user_money)

        if user_money > 199:
            with connection.cursor() as cursor:
                cursor.execute(
                    """SELECT name FROM dishes WHERE dishes.cost_rate = %s;""", # Запрос на названия блюд, рейтинг которых совпадает с найденным.
                (rating_money,))
                found_name = cursor.fetchone()
                i = 0
                markup_reply = telebot.types.InlineKeyboardMarkup()
                str_message = ConstsString.opportunity_dishes()
                
                while found_name is not None:
                    str_message = str_message + found_name[0]
                    item_yes = telebot.types.InlineKeyboardButton(text= str(found_name[0]), callback_data=str(found_name[0]))
                    found_name = cursor.fetchone()
                    markup_reply.add(item_yes)
                    i = i + 1
                    
                bot.send_message(message.chat.id, ConstsString.chose_recipe(), reply_markup=markup_reply)
        else:
            bot.send_message(message.from_user.id,ConstsString.low_money())
    else:
        bot.send_message(message.from_user.id, ConstsString.wrong_message())

@bot.callback_query_handler(func= lambda call: True)
def answer(call):
    choosen_dishes = call.data
    with connection.cursor() as cursor:
        
        cursor.execute(
            """SELECT photo,id FROM dishes WHERE (dishes.name = %s);""", # Запрос на фотографии и id выбранного блюда
            (choosen_dishes,))
        
        found_ph_id = cursor.fetchone()
        choosen_dishes_id = int(found_ph_id[1])

        cursor.execute(
            """SELECT cost_rate,time_rate FROM dishes WHERE (dishes.name = %s);""",
            (choosen_dishes,))
        found_cost_time = cursor.fetchone()

        rating_cost = int(found_cost_time[0])
        rating_time = int(found_cost_time[1])

        star_cost = 'Цена '
        star_time = 'Время '

        for i in range(rating_cost):
            star_cost = star_cost + "⭐️"

        for i in range(rating_time):
            star_time = star_time + "⭐️"

    with connection.cursor() as cursor:
        cursor.execute(
            """SELECT ingredients.name,dishes.id,dishes_ingredients.quantity,dishes_ingredients.units FROM dishes,ingredients 
            INNER JOIN dishes_ingredients ON ingredients.id = dishes_ingredients.ingredient_id 
            WHERE ((dish_id = %s) and (dishes.id = %s));""", # Запрос на названия ингредиентов
            (choosen_dishes_id,choosen_dishes_id))

        answer_1 = cursor.fetchone()
        markup_reply2 = telebot.types.ReplyKeyboardMarkup()
        str_message = choosen_dishes + '\n' + star_cost + '\n' + star_time + ConstsString.ingredients()

        while answer_1 is not None:
            str_message = str_message + '✔️' + answer_1[0] + '\t' + str(answer_1[2]) + ' ' + str(answer_1[3]) + '\n'
            item_yes = telebot.types.KeyboardButton(str(answer_1[0]))
            markup_reply2.add(item_yes)
            answer_1 = cursor.fetchone()

        bot.send_photo(call.from_user.id,photo=found_ph_id[0],caption = str_message)
    bot.answer_callback_query(callback_query_id=call.id)

#Запускаем бота
bot.polling(none_stop=True, interval=0)