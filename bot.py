import telebot
import os
from docx2pdf import convert

# توكن البوت
TOKEN = "8293825738:AAEmElvMDVzdG6n-ebjTOR-Ul3orF5D21Kc"
bot = telebot.TeleBot(TOKEN)

# إنشاء مجلد لتخزين الملفات المؤقتة
if not os.path.exists("files"):
    os.makedirs("files")

# دالة التحويل من Word إلى PDF
def convert_docx_to_pdf(docx_path, pdf_path):
    output_dir = os.path.dirname(pdf_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    convert(docx_path, pdf_path)

# رسالة ترحيب
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(
        message.chat.id,
        "مرحباً بك في بوت تحويل Word إلى PDF!\n"
        "أرسل أي ملف Word بصيغة .docx وسأحولّه لك مباشرة إلى PDF."
    )

# استقبال ملفات Word وتحويلها
@bot.message_handler(content_types=['document'])
def handle_docs(message):
    file_info = bot.get_file(message.document.file_id)
    file_name = message.document.file_name

    if file_name.endswith(".docx"):
        downloaded_file = bot.download_file(file_info.file_path)
        docx_path = f"files/{file_name}"
        with open(docx_path, "wb") as f:
            f.write(downloaded_file)

        pdf_path = docx_path.replace(".docx", ".pdf")
        convert_docx_to_pdf(docx_path, pdf_path)

        with open(pdf_path, "rb") as pdf_file:
            bot.send_document(message.chat.id, pdf_file, caption="تم التحويل إلى PDF ✔", timeout=120)

        # حذف الملفات المؤقتة
        os.remove(docx_path)
        os.remove(pdf_path)
    else:
        bot.reply_to(message, "أرسل ملف Word بصيغة .docx فقط")

# تشغيل البوت
bot.polling(none_stop=True)
