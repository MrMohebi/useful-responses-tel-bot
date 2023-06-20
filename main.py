import requests
from bs4 import BeautifulSoup
from uuid import uuid4
from telegram import InlineQueryResultArticle, InputTextMessageContent, Update
from telegram.ext import Application, ContextTypes, InlineQueryHandler
import threading
from time import sleep
from dotenv import load_dotenv
import os

load_dotenv()

MESSAGES = {}

CHANNEL = os.getenv('CHANNEL_USERNAME')
TOKEN = os.getenv('TELEGRAM_TOKEN')

def get_message_from_telegram(msg_id):
    global CHANNEL
    url = f'https://t.me/{CHANNEL}/{msg_id}'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    meta_tag = soup.find('meta', {'name': 'twitter:description'})
    return meta_tag.get('content')


def get_channel_messages_interval(max_search):
    while True:
        print("getting messages...")
        global MESSAGES
        for i in range(max_search):
            msg = get_message_from_telegram(i)
            if "You can view and join" not in msg:
                MESSAGES[i] = msg
        print("got messages: ")
        print(MESSAGES)
        sleep(120)


async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.inline_query.query

    if not query:
        return

    results = []
    try:
        if query.isnumeric():
            results.append(InlineQueryResultArticle(
                id=str(uuid4()),
                title=MESSAGES[int(query)].replace('\n', '') + f'({query})',
                input_message_content=InputTextMessageContent(MESSAGES[int(query)]),
            ))
        elif query.isalpha():
            searchIn = {k: v for k, v in MESSAGES.items() if query in v}
            for key in searchIn.keys():
                results.append(InlineQueryResultArticle(
                    id=str(uuid4()),
                    title=searchIn[key].replace('\n', '') + f'({key})',
                    input_message_content=InputTextMessageContent(searchIn[key]),
                ))

    except Exception as e:
        print("Err: ")
        print(e)

    await update.inline_query.answer(results)


thread_channel_messages = threading.Thread(target=get_channel_messages_interval, args=(10,))
thread_channel_messages.daemon = True
thread_channel_messages.start()

app = Application.builder().token(TOKEN).build()

app.add_handler(InlineQueryHandler(inline_query))

print("starting Bot...")
app.run_polling()
