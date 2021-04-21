# импортируем библиотеки
from flask import Flask, request
import logging
import os

import json

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

# sessionStorage[user_id] = {'suggests': ["Не хочу.", "Не буду.", "Отстань!" ]}
sessionStorage = {}


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

    handle_dialog(request.json, response)

    logging.info(f'Response:  {response!r}')

    return json.dumps(response)


TITLE = 'слона'


def handle_dialog(req, res):
    global TITLE
    k = 0
    user_id = req['session']['user_id']

    if req['session']['new']:
        sessionStorage[user_id] = {
            'suggests': [
                "Не хочу.",
                "Не буду.",
                "Отстань!",
            ]
        }
        res['response']['text'] = f'Привет! Купи {TITLE}!'
        res['response']['buttons'] = get_suggests(user_id)
        return

    # if req['request']['original_utterance'].lower() in [
    #     'ладно',
    #     'куплю',
    #     'покупаю',
    #     'хорошо'
    # ]:
    if any(i in req['request']['original_utterance'].lower() for i in [
        'ладно',
        'куплю',
        'покупаю',
        'хорошо'
    ]) and 'не' not in req['request']['original_utterance'].lower():
        if k == 1:
            res['response']['text'] = f'{TITLE} можно найти на Яндекс.Маркете!'
            res['response']['end_session'] = True
        else:
            k += 1
            res['response']['text'] = f'{TITLE} можно найти на Яндекс.Маркете!'
            TITLE = 'кролика'
            res['response']['text'] = f'Привет! Купи {TITLE}!'
            res['response']['buttons'] = get_suggests(user_id)
        return

    # Если нет, то убеждаем его купить слона!
    res['response']['text'] = \
        f"Все говорят '{req['request']['original_utterance']}', а ты купи {TITLE}!"
    res['response']['buttons'] = get_suggests(user_id)


# Функция возвращает две подсказки для ответа.
def get_suggests(user_id):
    session = sessionStorage[user_id]

    suggests = [
        {'title': suggest, 'hide': True}
        for suggest in session['suggests'][:2]
    ]

    # Убираем первую подсказку, чтобы подсказки менялись каждый раз.
    session['suggests'] = session['suggests'][1:]
    sessionStorage[user_id] = session

    if len(suggests) < 2:
        suggests.append({
            "title": "Ладно",
            "hide": True
        })

    return suggests


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
