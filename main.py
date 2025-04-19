import os
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from instaloader import Instaloader, Post
import logging

# Logging setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Telegram Bot Token and Webhook settings
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
PORT = int(os.getenv('PORT', 8443))  # Default Render port
WEBHOOK_URL = os.getenv('WEBHOOK_URL')  # Set this in Render environment

# Initialize Instaloader
loader = Instaloader()

async def start(update, context):
    await update.message.reply_text('Bhai! Instagram Reels download ke liye mujhe Reel ka URL bhej de. /help ke liye commands dekho!')

async def help_command(update, context):
    await update.message.reply_text('Commands:\n/start - Bot shuru karo\n/help - Yeh menu dekho\nBhejna - Instagram Reel URL (e.g., https://www.instagram.com/reel/abc123/)')

async def download_reel(update, context):
    url = update.message.text
    chat_id = update.message.chat_id

    try:
        logger.info(f"Received URL: {url}")
        await update.message.reply_text('Thodi der ruk, Reel download kar raha hu...')

        # Extract shortcode from URL
        shortcode = url.split('/reel/')[-1].split('/')[0]
        
        # Fetch the post
        post = Post.from_shortcode(loader.context, shortcode)
        
        # Download the video
        if not post.is_video:
            await update.message.reply_text('Bhai, yeh Reel nahi hai!')
            return

        loader.download_post(post, target=f"{chat_id}")
        
        # Send the downloaded video
        with open(f'{chat_id}/{post.shortcode}_REEL.mp4', 'rb') as video:
            await context.bot.send_video(chat_id=chat_id, video=video)

        # Clean up
        for file in os.listdir(f'{chat_id}'):
            os.remove(os.path.join(f'{chat_id}', file))
        os.rmdir(f'{chat_id}')
        logger.info(f"Sent reel to {chat_id}")

    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text('Bhai, kuch gadbad ho gaya. Sahi URL bhej ya thodi der baad try kar.')

def main():
    if not TOKEN or not WEBHOOK_URL:
        logger.error("TELEGRAM_BOT_TOKEN or WEBHOOK_URL not found in environment variables!")
        return

    # Create the Application and register handlers
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_reel))

    # Set webhook
    application.run_webhook(
        listen='0.0.0.0',
        port=PORT,
        url_path=TOKEN,
        webhook_url=f'{WEBHOOK_URL}/{TOKEN}'
    )

if __name__ == '__main__':
    main()
