'''Helper functions for "notifierapp" application.
'''
from telegram import Bot

async def send_expire_notification(bot_token, chat_id, items):
    '''Notifies users about item's expiration.

    Args:
        bot_token (str): Telelegram bot token
        chat_id (str): Chat ID that will receive notification
        items (list): Expired items
    '''
    # Getting the Telegram bot
    bot = Bot(bot_token)

    # Constracting the message text
    message = 'Next items have been expired:\n' + ', '.join(items)

    # Sending the notification
    await bot.send_message(chat_id=chat_id, text=message)
