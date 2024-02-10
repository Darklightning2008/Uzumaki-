from telegram.ext import Updater, CommandHandler
from telethon.sync import TelegramClient
from pymongo import MongoClient
from config import BOT_TOKEN, MONGO_URI, TELEGRAM_API_ID, TELEGRAM_API_HASH

# Initialize MongoDB
client = MongoClient(MONGO_URI)
db = client['naruto_game']

# Initialize Telethon
telethon_client = TelegramClient('naruto_bot', TELEGRAM_API_ID, TELEGRAM_API_HASH)
telethon_client.start()

def add_handler(update, context):
    if telethon_client.get_entity(update.message.from_user.id).status.is_admin():
        args = context.args
        if len(args) == 4:
            name, currency, amount, transaction_type = args
            db.deposits.insert_one({'name': name, 'currency': currency, 'amount': amount, 'type': transaction_type})
            update.message.reply_text(f'Successfully added {amount} {currency} {transaction_type} for {name}')
        else:
            update.message.reply_text('Invalid command format. Use /add {name} {currency} {amount} {transaction_type}')
    else:
        update.message.reply_text('Only group admins can use this command.')

def edit_handler(update, context):
    if telethon_client.get_entity(update.message.from_user.id).status.is_admin():
        args = context.args
        if len(args) == 3:
            name, currency, transaction_type = args
            db.deposits.update_one({'name': name, 'currency': currency}, {'$set': {'type': transaction_type}})
            update.message.reply_text(f'Successfully edited {name} {currency} to {transaction_type}')
        else:
            update.message.reply_text('Invalid command format. Use /edit {name} {currency} {transaction_type}')
    else:
        update.message.reply_text('Only group admins can use this command.')

def list_handler(update, context):
    deposit_list = db.deposits.find()
    formatted_list = [f"{item['name']} {item['currency']} {item['amount']} {item['type']}" for item in deposit_list]
    update.message.reply_text('\n'.join(formatted_list) if formatted_list else 'No records found.')

updater = Updater(token=BOT_TOKEN, use_context=True)
dp = updater.dispatcher

dp.add_handler(CommandHandler("add", add_handler))
dp.add_handler(CommandHandler("edit", edit_handler))
dp.add_handler(CommandHandler("list", list_handler))

updater.start_polling()
updater.idle()
print("bot alive") 
