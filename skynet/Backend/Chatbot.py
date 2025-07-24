import json
from json import load, dump
from dotenv import dotenv_values
import requests
import datetime
from groq import Groq

env_vars = dotenv_values(".env")

Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")

# Check for the API key and create the client
if not GroqAPIKey:
    print("❌ Error: GroqAPIKey not found in .env file. The chatbot cannot function.")
    client = None
else:
    client = Groq(api_key=GroqAPIKey)

messages = []

System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which also has real-time up-to-date information from the internet.
*** Do not tell time until I ask, do not talk too much, just answer the question.***
*** Reply in only English, even if the question is in Hindi, reply in English.***
*** Do not provide notes in the output, just answer the question and never mention your training data. ***
"""

SystemChatBot = [
    {"role": "system", "content": System}
]

# Load initial chat history safely
try:
    with open(r"Data\ChatLog.json", "r") as f:
        messages = load(f)
except (FileNotFoundError, json.JSONDecodeError):
    # If the file doesn't exist or is empty/corrupted, start with an empty list
    messages = []
    with open(r"Data\ChatLog.json", "w") as f:
        dump([], f)

def RealtimeInformation():
    current_date_time = datetime.datetime.now()
    day = current_date_time.strftime("%A")
    date = current_date_time.strftime("%d")
    month = current_date_time.strftime("%B")
    year = current_date_time.strftime("%Y")
    hour = current_date_time.strftime("%H")
    minute = current_date_time.strftime("%M")
    second = current_date_time.strftime("%S")

    data = f"Please use this real-time information if needed:\n"
    data += f"Day: {day}\nDate: {date}\nMonth: {month}\nYear: {year}\n"
    data += f"Time: {hour} hours, {minute} minutes, {second} seconds.\n"
    return data

def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    modified_answer = '\n'.join(non_empty_lines)
    return modified_answer

def ChatBot(Query):
    """ This function sends the user's query to the chatbot and returns the AI's response """
    if not client:
        return "Chatbot is offline. The Groq API key is missing."

    # The messages list is now managed globally and loaded once.
    messages.append({"role": "user", "content": f"{Query}"})

    try:
        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=SystemChatBot + [{"role": "system", "content": RealtimeInformation()}] + messages,
            max_tokens=1024,
            temperature=0.7,
            top_p=1,
            stream=True,
            stop=None
        )

        Answer = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content

        Answer = Answer.replace("</s>", "")

        # Add the valid assistant response to the history
        messages.append({"role": "assistant", "content": Answer})

        # --- MODIFICATION START ---
        # Save the updated history after a successful interaction
        with open(r"Data\ChatLog.json", "w") as f:
            dump(messages, f, indent=4)
        # --- MODIFICATION END ---

        return Answer

    except Exception as e:
        print(f"An error occurred: {e}")

        # --- MODIFICATION START ---
        # **This is the crucial fix.**
        # If an error occurs, we remove the user's last message that caused the error
        # from our in-memory list, so we don't save a broken conversation.
        # We no longer wipe the entire ChatLog.json file.
        if messages:
            messages.pop()
        # --- MODIFICATION END ---

        # Inform the user of the error without deleting their history
        return "I'm sorry, an error occurred while connecting to the AI service. Please try again."

if __name__ == "__main__":
    while True:
        user_input = input("Enter Your Question: ")
        if user_input.lower() in ['quit', 'exit']:
            break
        response = ChatBot(user_input)
        print(f"{Assistantname}: {response}")