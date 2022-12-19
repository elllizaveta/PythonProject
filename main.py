import json

import requests
import telebot

currate_api_key = "36e01b28ca567ea991fe8d0c355888b7"
bot_api_key = "5854439261:AAEUISDiHpFPRr6syefDWfomfiYu5AVJkfs"
bot = telebot.TeleBot(bot_api_key)
users = dict()
valute_pairs = dict(json.loads(open("valute_pairs.json", 'r').read()))


def init_users():
    global users
    try:
        users = dict(json.loads(open("users.json", 'r', encoding="utf-8").read()))
    except:
        users = dict()


def save_users():
    open("users.json", 'w', encoding="utf-8").write(json.dumps(users, ensure_ascii=False))


def get_user_by_id(user_id):
    return dict[user_id]


def add_user(user_id):
    users[user_id] = {
        "valutes": {},
        "waiting_for": "None"
    }


def get_sum(user_id):
    user = users[user_id]
    valsstr = ','.join([el["pair"] for el in valute_pairs.values()])
    currencies = json.loads(requests.get(f"https://currate.ru/api/?get=rates&pairs={valsstr}&key={currate_api_key}").text)[
        "data"]
    print(currencies)
    user_sum = 0.0
    for valute in user["valutes"]:
        if valute_pairs[valute]["reversed_pair"]:
            user_sum += user["valutes"][valute] \
                        / float(currencies[valute_pairs[valute]["pair"]])
        else:
            user_sum += user["valutes"][valute] \
                        * float(currencies[valute_pairs[valute]["pair"]])
    return user_sum


def add_valute(user_id, valute, count):
    users[user_id]["valutes"][valute] = count


def del_valute(user_id, valute):
    users[user_id]["valutes"].pop(valute)


@bot.message_handler(commands=["start", "delete_all"])
def reply(message: telebot.types.Message):
    add_user(str(message.from_user.id))
    save_users()
    bot.reply_to(message, "Ваш портфель пуст")
    bot.send_message(message.from_user.id, "Чтобы добавить валюту, отправьте\n/" + "\n/".join(valute_pairs))


@bot.message_handler(commands=["add_valute"])
def user_adds_value(message):
    bot.send_message(message.from_user.id, "Чтобы добавить валюту, отправьте\n/" + "\n/".join(valute_pairs))


@bot.message_handler(commands=["delete_valute"])
def what_val_del(message: telebot.types.Message):
    user = users[str(message.from_user.id)]
    user["waiting_for"] = "del_val"
    bot.send_message(message.from_user.id, "Какую валюту вы хотите удалить?\n/" + "\n/".join(user["valutes"]))


@bot.message_handler(commands=["moy_portfel"])
def send_case(message: telebot.types.Message):
    user = users[str(message.from_user.id)]
    if len(dict(user["valutes"])) == 0:
        bot.reply_to(message, "Ваш портфель пуст")
    res_str = ""
    for key in user["valutes"]:
        val = user["valutes"][key]
        res_str += f"{key} : {val}\n"
    bot.send_message(message.from_user.id, res_str)


@bot.message_handler(commands=["skokadenyak"])
def get_user_sum(message: telebot.types.Message):
    bot.send_message(message.from_user.id,
                     f"Ваш портфель стоит {get_sum(str(message.from_user.id)) :.2f}руб.")


@bot.message_handler(func=lambda message: message.text.startswith("/"))
def add_val(message: telebot.types.Message):
    user = users[str(message.from_user.id)]
    if message.text[1::] not in valute_pairs.keys():
        bot.reply_to(message, "Ты че, дурак? Добавь нормальную команду!!! Из списка плиииз")
        return
    if user["waiting_for"] == "del_val":
        del_valute(str(message.from_user.id), message.text[1::])
        bot.reply_to(message, "Успешно удалено")
        return
    user = users[str(message.from_user.id)]
    user["waiting_for"] = message.text[1::]
    bot.reply_to(message, f"Сколько у вас {message.text[1::]}")


@bot.message_handler(content_types=['text'])
def set_val(message: telebot.types.Message):
    user = users[str(message.from_user.id)]
    if user['waiting_for'] == 'None':
        bot.reply_to(message, "Слэш то хоть поставь, я ж глупый - без слэша не понимаю\n пысы. слэш - это палка наклонная")
    else:
        message_user = message.text.replace(',', '.')
        if message_user.isdigit():
            count = float(message.text.replace(',', '.'))
            add_valute(str(message.from_user.id), user["waiting_for"], count)
            user["waiting_for"] = "None"
            save_users()
            bot.reply_to(message, "Успешно добавлено")
        else:
            bot.reply_to(message, "чел ты\nпопросили же цифру нормально")

def json_lol():
    a = dict(json.loads(open("valute_pairs.json", "r").read()))
    for key in a.keys():
        a[key]["valute"] = key

    open("valute_pairs.json", "w").write(json.dumps(a, ensure_ascii=False))


if __name__ == "__main__":
    init_users()
    bot.infinity_polling()
    save_users()
