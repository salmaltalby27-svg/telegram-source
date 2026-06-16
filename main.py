import asyncio
from datetime import datetime
from telethon import TelegramClient, events
from telethon.tl.functions.account import UpdateProfileRequest
import os

api_id = 26521568
api_hash = "679f2bf421ad87978ba5743b2fba85f8"
GEMINI_API_KEY = "ضع_مفتاح_جمناي_هنا"

bot = TelegramClient("session_name", api_id, api_hash)

try:
    from google import genai
    ai_client = genai.Client(api_key=GEMINI_API_KEY)
except ImportError:
    ai_client = None

time_name_running = False
auto_reply_running = False

AI_PROMPT = "أنت مساعد ذكي مدمج في حساب تلجرام الشخصي للمستخدم سالم. سالم غير متصل حالياً بالإنترنت أو مشغول، ومهمتك هي الرد نيابة عنه بذكاء ولباقة. تحدث بلهجة ودية، طبيعية، ومختصرة. تفاعل مع النقاش بشكل حقيقي كأنك صديق أو مساعد شخصي له، وأخبرهم أنك ستنقل رسالتهم لسالم فور عودته."

chat_histories = {}

@bot.on(events.NewMessage(outgoing=True, pattern=r"^\.فحص$"))
async def check_source(event):
    await event.edit("⚡ السورس يعمل بنجاح وبأعلى كفاءة مع الذكاء الاصطناعي يا سالم!")

@bot.on(events.NewMessage(outgoing=True, pattern=r"^\.اسم وقتي تشغيل$"))
async def start_time_name(event):
    global time_name_running
    if time_name_running:
        await event.edit("⚠️ الاسم الوقتي مفعّل بالفعل!")
        return
    time_name_running = True
    await event.edit("⏰ تم تفعيل ميزة الاسم الوقتي بنجاح!\nسيتم تحديث اسمك كل دقيقة بالوقت الحالي.")
    while time_name_running:
        current_time = datetime.now().strftime("%I:%M")
        new_name = f"سالم | {current_time}"
        try:
            await bot(UpdateProfileRequest(first_name=new_name))
        except Exception as e:
            print(f"خطأ: {e}")
        await asyncio.sleep(60)
@bot.on(events.NewMessage(outgoing=True, pattern=r"^\.اسم وقتي ايقاف$"))
async def stop_time_name(event):
    global time_name_running
    if not time_name_running:
        await event.edit("⚠️ الاسم الوقتي متوقف بالفعل!")
        return
    time_name_running = False
    try:
        await bot(UpdateProfileRequest(first_name="سالم"))
        await event.edit("🛑 تم إيقاف الاسم الوقتي وإعادة اسمك الطبيعي.")
    except Exception as e:
        await event.edit(f"❌ خطأ: {e}")

@bot.on(events.NewMessage(outgoing=True, pattern=r"^\.رد تشغيل$"))
async def start_auto_reply(event):
    global auto_reply_running
    if auto_reply_running:
        await event.edit("⚠️ الرد الذكي مفعّل بالفعل!")
        return
    auto_reply_running = True
    await event.edit("🤖 تم تفعيل الرد التلقائي بالذكاء الاصطناعي بنجاح!")

@bot.on(events.NewMessage(outgoing=True, pattern=r"^\.رد ايقاف$"))
async def stop_auto_reply(event): 
    global auto_reply_running
    if not auto_reply_running:
        await event.edit("⚠️ الرد الذكي متوقف بالفعل!")
        return
    auto_reply_running = False
    chat_histories.clear()
    await event.edit("🛑 تم إيقاف الرد الذكي بنجاح. أهلاً بعودتك!")

@bot.on(events.NewMessage(incoming=True))
async def handle_incoming_messages(event):
    global auto_reply_running
    if auto_reply_running and event.is_private:
        sender = await event.get_sender()
        if sender and sender.bot:
            return
        user_id = event.chat_id
        user_message = event.text
        if not user_message or user_message.startswith("."):
            return
        try:
            async with bot.action(event.chat_id, "typing"):
                if ai_client and GEMINI_API_KEY != "ضع_مفتاح_جمناي_هنا":
                    if user_id not in chat_histories:
                        chat_histories[user_id] = ai_client.chats.create(model="gemini-2.5-flash", config={"system_instruction": AI_PROMPT})
                    response = chat_histories[user_id].send_message(user_message)
                    reply_text = response.text
                else:
                    reply_text = "📴 أهلاً بك، سالم غير متصل حالياً وسيعاود الاتصال فور تفرغه."
                await event.reply(reply_text)
        except Exception as e:
            print(f"خطأ: {e}")

print("🤖 جاري تشغيل السورس بنجاح...")
bot.start()
bot.run_until_disconnected()
