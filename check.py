import requests
import time
import telebot
from threading import Thread
current_price = None  # تعريف المتغير في البداية

# بعد ذلك استخدمه في أي مكان تريده
# API Key الخاص بك
api_key = "JZTk45PqY59FFCDx6q6PFTa9Y6oNIwdxSC5fn4Gb"

# Telegram bot token
telegram_token = "7027736814:AAFeBZuxiekR1_ki9owh9mNxCOuUmGZq2b8"

# إنشاء بوت تليجرام
bot = telebot.TeleBot(telegram_token)

# معرف المسؤول (Admin ID)
admin_id = 5919945751

# قائمة المستخدمين المسجلين
registered_users = []

# رابط الـ API لجلب الأسعار
url = f"https://smslive.pro/stubs/handler_api.php?api_key={api_key}&action=getPrices"

# رمز الدولة لهولندا
country_code = "48"

# رمز الخدمة لأي خدمة أخرى
service_code = "ot"

# متغيرات لتتبع حالات الإشعار
price_notified = False
last_notified_price = None

# فحص السعر وإرسال الإشعار إذا كان السعر 6 روبل
def check_price():
    global price_notified, last_notified_price, current_price
    try:
        response = requests.get(url)
        data = response.json()

        netherlands_prices = data.get(country_code, {}).get(service_code, {})

        for price, count in netherlands_prices.items():
            current_price = float(price)
            if current_price == 6.00 and not price_notified:
                message = "سعر الأرقام الهولندية الآن 6 روبل. يمكنك الشراء الآن!"
                for user in registered_users:
                    bot.send_message(chat_id=user, text=message)
                price_notified = True
                last_notified_price = current_price
            elif current_price != 6.00 and last_notified_price != current_price:
                message = f"السعر الحالي هو {current_price} روبل. سوف يتم إرسال رسالة لك عندما يكون السعر 6 روبل."
                for user in registered_users:
                    bot.send_message(chat_id=user, text=message)
                price_notified = False
                last_notified_price = current_price
        return current_price  # إعادة السعر الحالي لاستخدامه عند الأمر /start

    except ValueError:
        print("فشل في تحويل الاستجابة إلى JSON. تأكد من أن الاستجابة بصيغة JSON.")
    except Exception as e:
        print(f"حدث خطأ أثناء جلب الأسعار: {e}")
    return None

# فحص السعر بشكل دوري
def periodic_check():
    while True:
        check_price()
        time.sleep(60)  # انتظر دقيقة قبل الفحص مرة أخرى

# تشغيل الفحص الدوري في خلفية مستقلة
price_check_thread = Thread(target=periodic_check)
price_check_thread.start()

# التعامل مع الأوامر /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.chat.id
    if user_id not in registered_users:
        registered_users.append(user_id)
        bot.send_message(chat_id=user_id, text="برجاء الإنتظار...")
        
        if current_price is not None:
            bot.send_message(chat_id=user_id, text=f"السعر الحالي هو {current_price} روبل.")
    else:
        bot.send_message(chat_id=user_id, text=f"لم يحدث تغيير في السعر {current_price}.")

# التعامل مع الأوامر /count
@bot.message_handler(commands=['count'])
def count_users(message):
    user_id = message.chat.id
    if user_id == admin_id:
        if registered_users:
            user_list = "\n".join(str(user) for user in registered_users)
            bot.send_message(chat_id=user_id, text=f"المستخدمين المسجلين:\n{user_list}")
        else:
            bot.send_message(chat_id=user_id, text="لا يوجد مستخدمين مسجلين حاليًا.")
    else:
        bot.send_message(chat_id=user_id, text="عذرًا، لا يمكنك استخدام هذه الميزة.")

# بدء البوت
bot.polling()