import telebot
import psycopg2
from config import bot_token, config_database




bot = telebot.TeleBot(bot_token)


# Функция для запросов SQL:
def SQL_query(command, flag_commit=True):
    try:
        connect = psycopg2.connect(
            user=config_database["user"], 
            password=config_database["password"], 
            host=config_database["host"], 
            dbname=config_database["dbname"])
        with connect.cursor() as cursor:
            cursor.execute(command)
            if flag_commit:
                connect.commit()
            else:
                return cursor.fetchall()
    except Exception as e:
        print("[INFO]: Error while working with PostgreSQL", e)
    finally:
        if connect:
            connect.close()


# Функция добавление записей в базу данных:
def SQL_add(message):
    name_table = f'Table_{message.from_user.id}'
    SQL_query(f'INSERT INTO {name_table} (TASK) VALUES (\'{message.text.strip()}\')')
    bot.reply_to(message, "Задача добавлена в базу данных!")


# Функция создания таблицы при запуске telegram-бота:
@bot.message_handler(commands=['start'])
def start(message):
    name_table = f'Table_{message.from_user.id}'
    command = f'''CREATE TABLE IF NOT EXISTS {name_table} (
        ID serial primary key,
        TASK varchar(50)
        )
        '''
    SQL_query(command)


# Функция для команды добавления задач в базу данных:
@bot.message_handler(commands=['add'])
def add(message):
    bot.send_message(message.chat.id, "Введите название задачи:")
    bot.register_next_step_handler(message, SQL_add)
    

# Функция для команды вывода списка задач из базы данных:
@bot.message_handler(commands=['tsk'])
def tsk(message):
    name_table = f'Table_{message.from_user.id}'
    data = SQL_query(f"SELECT * FROM {name_table}", flag_commit=False)
    if len(data) > 0:
        info = "Cписок добавленных задач:\n\n"
        for d in data:
            info += f"{d[0]})\t\t{d[1]}\n"
        bot.send_message(message.chat.id, info)
    else:
        bot.send_message(message.chat.id, "Задачи ещё не были добавлены, таблица пустая!")



# Запуск программы:
if __name__ == "__main__":
    bot.polling(non_stop=True)