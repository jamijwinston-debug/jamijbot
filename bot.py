import os
import logging
import asyncio
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import TelegramError
import datetime
import schedule
import time
import random
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Bot configuration from environment variables (set these in Render.com dashboard)
BOT_TOKEN = os.getenv('BOT_TOKEN', '8242530682:AAEIrKAuv1OipAwQjgyNHw-d4F1SrGnCGFI')
CHAT_ID = os.getenv('CHAT_ID', '1002796725293')

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize bot
bot = Bot(token=BOT_TOKEN)

# Store user responses (in a real application, use a database)
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

async def send_daily_message():
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
            chat_id=CHAT_ID,
            text=full_message,
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
        logger.info("Daily message sent successfully")
        
    except TelegramError as e:
        logger.error(f"Error sending message: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")

async def check_engagement():
    """Check how many users have taken action"""
    try:
        engaged_users = len(user_responses)
        await bot.send_message(
            chat_id=CHAT_ID,
            text=f"📊 Engagement Update: So far, {engaged_users} users have taken action! Thank you to everyone who has participated! 🙏"
        )
    except Exception as e:
        logger.error(f"Error sending engagement check: {e}")

def run_scheduled_tasks():
    """Run the scheduled tasks in the asyncio event loop"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # Schedule messages
    schedule.every().day.at("10:00").do(lambda: loop.run_until_complete(send_daily_message()))
    schedule.every().day.at("16:00").do(lambda: loop.run_until_complete(check_engagement()))
    
    # Send initial message when deployed
    loop.run_until_complete(send_daily_message())
    logger.info("Bot started and initial message sent")
    
    # Keep the schedule running
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

if __name__ == '__main__':
    run_scheduled_tasks()
