import time
import os
import re
import codecs
from typing import List
from random import randint
from Emli.modules.helper_funcs.chat_status import user_admin
from Emli.modules.disable import DisableAbleCommandHandler
from Emli import (
    dispatcher,
    WALL_API,
)
import requests as r
import wikipedia
from requests import get, post
from telegram import (
    Chat,
    ChatAction,
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ParseMode,
    Message,
    MessageEntity,
    TelegramError,
)
from telegram.error import BadRequest
from telegram.ext.dispatcher import run_async
from telegram.ext import CallbackContext, Filters, CommandHandler
from Emli import StartTime
from Emli.modules.helper_funcs.chat_status import sudo_plus
from Emli.modules.helper_funcs.alternate import send_action, typing_action

MARKDOWN_HELP = f"""
  Markdown is a very powerful formatting tool supported by telegram. {} has some enhancements, to make sure that saved messages are correctly parsed, and to allow you to create buttons.\n
  <b>Supported Markdown:</b>
★  - <code>__italic__</code>: Double underscores will produce <i>italic</i> text.
★  - <code>**bold**</code>: Double asterisks will produce <b>bold</b> text. ★ - <code>`code`</code>: Backticks will produce <code>monospace</code> text.
★- <code>~~strike~~</code>: Double tildes will produce <del>strikethrough</del> text.
★  - <code>--underline--</code> Double Hyphen will produce <u>underline</u> text.
★ - <code>||spoiler||</code>: Double pipes will produce <spoiler>spoiler</spoiler> text.
★  - <code>[sometext](someURL)</code>: this will create a link. the message will just show sometext, and tapping on it will open the page at someURL.
  EG: <code>[test](example.com)</code>
  - <code>[buttontext](buttonurl:someURL)</code>: This is the formatting to create a telegram button. buttontext will be what is displayed on the button, and someurl will be the url to redirect.
  EG: <code>[This is a button](buttonurl:google.com)</code>

★  If you want multiple buttons on the same line, use :same, as such:
  <code>[one](buttonurl://example.com)</code>
  <code>[two](buttonurl://google.com:same)</code>
  This will create two buttons on a single line, instead of one button per line.

  Keep in mind that your message <b>MUST</b> contain some text other than just a button!
filling-format-helper: |
  You can customize the content of a text with the event context as well. For example, you want to mention user who joined the chat.
"""


@user_admin
def echo(update: Update, context: CallbackContext):
    args = update.effective_message.text.split(None, 1)
    message = update.effective_message

    if message.reply_to_message:
        message.reply_to_message.reply_text(
            args[1], parse_mode="MARKDOWN", disable_web_page_preview=True
        )
    else:
        message.reply_text(
            args[1], quote=False, parse_mode="MARKDOWN", disable_web_page_preview=True
        )
    message.delete()


def markdown_help_sender(update: Update):
    update.effective_message.reply_text(MARKDOWN_HELP, parse_mode=ParseMode.HTML)
    update.effective_message.reply_text(
        "Try forwarding the following message to me, and you'll see, and Use #test!"
    )
    update.effective_message.reply_text(
        "/save test This is a markdown test. _italics_, *bold*, code, "
        "[URL](example.com) [button](buttonurl:github.com) "
        "[button2](buttonurl://google.com:same)"
    )


def markdown_help(update: Update, context: CallbackContext):
    if update.effective_chat.type != "private":
        update.effective_message.reply_text(
            "Contact me in pm",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "Markdown help",
                            url=f"t.me/{context.bot.username}?start=markdownhelp",
                        )
                    ]
                ]
            ),
        )
        return
    markdown_help_sender(update)


