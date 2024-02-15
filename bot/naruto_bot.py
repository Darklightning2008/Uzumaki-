# naruto_bot.py

import os
import pymongo
from pyrogram import Client, filters
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up Pyrogram client and connect to MongoDB
api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
bot_token = os.getenv('BOT_TOKEN')
mongo_uri = os.getenv('MONGO_URI')

client = Client('naruto_bot', api_id=api_id, api_hash=api_hash, bot_token=bot_token)
db_client = pymongo.MongoClient(mongo_uri)
db = db_client.get_database('naruto_game')

# List of sudo users who can use /add, /edit, /clear
sudo_users = {1778618019, 1783097017, 6916220465, 1234567890}

# Check if a user is a sudo user
def is_sudo_user(_, __, message):
    return message.from_user.id in sudo_users

# Function to log actions to a specified channel
def log_action(action, name, record_type, currency, amount, sudo_user_id, target_user_name):
    log_text = (
        f"Name: {name}\n"
        f"Deposit/Loan: {currency} {amount}\n"
        f"Sudo: {sudo_user_id}\n"
        f"Target User: {target_user_name}\n"
    )
    log_channel = os.getenv('LOG_CHANNEL')
    if log_channel:
        client.send_message(log_channel, f"{action.capitalize()} Action:\n{log_text}")

# /start command handler
@client.on_message(filters.command("start") & (filters.private | filters.group))
def start_handler(client, message):
    message.reply_text("Hi! I am a bot to maintain deposits in Uzumaki Clan.\nUse /help for a list of available commands.")

# /reset command handler
@client.on_message(filters.command("reset") & is_sudo_user)
def reset_handler(client, message):
    args = message.text.split()[1:]
    if len(args) == 1:
        record_type = args[0]
        valid_record_types = ['deposit', 'loan']
        if record_type in valid_record_types:
            db.deposits.delete_many({'type': record_type})
            message.reply_text(f'Successfully reset {record_type} records.')
        else:
            message.reply_text('Invalid record type. Use /reset {{"deposit" or "loan"}}')
    else:
        message.reply_text('Invalid command format. Use /reset {{"deposit" or "loan"}}')

# /add_deposit command handler
@client.on_message(filters.command("add_deposit") & is_sudo_user)
def add_deposit_handler(client, message):
    args = message.text.split()[1:]
    if len(args) == 3:
        name, currency, amount = args
        db.deposits.insert_one({'name': name, 'type': 'deposit', 'currency': currency, 'amount': int(amount)})
        message.reply_text(f'Successfully added deposit for {name}. Amount: {amount} {currency}')
        log_action("add", name, "deposit", currency, amount, message.from_user.id, name)
    else:
        message.reply_text('Invalid command format. Use /add_deposit {name} {gems/tokens/coins} {amount}')

# /add_loan command handler
@client.on_message(filters.command("add_loan") & is_sudo_user)
def add_loan_handler(client, message):
    args = message.text.split()[1:]
    if len(args) == 3:
        name, currency, amount = args
        db.deposits.insert_one({'name': name, 'type': 'loan', 'currency': currency, 'amount': int(amount)})
        message.reply_text(f'Successfully added loan for {name}. Amount: {amount} {currency}')
        log_action("add", name, "loan", currency, amount, message.from_user.id, name)
    else:
        message.reply_text('Invalid command format. Use /add_loan {name} {gems/tokens/coins} {amount}')

# /edit command handler
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
            log_action("edit", name, record_type, currency, amount, message.from_user.id, name)
        else:
            message.reply_text(f'Invalid record type. Use /edit {name} {{"deposit" or "loan"}} {{"gems" or "tokens" or "coins"}} {new_amount}')
    else:
        message.reply_text('Invalid command format. Use /edit {name} {{"deposit" or "loan"}} {{"gems" or "tokens" or "coins"}} {new_amount}')

# /clear command handler
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
            log_action("clear", name, record_type, "", 0, message.from_user.id, name)
        else:
            message.reply_text(f'Invalid record type. Use /clear {name} {{"deposit" or "loan"}}')
    else:
        message.reply_text('Invalid command format. Use /clear {name} {{"deposit" or "loan"}}')

# /info command handler
@client.on_message(filters.command("info") & (filters.private | filters.group))
def info_handler(client, message):
    args = message.text.split()[1:]
    if len(args) == 1:
        name = args[0]
        user = message.from_user
        target_user = None

        # Check if the provided name is a username
        if name.startswith('@'):
            username = name[1:]
            try:
                target_user = client.get_users(username)
            except Exception as e:
                print(f"Error getting user by username: {e}")

        # If the provided name is not a username or couldn't be fetched, use it as a display name
        if target_user is None:
            target_user = user

        deposit_info = db.deposits.find_one({'name': target_user.username, 'type': 'deposit'}) or \
                       db.deposits.find_one({'name': target_user.first_name, 'type': 'deposit'})
        loan_info = db.deposits.find_one({'name': target_user.username, 'type': 'loan'}) or \
                    db.deposits.find_one({'name': target_user.first_name, 'type': 'loan'})

        deposit_text = f"Deposit: {deposit_info['amount']} {deposit_info['currency']}" if deposit_info else "No deposit record"
        loan_text = f"Loan: {loan_info['amount']} {loan_info['currency']}" if loan_info else "No loan record"

        message.reply_text(
            f"Name: {target_user.first_name} ({target_user.username})\n"
            f"{deposit_text}\n"
            f"{loan_text}"
        )
    else:
        message.reply_text('Invalid command format. Use /info {name}')

