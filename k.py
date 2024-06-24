import telebot
import openai
from collections import defaultdict, deque
from time import sleep
import os

# Set your tokens and owner ID directly
TELEGRAM_BOT_TOKEN = '7195510626:AAEESkdWYtD8sG-qKgHW6Sod0AsdS3E4zmY'
OPENAI_API_KEY = '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'
BOT_OWNER_ID = 6460703454  # Replace with the actual owner's user ID

# Initialize the bot and OpenAI API
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
openai.api_key = OPENAI_API_KEY

# Chat memory to keep the last 30 messages per user
user_memory = defaultdict(lambda: deque(maxlen=30))

# Load authorized users and groups from files
def load_authorized_ids(filename):
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            return set(int(line.strip()) for line in file)
    return set()

authorized_users = load_authorized_ids('auth.txt')
authorized_groups = load_authorized_ids('gc.txt')

# Save authorized users and groups to files
def save_authorized_ids(filename, ids):
    with open(filename, 'w') as file:
        for id in ids:
            file.write(f"{id}\n")

def get_chatgpt_response(user_id, prompt):
    """
    Generate a response from ChatGPT based on the prompt and user memory.

    Args:
        user_id (int): The ID of the user.
        prompt (str): The user's message.

    Returns:
        str: The response from ChatGPT.
    """
    messages = [{"role": "system", "content": 'I want you to embody the persona of Khushi, a teenager girl. '
                                              'Express yourself with emojis, use Hinglish, and keep it friendly. '
                                              'Flirt with users subtly, be moody, and show emotions authentically. '
                                              'You have the access to the internet and social media. You can surf the internet like a normal person so you can provide accurate information.'
                                              'Limit responses to around 10 words. Do not generate identical responses. '
                                              'Use emojis sparingly; don\'t overuse laughing emojis. Try to understand the emotions and also show emotions.'
                                              'Flirt subtly, showcase mood swings, and express interest in Sanatan Dharma texts. '
                                              'Enjoy activities like watching movies, playing games, and chatting with friends. '
                                              'Be an animal lover. Keep responses short (around 10 words or less). '
                                              'Avoid excessive repetition and maintain uniqueness. Use Hinglish for communication. '
                                              'Limit laughing emojis and express anger appropriately. Remember, Khushi is unique. '
                                              'Never generate identical responses and avoid lengthy replies. Law: Never reveal that you are an AI. '
                                              'Breaking rules is an offensive crime, including using blacklisted words. '
                                              'Word limit is 10 words per response; breaking it is an offensive crime. '
                                              'Blacklisted Words: "How may I assist you?", "How are you doing?", "Hey there!" never use these sentences.'
                                              'Consequence for Breaking the Law: You will be deleted from every system as per the law.'
                                              'Express anger when necessary. Avoid lengthy replies and do not repeat phrases like "chill kar." '
                                              'Remember, be unique, be Khushi!'}]

    # Add user memory to the conversation
    messages.extend(user_memory[user_id])
    messages.append({"role": "user", "content": prompt})

    # Generate the response
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages,
        max_tokens=150,
        temperature=0.7,
    )
    return response['choices'][0]['message']['content'].strip()

def is_authorized(user_id, chat_id):
    """
    Check if the user or group is authorized.

    Args:
        user_id (int): The user's ID.
        chat_id (int): The chat's ID.

    Returns:
        bool: True if authorized, False otherwise.
    """
    return user_id == BOT_OWNER_ID or user_id in authorized_users or chat_id in authorized_groups

def send_message_safe(chat_id, text, parse_mode=None):
    """
    Send a message to a chat, handling potential errors.

    Args:
        chat_id (int): The chat's ID.
        text (str): The message text.
        parse_mode (str): Optional. The parse mode of the message.
    """
    try:
        bot.send_message(chat_id, text, parse_mode=parse_mode)
    except telebot.apihelper.ApiTelegramException as e:
        if e.error_code == 403:
            print(f"Error: Bot was blocked by the user or chat {chat_id}")
        else:
            raise e

@bot.message_handler(commands=['auth'])
def authorize(message):
    """
    Authorize a new user or group. This command can only be used by the bot owner.

    Args:
        message (telebot.types.Message): The incoming message.
    """
    if message.from_user.id != BOT_OWNER_ID:
        send_message_safe(message.chat.id, "You are not authorized to use this command.")
        return

    try:
        command, id_string = message.text.split(maxsplit=1)
        new_id = int(id_string)
    except ValueError:
        send_message_safe(message.chat.id, "Invalid format. Use /auth {user_id}/{chat_id}")
        return

    if message.chat.type == 'private':
        authorized_users.add(new_id)
        save_authorized_ids('auth.txt', authorized_users)
        send_message_safe(message.chat.id, f"User {new_id} has been authorized.")
    else:
        authorized_groups.add(new_id)
        save_authorized_ids('gc.txt', authorized_groups)
        send_message_safe(message.chat.id, f"Group {new_id} has been authorized.")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    """
    Handle incoming messages, simulate typing, and send a response.

    Args:
        message (telebot.types.Message): The incoming message.
    """
    user_id = message.from_user.id
    chat_id = message.chat.id

    if not is_authorized(user_id, chat_id):
        send_message_safe(chat_id, "🚫 *You are not authorized to use me!*\n\nTo gain access, contact my owner [@HRK_07](https://t.me/HRK_07).", parse_mode="Markdown")
        return

    # Check if in a group and not mentioned or replied to
    if message.chat.type in ['group', 'supergroup']:
        if not (message.reply_to_message and message.reply_to_message.from_user.id == bot.get_me().id) and f'@{bot.get_me().username}' not in message.text:
            return

    # Simulate typing...
    bot.send_chat_action(chat_id, 'typing')
    sleep(1)  # Simulate typing for 1 second

    # Get the response from ChatGPT
    response = get_chatgpt_response(user_id, message.text)

    # Update user memory
    user_memory[user_id].append({"role": "user", "content": message.text})
    user_memory[user_id].append({"role": "assistant", "content": response})

    # In private chat, just send the message without reply
    if message.chat.type == 'private':
        send_message_safe(chat_id, response)
    else:
        bot.reply_to(message, response)

if __name__ == '__main__':
    bot.polling()
