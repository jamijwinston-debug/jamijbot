import logging
import random
import os
from datetime import datetime
from telegram import Update, ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot configuration
BOT_TOKEN = os.getenv("BOT_TOKEN", "8242530682:AAEIrKAuv1OipAwQjgyNHw-d4F1SrGnCGFI")
GROUP_NAME = os.getenv("GROUP_NAME", "@growandhelp")

# Store and donation links with persuasive messages
PROMOTIONAL_MESSAGES = [
    # Morning messages (9 AM)
    {
        "time": {"hour": 9, "minute": 0},
        "message": "🌟 Good morning! 🌟\n\nStart your day in style with JJ Fancy Boutique! "
                  "Discover our exclusive collection that will make you stand out. "
                  "Visit us now: http://jjfancyboutique.com"
    },
    {
        "time": {"hour": 9, "minute": 0},
        "message": "🌞 Rise and shine! 🌞\n\nVisit Jami's Stan Store for unique offerings: "
                  "https://stan.store/jamij54"
    },
    # Evening messages (7 PM)
    {
        "time": {"hour": 19, "minute": 0},
        "message": "✨ Good evening! ✨\n\nConsider supporting our community members in need. "
                  "Every donation makes a difference: https://gofund.me/410e7e74"
    },
    {
        "time": {"hour": 19, "minute": 0},
        "message": "🌙 Evening of generosity 🌙\n\nYour support can change lives: "
                  "https://gofund.me/aeb8edbf"
    }
]

# Greeting messages
GREETINGS = {
    "morning": [
        "🌅 Good morning, amazing people! Have a productive day! 🌅",
        "☀️ Rise and shine! Wishing everyone a wonderful morning! ☀️"
    ],
    "afternoon": [
        "🌞 Good afternoon, everyone! Hope your day is going great! 🌞",
        "🕑 Afternoon check-in! Keep up the good work! 🕑"
    ],
    "evening": [
        "🌇 Good evening, lovely people! Hope you had a fantastic day! 🌇",
        "🌆 Evening greetings! Time to relax and recharge! 🌆"
    ],
    "night": [
        "🌙 Good night, dreamers! Rest well for another amazing tomorrow! 🌙",
        "🌌 Nighty night, everyone! Sweet dreams! 🌌"
    ]
}

class SimpleGroupBot:
    def __init__(self, token):
        self.updater = Updater(token=token, use_context=True)
        self.dispatcher = self.updater.dispatcher
        self.scheduler = BackgroundScheduler()
        
        # Set up command handlers
        self.dispatcher.add_handler(CommandHandler("start", self.start))
        self.dispatcher.add_handler(CommandHandler("help", self.help))
        self.dispatcher.add_handler(CommandHandler("send_message", self.send_custom_message))
        
    def start(self, update: Update, context: CallbackContext):
        update.message.reply_text(
            "Hello! I'm your group reminder bot. "
            "I'll send daily greetings and promotional messages automatically."
        )
    
    def help(self, update: Update, context: CallbackContext):
        help_text = """
        🤖 *Group Management Bot* 🤖
        
        *Commands:*
        /start - Introduction
        /help - Show this help
        /send_message [text] - Send a custom message to the group
        
        I automatically send:
        • Daily greetings (8AM, 1PM, 6PM, 10PM)
        • Promotional messages (9AM, 7PM)
        """
        update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)
    
    def send_custom_message(self, update: Update, context: CallbackContext):
        if context.args:
            message = " ".join(context.args)
            self.send_to_group(message)
            update.message.reply_text("Message sent to group!")
        else:
            update.message.reply_text("Please provide a message to send.")
    
    def send_to_group(self, message):
        try:
            self.updater.bot.send_message(
                chat_id=GROUP_NAME,
                text=message,
                parse_mode=ParseMode.MARKDOWN
            )
            logger.info(f"Message sent to group: {message[:50]}...")
        except Exception as e:
            logger.error(f"Error sending message: {e}")
    
    def send_greeting(self, time_of_day):
        try:
            greeting = random.choice(GREETINGS[time_of_day])
            self.send_to_group(greeting)
        except Exception as e:
            logger.error(f"Error sending greeting: {e}")
    
    def send_promotional_message(self, index):
        try:
            if index < len(PROMOTIONAL_MESSAGES):
                message = PROMOTIONAL_MESSAGES[index]["message"]
                self.send_to_group(message)
        except Exception as e:
            logger.error(f"Error sending promotional message: {e}")
    
    def schedule_messages(self):
        # Schedule greetings
        self.scheduler.add_job(
            lambda: self.send_greeting("morning"),
            'cron', hour=8, minute=0
        )
        self.scheduler.add_job(
            lambda: self.send_greeting("afternoon"),
            'cron', hour=13, minute=0
        )
        self.scheduler.add_job(
            lambda: self.send_greeting("evening"),
            'cron', hour=18, minute=0
        )
        self.scheduler.add_job(
            lambda: self.send_greeting("night"),
            'cron', hour=22, minute=0
        )
        
        # Schedule promotional messages
        for i, msg in enumerate(PROMOTIONAL_MESSAGES):
            self.scheduler.add_job(
                lambda idx=i: self.send_promotional_message(idx),
                'cron', **msg["time"]
            )
    
    def run(self):
        # Schedule messages
        self.schedule_messages()
        self.scheduler.start()
        
        # Start the bot
        logger.info("Starting bot...")
        self.updater.start_polling()
        self.updater.idle()

# Run the bot
if __name__ == '__main__':
    bot = SimpleGroupBot(BOT_TOKEN)
    bot.run()
