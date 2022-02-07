import psycopg2
import telebot
import telebot.types

from config import host,user,password, db_name, TOKEN
# Создаем экземпляр бота
bot = telebot.TeleBot(TOKEN)
connection = psycopg2.connect(
        host = host,
        user = user,
        password = password,
        database = db_name
)

# Функция, обрабатывающая команду /start
@bot.message_handler(commands=["start"])
def start(m, res=False):
   bot.send_message(m.chat.id, 'Привет! Я помогу тебе не умереть с голоду! Напиши мне сумму, которую ты готов потратить на блюдо')

# Получение сообщений от юзера
@bot.message_handler(content_types=["text"])
def handle_text(message):
    user_money = message.text
    print(user_money)
    if user_money.isdigit():
        user_money = int(user_money)
        if user_money >50:
            with connection.cursor() as cursor:
                cursor.execute(
                    """SELECT recipe_name,all_cost FROM recipe WHERE recipe.all_cost < %s;""",
                (user_money,))
                answer = cursor.fetchone()
                i = int(0)
                markup_reply = telebot.types.InlineKeyboardMarkup()
                str_message = "Исходя из вашего бюджета вы можете приготовить: \n"
                while answer is not None:
                    str_message = str_message + answer[0] + " - " + str(answer[1]) + " рублей\n"
                    item_yes = telebot.types.InlineKeyboardButton(text= str(answer[0]), callback_data=str(answer[0]))
                    answer = cursor.fetchone()
                    markup_reply.add(item_yes)
                    i = i + 1
                bot.send_message(message.chat.id, "Выберите понравившийся рецепт", reply_markup=markup_reply)

        else:
            bot.send_message(message.from_user.id,'У тебя слишком мало денег, чтобы позволить себе поесть. Стоит задуматься')
    else:
        bot.send_message(message.from_user.id,'Вы должны ввести сумму, которую готовы потратить на блюдо')

@bot.callback_query_handler(func= lambda call: True)
def answer(call):
    choosen_dishes = call.data
    with connection.cursor() as cursor:
        cursor.execute(
            """SELECT ingredient_name FROM ingredient,recipe WHERE (recipe.id = ingredient.ingr_id) and (recipe.recipe_name = %s);""",
        (choosen_dishes,))
        answer_1 = cursor.fetchone()
        markup_reply2 = telebot.types.ReplyKeyboardMarkup()
        str_message = "Для приготовления выбранного блюда потребуются следующие игредиенты: \n"
        while answer_1 is not None:
            str_message = str_message + answer_1[0] + '\n'
            item_yes = telebot.types.KeyboardButton(str(answer_1[0]))
            markup_reply2.add(item_yes)
            answer_1 = cursor.fetchone()
    # bot.send_message(call.from_user.id, 'Чек лист', reply_markup=markup_reply2)
    bot.send_message(call.from_user.id, str_message)
    bot.answer_callback_query(callback_query_id=call.id)

#Запускаем бота
bot.polling(none_stop=True, interval=0)