def wiki(update: Update, context: CallbackContext):
    kueri = re.split(pattern="wiki", string=update.effective_message.text)
    wikipedia.set_lang("en")
    if len(str(kueri[1])) == 0:
        update.effective_message.reply_text("Enter keywords!")
    else:
        try:
            pertama = update.effective_message.reply_text("🔄 Loading...")
            keyboard = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="🔧 More Info...",
                            url=wikipedia.page(kueri).url,
                        )
                    ]
                ]
            )
            context.bot.editMessageText(
                chat_id=update.effective_chat.id,
                message_id=pertama.message_id,
                text=wikipedia.summary(kueri, sentences=10),
                reply_markup=keyboard,
            )
        except wikipedia.PageError as e:
            update.effective_message.reply_text(f"⚠ Error: {e}")
        except BadRequest as et:
            update.effective_message.reply_text(f"⚠ Error: {et}")
        except wikipedia.exceptions.DisambiguationError as eet:
            update.effective_message.reply_text(
                f"⚠ Error\n There are too many query! Express it more!\nPossible query result:\n{eet}"
            )


@send_action(ChatAction.UPLOAD_PHOTO)
def wall(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    msg = update.effective_message
    msg_id = update.effective_message.message_id
    args = context.args
    query = " ".join(args)
    if not query:
        msg.reply_text("Please enter a query!")
        return
    caption = query
    term = query.replace(" ", "%20")
    json_rep = r.get(
        f"https://wall.alphacoders.com/api2.0/get.php?auth={WALL_API}&method=search&term={term}"
    ).json()
    if not json_rep.get("success"):
        msg.reply_text("An error occurred!")

    else:
        wallpapers = json_rep.get("wallpapers")
        if not wallpapers:
            msg.reply_text("No results found! Refine your search.")
            return
        index = randint(0, len(wallpapers) - 1)  # Choose random index
        wallpaper = wallpapers[index]
        wallpaper = wallpaper.get("url_image")
        wallpaper = wallpaper.replace("\\", "")
        context.bot.send_photo(
            chat_id,
            photo=wallpaper,
            caption="Preview",
            reply_to_message_id=msg_id,
            timeout=60,
        )
        context.bot.send_document(
            chat_id,
            document=wallpaper,
            filename="wallpaper",
            caption=caption,
            reply_to_message_id=msg_id,
            timeout=60,
        )


__help__ = """
*Available commands:*

❂ /markdownhelp*:* quick summary of how markdown works in telegram - can only be called in private chats
❂ /paste*:* Saves replied content to `nekobin.com` and replies with a url
❂ /react*:* Reacts with a random reaction 
❂ /ud <word>*:* Type the word or expression you want to search use
❂ /reverse*:* Does a reverse image search of the media which it was replied to.
❂ /wiki <query>*:* wikipedia your query
❂ /pdf *:*  reply to img to create pdf
❂ /cs *:* gets cricket score global
❂ /spwinfo get ◢ Intellivoid• SpamProtection Info
❂ /gps <location>*:* find a location via Google maps
❂ /crypto [currency]
        Get Real Time value from currency given, Like /crypto btc.
❂ /wall <query>*:* get a wallpaper from wall.alphacoders.com
❂ /cash*:* currency converter
 Example:
 `/cash 1 USD INR`  
      _OR_
 `/cash 1 usd inr`
 Output: `1.0 USD = 75.505 INR`


"""

ECHO_HANDLER = DisableAbleCommandHandler(
    "echo", echo, filters=Filters.chat_type.groups, run_async=True)
MD_HELP_HANDLER = CommandHandler("markdownhelp", markdown_help, run_async=True)
WIKI_HANDLER = DisableAbleCommandHandler("wiki", wiki)
WALLPAPER_HANDLER = DisableAbleCommandHandler("wall", wall, run_async=True)

dispatcher.add_handler(ECHO_HANDLER)
dispatcher.add_handler(MD_HELP_HANDLER)
dispatcher.add_handler(WIKI_HANDLER)
dispatcher.add_handler(WALLPAPER_HANDLER)

__mod_name__ = "Extras"
__command_list__ = ["id", "echo", "wiki", "wall"]
__handlers__ = [
    ECHO_HANDLER,
    MD_HELP_HANDLER,
    WIKI_HANDLER,
    WALLPAPER_HANDLER,
]
