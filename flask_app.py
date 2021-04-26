import os
from flask import Flask, request
import logging
import json
import random

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

# создаем словарь, в котором ключ — название города,
# а значение — массив, где перечислены id картинок,
# которые мы записали в прошлом пункте.

countries = {
    'москва': 'россия',
    'париж': 'франция',
    'нью-йорк': 'сша'

}

cities = {
    'москва': ['1540737/daa6e420d33102bf6947',
               '213044/7df73ae4cc715175059e'],
    'нью-йорк': ['1652229/728d5c86707054d4745f',
                 '1030494/aca7ed7acefde2606bdc'],
    'париж': ["1652229/f77136c2364eb90a3ea8",
              '3450494/aca7ed7acefde22341bdc']
}

# создаем словарь, где для каждого пользователя
# мы будем хранить его имя
sessionStorage = {}

pretty_flag = False

@app.route('/post', methods=['POST'])
def main():
    logging.info(f'Request: {request.json!r}')
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }
    handle_dialog(response, request.json)
    logging.info(f'Response: {response!r}')
    return json.dumps(response)


def handle_dialog(res, req):
    global pretty_flag
    user_id = req['session']['user_id']

    # если пользователь новый, то просим его представиться.
    if req['session']['new']:
        res['response']['text'] = '(8) Привет! Назови свое имя!'
        # создаем словарь в который в будущем положим имя пользователя
        sessionStorage[user_id] = {
            'first_name': None
        }
        return

    # если пользователь не новый, то попадаем сюда.
    # если поле имени пустое, то это говорит о том,
    # что пользователь еще не представился.
    if sessionStorage[user_id]['first_name'] is None:
        # в последнем его сообщение ищем имя.
        first_name = get_first_name(req)
        # если не нашли, то сообщаем пользователю что не расслышали.
        if first_name is None:
            res['response']['text'] = \
                'Не расслышала имя. Повтори, пожалуйста!'
        # если нашли, то приветствуем пользователя.
        # И спрашиваем какой город он хочет увидеть.
        else:
            sessionStorage[user_id]['first_name'] = first_name
            res['response'][
                'text'] = 'Приятно познакомиться, ' \
                          + first_name.title() \
                          + '. Я - Алиса. Хочешь угадать город?'

    # получаем варианты buttons из ключей нашего словаря cities
    # если мы знакомы с пользователем и он нам что-то написал,
    # то это говорит о том, что он уже говорит о городе,
    # что хочет увидеть.
    else:
        good = random.choice(['москва'])
        if 'да' in req["request"]['command']:

            res['response']['card'] = {}
            res['response']['card']['type'] = 'BigImage'
            res['response']['card']['title'] = \
                sessionStorage[user_id]['first_name'].title() + ' Угадай город'
            res['response']['card']['image_id'] = random.choice(cities[good])
            res['response']['text'] = 'Я угадал!'

        elif 'нет' in req["request"]['command']:
            res['response']['text'] = 'Как хочешь'
        elif not pretty_flag:
            city = req["request"]['command']
            # если этот город среди известных нам,
            # то показываем его (выбираем одну из двух картинок случайно)
            if good in city.lower():
                res['response']['text'] = 'Верно!, ' \
                                          + sessionStorage[user_id]['first_name'].title() \
                                          + ', Угадаешь страну?'
                pretty_flag = True
            # если не нашел, то отвечает пользователю
            # 'Первый раз слышу об этом городе.'
            else:
                res['response']['text'] = \
                    'Неверно. Попробуй еще разок!'
        elif countries[good] in req["request"]['command'] and pretty_flag:
                res['response']['text'] = 'Всё верно, ' + sessionStorage[user_id]['first_name'].title() + ', продолжим?))'
                res['response']['buttons'] = [
                    {
                        'title': 'Показать на карте',
                        'hide': True,
                        "url": f"https://yandex.ru/maps/?mode=search&text={good}"
                    },
                    {
                        'title': 'да',
                        'hide': True,
                    },
                    {
                        'title': 'нет',
                        'hide': True,
                    },
                ]
                pretty_flag = False
        else:
            res['response']['text'] = \
                'Неверно. ' + sessionStorage[user_id]['first_name'].title() + ', Попробуй еще разок!'
            # ищем город в сообщение от пользователя


def get_city(req):
    # перебираем именованные сущности
    for entity in req['request']['nlu']['entities']:
        # если тип YANDEX.GEO то пытаемся получить город(city),
        # если нет, то возвращаем None
        if entity['type'] == 'YANDEX.GEO':
            # возвращаем None, если не нашли сущности с типом YANDEX.GEO
            return entity['value'].get('city', None)


def get_first_name(req):
    # перебираем сущности
    for entity in req['request']['nlu']['entities']:
        # находим сущность с типом 'YANDEX.FIO'
        if entity['type'] == 'YANDEX.FIO':
            # Если есть сущность с ключом 'first_name',
            # то возвращаем ее значение.
            # Во всех остальных случаях возвращаем None.
            return entity['value'].get('first_name', None)


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

