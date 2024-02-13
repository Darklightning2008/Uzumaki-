

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

def is_sudo_user(user_id):
    return user_id in sudo_users

def save_sudo_users(users):
    

@client.on_message(filters.command("edit_deposit") & is_sudo_user)
def edit_deposit_handler(client, message):
    args = message.text.split()[1:]
    if len(args) == 3:
        name, currency, amount = args
        filter_condition = {'name': name, 'currency': currency, 'type': 'deposit'}
        update_data = {'$set': {'amount': int(amount)}}
        db.deposits.update_one(filter_condition, update_data)
        message.reply_text(f'Successfully edited deposit for {name}. New amount: {amount}')
    else:
        message.reply_text('Invalid command format. Use /edit_deposit {name} {gems/tokens/coins} {new_amount}')

@client.on_message(filters.command("edit_loan") & is_sudo_user)
def edit_loan_handler(client, message):
    args = message.text.split()[1:]
    if len(args) == 3:
        name, currency, amount = args
        filter_condition = {'name': name, 'currency': currency, 'type': 'loan'}
        update_data = {'$set': {'amount': int(amount)}}
        db.deposits.update_one(filter_condition, update_data)
        message.reply_text(f'Successfully edited loan for {name}. New amount: {amount}')
    else:
        message.reply_text('Invalid command format. Use /edit_loan {name} {gems/tokens/coins} {new_amount}')

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
            message.reply_text(f'Invalid record type. Use /clear {name} {" or ".join(valid_record_types)}')
    else:
        message.reply_text('Invalid command format. Use /clear {name} {deposit/loan}')


 
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

@client.on_message(filters.command("list") & (filters.private | filters.group))
def list_handler(client, message):
    deposit_list = db.deposits.find({'type': 'deposit'})
    loan_list = db.deposits.find({'type': 'loan'})

    deposit_tokens = [f"{item['name']} {item['amount']} {item['currency']}" for item in deposit_list if item['currency'] == 'tokens']
    deposit_gems = [f"{item['name']} {item['amount']} {item['currency']}" for item in deposit_list if item['currency'] == 'gems']
    deposit_coins = [f"{item['name']} {item['amount']} {item['currency']}" for item in deposit_list if item['currency'] == 'coins']

    loan_tokens = [f"{item['name']} {item['amount']} {item['currency']}" for item in loan_list if item['currency'] == 'tokens']
    loan_gems = [f"{item['name']} {item['amount']} {item['currency']}" for item in loan_list if item['currency'] == 'gems']
    loan_coins = [f"{item['name']} {item['amount']} {item['currency']}" for item in loan_list if item['currency'] == 'coins']

    deposit_tokens_text = '\n'.join(deposit_tokens) if deposit_tokens else 'No token deposits.'
    deposit_gems_text = '\n'.join(deposit_gems) if deposit_gems else 'No gem deposits.'
    deposit_coins_text = '\n'.join(deposit_coins) if deposit_coins else 'No coin deposits.'

    loan_tokens_text = '\n'.join(loan_tokens) if loan_tokens else 'No token loans.'
    loan_gems_text = '\n'.join(loan_gems) if loan_gems else 'No gem loans.'
    loan_coins_text = '\n'.join(loan_coins) if loan_coins else 'No coin loans.'

    message.reply_text(
        f"Token Deposits:\n{deposit_tokens_text}\n\nGem Deposits:\n{deposit_gems_text}\n\nCoin Deposits:\n{deposit_coins_text}\n\n"
        f"Token Loans:\n{loan_tokens_text}\n\nGem Loans:\n{loan_gems_text}\n\nCoin Loans:\n{loan_coins_text}"
    )

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
        "Welcome to Uzumaki Clan Deposit Bot!\n\n"
        "/add_deposit {name} {gems/tokens/coins} {amount}\n"
        "/add_loan {name} {gems/tokens/coins} {amount}\n"
        "/edit {name} {deposit/loan} {gems/tokens/coins} {amount}\n"
        "/edit_deposit {name} {gems/tokens/coins} {amount}\n"
        "/edit_loan {name} {gems/tokens/coins} {amount}\n"
        "/list\n"
        "/info {name}\n"
        "/help"
    )

    message.reply_text(help_text)

@client.on_message(filters.command("start") & (filters.private | filters.group))
def start_handler(client, message):
    message.reply_text("Hi! I am a bot to maintain deposits in Uzumaki Clan.\nUse /help for a list of available commands.")

client.run()
