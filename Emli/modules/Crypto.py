from pyrogram import filters

from Emli import pbot
from Emli.ex_plugins.errors import capture_err
from Emli.services.keyboard import ikb
from Emli.services.sections import section
from Emli.utils.http import get




@pbot.on_message(filters.command("crypto"))
@capture_err
async def crypto(_, message):
    if len(message.command) < 2:
        return await message.reply("/crypto [currency]")

    currency = message.text.split(None, 1)[1].lower()

    btn = ikb(
        {"Available Currencies": "https://plotcryptoprice.herokuapp.com"},
    )

    m = await message.reply("`Processing...`")

    try:
        r = await get(
            "https://x.wazirx.com/wazirx-falcon/api/v2.0/crypto_rates",
            timeout=5,
        )
    except Exception:
        return await m.edit("[ERROR]: Something went wrong.")

    if currency not in r:
        return await m.edit(
            "[ERROR]: INVALID CURRENCY",
            reply_markup=btn,
        )

    body = {i.upper(): j for i, j in r.get(currency).items()}

    text = section(
        "Current Crypto Rates For " + currency.upper(),
        body,
    )
    await m.edit(text, reply_markup=btn)

__mod_name__ = "Crypto"
