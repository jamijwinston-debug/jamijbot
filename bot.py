import os
import asyncio
import logging
from datetime import datetime
from typing import List, Dict
from dotenv import load_dotenv
import schedule
import time

from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Load environment variables
load_dotenv()

# Bot configuration - using your provided chat ID
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = '1002796725293'  # Your group chat ID

# Initialize bot
bot = Bot(token=BOT_TOKEN)

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Links to promote
LINKS = {
    "boutique": "http://jjfancyboutique.com",
    "stan_store": "https://stan.store/jamij54",
    "gofundme1": "https://gofund.me/410e7e74",
    "gofundme2": "https://gofund.me/aeb8edbf"
}

# Messages for each link
PROMOTIONAL_MESSAGES = {
    "boutique": (
        "🛍️ Discover the latest fashion trends at JJ Fancy Boutique! "
        "We offer a wide range of stylish clothing and accessories to elevate your wardrobe. "
        "Visit our store now and get 15% off your first purchase with code: TELEGRAM15"
    ),
    "stan_store": (
        "🌟 Exclusive content and personalized interactions await you at Jami's Stan Store! "
        "Get access to premium content, custom requests, and connect directly. "
        "Subscribe now for special perks and behind-the-scenes access!"
    ),
    "gofundme1": (
        "🤝 We need your support! Our community initiative is raising funds to make a difference. "
        "Every contribution, no matter how small, helps us reach our goal. "
        "Please consider donating and sharing with your network. Together we can achieve great things!"
    ),
    "gofundme2": (
        "💖 Help us make an impact! We're raising funds for an important cause that affects many in our community. "
        "Your generosity can create real change. Please donate what you can and help us spread the word!"
    )
}

# Follow-up questions
FOLLOW_UPS = {
    "boutique": "Have you checked out the latest collection at JJ Fancy Boutique yet?",
    "stan_store": "Have you subscribed to Jami's Stan Store for exclusive content?",
    "gofundme1": "Have you had a chance to contribute to our fundraising campaign?",
    "gofundme2": "Did you get a chance to support our second fundraising initiative?"
}

def get_time_based_greeting() -> str:
    """Return appropriate greeting based on time of day"""
    hour = datetime.now().hour
    
    if 5 <= hour < 12:
        return "Good morning"
    elif 12 <= hour < 17:
        return "Good afternoon"
    elif 17 <= hour < 21:
        return "Good evening"
    else:
        return "Hello night owls"

async def send_daily_message(link_key: str) -> None:
    """Send the daily message with appropriate greeting and promotional content"""
    greeting = get_time_based_greeting()
    
    message = (
        f"{greeting}, wonderful community! 👋\n\n"
        "How is everyone doing today? Hope you're all having a fantastic day! 😊\n\n"
        f"{PROMOTIONAL_MESSAGES[link_key]}"
    )
    
    # Create inline keyboard with action button
    keyboard = [
        [InlineKeyboardButton("Take Action", url=LINKS[link_key])]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        await bot.send_message(
            chat_id=CHAT_ID,
            text=message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        logger.info(f"Message sent for {link_key}")
        
        # Schedule follow-up question 6 hours later
        schedule_follow_up(link_key)
        
    except Exception as e:
        logger.error(f"Error sending message: {e}")

async def send_follow_up(link_key: str) -> None:
    """Send follow-up question about the promotional content"""
    question = (
        f"Quick question for everyone: {FOLLOW_UPS[link_key]} "
        "Let us know in the comments! 💬"
    )
    
    try:
        await bot.send_message(
            chat_id=CHAT_ID,
            text=question
        )
        logger.info(f"Follow-up sent for {link_key}")
    except Exception as e:
        logger.error(f"Error sending follow-up: {e}")

def schedule_follow_up(link_key: str) -> None:
    """Schedule a follow-up message"""
    # Clear any existing jobs to avoid duplicates
    schedule.clear(f'follow_up_{link_key}')
    
    # Schedule follow-up for 6 hours later
    schedule.every().day.at((datetime.now().hour + 6) % 24).do(
        lambda: asyncio.create_task(send_follow_up(link_key))
    ).tag(f'follow_up_{link_key}')

def schedule_daily_messages() -> None:
    """Schedule all daily messages"""
    # Schedule messages for different times of day
    schedule.every().day.at("09:00").do(
        lambda: asyncio.create_task(send_daily_message("boutique"))
    ).tag("daily_boutique")
    
    schedule.every().day.at("12:00").do(
        lambda: asyncio.create_task(send_daily_message("stan_store"))
    ).tag("daily_stan_store")
    
    schedule.every().day.at("15:00").do(
        lambda: asyncio.create_task(send_daily_message("gofundme1"))
    ).tag("daily_gofundme1")
    
    schedule.every().day.at("18:00").do(
        lambda: asyncio.create_task(send_daily_message("gofundme2"))
    ).tag("daily_gofundme2")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued"""
    user = update.effective_user
    await update.message.reply_text(
        f"Hi {user.first_name}! I'm your automated posting bot. "
        "I'll post scheduled messages to the group every day."
    )

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle button clicks"""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text=f"Thank you for taking action! ✅")

def main() -> None:
    """Run the bot"""
    # Create the Application
    application = Application.builder().token(BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_click))

    # Schedule daily messages
    schedule_daily_messages()
    
    # Start the Bot
    logger.info("Bot started and scheduling messages...")
    
    # Start the scheduler in a separate thread
    def run_scheduler():
        while True:
            schedule.run_pending()
            time.sleep(1)
    
    import threading
    scheduler_thread = threading.Thread(target=run_scheduler)
    scheduler_thread.daemon = True
    scheduler_thread.start()
    
    # Run the bot until you press Ctrl-C
    application.run_polling()

if __name__ == '__main__':
    main()
