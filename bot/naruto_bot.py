from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
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

def get_role_link(role):
    if role == "leader":
        return "https://t.me/Proudly_Tamizhan"
    elif role == "vc":
        return "https://t.me/yaseen"
    elif role == "owner":
        return "https://t.me/speedy208"
    else:
        return ""

@client.on_message(filters.command("start") & filters.private)
def start_handler(client, message):
    start_text = (
        "Hi! I am a bot to maintain deposits in Uzumaki clan.\n\n"
        "Use the following commands:\n"
        "/add {name} {currency} {amount} {transaction_type}\n"
        "/edit {name} {deposit/loan} {currency} {amount}\n"
        "/list\n"
        "/deposit\n"
        "/loan"
    )

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Leader", callback_data="leader"),
                InlineKeyboardButton("VC", callback_data="vc"),
                InlineKeyboardButton("Owner", callback_data="owner"),
            ]
        ]
    )

    message.reply_text(start_text, reply_markup=keyboard)

@client.on_callback_query()
def callback_query_handler(client, query):
    # Handle button callbacks here
    data = query.data
    user_id = query.from_user.id

    link = get_role_link(data)
    if link:
        message_text = f"Hello {data.capitalize()}! Click [here]({link}) for more information."
        client.send_message(user_id, message_text, disable_web_page_preview=True, parse_mode="markdown")

    # Answer the callback query to remove the "spinner" on the button
    query.answer()

@client.on_message(filters.command("add") & (filters.private | filters.group))
def add_handler(client, message):
    if is_bot_admin(client, message.chat.id, message.from_user.id):
        args = message.text.split()[1:]
        if len(args) == 4:
            name, currency, amount, transaction_type = args
            db.deposits.insert_one({'name': name, 'currency': currency, 'amount': amount, 'type': transaction_type})
            message.reply_text(f'Successfully added {amount} {currency} {transaction_type} for {name}')
        else:
            message.reply_text('Invalid command format. Use /add {name} {currency} {amount} {transaction_type}')
    else:
        message.reply_text('You are not authorized to use this command.')

@client.on_message(filters.command("edit") & (filters.private | filters.group))
def edit_handler(client, message):
    if is_bot_admin(client, message.chat.id, message.from_user.id):
        args = message.text.split()[1:]
        if len(args) == 4:
            name, transaction_type, currency, amount = args
            db.deposits.update_one({'name': name, 'type': transaction_type, 'currency': currency}, {'$set': {'amount': amount}})
            message.reply_text(f'Successfully edited {name} {transaction_type} {currency} to {amount}')
        else:
            message.reply_text('Invalid command format. Use /edit {name} {deposit/loan} {currency} {amount}')
    else:
        message.reply_text('You are not authorized to use this command.')

@client.on_message(filters.command("clear") & (filters.private | filters.group))
def clear_handler(client, message):
    if is_bot_admin(client, message.chat.id, message.from_user.id):
        db.deposits.delete_many({})
        message.reply_text('All records have been cleared.')
    else:
        message.reply_text('You are not authorized to use this command.')

@client.on_message(filters.command("list") & (filters.private | filters.group))
def list_handler(client, message):
    deposit_list = db.deposits.find()
    formatted_list = [f"{item['name']} {item['currency']} {item['amount']} {item['type']}" for item in deposit_list]
    message.reply_text('\n'.join(formatted_list) if formatted_list else 'No records found.')

@client.on_message(filters.command("deposit") & (filters.private | filters.group))
def deposit_list_handler(client, message):
    deposit_list = db.deposits.find({'type': 'deposit'})
    formatted_list = [f"{item['name']} {item['type']} {item['currency']} {item['amount']}" for item in deposit_list]
    message.reply_text('\n'.join(formatted_list) if formatted_list else 'No deposit records found.')

@client.on_message(filters.command("loan") & (filters.private | filters.group))
def loan_list_handler(client, message):
    loan_list = db.deposits.find({'type': 'loan'})
    formatted_list = [f"{item['name']} {item['type']} {item['currency']} {item['amount']}" for item in loan_list]
    message.reply_text('\n'.join(formatted_list) if formatted_list else 'No loan records found.')

def is_bot_admin(client, chat_id, user_id):
    chat_member = client.get_chat_member(chat_id=chat_id, user_id=user_id)
    return chat_member.status in ["administrator", "creator"]

client.run()
