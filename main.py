import logging
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import CommandHandler, CallbackContext, Application
import requests
from datetime import datetime

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Retrieve environment variables
TOKEN = os.getenv("TELEGRAM_API_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# List of URLs to monitor
URLS:list = os.getenv("SERVICE_URLS")

# Check interval in seconds
CHECK_INTERVAL = 60

async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("Bot Started, I will notify you when any of the services are down.")

async def check_service(context: CallbackContext):
    for url in URLS:
        try:
            response = requests.get(url)
            if response.status_code != 200:
                await context.bot.send_message(
                    chat_id=CHAT_ID,
                    text=f"{url} is down \n time: {datetime.utcnow()}\n status code: {response.status_code}"
                )
        except requests.exceptions.RequestException as e:
            await context.bot.send_message(
                chat_id=CHAT_ID,
                text=f"{url} is down \n time: {datetime.utcnow()}\n error: {e}"
            )
        except Exception as e:
            logger.error(e)
            await context.bot.send_message(
                chat_id=CHAT_ID,
                text=f"{url} is down \n time: {datetime.utcnow()}\n error: {e}"
            )

def main():
    application = Application.builder().token(TOKEN).build()

    # Add the /start command handler
    application.add_handler(CommandHandler("start", start))

    # Set up the job queue to run the check_service function every CHECK_INTERVAL seconds
    job_queue = application.job_queue
    job_queue.run_repeating(check_service, interval=CHECK_INTERVAL, first=0)

    # Start the Bot
    application.run_polling()

if __name__ == "__main__":
    main()