# /help command handler
@client.on_message(filters.command("help") & (filters.private | filters.group))
def help_handler(client, message):
    help_text = (
        "List of available commands:\n"
        "/start - Start the bot\n"
        "/reset {deposit/loan} - Reset all deposit or loan records\n"
        "/add_deposit {name} {gems/tokens/coins} {amount} - Add a deposit record\n"
        "/add_loan {name} {gems/tokens/coins} {amount} - Add a loan record\n"
        "/edit {name} {deposit/loan} {gems/tokens/coins} {amount} - Edit a deposit or loan record\n"
        "/clear {name} {deposit/loan} - Clear a deposit or loan record\n"
        "/info {name} - Get information about a user's deposit and loan\n"
        "/deposit_list - View a list of deposit records\n"
        "/loan_list - View a list of loan records\n"
        "/broadcast {message} - Broadcast a message to all users\n"
    )
    message.reply_text(help_text)

# /deposit_list command handler
@client.on_message(filters.command("deposit_list") & is_sudo_user)
def deposit_list_handler(client, message):
    currencies = ['tokens', 'gems', 'coins']
    deposit_records = db.deposits.find({'type': 'deposit'})
    deposit_text = {currency: [] for currency in currencies}

    for record in deposit_records:
        currency = record['currency']
        if currency in currencies:
            deposit_text[currency].append(f"{record['name']} {record['amount']} {currency.capitalize()}")

    reply_text = "\n".join([f"{currency.capitalize()}:\n{', '.join(deposit_text[currency])}" for currency in currencies])
    message.reply_text(f"Deposit List:\n{reply_text}")

# /loan_list command handler
@client.on_message(filters.command("loan_list") & is_sudo_user)
def loan_list_handler(client, message):
    currencies = ['tokens', 'gems', 'coins']
    loan_records = db.deposits.find({'type': 'loan'})
    loan_text = {currency: [] for currency in currencies}

    for record in loan_records:
        currency = record['currency']
        if currency in currencies:
            loan_text[currency].append(f"{record['name']} {record['amount']} {currency.capitalize()}")

    reply_text = "\n".join([f"{currency.capitalize()}:\n{', '.join(loan_text[currency])}" for currency in currencies])
    message.reply_text(f"Loan List:\n{reply_text}")

# /broadcast command handler
@client.on_message(filters.command("broadcast") & is_sudo_user)
def broadcast_handler(client, message):
    broadcast_text = message.text.split(" ", 1)[1]
    user_ids = [user.id for user in client.iter_chat_members(message.chat.id)]
    for user_id in user_ids:
        try:
            client.send_message(user_id, broadcast_text)
        except Exception as e:
            print(f"Error sending broadcast to user {user_id}: {e}")
    message.reply_text("Broadcast sent to all users.")

# /reset command handler
@client.on_message(filters.command("reset") & is_sudo_user)
def reset_handler(client, message):
    args = message.text.split()[1:]
    if len(args) == 1:
        record_type = args[0]
        valid_record_types = ['deposit', 'loan']
        if record_type in valid_record_types:
            db.deposits.delete_many({'type': record_type})
            message.reply_text(f'Successfully reset {record_type} records.')
        else:
            message.reply_text('Invalid record type. Use /reset {{"deposit" or "loan"}}')
    else:
        message.reply_text('Invalid command format. Use /reset {{"deposit" or "loan"}}')

# /info command handler
@client.on_message(filters.command("info") & (filters.private | filters.group))
def info_handler(client, message):
    args = message.text.split()[1:]
    if len(args) == 1:
        name = args[0]
        user = message.from_user
        target_user = None

        # Check if the provided name is a username
        if name.startswith('@'):
            username = name[1:]
            try:
                target_user = client.get_users(username)
            except Exception as e:
                print(f"Error getting user by username: {e}")

        # If the provided name is not a username or couldn't be fetched, use it as a display name
        if target_user is None:
            target_user = user

        deposit_info = db.deposits.find_one({'name': target_user.username, 'type': 'deposit'}) or \
                       db.deposits.find_one({'name': target_user.first_name, 'type': 'deposit'})
        loan_info = db.deposits.find_one({'name': target_user.username, 'type': 'loan'}) or \
                    db.deposits.find_one({'name': target_user.first_name, 'type': 'loan'})

        deposit_text = f"Deposit: {deposit_info['amount']} {deposit_info['currency']}" if deposit_info else "No deposit record"
        loan_text = f"Loan: {loan_info['amount']} {loan_info['currency']}" if loan_info else "No loan record"

        message.reply_text(
            f"Name: {target_user.first_name} ({target_user.username})\n"
            f"{deposit_text}\n"
            f"{loan_text}"
        )
    else:
        message.reply_text('Invalid command format. Use /info {name}')

# /help command handler
@client.on_message(filters.command("help") & (filters.private | filters.group))
def help_handler(client, message):
    help_text = (
        "List of available commands:\n"
        "/start - Start the bot\n"
        "/reset {deposit/loan} - Reset all deposit or loan records\n"
        "/add_deposit {name} {gems/tokens/coins} {amount} - Add a deposit record\n"
        "/add_loan {name} {gems/tokens/coins} {amount} - Add a loan record\n"
        "/edit {name} {deposit/loan} {gems/tokens/coins} {amount} - Edit a deposit or loan record\n"
        "/clear {name} {deposit/loan} - Clear a deposit or loan record\n"
        "/info {name} - Get information about a user's deposit and loan\n"
        "/deposit_list - View a list of deposit records\n"
        "/loan_list - View a list of loan records\n"
        "/broadcast {message} - Broadcast a message to all users\n"
    )
    message.reply_text(help_text)

# Run the bot
client.run()
