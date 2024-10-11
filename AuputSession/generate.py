from telethon import TelegramClient
from pyrogram.types import Message
from pyrogram import Client, filters
from asyncio.exceptions import TimeoutError
from telethon.sessions import StringSession
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import (
    ApiIdInvalid,
    PhoneNumberInvalid,
    PhoneCodeInvalid,
    PhoneCodeExpired,
    SessionPasswordNeeded,
    PasswordHashInvalid
)

from telethon.errors import (
    ApiIdInvalidError,
    PhoneNumberInvalidError,
    PhoneCodeInvalidError,
    PhoneCodeExpiredError,
    SessionPasswordNeededError,
    PasswordHashInvalidError
)

from data import Data


ask_ques = "Please choose the python library you want to generate string session for"
buttons_ques = [
    [
        InlineKeyboardButton("Pyrogram", callback_data="pyrogram"),
        InlineKeyboardButton("Telethon", callback_data="telethon"),
    ],
    [
        InlineKeyboardButton("Pyrogram Bot", callback_data="pyrogram_bot"),
        InlineKeyboardButton("Telethon Bot", callback_data="telethon_bot"),
    ],
]


@Client.on_message(filters.private & ~filters.forwarded & filters.command('generate'))
async def main(_, msg):
    await msg.reply(ask_ques, reply_markup=InlineKeyboardMarkup(buttons_ques))







API_HASH = "efd77b34c69c164ce158037ff5a0d117"  # ضع هنا الـ API_HASH الخاص بك
BOT_TOKEN = "12345:abcdefghijklmnopqrstuvwxyz"  # ضع هنا توكن البوت الخاص بك

async def generate_session(bot: Client, msg: Message, telethon=False, is_bot: bool = False):
    if telethon:
        ty = "Telethon"
    else:
        ty = "Pyrogram v2"
    if is_bot:
        ty += " بوت"
    await msg.edit(f"بدء إنشاء جلسة {ty}...")
    user_id = msg.chat.id


    api_id = API_ID
    api_hash = API_HASH

    if not is_bot:
        t = "الرجاء إرسال `رقم الهاتف` الخاص بك مع رمز الدولة. \nمثال: `+201234567890`"
        phone_number_msg = await bot.ask(user_id, t, filters=filters.text)
        if await cancelled(phone_number_msg):
            return
        phone_number = phone_number_msg.text
    else:

        phone_number = BOT_TOKEN

    if not is_bot:
        await msg.reply("جارٍ إرسال رمز التحقق...")
    else:
        await msg.reply("تسجيل الدخول كبوت...")

    if telethon and is_bot:
        client = TelegramClient(StringSession(), api_id, api_hash)
    elif telethon:
        client = TelegramClient(StringSession(), api_id, api_hash)
    elif is_bot:
        client = Client(name=f"bot_{user_id}", api_id=api_id, api_hash=api_hash, bot_token=phone_number, in_memory=True)
    else:
        client = Client(name=f"user_{user_id}", api_id=api_id, api_hash=api_hash, in_memory=True)


    await client.connect()
    try:
        code = None
        if not is_bot:
            if telethon:
                code = await client.send_code_request(phone_number)
            else:
                code = await client.send_code(phone_number)
    except (ApiIdInvalid, ApiIdInvalidError):
        await msg.reply('تركيبة `API_ID` و `API_HASH` غير صحيحة. يرجى إعادة المحاولة.', reply_markup=InlineKeyboardMarkup(Data.generate_button))
        return
    except (PhoneNumberInvalid, PhoneNumberInvalidError):
        await msg.reply('رقم الهاتف غير صالح. يرجى إعادة المحاولة.', reply_markup=InlineKeyboardMarkup(Data.generate_button))
        return
    try:
        phone_code_msg = None
        if not is_bot:
            phone_code_msg = await bot.ask(user_id, "الرجاء التحقق من رمز التفعيل في <a href=tg://openmessage?user_id=777000>حساب Telegram</a> . إذا استلمته، أرسل الرمز هنا باتباع التنسيق التالي. \nإذا كان الرمز هو `12345`، **يرجى إرساله كـ** `1 2 3 4 5`.", filters=filters.text, timeout=600)
            if await cancelled(phone_code_msg):
                return
    except TimeoutError:
        await msg.reply('انتهت المهلة المحددة (10 دقائق). يرجى إعادة المحاولة.', reply_markup=InlineKeyboardMarkup(Data.generate_button))
        return
    if not is_bot:
        phone_code = phone_code_msg.text.replace(" ", "")
        try:
            if telethon:
                await client.sign_in(phone_number, phone_code, password=None)
            else:
                await client.sign_in(phone_number, code.phone_code_hash, phone_code)
        except (PhoneCodeInvalid, PhoneCodeInvalidError):
            await msg.reply('رمز التحقق غير صحيح. يرجى إعادة المحاولة.', reply_markup=InlineKeyboardMarkup(Data.generate_button))
            return
        except (PhoneCodeExpired, PhoneCodeExpiredError):
            await msg.reply('رمز التحقق منتهي الصلاحية. يرجى إعادة المحاولة.', reply_markup=InlineKeyboardMarkup(Data.generate_button))
            return
        except (SessionPasswordNeeded, SessionPasswordNeededError):
            try:
                two_step_msg = await bot.ask(user_id, 'حسابك يحتوي على تحقق بخطوتين. يرجى إدخال كلمة المرور.', filters=filters.text, timeout=300)
            except TimeoutError:
                await msg.reply('انتهت المهلة المحددة (5 دقائق). يرجى إعادة المحاولة.', reply_markup=InlineKeyboardMarkup(Data.generate_button))
                return
            try:
                password = two_step_msg.text
                if telethon:
                    await client.sign_in(password=password)
                else:
                    await client.check_password(password=password)
            except (PasswordHashInvalid, PasswordHashInvalidError):
                await two_step_msg.reply('كلمة المرور غير صحيحة. يرجى إعادة المحاولة.', quote=True, reply_markup=InlineKeyboardMarkup(Data.generate_button))
                return
    else:
        if telethon:
            await client.start(bot_token=phone_number)
        else:
            await client.sign_in_bot(phone_number)

    if telethon:
        string_session = client.session.save()
    else:
        string_session = await client.export_session_string()

    text = f"**{ty.upper()} STRING SESSION** \n\n`{string_session}` \n\nتم إنشاؤه بواسطة @NezukoStringBot"
    try:
        if not is_bot:
            await client.send_message("me", text)
            await client.join_chat("UputtSupport")
            await client.join_chat("puttaull")
        else:
            await bot.send_message(msg.chat.id, text)
    except KeyError:
        pass

    await client.disconnect()
    await bot.send_message(msg.chat.id, "تم إنشاء جلسة سلسلة بنجاح. \n\nالرجاء التحقق من الرسائل المحفوظة لديك! \n\nبواسطة: @UputtSupport 🐣")





async def cancelled(msg):
    if "/cancel" in msg.text:
        await msg.reply("Cancelled the Process!", quote=True, reply_markup=InlineKeyboardMarkup(Data.generate_button))
        return True
    elif "/restart" in msg.text:
        await msg.reply("Restarted the Bot!", quote=True, reply_markup=InlineKeyboardMarkup(Data.generate_button))
        return True
    elif msg.text.startswith("/"):  # Bot Commands
        await msg.reply("Cancelled the generation process!", quote=True)
        return True
    else:
        return False
