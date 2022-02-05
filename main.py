# import logging
# import psycopg2
# from config import host,user,password, db_name
# user_money = ' '
# nominalo_1 = 1
# nominalo_5 = 5
# answer_1 = ''
# i = 0;
# warning = "DROP table"
# from aiogram import Bot, Dispatcher, executor,types
#
# #задаем уровень логов
# logging.basicConfig(level=logging.INFO)
#
# #инициализируем бота
# bot = Bot(token='5260401916:AAGgSG5GO4Y2VFqc6EEeGPSppgk0W7wCJtg')
# dp = Dispatcher(bot)
# connection = psycopg2.connect(
#         host = host,
#         user = user,
#         password = password,
#         database = db_name
# )
#
#
# connection.autocommit = True
# @dp.message_handler()
# async def echo(message: types.Message):
#     user_money = int(message.text)
#     if user_money >50:
#         with connection.cursor() as cursor:
#             cursor.execute(
#                 """SELECT recipe_name FROM recipe WHERE recipe.all_cost < %s;""",
#             (user_money,))
#             await bot.send_message(message.from_user.id, "Из расчета вашего бюджета я могу предложить рецепты: ")
#             answer = cursor.fetchone()
#             while answer is not None:
#                 await bot.send_message(message.from_user.id, answer[0])
#                 answer = cursor.fetchone()
#         with connection.cursor() as cursor:
#             cursor.execute(
#                 """SELECT ingredient_name FROM ingredient,recipe WHERE (recipe.id = ingredient.ingr_id) and (recipe.all_cost < %s);""",
#             (user_money,))
#             answer_1 = cursor.fetchone()
#             await bot.send_message(message.from_user.id, "Для него нужно купить следующие ингредиенты ")
#             while answer_1 is not None:
#                 await bot.send_message(message.from_user.id, answer_1[0])
#                 answer_1 = cursor.fetchone()
#     else:
#         await message.answer('У тебя слишком мало денег, чтобы позволить себе поесть. Стоит задуматься')
# #запускаем лонг поллинг
# if __name__ == '__main__':
#     executor.start_polling(dp, skip_updates=True)


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
    user_money = int(message.text)
    if user_money >50:
        with connection.cursor() as cursor:
            cursor.execute(
                """SELECT recipe_name FROM recipe WHERE recipe.all_cost < %s;""",
            (user_money,))
            bot.send_message(message.from_user.id, "Из расчета вашего бюджета я могу предложить рецепты: ")
            answer = cursor.fetchone()
            while answer is not None:
                bot.send_message(message.from_user.id, answer[0])
                answer = cursor.fetchone()
        with connection.cursor() as cursor:
            cursor.execute(
                """SELECT ingredient_name FROM ingredient,recipe WHERE (recipe.id = ingredient.ingr_id) and (recipe.all_cost < %s);""",
            (user_money,))
            answer_1 = cursor.fetchone()
            bot.send_message(message.from_user.id, "Для него нужно купить следующие ингредиенты ")
            while answer_1 is not None:
                bot.send_message(message.from_user.id, answer_1[0])
                answer_1 = cursor.fetchone()
    else:
        bot.send_message(message.from_user.id,'У тебя слишком мало денег, чтобы позволить себе поесть. Стоит задуматься')

#Запускаем бота
bot.polling(none_stop=True, interval=0)