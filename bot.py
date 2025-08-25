import os
import logging
import threading
import datetime
import random
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from telegram.error import TelegramError

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

async def send_daily_message(chat_id, bot):
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
        await bot.send_message(
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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_text(
        f"Hi {user.first_name}! I'm your auto-posting bot. Add me to any group and I'll send daily messages!"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /help is issued."""
    await update.message.reply_text("I'm a bot that sends daily messages to groups! Add me to any group to get started.")

async def new_chat_members(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle new chat members (when bot is added to a group)."""
    for member in update.message.new_chat_members:
        if member.id == context.bot.id:
            # Bot was added to a group
            chat_id = update.effective_chat.id
            active_groups.add(chat_id)
            logger.info(f"Bot added to group: {chat_id}")
            
            # Send welcome message
            await update.message.reply_text(
                "Hello everyone! 👋 I'm your daily message bot. "
                "I'll post inspirational messages every day at 10:00 AM. "
                "Use /daily to get a message right now!"
            )

async def left_chat_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle when bot is removed from a group."""
    if update.message.left_chat_member.id == context.bot.id:
        chat_id = update.effective_chat.id
        if chat_id in active_groups:
            active_groups.remove(chat_id)
            logger.info(f"Bot removed from group: {chat_id}")

async def daily_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a daily message on command."""
    chat_id = update.effective_chat.id
    await send_daily_message(chat_id, context.bot)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "action_taken":
        user_id = query.from_user.id
        user_responses[user_id] = True
        await query.edit_message_text(text=f"Thank you {query.from_user.first_name} for taking action! 🙌")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log errors caused by Updates."""
    logger.error(f"Exception while handling an update: {context.error}")

async def send_scheduled_messages(bot):
    """Send scheduled messages to all active groups"""
    while True:
        try:
            now = datetime.datetime.now()
            # Send at 10:00 AM every day
            if now.hour == 10 and now.minute == 0:
                for chat_id in list(active_groups):
                    await send_daily_message(chat_id, bot)
                # Wait 1 hour to avoid sending multiple times
                await asyncio.sleep(3600)
            else:
                # Check every minute
                await asyncio.sleep(60)
        except Exception as e:
            logger.error(f"Error in scheduled messages: {e}")
            await asyncio.sleep(60)

def run_scheduler(application):
    """Run the scheduler in a separate thread"""
    async def scheduler_task():
        await send_scheduled_messages(application.bot)
    
    # Run the scheduler in the event loop
    loop = application._get_running_loop()
    asyncio.run_coroutine_threadsafe(scheduler_task(), loop)

def main():
    """Start the bot."""
    # Create the Application
    application = Application.builder().token(BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("daily", daily_command))
    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, new_chat_members))
    application.add_handler(MessageHandler(filters.StatusUpdate.LEFT_CHAT_MEMBER, left_chat_member))
    application.add_handler(CallbackQueryHandler(button_handler))
    
    # Add error handler
    application.add_error_handler(error_handler)

    # Start the scheduler in a separate thread
    scheduler_thread = threading.Thread(target=run_scheduler, args=(application,))
    scheduler_thread.daemon = True
    scheduler_thread.start()

    # Start the Bot
    application.run_polling()

if __name__ == '__main__':
    import asyncio
    main()
