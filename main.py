import psycopg2
import telebot

from config import host,user,password, db_name
# Создаем экземпляр бота
bot = telebot.TeleBot('5260401916:AAGgSG5GO4Y2VFqc6EEeGPSppgk0W7wCJtg')

connection = psycopg2.connect(
        host = host,
        user = user,
        password = password,
        database = db_name
)

# Функция, обрабатывающая команду /start
@bot.message_handler(commands=["start"])
def start(m, res=False):
   bot.send_message(m.chat.id, 'Я на связи. Напиши мне что-нибудь )')

# Получение сообщений от юзера
@bot.message_handler(content_types=["text"])
def handle_text(message):
    user_money = message.text
    if user_money.isdigit():
        user_money = int(user_money)
        if user_money >50:
            # callback_data = 0;
            # start_markup = telebot.types.InlineKeyboardMarkup()
            # btn1 = telebot.types.InlineKeyboardButton('суп', callback_data=1)
            # start_markup.add(btn1)
            with connection.cursor() as cursor:
                cursor.execute(
                    """SELECT recipe_name,all_cost FROM recipe WHERE recipe.all_cost < %s;""",
                (user_money,))
                answer = cursor.fetchone()
                str_message = "Исходя из вашего бюджета вы можете приготовить: \n"
                while answer is not None:
                    str_message = str_message + answer[0] + " - " + str(answer[1]) + " рублей\n"
                    answer = cursor.fetchone()

            with connection.cursor() as cursor:
                cursor.execute(
                    """SELECT ingredient_name FROM ingredient,recipe WHERE (recipe.id = ingredient.ingr_id) and (recipe.all_cost < %s);""",
                (user_money,))
                answer_1 = cursor.fetchone()
                str_message = str_message + '\n' + "Для него нужно купить следующие ингредиенты " + '\n'
                while answer_1 is not None:
                    str_message = str_message + answer_1[0] + '\n'
                    answer_1 = cursor.fetchone()
                bot.send_message(message.from_user.id, str_message)

        else:
            bot.send_message(message.from_user.id,'У тебя слишком мало денег, чтобы позволить себе поесть. Стоит задуматься')
    else:
        bot.send_message(message.from_user.id, 'Вы должны ввести число')

#Запускаем бота
bot.polling(none_stop=True, interval=0)