# naruto_bot.py

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
    'naruto_bot',
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
)

db_client = MongoClient(MONGO_URI)
db = db_client['naruto_game']

sudo_users = {6916220465, 1234567890}

def is_sudo_user(_, message):
    user_id = message.from_user.id
    return user_id in sudo_users

def save_sudo_users(users):
    pass

@client.on_message(filters.command("add_deposit") & is_sudo_user)
def add_deposit_handler(client, message):
    args = message.text.split()[1:]
    if len(args) == 3:
        name, currency, amount = args
        db.deposits.insert_one({'name': name, 'type': 'deposit', 'currency': currency, 'amount': int(amount)})
        message.reply_text(f'Successfully added deposit for {name}. Amount: {amount} {currency}')
    else:
        message.reply_text('Invalid command format. Use /add_deposit {name} {gems/tokens/coins} {amount}')

@client.on_message(filters.command("add_loan") & is_sudo_user)
def add_loan_handler(client, message):
    args = message.text.split()[1:]
    if len(args) == 3:
        name, currency, amount = args
        db.deposits.insert_one({'name': name, 'type': 'loan', 'currency': currency, 'amount': int(amount)})
        message.reply_text(f'Successfully added loan for {name}. Amount: {amount} {currency}')
    else:
        message.reply_text('Invalid command format. Use /add_loan {name} {gems/tokens/coins} {amount}')

@client.on_message(filters.command("edit") & is_sudo_user)
def edit_handler(client, message):
    args = message.text.split()[1:]
    if len(args) == 4:
        name, record_type, currency, amount = args
        valid_record_types = ['deposit', 'loan']
        if record_type in valid_record_types:
            filter_condition = {'name': name, 'type': record_type}
            update_data = {'$set': {'amount': int(amount)}}
            db.deposits.update_one(filter_condition, update_data)
            message.reply_text(f'Successfully edited {record_type} for {name}. New amount: {amount}')
        else:
            message.reply_text(f'Invalid record type. Use /edit {name} {{"deposit" or "loan"}} {{"gems" or "tokens" or "coins"}} {new_amount}')
    else:
        message.reply_text('Invalid command format. Use /edit {name} {{"deposit" or "loan"}} {{"gems" or "tokens" or "coins"}} {new_amount}')

@client.on_message(filters.command("clear") & is_sudo_user)
def clear_handler(client, message):
    args = message.text.split()[1:]
    if len(args) == 2:
        name, record_type = args
        valid_record_types = ['deposit', 'loan']
        if record_type in valid_record_types:
            filter_condition = {'name': name, 'type': record_type}
            db.deposits.delete_many(filter_condition)
            message.reply_text(f'Successfully cleared {record_type} record for {name}.')
        else:
            message.reply_text(f'Invalid record type. Use /clear {name} {{"deposit" or "loan"}}')
    else:
        message.reply_text('Invalid command format. Use /clear {name} {{"deposit" or "loan"}}')

@client.on_message(filters.command("loan") & (filters.private | filters.group))
def loan_handler(client, message):
    loan_list = db.deposits.find({'type': 'loan'})
    loan_text = '\n'.join([f"{item['name']} {item['amount']} {item['currency']}" for item in loan_list])
    message.reply_text(loan_text or 'No loan records.')

@client.on_message(filters.command("deposit") & (filters.private | filters.group))
def deposit_handler(client, message):
    deposit_list = db.deposits.find({'type': 'deposit'})
    deposit_text = '\n'.join([f"{item['name']} {item['amount']} {item['currency']}" for item in deposit_list])
    message.reply_text(deposit_text or 'No deposit records.')

@client.on_message(filters.command("info") & (filters.private | filters.group))
def info_handler(client, message):
    args = message.text.split()[1:]
    if len(args) == 1:
        name = args[0]
        deposit_info = db.deposits.find_one({'name': name, 'type': 'deposit'})
        loan_info = db.deposits.find_one({'name': name, 'type': 'loan'})

        deposit_text = f"Deposit: {deposit_info['amount']} {deposit_info['currency']}" if deposit_info else 'No deposit.'
        loan_text = f"Loan: {loan_info['amount']} {loan_info['currency']}" if loan_info else 'No loan.'

        message.reply_text(f"Name: {name}\n{deposit_text}\n{loan_text}")
    else:
        message.reply_text('Invalid command format. Use /info {name}')

@client.on_message(filters.command("help") & (filters.private | filters.group))
def help_handler(client, message):
    help_text = (
        "Welcome to Uzumaki Clan Deposit Bot!,Use these commands:\n\n"
        "/add_deposit {name} {gems/tokens/coins} {amount}\n"
        "/add_loan {name} {gems/tokens/coins} {amount}\n"
        "/edit {name} {deposit/loan} {gems/tokens/coins} {amount}\n"
        "/info {name}\n"
        "/help"
    )

    message.reply_text(help_text)

@client.on_message(filters.command("start") & (filters.private | filters.group))
def start_handler(client, message):
    message.reply_text("Hi! I am a bot to maintain deposits in Uzumaki Clan.\nUse /help for a list of available commands.")
print("Bot is alive") 
client.run()
