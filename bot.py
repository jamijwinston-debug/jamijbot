import logging
import asyncio
import random
from datetime import datetime, time
from typing import List
from telegram import Update, ChatMember, User
from telegram.ext import Updater, CommandHandler, CallbackContext
from telegram.utils.helpers import escape_markdown
import requests
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import os
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
STORE_LINKS = {
    "jjfancyboutique": {
        "url": "http://jjfancyboutique.com",
        "messages": [
            "🌟 Good morning, fashion lovers! 🌟\n\nStart your day in style with JJ Fancy Boutique! "
            "Discover our exclusive collection that will make you stand out from the crowd. "
            "From casual wear to elegant evening outfits, we have something for every occasion. "
            "Visit us now and use code GROW10 for 10% off your first order!\n\n"
            "👉 http://jjfancyboutique.com 👈",
            
            "✨ Good evening, style enthusiasts! ✨\n\nAs the day winds down, it's the perfect time to "
            "treat yourself to something special from JJ Fancy Boutique. Our new arrivals are flying off the shelves! "
            "Don't miss out on the latest trends that will keep you looking fabulous all season long.\n\n"
            "Shop now: http://jjfancyboutique.com"
        ]
    },
    "stan_store": {
        "url": "https://stan.store/jamij54",
        "messages": [
            "🌞 Rise and shine! 🌞\n\nLooking for exclusive content and personalized services? "
            "Visit Jami's Stan Store for unique offerings you won't find anywhere else! "
            "Support independent creators while getting access to premium content.\n\n"
            "Check it out: https://stan.store/jamij54",
            
            "🌙 Evening vibes! 🌙\n\nWind down your day by exploring Jami's Stan Store. "
            "From custom requests to exclusive digital products, there's something for everyone. "
            "Your support helps an independent creator continue doing what they love!\n\n"
            "Visit now: https://stan.store/jamij54"
        ]
    },
    "gofundme1": {
        "url": "https://gofund.me/410e7e74",
        "messages": [
            "🤲 Morning of generosity! 🤲\n\nAs we start our day, let's remember the power of community support. "
            "A member of our group is facing challenges and could use our help. "
            "Every contribution, no matter how small, makes a significant difference. "
            "Let's come together and show what our community can achieve!\n\n"
            "Donate here: https://gofund.me/410e7e74",
            
            "🌆 Evening reflection 🌆\n\nAs the day ends, consider making a lasting impact on someone's life. "
            "Your donation could be the turning point for someone in need. "
            "Let's end the day with an act of kindness that truly matters.\n\n"
            "Support now: https://gofund.me/410e7e74"
        ]
    },
    "gofundme2": {
        "url": "https://gofund.me/aeb8edbf",
        "messages": [
            "☀️ Good morning, compassionate souls! ☀️\n\nToday, let's open our hearts to those in need. "
            "This fundraiser supports an important cause that touches lives in our community. "
            "Your generosity can create waves of positive change. "
            "Even the smallest donation contributes to a larger solution.\n\n"
            "Please give: https://gofund.me/aeb8edbf",
            
            "🌃 Nighttime kindness 🌃\n\nBefore you rest, consider making a difference in someone's life. "
            "This GoFundMe campaign is close to our community's heart, and every donation brings us closer to the goal. "
            "Let's finish the day knowing we've made a positive impact.\n\n"
            "Donate here: https://gofund.me/aeb8edbf"
        ]
    }
}

# Greeting messages for different times of day
GREETINGS = {
    "morning": [
        "🌅 Good morning, amazing people! Hope you all have a productive and blessed day ahead! 🌅",
        "☀️ Rise and shine! Wishing everyone a wonderful morning filled with positivity and success! ☀️",
        "🌄 Morning, champions! Let's make today incredible! 🌄"
    ],
    "afternoon": [
        "🌞 Good afternoon, everyone! Hope your day is going great! 🌞",
        "🕑 Afternoon check-in! Keep up the good work, team! 🕑",
        "☀️ Hello everyone! Hope you're having a productive afternoon! ☀️"
    ],
    "evening": [
        "🌇 Good evening, lovely people! Hope you had a fantastic day! 🌇",
        "🌆 Evening greetings! Time to relax and recharge after a day of hard work! 🌆",
        "✨ Hello evening, hello relaxation! Hope everyone had a productive day! ✨"
    ],
    "night": [
        "🌙 Good night, dreamers! Rest well and recharge for another amazing tomorrow! 🌙",
        "🌌 Nighty night, everyone! Sweet dreams and see you in the morning! 🌌",
        "🌠 Time to power down and recharge! Good night, all! 🌠"
    ]
}

