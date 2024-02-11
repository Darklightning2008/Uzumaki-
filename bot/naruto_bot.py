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

# Owners who can add sudo users
owners = {6916220465}  # Add the specified user ID to the owners set

def load_sudo_users():
    sudo_users_data = db.settings.find_one({'key': 'sudo_users'})
    return set(sudo_users_data['value']) if sudo_users_data else set()

def save_sudo_users(sudo_users_set):
    db.settings.update_one({'key': 'sudo_users'}, {'$set': {'value': list(sudo_users_set)}}, upsert=True)

# Load sudo users on startup
sudo_users = load_sudo_users()

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
        "/add_deposit {name} {gems/tokens/coins} {amount}\n"
        "/add_loan {name} {gems/tokens/coins} {amount}\n"
        "/edit {name} {deposit/loan} {gems/tokens/coins} {amount}\n"
        "/edit_deposit {name} {gems/tokens/coins} {amount}\n"
        "/edit_loan {name} {gems/tokens/coins} {amount}\n"
        "/list\n"
        "/deposit\n"
        "/loan\n"
        "/info {name}\n"
        "/help"
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
        save_sudo_users(sudo_users)
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

@client.on_message(filters.command("add_deposit") & (filters.private | filters.group))
def add_deposit_handler(client, message):
    if is_sudo_user(message.from_user.id):
        args = message.text.split()[1:]
        if len(args) == 3:
            name, currency, amount = args
            db.deposits.insert_one({'name': name, 'currency': currency, 'amount': amount, 'type': 'deposit'})
            message.reply_text(f'Successfully added {amount} {currency} to deposit for {name}')
        else:
            message.reply_text('Invalid command format. Use /add_deposit {name} {gems/tokens/coins} {amount}')
    else:
        message.reply_text('You are not authorized to use this command.')

@client.on_message(filters.command("add_loan") & (filters.private | filters.group))
def add_loan_handler(client, message):
    if is_sudo_user(message.from_user.id):
        args = message.text.split()[1:]
        if len(args) == 3:
            name, currency, amount = args
            db.deposits.insert_one({'name': name, 'currency': currency, 'amount': amount, 'type': 'loan'})
            message.reply_text(f'Successfully added {amount} {currency} to loan for {name}')
        else:
            message.reply_text('Invalid command format. Use /add_loan {name} {gems/tokens/coins} {amount}')
    else:
        message.reply_text('You are not authorized to use this command.')

@client.on_message(filters.command("edit") & (filters.private | filters.group))
def edit_handler(client, message):
    if is_sudo_user(message.from_user.id):
        args = message.text.split()[1:]
        if len(args) == 4:
            name, transaction_type, currency, amount = args
            transaction_type = transaction_type.lower()
            if transaction_type == "deposit":
                db.deposits.update_one({'name': name, 'type': 'deposit', 'currency': currency}, {'$set': {'amount': amount}})
                message.reply_text(f'Successfully edited {name} deposit {currency} to {amount}')
            elif transaction_type == "loan":
                db.deposits.update_one({'name': name, 'type': 'loan', 'currency': currency}, {'$set': {'amount': amount}})
                message.reply_text(f'Successfully edited {name} loan {currency} to {amount}')
            else:
                message.reply_text('Invalid transaction type. Use /edit {name} {deposit/loan} {currency} {amount}')
        else:
            message.reply_text('Invalid command format. Use /edit {name} {deposit/loan} {currency} {amount}')
    else:
        message.reply_text('You are not authorized to use this command.')

@client.on_message(filters.command("edit_deposit") & (filters.private | filters.group))
def edit_deposit_handler(client, message):
    if is_sudo_user(message.from_user.id):
        args = message.text.split()[1:]
        if len(args) == 3:
            name, currency, amount = args
            db.deposits.update_one({'name': name, 'type': 'deposit', 'currency': currency}, {'$set': {'amount': amount}})
            message.reply_text(f'Successfully edited {name} deposit {currency} to {amount}')
        else:
            message.reply_text('Invalid command format. Use /edit_deposit {name} {gems/tokens/coins} {amount}')
    else:
        message.reply_text('You are not authorized to use this command.')

@client.on_message(filters.command("edit_loan") & (filters.private | filters.group))
def edit_loan_handler(client, message):
    if is_sudo_user(message.from_user.id):
        args = message.text.split()[1:]
        if len(args) == 3:
            name, currency, amount = args
            db.deposits.update_one({'name': name, 'type': 'loan', 'currency': currency}, {'$set': {'amount': amount}})
            message.reply_text(f'Successfully edited {name} loan {currency} to {amount}')
        else:
            message.reply_text('Invalid command format. Use /edit_loan {name} {gems/tokens/coins} {amount}')
    else:
        message.reply_text('You are not authorized to use this command.')

