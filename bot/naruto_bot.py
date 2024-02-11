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

# Sudo users who can use /add, /edit, /clear
sudo_users = set()

# Owners who can add sudo users
owners = {6916220465}  # Add the specified user ID to the owners set

def get_role_link(role):
    if role == "leader":
        return "https://t.me/Proudly_Tamizhan"
    elif role == "vc":
        return "https://t.me/yaseen_yasir"
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

    # Send a welcome message to the user
    welcome_message = "Welcome! The bot has started. Use /start to see available commands."
    client.send_message(message.chat.id, welcome_message)

@client.on_message(filters.command("addsudo") & filters.private)
def addsudo_handler(client, message):
    if is_owner(message.from_user.id):
        user_id = message.text.split()[1]
        sudo_users.add(int(user_id))
        message.reply_text(f'Successfully added user with ID {user_id} to sudo users.')
    else:
        message.reply_text('You are not authorized to use this command.')

@client.on_message(filters.command("addowner") & filters.private)
def addowner_handler(client, message):
    if is_owner(message.from_user.id):
        user_id = message.text.split()[1]
        owners.add(int(user_id))
        message.reply_text(f'Successfully added user with ID {user_id} to owners.')
    else:
        message.reply_text('You are not authorized to use this command.')

@client.on_message(filters.command("add") & (filters.private | filters.group))
def add_handler(client, message):
    if is_sudo_user(message.from_user.id):
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
    if is_sudo_user(message.from_user.id):
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
    if is_sudo_user(message.from_user.id):
        db.deposits.delete_many({})
        message.reply_text('All records have been cleared.')
    else:
        message.reply_text('You are not authorized to use this command.')

@client.on_message(filters.command("list") & (filters.private | filters.group))
def list_handler(client, message):
    deposit_list = db.deposits.find({'type': 'deposit'})
    loan_list = db.deposits.find({'type': 'loan'})

    deposit_formatted_list = [f"{item['name']} {item['type']} {item['currency']} {item['amount']}" for item in deposit_list]
    loan_formatted_list = [f"{item['name']} {item['type']} {item['currency']} {item['amount']}" for item in loan_list]

    deposit_text = '\n'.join(deposit_formatted_list) if deposit_formatted_list else 'No deposit records found.'
    loan_text = '\n'.join(loan_formatted_list) if loan_formatted_list else 'No loan records found.'

    message.reply_text(f"Deposit records:\n{deposit_text}\n\nLoan records:\n{loan_text}")

def is_owner(user_id):
    return user_id in owners

def is_sudo_user(user_id):
    return user_id in sudo_users

client.run()