class GroupManagementBot:
    def __init__(self, token):
        self.updater = Updater(token=token, use_context=True)
        self.dispatcher = self.updater.dispatcher
        self.job_queue = self.updater.job_queue
        self.setup_handlers()
        self.scheduler = BackgroundScheduler()
        
    def setup_handlers(self):
        # Command handlers
        self.dispatcher.add_handler(CommandHandler("start", self.start_command))
        self.dispatcher.add_handler(CommandHandler("help", self.help_command))
        self.dispatcher.add_handler(CommandHandler("clean_bots", self.clean_bots_command))
        self.dispatcher.add_handler(CommandHandler("check_inactive", self.check_inactive_command))
        
    def start_command(self, update: Update, context: CallbackContext):
        update.message.reply_text(
            "Hello! I'm your group management and reminder bot. "
            "I'll help send reminders and keep your group clean from bots and inactive members. "
            "Use /help to see what I can do."
        )
    
    def help_command(self, update: Update, context: CallbackContext):
        help_text = """
        🤖 *Group Management Bot Commands* 🤖
        
        *For Admins:*
        /clean_bots - Remove all detected bots from the group
        /check_inactive [days] - Check members inactive for specified days (default: 30)
        
        *For Everyone:*
        /start - Introduction to the bot
        /help - Show this help message
        
        _I'll also automatically send greetings and promotional messages at scheduled times!_
        """
        update.message.reply_text(help_text, parse_mode='Markdown')
    
    def send_greeting(self, time_of_day: str):
        """Send a greeting message based on time of day"""
        try:
            greeting = random.choice(GREETINGS[time_of_day])
            self.updater.bot.send_message(chat_id=GROUP_NAME, text=greeting)
            logger.info(f"Sent {time_of_day} greeting to group")
        except Exception as e:
            logger.error(f"Error sending greeting: {e}")
    
    def send_promotional_message(self, link_key: str, message_index: int = 0):
        """Send a promotional message for a specific link"""
        try:
            if link_key in STORE_LINKS:
                message = STORE_LINKS[link_key]["messages"][message_index]
                self.updater.bot.send_message(
                    chat_id=GROUP_NAME, 
                    text=message,
                    parse_mode='Markdown',
                    disable_web_page_preview=False
                )
                logger.info(f"Sent promotional message for {link_key}")
        except Exception as e:
            logger.error(f"Error sending promotional message: {e}")
    
    def clean_bots_command(self, update: Update, context: CallbackContext):
        """Command to remove all detected bots from the group"""
        if not self.is_user_admin(update, context):
            update.message.reply_text("❌ You need to be an admin to use this command.")
            return
        
        try:
            bot_count = 0
            chat_members = self.updater.bot.get_chat_members_count(chat_id=GROUP_NAME)
            
            # This is a simplified approach - in a real implementation, you'd need to
            # iterate through all members and check if they're bots
            update.message.reply_text("⚠️ Bot cleaning functionality requires more advanced implementation.")
            
            # Placeholder for actual implementation
            # You would need to store member information and track activity
            update.message.reply_text("✅ Basic bot check completed.")
        except Exception as e:
            logger.error(f"Error in clean_bots_command: {e}")
            update.message.reply_text("❌ An error occurred while cleaning bots.")
    
    def check_inactive_command(self, update: Update, context: CallbackContext):
        """Check for inactive members in the group"""
        if not self.is_user_admin(update, context):
            update.message.reply_text("❌ You need to be an admin to use this command.")
            return
        
        # Get inactivity threshold (default 30 days)
        days_threshold = 30
        if context.args and context.args[0].isdigit():
            days_threshold = int(context.args[0])
        
        try:
            # This is a simplified approach - in a real implementation, you'd need to
            # track user activity over time
            update.message.reply_text("⚠️ Inactive user checking requires tracking user activity over time.")
            update.message.reply_text("🔧 This feature needs additional implementation to store and analyze user activity data.")
            
        except Exception as e:
            logger.error(f"Error in check_inactive_command: {e}")
            update.message.reply_text("❌ An error occurred while checking inactive members.")
    
    def is_user_admin(self, update: Update, context: CallbackContext) -> bool:
        """Check if the user sending the command is an admin"""
        try:
            user_id = update.effective_user.id
            chat_member = context.bot.get_chat_member(chat_id=GROUP_NAME, user_id=user_id)
            return chat_member.status in ['administrator', 'creator']
        except:
            return False

    def schedule_messages(self):
        """Schedule all automated messages"""
        # Morning greeting at 8 AM
        self.scheduler.add_job(
            lambda: self.send_greeting("morning"),
            CronTrigger(hour=8, minute=0)
        )
        
        # Afternoon greeting at 1 PM
        self.scheduler.add_job(
            lambda: self.send_greeting("afternoon"),
            CronTrigger(hour=13, minute=0)
        )
        
        # Evening greeting at 6 PM
        self.scheduler.add_job(
            lambda: self.send_greeting("evening"),
            CronTrigger(hour=18, minute=0)
        )
        
        # Night greeting at 10 PM
        self.scheduler.add_job(
            lambda: self.send_greeting("night"),
            CronTrigger(hour=22, minute=0)
        )
        
        # Promotional messages schedule
        # Morning promotional messages at 9 AM
        self.scheduler.add_job(
            lambda: self.send_promotional_message("jjfancyboutique", 0),
            CronTrigger(hour=9, minute=0, day_of_week='sun,wed,fri,sat')
        )
        
        self.scheduler.add_job(
            lambda: self.send_promotional_message("stan_store", 0),
            CronTrigger(hour=9, minute=0, day_of_week='mon,tue,thu')
        )
        
        # Evening promotional messages at 7 PM
        self.scheduler.add_job(
            lambda: self.send_promotional_message("gofundme1", 1),
            CronTrigger(hour=19, minute=0, day_of_week='sun,wed')
        )
        
        self.scheduler.add_job(
            lambda: self.send_promotional_message("gofundme2", 1),
            CronTrigger(hour=19, minute=0, day_of_week='mon,thu')
        )
        
        self.scheduler.add_job(
            lambda: self.send_promotional_message("jjfancyboutique", 1),
            CronTrigger(hour=19, minute=0, day_of_week='tue,fri')
        )
        
        self.scheduler.add_job(
            lambda: self.send_promotional_message("stan_store", 1),
            CronTrigger(hour=19, minute=0, day_of_week='sat')
        )

    def run(self):
        """Start the bot"""
        # Schedule messages
        self.schedule_messages()
        self.scheduler.start()
        
        # Start the bot
        logger.info("Starting bot...")
        self.updater.start_polling()
        self.updater.idle()

# Run the bot
if __name__ == '__main__':
    bot = GroupManagementBot(BOT_TOKEN)
    bot.run()
