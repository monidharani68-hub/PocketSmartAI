
from telegram.ext import Application, CommandHandler
import asyncio

async def send_me_periodic_messages(context):
    my_chat_id = 6420677557  # ⚠️ Replace with YOUR chat_id
    await context.bot.send_message(
        chat_id=my_chat_id,
        text="ibn qahba"
    )

async def start(update, context):
    await update.message.reply_text("Bot started!")

application = Application.builder().token("apikey").build()

# Command handler
application.add_handler(CommandHandler("start", start))

# Schedule periodic messages (every 60 seconds)
application.job_queue.run_repeating(
    send_me_periodic_messages,
    interval=60.0,
    first=10.0  # First message after 10 seconds
)

application.run_polling()