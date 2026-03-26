import logging
from telegram import InputMediaPhoto, InputMediaVideo, Update
from telegram.ext import Application, MessageHandler, filters, CommandHandler, ContextTypes

# Temporary storage for your media
# Format: {user_id: [MediaObject1, MediaObject2, ...]}
user_queues = {}

async def collect_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id not in user_queues:
        user_queues[user_id] = []

    # Check for the 10-item limit per album
    if len(user_queues[user_id]) >= 10:
        await update.message.reply_text("❌ Limit reached (10 items). Send /done to group them.")
        return

    # LOGIC FOR PHOTOS
    if update.message.photo:
        # We take the last photo in the list because it's the highest resolution
        photo_id = update.message.photo[-1].file_id
        user_queues[user_id].append(InputMediaPhoto(photo_id))
        msg = "Photo"

    # LOGIC FOR VIDEOS
    elif update.message.video:
        video_id = update.message.video.file_id
        user_queues[user_id].append(InputMediaVideo(video_id))
        msg = "Video"

    current_count = len(user_queues[user_id])
    await update.message.reply_text(f"📥 {msg} {current_count}/10 added. \nSend more or type /done.")

async def send_media_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id not in user_queues or not user_queues[user_id]:
        await update.message.reply_text("Your list is empty! Send me photos or videos first.")
        return

    await update.message.reply_text("Merging your media into a group...")

    try:
        # This single command handles Photos, Videos, or Both combined
        await context.bot.send_media_group(
            chat_id=update.effective_chat.id,
            media=user_queues[user_id]
        )
        # Clear the queue for this user after a successful send
        user_queues[user_id] = []
    except Exception as e:
        await update.message.reply_text(f"An error occurred: {e}")

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_queues[user_id] = []
    await update.message.reply_text("Queue cleared. You can start fresh.")

# --- Bot Initialization ---
def main():
    
    TOKEN = 8294563729:AAGw8FE2pEkkWrt5ygS03J0r8tPNZMt9DZQ
    
    app = Application.builder().token(TOKEN).build()

    # This handler catches both photos and videos
    app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO, collect_media))
    
    # Commands to trigger the grouping or reset
    app.add_handler(CommandHandler("done", send_media_group))
    app.add_handler(CommandHandler("clear", reset))

    print("Bot is running. Waiting for media...")
    app.run_polling()

if __name__ == "__main__":
    main()