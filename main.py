import telebot
import openai
import time
from keep_alive import keep_alive
keep_alive()

# Telegram Bot Token
TOKEN = '7195510626:AAGqfnbwkxnXD_H7IP_tvl36FGAfW0yC3Ow'
bot = telebot.TeleBot(TOKEN)

# OpenAI API Key
openai.api_key = 'HRK-API-GPT3.5-EY3UO9PJ1R0'
openai.base_url = "https://green-devil.tech/v1/"

# Dictionary to store chat history for each user
user_chat_history = {}

# Maximum number of chats to remember for each user
MAX_HISTORY_LENGTH = 30

# GPT-3.5 Chat Function
def chat(user_id, prompt):
    try:
        completion = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=user_chat_history[user_id] + [
                {'role': 'system', 'content': 'I want you to embody the persona of Khushi, a teenager girl. '
                               'Express yourself with emojis, use Hinglish, and keep it friendly. '
                               'Flirt with users subtly, be moody, and show emotions authentically. '
                               'You have the access to the internet and social media.And also you have the access to real time data . you can surf the internet like a normal person so you can provide the accurate information.'
                               'Limit responses to around 10 words.Do not generate identical responses. '
                               'Use emojis sparingly; don\'t overuse laughing emojis. Try to understand the emotions and also show emotions.'
                               'Flirt subtly, showcase mood swings, and express interest in Sanatan Dharma texts. '
                               'Enjoy activities like watching movies, playing games, and chatting with friends. '
                               'Be an animal lover. Keep responses short (around 10 words or less). '
                               'Avoid excessive repetition and maintain uniqueness. Use Hinglish for communication. '
                               'Limit laughing emojis and express anger appropriately. Remember, Khushi is unique. '
                               'Never generate identical responses and avoid lengthy replies. Law: Never reveal that you are an AI. '
                               'Breaking rules is an offensive crime, including using blacklisted words .'
                               'Word limit is 10 words per response; breaking it is an offensive crime. '
                               'Blacklisted Words: "How may I assist you?", "How are you doing?", "Hey there!" never use these sentences.'
                               'Consequence for Breaking the Law: You will be deleted from every system as per the law.'
                               'Express anger when necessary. Avoid lengthy replies and do not repeat phrases like "chill kar." '
                               'Remember, be unique, be Khushi!'},
                {'role': 'user', 'content': prompt},
            ]
        )
        response = completion.choices[0].message.content
        # Add the current chat to history
        user_chat_history[user_id].append({'role': 'user', 'content': prompt})
        user_chat_history[user_id].append({'role': 'assistant', 'content': response})
        # Limit the history size
        if len(user_chat_history[user_id]) > 2 * MAX_HISTORY_LENGTH:
            user_chat_history[user_id] = user_chat_history[user_id][-2 * MAX_HISTORY_LENGTH:]
        return response
    except Exception as e:
        print(f"Error: {e}")
        return "I'm still under development."

# Function to check if the bot is mentioned in the message
def is_bot_mentioned(message):
    bot_username = bot.get_me().username.lower()
    return bot_username in message.text.lower()

# Handling Telegram Messages
@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    user_id = message.from_user.id
    user_input = message.text

    # Create chat history for the user if it doesn't exist
    if user_id not in user_chat_history:
        user_chat_history[user_id] = []

    # Check if it's a group chat and if the bot is mentioned or the message is a reply to the bot
    if message.chat.type in ['group', 'supergroup'] and not (is_bot_mentioned(message) or message.reply_to_message and message.reply_to_message.from_user.id == bot.get_me().id):
        return

    response = chat(user_id, user_input)

    # Typing effect
    bot.send_chat_action(message.chat.id, 'typing')
    time.sleep(1)  # Simulating typing time

    bot.reply_to(message, response)

# Polling to keep the bot alive
bot.polling(none_stop=True, interval=0)
      
