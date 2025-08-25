import os
import logging
import asyncio
import threading
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, CallbackContext
from telegram.error import TelegramError
import datetime
import random
import time

# Bot configuration
BOT_TOKEN = os.getenv('BOT_TOKEN', '8242530682:AAEIrKAuv1OipAwQjgyNHw-d4F1SrGnCGFI')

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Store active groups and user responses
active_groups = set()
user_responses = {}

# Define the links and their messages
LINKS = [
    {
        "url": "http://jjfancyboutique.com",
        "message": "🌟 Discover the latest fashion trends at JJ Fancy Boutique! We have new arrivals every week. Shop now for exclusive styles that will make you stand out! 🌟",
        "button_text": "🛍️ Shop Now"
    },
    {
        "url": "https://stan.store/jamij54",
        "message": "🎉 Check out my exclusive content and offers on Stan Store! Support my work and get access to special perks, behind-the-scenes content, and more. 🎉",
        "button_text": "🌟 Exclusive Content"
    },
    {
        "url": "https://gofund.me/410e7e74",
        "message": "🙏 Your support can make a real difference! Please consider contributing to our cause. Every little bit helps us get closer to our goal. Thank you for your generosity! 🙏",
        "button_text": "❤️ Donate Now"
    },
    {
        "url": "https://gofund.me/aeb8edbf",
        "message": "💖 Help us reach our goal! This fundraiser will support an important initiative in our community. Your contribution, no matter the size, will have a significant impact. 💖",
        "button_text": "🤝 Support Us"
    }
]

def get_time_based_greeting():
    """Return appropriate greeting based on time of day"""
    hour = datetime.datetime.now().hour
    
    if 5 <= hour < 12:
        return "Good morning"
    elif 12 <= hour < 17:
        return "Good afternoon"
    elif 17 <= hour < 22:
        return "Good evening"
    else:
        return "Good night"

def send_daily_message(chat_id, context):
    """Send the daily message with a greeting and promotional content"""
    try:
        # Get appropriate greeting
        greeting = get_time_based_greeting()
        
        # Select a random link for today
        link_data = random.choice(LINKS)
        
        # Create keyboard with action button
        keyboard = [
            [InlineKeyboardButton(link_data["button_text"], url=link_data["url"])],
            [InlineKeyboardButton("Yes, I've taken action! ✅", callback_data="action_taken")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Create the full message
        full_message = f"{greeting} everyone! 👋\n\nHow are you all doing today?\n\n{link_data['message']}"
        
        # Send the message
        context.bot.send_message(
            chat_id=chat_id,
            text=full_message,
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
        logger.info(f"Daily message sent to chat {chat_id}")
        
    except TelegramError as e:
        logger.error(f"Error sending message to chat {chat_id}: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")

def start(update: Update, context: CallbackContext):
    """Send a message when the command /start is issued."""
    user = update.effective_user
    update.message.reply_text(
        f"Hi {user.first_name}! I'm your auto-posting bot. Add me to any group and I'll send daily messages!"
    )

def help_command(update: Update, context: CallbackContext):
    """Send a message when the command /help is issued."""
    update.message.reply_text("I'm a bot that sends daily messages to groups! Add me to any group to get started.")

def new_chat_members(update: Update, context: CallbackContext):
    """Handle new chat members (when bot is added to a group)."""
    for member in update.message.new_chat_members:
        if member.id == context.bot.id:
            # Bot was added to a group
            chat_id = update.effective_chat.id
            active_groups.add(chat_id)
            logger.info(f"Bot added to group: {chat_id}")
            
            # Send welcome message
            update.message.reply_text(
                "Hello everyone! 👋 I'm your daily message bot. "
                "I'll post inspirational messages every day at 10:00 AM. "
                "Use /daily to get a message right now!"
            )

def left_chat_member(update: Update, context: CallbackContext):
    """Handle when bot is removed from a group."""
    if update.message.left_chat_member.id == context.bot.id:
        chat_id = update.effective_chat.id
        if chat_id in active_groups:
            active_groups.remove(chat_id)
            logger.info(f"Bot removed from group: {chat_id}")

def daily_command(update: Update, context: CallbackContext):
    """Send a daily message on command."""
    chat_id = update.effective_chat.id
    send_daily_message(chat_id, context)

def button_handler(update: Update, context: CallbackContext):
    """Handle button callbacks"""
    query = update.callback_query
    query.answer()
    
    if query.data == "action_taken":
        user_id = query.from_user.id
        user_responses[user_id] = True
        query.edit_message_text(text=f"Thank you {query.from_user.first_name} for taking action! 🙌")

def error_handler(update: Update, context: CallbackContext):
    """Log errors caused by Updates."""
    logger.error(f"Exception while handling an update: {context.error}")

def send_scheduled_messages():
    """Send scheduled messages to all active groups"""
    while True:
        try:
            now = datetime.datetime.now()
            # Send at 10:00 AM every day
            if now.hour == 10 and now.minute == 0:
                for chat_id in list(active_groups):
                    # Create a minimal context for sending messages
                    class MinimalContext:
                        def __init__(self, bot):
                            self.bot = bot
                    
                    context = MinimalContext(updater.bot)
                    send_daily_message(chat_id, context)
                # Wait 1 hour to avoid sending multiple times
                time.sleep(3600)
            else:
                # Check every minute
                time.sleep(60)
        except Exception as e:
            logger.error(f"Error in scheduled messages: {e}")
            time.sleep(60)

def main():
    """Start the bot."""
    global updater
    
    # Create the Updater
    updater = Updater(BOT_TOKEN, use_context=True)
    
    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add handlers
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("daily", daily_command))
    dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, new_chat_members))
    dp.add_handler(MessageHandler(Filters.status_update.left_chat_member, left_chat_member))
    dp.add_handler(CallbackQueryHandler(button_handler))
    
    # Add error handler
    dp.add_error_handler(error_handler)

    # Start the scheduled messages in a separate thread
    scheduler_thread = threading.Thread(target=send_scheduled_messages)
    scheduler_thread.daemon = True
    scheduler_thread.start()

    # Start the Bot
    updater.start_polling()
    
    # Run the bot until you press Ctrl-C
    updater.idle()

if __name__ == '__main__':
    main()
