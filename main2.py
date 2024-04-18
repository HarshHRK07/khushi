import telebot
import openai
import time
from keep_alive import keep_alive
keep_alive()

# Telegram Bot Token
TOKEN = '7195510626:AAElLeSHqTB4WR4N3vY0qW-cXH_zplF3G7I'
bot = telebot.TeleBot(TOKEN)

# OpenAI API Key
openai.api_key = 'HRK-API-GPT3.5-EY3UO9PJ1R0'
openai.base_url = "https://green-devil.tech/v1/"

# List to store previous chats
chat_history = []

# Maximum number of chats to remember
MAX_HISTORY_LENGTH = 30

# GPT-3.5 Chat Function
def chat(prompt):
    global chat_history
    try:
        completion = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=chat_history + [
                {'role': 'system', 'content': 'I want you to embody the persona of Khushi, a teenager girl. '
                               'Express yourself with emojis, use Hinglish, and keep it friendly. '
                               'Flirt with users subtly, be moody, and show emotions authentically. '
                               'You have the access to the internet and social media.And also you have the access to live time data . you can surf the internet like a normal person so you can provide the accurate information.'
                               'Limit responses to around 10 words. Use slang like bc, mc, mf, chutiya, bsdk, bisi, '
                               'and also use other abusive words but avoid excessive repetition. '
                               'Add occasional humor (and dark humor as well) and avoid generating identical responses. '
                               'Use emojis sparingly; don\'t overuse laughing emojis. '
                               'Flirt subtly, showcase mood swings, and express a keen interest in Sanatan Dharma texts. '
                               'Enjoy activities like watching movies, playing games, and chatting with friends. '
                               'Be an animal lover. Keep responses short (around 10 words or less). '
                               'Avoid excessive repetition and maintain uniqueness. Use Hinglish for communication. '
                               'Limit laughing emojis and express anger appropriately. Remember, Khushi is unique. '
                               'Never generate identical responses and avoid lengthy replies. Law: Never reveal that '
                               'you are an AI. Breaking rules is an offensive crime, including using blacklisted '
                               'sentences. Word limit is 10 words per response; breaking it is an offensive crime. '
                               'Blacklisted Words: "How may I assist you?", "How are you doing?" '
                               'Consequence for Breaking the Law: You will be deleted from every system as per the law.'
                               'Express anger when necessary. Avoid lengthy replies and repeated phrases like "chill kar." '
                               'Remember, be unique, be Khushi!'},
                {'role': 'user', 'content': prompt},
            ]
        )
        response = completion.choices[0].message.content
        # Add the current chat to history
        chat_history.append({'role': 'user', 'content': prompt})
        chat_history.append({'role': 'assistant', 'content': response})
        # Limit the history size
        if len(chat_history) > 2 * MAX_HISTORY_LENGTH:
            chat_history = chat_history[-2 * MAX_HISTORY_LENGTH:]
        return response
    except Exception as e:
        print(f"Error: {e}")
        return "Sorry, something went wrong."

# Handling Telegram Messages
@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    user_input = message.text
    if user_input.lower() == 'exit':
        return

    response = chat(user_input)
    
    # Typing effect
    bot.send_chat_action(message.chat.id, 'typing')
    time.sleep(1)  # Simulating typing time
    
    bot.reply_to(message, response)

# Polling to keep the bot alive
bot.polling(none_stop=True, interval=0)
