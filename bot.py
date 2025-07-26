"""
بوت SafeLinker لفحص الروابط عبر VirusTotal
------------------------------------------
هذا البوت يقوم بالمهام التالية:
1. استقبال أي رابط من المستخدم.
2. إرسال الرابط إلى واجهة VirusTotal API لفحصه.
3. الانتظار حتى يكتمل الفحص واسترجاع النتيجة.
4. حساب نسبة الأمان والخطر وعرض تقرير كامل للمستخدم.
5. تصنيف النتيجة (آمن، مشبوه، خطر) باستخدام ألوان/إيموجي.

المتطلبات:
- pyTelegramBotAPI للتعامل مع تيليغرام.
- vt-py للتعامل مع VirusTotal API.
- مفتاح API من VirusTotal (مجاني بعد التسجيل).
- توكن بوت من BotFather في تيليغرام.
"""

import telebot
import asyncio
import vt

TOKEN = "8455216093:AAEwv31E-bpv995VnijQEn3mA0p4qyNCNTc"
VT_API_KEY = "2775f96a0b71e785e6fafaa2e64e481f2662580b66a23a14c99210420b77dd6b"
bot = telebot.TeleBot(TOKEN)

# إنشاء كائن البوت
bot = telebot.TeleBot(TOKEN)


# ======= دالة لتصنيف النتيجة =======
def classify_risk(safe, danger):
    """تحديد مستوى الخطر حسب النسب"""
    if danger == 0:
        return "🟢 آمن تماماً"
    elif danger <= 10:
        return "🟡 مشبوه قليلاً، توخَّ الحذر"
    else:
        return "🔴 خطر عالي! تجنّب الرابط"


# ======= دالة فحص الرابط عبر VirusTotal =======
async def scan_url(url):
    async with vt.Client(VT_API_KEY) as client:
        # إرسال الرابط للفحص
        analysis = await client.scan_url_async(url)

        # إعادة محاولة الحصول على النتيجة حتى تكتمل
        for _ in range(10):  # 10 محاولات = 50 ثانية تقريباً
            result = await client.get_object_async(f"/analyses/{analysis.id}")
            if result.status == "completed":
                stats = result.stats
                harmless = stats.get("harmless", 0)
                malicious = stats.get("malicious", 0)
                suspicious = stats.get("suspicious", 0)

                total = harmless + malicious + suspicious
                if total == 0:
                    total = 1  # لتجنب القسمة على صفر

                safe_percent = round((harmless / total) * 100, 2)
                danger_percent = round(((malicious + suspicious) / total) * 100, 2)

                report_link = f"https://www.virustotal.com/gui/url/{analysis.id}"
                return safe_percent, danger_percent, report_link

            # لو النتيجة لم تكتمل، انتظر 5 ثواني وأعد المحاولة
            await asyncio.sleep(5)

        # لو ما اكتملت النتيجة
        return 0, 0, f"https://www.virustotal.com/gui/url/{analysis.id}"


# ======= دالة التعامل مع الرسائل =======
@bot.message_handler(func=lambda message: message.text and message.text.startswith("http"))
def handle_url(message):
    """تستقبل الرابط من المستخدم وتفحصه"""
    url = message.text
    bot.send_message(message.chat.id, "🔍 جاري فحص الرابط، يرجى الانتظار...")

    # استخدام asyncio لتشغيل الفحص غير المتزامن
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    safe, danger, report = loop.run_until_complete(scan_url(url))

    # تصنيف النتيجة
    status = classify_risk(safe, danger)

    # إرسال النتيجة للمستخدم
    bot.send_message(
        message.chat.id,
        f"**نتيجة الفحص:**\n"
        f"نسبة الأمان: {safe}%\n"
        f"نسبة الخطر: {danger}%\n"
        f"{status}\n\n"
        f"[عرض التقرير الكامل]({report})",
        parse_mode="Markdown"
    )


# ======= رسالة ترحيب عند /start =======
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(
        message.chat.id,
        "👋 أهلاً بك في بوت **SafeLinker**!\n"
        "أرسل أي رابط (يبدأ بـ http أو https) وسأقوم بفحصه عبر VirusTotal وأخبرك إذا كان آمنًا أو مشبوهًا."
    )

from flask import Flask
import threading

app = Flask(__name__)

@app.route('/')
def home():
    return "SafeLinker Bot is running!"

def run_web():
    app.run(host='0.0.0.0', port=10000)

threading.Thread(target=run_web).start()
# ======= تشغيل البوت =======
bot.polling(none_stop=True)