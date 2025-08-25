import os
import logging
import asyncio
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import TelegramError, BadRequest
import datetime
import schedule
import time
import random
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Bot configuration from environment variables
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

# Store user responses
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
        
    except BadRequest as e:
        if "Chat not found" in str(e):
            logger.error(f"Chat not found. Please make sure:")
            logger.error(f"1. The bot is added to the chat/channel")
            logger.error(f"2. The chat ID '{CHAT_ID}' is correct")
            logger.error(f"3. The bot has permission to send messages")
        else:
            logger.error(f"BadRequest error: {e}")
    except TelegramError as e:
        logger.error(f"Telegram error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")

async def check_bot_health():
    """Check if bot can access Telegram API"""
    try:
        me = await bot.get_me()
        logger.info(f"Bot is working: @{me.username}")
        return True
    except Exception as e:
        logger.error(f"Bot health check failed: {e}")
        return False

async def test_chat_access():
    """Test if bot can access the chat"""
    try:
        chat = await bot.get_chat(chat_id=CHAT_ID)
        logger.info(f"Chat access successful: {chat.title if hasattr(chat, 'title') else 'Private chat'}")
        return True
    except BadRequest as e:
        if "Chat not found" in str(e):
            logger.error("Chat not found. The bot needs to be added to the chat first.")
        else:
            logger.error(f"Chat access error: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected chat access error: {e}")
        return False

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
    
    # First check if bot can connect
    health_ok = loop.run_until_complete(check_bot_health())
    if not health_ok:
        logger.error("Bot health check failed. Check your BOT_TOKEN.")
        return
    
    # Check if bot can access the chat
    chat_ok = loop.run_until_complete(test_chat_access())
    if not chat_ok:
        logger.error("Chat access failed. The bot needs to be added to the chat first.")
        logger.error("Make sure the bot is added as an administrator with send message permissions.")
        return
    
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
