import logging
import asyncio
from datetime import datetime, time
from typing import List, Dict
from telegram import Update, ChatMember, User
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.constants import ParseMode
import requests
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot configuration
BOT_TOKEN = "8242530682:AAEIrKAuv1OipAwQjgyNHw-d4F1SrGnCGFI"
GROUP_NAME = "@growandhelp"

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
        self.application = Application.builder().token(token).build()
        self.setup_handlers()
        
    def setup_handlers(self):
        # Command handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("clean_bots", self.clean_bots_command))
        self.application.add_handler(CommandHandler("check_inactive", self.check_inactive_command))
        
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "Hello! I'm your group management and reminder bot. "
            "I'll help send reminders and keep your group clean from bots and inactive members. "
            "Use /help to see what I can do."
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        help_text = """
        🤖 <b>Group Management Bot Commands</b> 🤖
        
        <b>For Admins:</b>
        /clean_bots - Remove all detected bots from the group
        /check_inactive [days] - Check members inactive for specified days (default: 30)
        
        <b>For Everyone:</b>
        /start - Introduction to the bot
        /help - Show this help message
        
        <i>I'll also automatically send greetings and promotional messages at scheduled times!</i>
        """
        await update.message.reply_text(help_text, parse_mode=ParseMode.HTML)
    
    async def send_greeting(self, time_of_day: str):
        """Send a greeting message based on time of day"""
        try:
            greeting = np.random.choice(GREETINGS[time_of_day])
            await self.application.bot.send_message(chat_id=GROUP_NAME, text=greeting)
            logger.info(f"Sent {time_of_day} greeting to group")
        except Exception as e:
            logger.error(f"Error sending greeting: {e}")
    
    async def send_promotional_message(self, link_key: str, message_index: int = 0):
        """Send a promotional message for a specific link"""
        try:
            if link_key in STORE_LINKS:
                message = STORE_LINKS[link_key]["messages"][message_index]
                await self.application.bot.send_message(
                    chat_id=GROUP_NAME, 
                    text=message,
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=False
                )
                logger.info(f"Sent promotional message for {link_key}")
        except Exception as e:
            logger.error(f"Error sending promotional message: {e}")
    
    async def clean_bots_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Command to remove all detected bots from the group"""
        if not await self.is_user_admin(update, context):
            await update.message.reply_text("❌ You need to be an admin to use this command.")
            return
        
        try:
            bot_count = 0
            async for member in self.application.bot.get_chat_members(chat_id=GROUP_NAME):
                if member.user.is_bot and member.user.id != self.application.bot.id:
                    try:
                        await self.application.bot.ban_chat_member(
                            chat_id=GROUP_NAME, 
                            user_id=member.user.id
                        )
                        bot_count += 1
                        await asyncio.sleep(0.5)  # Avoid rate limiting
                    except Exception as e:
                        logger.error(f"Could not remove bot {member.user.username}: {e}")
            
            await update.message.reply_text(f"✅ Removed {bot_count} bots from the group.")
        except Exception as e:
            logger.error(f"Error in clean_bots_command: {e}")
            await update.message.reply_text("❌ An error occurred while cleaning bots.")
    
    async def check_inactive_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Check for inactive members in the group"""
        if not await self.is_user_admin(update, context):
            await update.message.reply_text("❌ You need to be an admin to use this command.")
            return
        
        # Get inactivity threshold (default 30 days)
        days_threshold = 30
        if context.args and context.args[0].isdigit():
            days_threshold = int(context.args[0])
        
        try:
            inactive_members = []
            async for member in self.application.bot.get_chat_members(chat_id=GROUP_NAME):
                # Skip bots
                if member.user.is_bot:
                    continue
                
                # Check if user has a last activity date (this is approximate)
                # Note: Telegram doesn't provide exact last activity date for privacy reasons
                # This is a heuristic approach
                if member.user.username and not await self.is_user_active(member.user):
                    inactive_members.append(member.user)
            
            if not inactive_members:
                await update.message.reply_text("✅ No inactive members found!")
                return
            
            # Format response
            response = f"🚫 Found {len(inactive_members)} potentially inactive members (no activity in ~{days_threshold} days):\n\n"
            for user in inactive_members[:10]:  # Show first 10 to avoid message too long
                response += f"• {user.first_name}"
                if user.username:
                    response += f" (@{user.username})"
                response += "\n"
            
            if len(inactive_members) > 10:
                response += f"\n... and {len(inactive_members) - 10} more."
            
            response += f"\nUse /clean_inactive to remove them (if implemented)."
            
            await update.message.reply_text(response)
        except Exception as e:
            logger.error(f"Error in check_inactive_command: {e}")
            await update.message.reply_text("❌ An error occurred while checking inactive members.")
    
    async def is_user_admin(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Check if the user sending the command is an admin"""
        try:
            user_id = update.effective_user.id
            chat_member = await context.bot.get_chat_member(chat_id=GROUP_NAME, user_id=user_id)
            return chat_member.status in [ChatMember.ADMINISTRATOR, ChatMember.OWNER]
        except:
            return False
    
    async def is_user_active(self, user: User) -> bool:
        """Heuristic to check if a user is active (this is approximate)"""
        # This is a simplified check - in a real implementation, you might track
        # user activity through message monitoring or use other indicators
        return True  # Placeholder - implement your own logic based on your needs

    async def schedule_messages(self):
        """Schedule all automated messages"""
        # Morning greeting at 8 AM
        self.application.job_queue.run_daily(
            lambda context: self.send_greeting("morning"),
            time(hour=8, minute=0),
            days=(0, 1, 2, 3, 4, 5, 6)
        )
        
        # Afternoon greeting at 1 PM
        self.application.job_queue.run_daily(
            lambda context: self.send_greeting("afternoon"),
            time(hour=13, minute=0),
            days=(0, 1, 2, 3, 4, 5, 6)
        )
        
        # Evening greeting at 6 PM
        self.application.job_queue.run_daily(
            lambda context: self.send_greeting("evening"),
            time(hour=18, minute=0),
            days=(0, 1, 2, 3, 4, 5, 6)
        )
        
        # Night greeting at 10 PM
        self.application.job_queue.run_daily(
            lambda context: self.send_greeting("night"),
            time(hour=22, minute=0),
            days=(0, 1, 2, 3, 4, 5, 6)
        )
        
        # Promotional messages schedule
        # Morning promotional messages at 9 AM
        self.application.job_queue.run_daily(
            lambda context: self.send_promotional_message("jjfancyboutique", 0),
            time(hour=9, minute=0),
            days=(0, 2, 4, 6)  # Sun, Tue, Thu, Sat
        )
        
        self.application.job_queue.run_daily(
            lambda context: self.send_promotional_message("stan_store", 0),
            time(hour=9, minute=0),
            days=(1, 3, 5)  # Mon, Wed, Fri
        )
        
        # Evening promotional messages at 7 PM
        self.application.job_queue.run_daily(
            lambda context: self.send_promotional_message("gofundme1", 1),
            time(hour=19, minute=0),
            days=(0, 3)  # Sun, Wed
        )
        
        self.application.job_queue.run_daily(
            lambda context: self.send_promotional_message("gofundme2", 1),
            time(hour=19, minute=0),
            days=(1, 4)  # Mon, Thu
        )
        
        self.application.job_queue.run_daily(
            lambda context: self.send_promotional_message("jjfancyboutique", 1),
            time(hour=19, minute=0),
            days=(2, 5)  # Tue, Fri
        )
        
        self.application.job_queue.run_daily(
            lambda context: self.send_promotional_message("stan_store", 1),
            time(hour=19, minute=0),
            days=(6)  # Sat
        )

    def run(self):
        """Start the bot"""
        # Schedule messages
        self.schedule_messages()
        
        # Start the bot
        logger.info("Starting bot...")
        self.application.run_polling()

# Run the bot
if __name__ == '__main__':
    bot = GroupManagementBot(BOT_TOKEN)
    bot.run()
