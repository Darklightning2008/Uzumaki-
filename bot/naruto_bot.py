from pyrogram import Client, filters
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

API_ID = os.getenv('TELEGRAM_API_ID')
API_HASH = os.getenv('TELEGRAM_API_HASH')
BOT_TOKEN = os.getenv('BOT_TOKEN')
MONGO_URI = os.getenv('MONGO_URI')

client = Client(
    'my_bot',
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
)

db_client = MongoClient(MONGO_URI)
db = db_client['naruto_game']

@client.on_message(filters.command("add") & filters.private)
def add_handler(client, message):
    args = message.text.split()[1:]
    if len(args) == 4:
        name, currency, amount, transaction_type = args
        db.deposits.insert_one({'name': name, 'currency': currency, 'amount': amount, 'type': transaction_type})
        message.reply_text(f'Successfully added {amount} {currency} {transaction_type} for {name}')
    else:
        message.reply_text('Invalid command format. Use /add {name} {currency} {amount} {transaction_type}')

@client.on_message(filters.command("edit") & filters.private)
def edit_handler(client, message):
    args = message.text.split()[1:]
    if len(args) == 3:
        name, currency, transaction_type = args
        db.deposits.update_one({'name': name, 'currency': currency}, {'$set': {'type': transaction_type}})
        message.reply_text(f'Successfully edited {name} {currency} to {transaction_type}')
    else:
        message.reply_text('Invalid command format. Use /edit {name} {currency} {transaction_type}')

@client.on_message(filters.command("list") & filters.private)
def list_handler(client, message):
    deposit_list = db.deposits.find()
    formatted_list = [f"{item['name']} {item['currency']} {item['amount']} {item['type']}" for item in deposit_list]
    message.reply_text('\n'.join(formatted_list) if formatted_list else 'No records found.')

client.run()
