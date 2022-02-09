import psycopg2
from config import host,user,password, db_name

connection = psycopg2.connect(
        host = host,
        user = user,
        password = password,
        database = db_name
)

class DbRequests:

        @classmethod
        def dishes_request(cls,rating_money):
                with connection.cursor() as cursor:
                        cursor.execute(
                                """SELECT name FROM dishes WHERE dishes.cost_rate = %s;""",
                                # Запрос на названия блюд, рейтинг которых совпадает с найденным.
                                (rating_money,))
                        found_name = cursor.fetchall()
                return found_name

        @classmethod
        def photo_id_reques(cls,choosen_dishes):
                with connection.cursor() as cursor:
                        cursor.execute(
                                """SELECT photo,id FROM dishes WHERE (dishes.name = %s);""",
                                # Запрос на фотографии и id выбранного блюда
                                (choosen_dishes,))

                        found_ph_id = cursor.fetchall()
                        return found_ph_id

        @classmethod
        def cost_time_reques(cls, choosen_dishes):
                with connection.cursor() as cursor:
                        cursor.execute(
                                """SELECT cost_rate,time_rate FROM dishes WHERE (dishes.name = %s);""",
                                (choosen_dishes,))
                        found_cost_time = cursor.fetchall()
                        return found_cost_time
        @classmethod
        def ingr_name_request(cls,choosen_dishes_id):
                with connection.cursor() as cursor:
                    cursor.execute(
                        """SELECT ingredients.name,dishes_ingredients.quantity,dishes_ingredients.units FROM dishes,ingredients
                        INNER JOIN dishes_ingredients ON ingredients.id = dishes_ingredients.ingredient_id
                        WHERE ((dish_id = %s) and (dishes.id = %s));""", # Запрос на названия ингредиентов
                        (choosen_dishes_id,choosen_dishes_id))

                    answer_1 = cursor.fetchall()
                    return answer_1