@client.on_message(filters.command("list") & (filters.private | filters.group))
def list_handler(client, message):
    deposit_list = db.deposits.find({'type': 'deposit'})
    loan_list = db.deposits.find({'type': 'loan'})

    deposit_tokens = [f"{item['name']} {item['amount']}" for item in deposit_list if item['currency'] == 'tokens']
    deposit_gems = [f"{item['name']} {item['amount']}" for item in deposit_list if item['currency'] == 'gems']
    deposit_coins = [f"{item['name']} {item['amount']}" for item in deposit_list if item['currency'] == 'coins']

    loan_tokens = [f"{item['name']} {item['amount']}" for item in loan_list if item['currency'] == 'tokens']
    loan_gems = [f"{item['name']} {item['amount']}" for item in loan_list if item['currency'] == 'gems']
    loan_coins = [f"{item['name']} {item['amount']}" for item in loan_list if item['currency'] == 'coins']

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

@client.on_message(filters.command("deposit") & (filters.private | filters.group))
def deposit_handler(client, message):
    deposit_list = db.deposits.find({'type': 'deposit'})
    deposit_tokens = [f"{item['name']} {item['amount']}" for item in deposit_list if item['currency'] == 'tokens']
    deposit_gems = [f"{item['name']} {item['amount']}" for item in deposit_list if item['currency'] == 'gems']
    deposit_coins = [f"{item['name']} {item['amount']}" for item in deposit_list if item['currency'] == 'coins']

    deposit_tokens_text = '\n'.join(deposit_tokens) if deposit_tokens else 'No token deposits.'
    deposit_gems_text = '\n'.join(deposit_gems) if deposit_gems else 'No gem deposits.'
    deposit_coins_text = '\n'.join(deposit_coins) if deposit_coins else 'No coin deposits.'

    message.reply_text(
        f"Token Deposits:\n{deposit_tokens_text}\n\nGem Deposits:\n{deposit_gems_text}\n\nCoin Deposits:\n{deposit_coins_text}"
    )

@client.on_message(filters.command("loan") & (filters.private | filters.group))
def loan_handler(client, message):
    loan_list = db.deposits.find({'type': 'loan'})
    loan_tokens = [f"{item['name']} {item['amount']}" for item in loan_list if item['currency'] == 'tokens']
    loan_gems = [f"{item['name']} {item['amount']}" for item in loan_list if item['currency'] == 'gems']
    loan_coins = [f"{item['name']} {item['amount']}" for item in loan_list if item['currency'] == 'coins']

    loan_tokens_text = '\n'.join(loan_tokens) if loan_tokens else 'No token loans.'
    loan_gems_text = '\n'.join(loan_gems) if loan_gems else 'No gem loans.'
    loan_coins_text = '\n'.join(loan_coins) if loan_coins else 'No coin loans.'

    message.reply_text(
        f"Token Loans:\n{loan_tokens_text}\n\nGem Loans:\n{loan_gems_text}\n\nCoin Loans:\n{loan_coins_text}"
    )

@client.on_message(filters.command("info") & (filters.private | filters.group))
def info_handler(client, message):
    args = message.text.split()[1:]
    if len(args) == 1:
        name = args[0]
        deposit_record = db.deposits.find_one({'name': name, 'type': 'deposit'})
        loan_record = db.deposits.find_one({'name': name, 'type': 'loan'})

        deposit_text = (
            f"Deposit : {deposit_record['currency']} {deposit_record['amount']}" if deposit_record else 'No deposit record'
        )
        loan_text = (
            f"Loan : {loan_record['currency']} {loan_record['amount']}" if loan_record else 'No loan record'
        )

        message.reply_text(f"Name : {name}\n{deposit_text}\n{loan_text}")
    else:
        message.reply_text('Invalid command format. Use /info {name}')

@client.on_message(filters.command("help") & (filters.private | filters.group))
def help_handler(client, message):
    help_text = (
        "Welcome to Uzumaki Clan Deposit Bot!\n\n"
        "Available commands:\n"
        "/add_deposit {name} {gems/tokens/coins} {amount}\n"
        "/add_loan {name} {gems/tokens/coins} {amount}\n"
        "/edit {name} {deposit/loan} {gems/tokens/coins} {amount}\n"
        "/edit_deposit {name} {gems/tokens/coins} {amount}\n"
        "/edit_loan {name} {gems/tokens/coins} {amount}\n"
        "/list\n"
        "/deposit\n"
        "/loan\n"
        "/info {name}\n"
        "/help"
    )

    message.reply_text(help_text)


@client.on_message(filters.command("broadcast") & filters.user(6916220465))
def broadcast_handler(client, message):
    args = message.text.split()[1:]
    if len(args) >= 2:
        target = args[0]
        text = ' '.join(args[1:])
        users = db.deposits.distinct('name', {'type': target})
        
        for user in users:
            client.send_message(user, text)

@client.on_message(filters.command("sendall") & filters.user(6916220465))
def send_all_handler(client, message):
    text = ' '.join(message.text.split()[1:])
    users = db.deposits.distinct('name')
    
    for user in users:
        client.send_message(user, text)



client.run()
