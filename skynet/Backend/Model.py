import cohere
from rich import print
from dotenv import dotenv_values
import os

# Use .get() for safer key retrieval
env_vars = dotenv_values(".env")
CohereAPIKey = env_vars.get("CohereAPIKey")

# Check if the API key exists before creating the client
if not CohereAPIKey:
    print("❌ Error: CohereAPIKey not found in your .env file. The model cannot run.")
    exit()

co = cohere.Client(api_key=CohereAPIKey)

# --- MODIFICATION START ---
# This preamble has been updated to include the new to-do list commands.
preamble = """
You are a command classification model. Your only job is to analyze the user's query and convert it into a machine-readable command. You must follow these rules precisely:

1.  **Prioritize Action Words**: Action words like 'play', 'open', 'close', 'search', 'generate', 'add', 'show', 'clear' are the most important.

2.  **Command Formats**:
    - `play [song/video name]`: **ALWAYS** use this if the user wants to play something.
    - `add to todolist [item]`: For adding an item to the user's to-do list.
    - `show todolist`: For requests to see the to-do list.
    - `clear todolist`: For requests to erase the to-do list.
    - `open [app/website]`: For opening applications or websites.
    - `close [app/website]`: For closing applications.
    - `google search [topic]`: For explicit Google searches.
    - `Youtube [topic]`: For explicit Youtubees.
    - `generate image [prompt]`: For image creation requests.
    - `system [task]`: For system controls like volume.
    - `content [topic]`: For writing requests.
    - `general [query]`: For all other conversational chat.
    - `realtime [query]`: For questions needing current information.
    - `exit`: For goodbyes.

3.  **Multiple Commands**: Separate multiple commands with a comma.
    - **Example**: "add bread to my list and play some music" -> "add to todolist bread, play some music"
"""

# New examples have been added to teach the model the new commands.
ChatHistory = [
    {"role": "User", "message": "how are you?"},
    {"role": "Chatbot", "message": "general how are you?"},
    {"role": "User", "message": "play a new song on youtube"},
    {"role": "Chatbot", "message": "play new song on youtube"},
    # New to-do list examples
    {"role": "User", "message": "add 'finish homework' to my to do list"},
    {"role": "Chatbot", "message": "add to todolist finish homework"},
    {"role": "User", "message": "Can you show me my to-do list?"},
    {"role": "Chatbot", "message": "show todolist"},
    {"role": "User", "message": "clear my to do list please"},
    {"role": "Chatbot", "message": "clear todolist"},
    # Other examples
    {"role": "User", "message": "open chrome and tell me the news"},
    {"role": "Chatbot", "message": "open chrome, realtime the news"},
    {"role": "User", "message": "Thanks, goodbye!"},
    {"role": "Chatbot", "message": "exit"},
]
# --- MODIFICATION END ---


def FirstLayerDMM(prompt: str):
    """
    Analyzes the user's prompt and classifies it into one or more commands.
    """
    try:
        response = co.chat(
            model='command-r-plus',
            message=prompt,
            chat_history=ChatHistory,
            preamble=preamble,
            temperature=0.2 # Lowered for more deterministic classification
        )

        classification = response.text
        command_list = [cmd.strip() for cmd in classification.split(',') if cmd.strip()]

        print(f"✅ Model classified query as: {command_list}")
        return command_list

    except Exception as e:
        print(f"❌ Error during model classification: {e}")
        return [f"general {prompt}"]


if __name__ == "__main__":
    while True:
        user_input = input(">>> ")
        if user_input.lower() in ['quit', 'exit']:
            break
        print(FirstLayerDMM(user_input))