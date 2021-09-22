import asyncio

from bot import bot, HU_APP
from pyromod import listen
from asyncio.exceptions import TimeoutError

from pyrogram import filters, Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import (
    SessionPasswordNeeded, FloodWait,
    PhoneNumberInvalid, ApiIdInvalid,
    PhoneCodeInvalid, PhoneCodeExpired
)

API_TEXT = """Hi, {}.
Bot ini dapat digunakan untuk mencari String Pyrogram\n
Oleh @FJ_GAMING


Kirim api nya ya `API_ID` yang sama dengan `APP_ID` untuk dapatkan string."""
HASH_TEXT = "Sekarang kirim `API_HASH`.\n\n klik /cancel Untuk membatalkan tugas."
PHONE_NUMBER_TEXT = (
    "Sekarang kirim no telegram mu dengan format internasional.\n"
    "Termasuk kode negara. Contoh: **+14154566376**\n\n"
    "Klik /cancel Untuk membatalkan tugas."
)

@bot.on_message(filters.private & filters.command ("start"))
async def genStr(_, msg: Message):
    chat = msg.chat
    api = await bot.ask(
        chat.id, API_TEXT.format(msg.from_user.mention)
    )
    if await is_cancel(msg, api.text):
        return
    try:
        check_api = int(api.text)
    except Exception:
        await msg.reply("`API_ID` Salah ngab.\nTekan /start Ulagi ngab.")
        return
    api_id = api.text
    hash = await bot.ask(chat.id, HASH_TEXT)
    if await is_cancel(msg, hash.text):
        return
    if not len(hash.text) >= 30:
        await msg.reply("`API_HASH` Salah ngab.\nKlik /start to Coba lagi ngab.")
        return
    api_hash = hash.text
    while True:
        number = await bot.ask(chat.id, PHONE_NUMBER_TEXT)
        if not number.text:
            continue
        if await is_cancel(msg, number.text):
            return
        phone = number.text
        confirm = await bot.ask(chat.id, f'`yakin "{phone}" sudah benar? (y/n):` \n\nKetik: `y` (untuk ya)\nKetik: `n` (untuk No)')
        if await is_cancel(msg, confirm.text):
            return
        if "y" in confirm.text:
            break
    try:
        client = Client("my_account", api_id=api_id, api_hash=api_hash)
    except Exception as e:
        await bot.send_message(chat.id ,f"**ERROR:** `{str(e)}`\nKetik /start Ulangi ngab.")
        return
    try:
        await client.connect()
    except ConnectionError:
        await client.disconnect()
        await client.connect()
    try:
        code = await client.send_code(phone)
        await asyncio.sleep(1)
    except FloodWait as e:
        await msg.reply(f"Terlalu banyak mencoba,coba lagi nanti {e.x} detik")
        return
    except ApiIdInvalid:
        await msg.reply("API ID and API Hash Tidak ada.\n\nKlik /start Silahkan coba lagi.")
        return
    except PhoneNumberInvalid:
        await msg.reply("Nomor tidak valid.\n\nKlik /start dan Coba lagi.")
        return
    try:
        otp = await bot.ask(
            chat.id, ("Kode OTP Sudah di kirim ke nomermu ngab, "
                      "Masukan OTP dengan format `1 2 3 4 5` format. __(Kasih jarak 1 spasi!)__ \n\n"
                      "If Bot tidak mengirim OTP silahkan Coba lagi /restart dan start lagi ngab /start command ke bot.\n"
                      "Tekan /cancel untuk berhenti."), timeout=300)

    except TimeoutError:
        await msg.reply("Waktu habis, sudah 5 min.\nTekan /start dan Coba lagi.")
        return
    if await is_cancel(msg, otp.text):
        return
    otp_code = otp.text
    try:
        await client.sign_in(phone, code.phone_code_hash, phone_code=' '.join(str(otp_code)))
    except PhoneCodeInvalid:
        await msg.reply("Kode salah .\n\nKlik /start silahkan Coba lagi.")
        return
    except PhoneCodeExpired:
        await msg.reply("Kode kadaluarsa.\n\nKlik /start dan Coba lagi.")
        return
    except SessionPasswordNeeded:
        try:
            two_step_code = await bot.ask(
                chat.id, 
                "sesi dua langkah diaktifkan.\nKirim Password.\n\nKlik /cancel Untuk berhenti.",
                timeout=300
            )
        except TimeoutError:
            await msg.reply("`Waktu sudah melebihi batas 5 min.\n\nKlik /start dan Coba lagi.`")
            return
        if await is_cancel(msg, two_step_code.text):
            return
        new_code = two_step_code.text
        try:
            await client.check_password(new_code)
        except Exception as e:
            await msg.reply(f"**ERROR:** `{str(e)}`")
            return
    except Exception as e:
        await bot.send_message(chat.id ,f"**ERROR:** `{str(e)}`")
        return
    try:
        session_string = await client.export_session_string()
        await client.send_message("me", f"#PYROGRAM #STRING_SESSION\n\n```{session_string}``` \n\nBy [@Get_String_Pyrogrambot] \nOwner bot @FJ_GAMING")
        await client.disconnect()
        text = "String sukses di buat.\nKlik button."
        reply_markup = InlineKeyboardMarkup(
            [[InlineKeyboardButton(text="Lihat String Session", url=f"tg://openmessage?user_id={chat.id}")]]
        )
        await bot.send_message(chat.id, text, reply_markup=reply_markup)
    except Exception as e:
        await bot.send_message(chat.id ,f"**ERROR:** `{str(e)}`")
        return


@bot.on_message(filters.private & filters.command("restart"))
async def restart(_, msg: Message):
    await msg.reply("Mulai ulang!")
    HU_APP.restart()


@bot.on_message(filters.private & filters.command("help"))
async def restart(_, msg: Message):
    out = f"""
Hi, {msg.from_user.mention}. Ini Bot pembuat string. \
Saya berikan `STRING_SESSION` untuk UserBot anda.

Saya minat `API_ID`, `API_HASH`, Nomer hp untuk verifikasi kode. \
Yang di kirim ke telegram anda.
Anda dapat kirim **OTP** dengan `1 2 3 4 5` untuk format. __(Kasih jarak 1 spasi!)__

**NOTE:** Jika bot tidak mengirim kode OTP ke telegram mu coba klik /restart lalu coba lagi terus /start untuk mulai lagi. 

Anda kalau mau tau Bot Updates join channelnya ya !!
"""
    reply_markup = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton('Channel', url='https://t.me/TeamKingUserbot'),
                InlineKeyboardButton('Developer', url='https://t.me/FJ_GAMING')
            ],
            [
                InlineKeyboardButton('Bots Updates Group', url='https://t.me/KingUserbotSupport'),
                InlineKeyboardButton('Github', url='https://github.com/fjgaming212/String_Session_Pyrogram')
            ],
        ]
    )
    await msg.reply(out, reply_markup=reply_markup)


async def is_cancel(msg: Message, text: str):
    if text.startswith("/cancel"):
        await msg.reply("Proses di batalkan.")
        return True
    return False

if __name__ == "__main__":
    bot.run()
