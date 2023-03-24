from django.core.management.base import BaseCommand
from django.conf import settings

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
)

from notifierapp.models import Subscription

async def start(update, context):
    '''Sends the list of commands to the user.
    '''
    await update.message.reply_text(
        'You can use the next commands:\n'
        '  /subscribe - to subscribe on notifications\n'
        '  /unsubscribe - to unsubscribe from notifications'
    )

async def subscribe(update, context):
    '''Adds client chat ID to the subscription list.
    '''
    # Getting user's chat ID
    chat_id = update.effective_chat.id

    # Adding the chat ID to the subscription list
    await Subscription.objects.aupdate_or_create(
        chat_id=chat_id,
        defaults={'chat_id': chat_id}
    )

    # Answering the user
    await update.message.reply_text("You've been subscribed!")

async def unsubscribe(update, context):
    '''Removes client chat ID from the subscription list.
    '''
    # Getting user's chat ID
    chat_id = update.effective_chat.id

    # Removing the chat ID from the subscription list
    await Subscription.objects.filter(chat_id=chat_id).adelete()

    # Answering the user
    await update.message.reply_text("You've been unsubscribed!")

class Command(BaseCommand):
    '''Represents a handler of "run_bot" command.
    '''
    help = 'Runs the bot.'

    def handle(self, *args, **options):
        # Building Telegram application
        app = ApplicationBuilder().token(settings.TELEGRAM_BOT_TOKEN).build()

        # Declaring commands handlers
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("subscribe", subscribe))
        app.add_handler(CommandHandler("unsubscribe", unsubscribe))

        # Running polling
        app.run_polling()
