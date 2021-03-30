"""
Simple Bot to reply to Telegram messages taken from the python-telegram-bot examples.
Deployed using heroku.
Author: liuhh02 https://medium.com/@liuhh02
"""

import logging
from telegram import (Update, ParseMode)
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, PollAnswerHandler
import os
PORT = int(os.environ.get('PORT', 5000))

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)
TOKEN = ''
# try:
#     from token import TOKEN
# except:
#     print("Crear un archivo token.py y agregar dentro una varible TOKEN")
#     # Define a few command handlers. These usually take the two arguments update and
#     # context. Error handlers also receive the raised TelegramError object in error.


def start(update, context):
    """Send a message when the command /start is issued."""
    print("recibido")
    update.message.reply_text(
        'holaaaaa SUPERTORNEO DE AJEDREZ, enviame los nombres de !')


def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text(
        'Manda el nombre de los participantes en el siguiente formato: \n lista:\n Willi,Yumi,Sergio')


def mensaje_handler(update, context):
    """Echo the user message."""
    msj = update.message.text

    if 'lista' in msj:  # traemos los participantes
        participantes = msj.split(':')[1]  # tomamos la segunda parte
        participantes = participantes.split(',')
        update.message.reply_text(
            'Los participantes son: {}'.format(str(participantes)))
    else:
        update.message.reply_text("Formato Erroneo")


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def update_scores(update: Update, context: CallbackContext) -> None:
    """Sends a predefined poll"""
    questions = ["Willi", "Sergio", "Yumi", "Fer", "Maby", "Steven"]
    message = context.bot.send_poll(
        update.effective_chat.id,
        "Quien gano esta ronda?",
        questions,
        is_anonymous=False,
        allows_multiple_answers=True,
    )
    # Save some info about the poll the bot_data for later use in receive_poll_answer
    payload = {
        message.poll.id: {
            "questions": questions,
            "message_id": message.message_id,
            "chat_id": update.effective_chat.id,
            "answers": 0,
        }
    }
    context.bot_data.update(payload)


def receive_poll_answer(update: Update, context: CallbackContext) -> None:
    """Summarize a users poll vote"""
    answer = update.poll_answer
    poll_id = answer.poll_id
    try:
        questions = context.bot_data[poll_id]["questions"]
    # this means this poll answer update is from an old poll, we can't do our answering then
    except KeyError:
        return
    selected_options = answer.option_ids
    answer_string = ""
    for question_id in selected_options:
        if question_id != selected_options[-1]:
            answer_string += questions[question_id] + ","
        else:
            answer_string += questions[question_id]
    context.bot.send_message(
        context.bot_data[poll_id]["chat_id"],
        f"{update.effective_user.mention_html()} actualizo el estado, los ganadores de esta ronda son: {answer_string}!",
        parse_mode=ParseMode.HTML,
    )
    context.bot_data[poll_id]["answers"] += 1
    # Close poll after three participants voted
    if context.bot_data[poll_id]["answers"] == 3:
        context.bot.stop_poll(
            context.bot_data[poll_id]["chat_id"], context.bot_data[poll_id]["message_id"]
        )


def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("update", update_scores))
    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, mensaje_handler))
    dp.add_handler(PollAnswerHandler(receive_poll_answer))
    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    # updater.start_webhook(listen="0.0.0.0",
    #                      port=int(PORT),
    #                      url_path=TOKEN)
    # updater.bot.setWebhook('https://botteelgramajedrez.herokuapp.com/' + TOKEN)

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # is non-blocking and will stop the bot gracefully.
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
