from AppOpener import close, open as appopen
from webbrowser import open as webopen
from pywhatkit import search
from dotenv import dotenv_values
from bs4 import BeautifulSoup
from rich import print
from groq import Groq
import webbrowser
import subprocess
import requests
import keyboard
import asyncio
import os
import urllib.parse
import platform
import random
import json  # <-- Required import for the new feature

env_vars = dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKey")

# This part of your code seems to be related to web scraping, but it is not used in the provided functions.
classes = ["zCubwf", "hgKELc", "LTKOO SY7ric", "ZOLcW", "gsrt vk_bk FzvWSb YwPhnf", "pclqee", "tw-Data-text tw-text-small tw-ta",
           "IZ6rdc", "05uR6d LTKOO", "vlzY6d", "webanswers-webanswers_table_webanswers-table", "dDoNo ikb4Bb gsrt", "sXLa0e",
           "LWkfKe", "VQF4g", "qv3Wpe", "kno-rdesc", "SPZz6b"]

useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36'

# Initialize Groq client only if API key exists
client = None
if GroqAPIKey:
    client = Groq(api_key=GroqAPIKey)

professional_responses = [
    "Your satisfaction is my top priority; feel free to reach out if there's anything else I can help you with.",
    "I'm at your service for any additional questions or support you may need—don't hesitate to ask.",
]

messages = []

SystemChatBot = [{"role": "system", "content": f"Hello, I am {os.environ.get('Username', 'User')}, a content writer. You have to write content like letters, codes, applications, essays, notes, songs, poems, etc."}]


def GoogleSearch(topic):
    search(topic)
    return True


def Content(topic):
    def OpenNotepad(file):
        try:
            default_text_editor = 'notepad.exe'
            subprocess.Popen([default_text_editor, file])
            return True
        except Exception as e:
            print(f"Error opening notepad: {e}")
            return False

    def ContentWriterAI(prompt):
        if not client:
            print("Error: Groq API key not found. Please check your .env file.")
            return "Error: Unable to generate content - API key missing."

        try:
            messages.append({"role": "user", "content": f"{prompt}"})

            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=SystemChatBot + messages,
                max_tokens=2048,
                temperature=0.7,
                top_p=1,
                stream=True,
                stop=None
            )

            answer = ""

            for chunk in completion:
                if chunk.choices[0].delta.content:
                    answer += chunk.choices[0].delta.content

            answer = answer.replace("</s>", "")
            messages.append({"role": "assistant", "content": answer})
            return answer
        except Exception as e:
            print(f"Error generating content: {e}")
            return f"Error: Unable to generate content - {str(e)}"

    topic = topic.replace("content", "").strip()
    content_by_ai = ContentWriterAI(topic)

    data_dir = "Data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        print(f"Created directory: {data_dir}")

    filepath = os.path.join(data_dir, f"{topic.lower().replace(' ', '_')}.txt")

    try:
        with open(filepath, "w", encoding="utf-8") as file:
            file.write(content_by_ai)
        print(f"Content written to: {filepath}")

        OpenNotepad(filepath)
        return True
    except Exception as e:
        print(f"Error writing content to file: {e}")
        return False

def YouTubeSearch(topic):
    try:
        query_encoded = urllib.parse.quote_plus(topic)
        url = f"https://www.youtube.com/results?search_query={query_encoded}"
        print(f"Searching YouTube for: '{topic}' at URL: {url}")
        webbrowser.open(url)
        return True
    except Exception as e:
        print(f"Error opening Youtube: {e}")
        return False

def PlayYoutube(query):
    generic_queries = ["a song on youtube", "song on youtube", "any song", "some music", "a song"]

    if query.lower().strip() in generic_queries:
        print("Generic song request detected. Picking a random song...")
        popular_songs = [
            "Blinding Lights by The Weeknd", "Shape of You by Ed Sheeran",
            "Bohemian Rhapsody by Queen", "Uptown Funk by Mark Ronson ft. Bruno Mars",
            "Someone Like You by Adele", "Hotel California by Eagles",
            "Despacito by Luis Fonsi", "Rolling in the Deep by Adele",
            "Billie Jean by Michael Jackson", "As It Was by Harry Styles"
        ]
        song_to_play = random.choice(popular_songs)
        print(f"Randomly selected: {song_to_play}")
        query = song_to_play

    try:
        search_url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}"
        print(f"Searching for '{query}' on YouTube...")

        headers = {'User-Agent': useragent}
        response = requests.get(search_url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        video_link = None
        for link in soup.find_all('a', href=True):
            if '/watch?v=' in link['href']:
                video_link = f"https://www.youtube.com{link['href']}"
                break

        if video_link:
            print(f"Found first video. Playing: {video_link}")
            webbrowser.open(video_link)
        else:
            print("Could not find a direct video link. Opening search page instead.")
            webbrowser.open(search_url)

        return True
    except Exception as e:
        print(f"Error playing YouTube video: {e}")
        return False

def OpenApp(app, sess=requests.session()):
    try:
        appopen(app, match_closest=True, output=True, throw_error=True)
        return True
    except:
        def extract_links(html):
            if html is None:
                return []
            soup = BeautifulSoup(html, 'html.parser')
            links = soup.find_all('a', href=True)
            return [link.get('href') for link in links]

        def search_google(query):
            url = f"https://www.microsoft.com/en-us/search?q={query}"
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}
            response = sess.get(url, headers=headers)
            if response.status_code == 200:
                return response.text
            else:
                print("Failed to retrieve search results.")
                return None

        def open_in_chrome(url):
            system = platform.system()
            try:
                if system == "Windows":
                    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
                    if not os.path.exists(chrome_path):
                         chrome_path = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"

                    if os.path.exists(chrome_path):
                        subprocess.run([chrome_path, url])
                        return True
                elif system == "Darwin": # macOS
                    subprocess.run(["open", "-a", "Google Chrome", url])
                    return True
                elif system == "Linux":
                    subprocess.run(["google-chrome", url])
                    return True

                print("Google Chrome not found, opening in default browser.")
                webbrowser.open(url)
                return True
            except Exception as e:
                print(f"Error opening in Chrome: {e}")
                webbrowser.open(url) # Final fallback
                return True

        html = search_google(app)
        if html:
            links = extract_links(html)
            if links:
                link = links[0]
                open_in_chrome(link)
        return True

def CloseApp(app):
    if "chrome" in app.lower():
        try:
            subprocess.run(["taskkill", "/f", "/im", "chrome.exe"], check=True)
            print(f"Closed Chrome using taskkill")
            return True
        except:
            pass
    try:
        close(app, match_closest=True, output=True, throw_error=True)
        print(f"Closed {app} using AppOpener")
        return True
    except Exception as e:
        print(f"Error closing {app}: {e}")
        return False


def System(command):
    def mute():
        keyboard.press_and_release("volume mute")

    def unmute():
        keyboard.press_and_release("volume mute")

    def volume_up():
        keyboard.press_and_release("volume up")

    def volume_down():
        keyboard.press_and_release("volume down")

    try:
        if command == "mute": mute()
        elif command == "unmute": unmute()
        elif command == "volume up": volume_up()
        elif command == "volume down": volume_down()
        else:
            print(f"Unknown system command: {command}")
            return False
        print(f"Executed system command: {command}")
        return True
    except Exception as e:
        print(f"Error executing system command {command}: {e}")
        return False

# === MODIFICATION START: To-Do List Feature ===

# Define the file path for the to-do list
TODOLIST_FILEPATH = os.path.join("Data", "todolist.json")

def _load_todolist():
    """Helper function to load the to-do list from its file safely."""
    if not os.path.exists(TODOLIST_FILEPATH):
        return []
    try:
        with open(TODOLIST_FILEPATH, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def _save_todolist(tasks):
    """Helper function to save the to-do list to its file."""
    # Ensure the Data directory exists before saving
    os.makedirs("Data", exist_ok=True)
    with open(TODOLIST_FILEPATH, "w") as f:
        json.dump(tasks, f, indent=4)

def add_to_todolist(item: str):
    """Adds an item to the to-do list."""
    if not item: return "There's nothing to add."
    print(f"Adding '{item}' to to-do list.")
    tasks = _load_todolist()
    tasks.append(item)
    _save_todolist(tasks)
    # This return value will be spoken by the assistant
    return f"Okay, I've added '{item}' to your to-do list."

def show_todolist(query: str):
    """Shows all items currently in the to-do list."""
    print("Showing to-do list.")
    tasks = _load_todolist()
    if not tasks:
        return "Your to-do list is currently empty."
    
    response = "Here are the items on your to-do list:\n"
    for i, task in enumerate(tasks, 1):
        response += f"{i}. {task}\n"
    return response

def clear_todolist(query: str):
    """Clears all items from the to-do list."""
    print("Clearing to-do list.")
    _save_todolist([]) # Save an empty list to the file
    return "I have cleared your to-do list."

# === MODIFICATION END ===


async def TranslateAndExecute(commands: list[str]):
    funcs = []

    for command in commands:
        print(f"Processing command: {command}")

        if command.startswith("open "):
            app_name = command.removeprefix("open ").strip()
            fun = asyncio.to_thread(OpenApp, app_name)
            funcs.append(fun)
        elif command.startswith("close "):
            app_name = command.removeprefix("close ").strip()
            fun = asyncio.to_thread(CloseApp, app_name)
            funcs.append(fun)
        elif command.startswith("play "):
            query = command.removeprefix("play ").strip()
            fun = asyncio.to_thread(PlayYoutube, query)
            funcs.append(fun)
        elif command.startswith("content "):
            topic = command.removeprefix("content ").strip()
            fun = asyncio.to_thread(Content, topic)
            funcs.append(fun)
        elif command.startswith("google search "):
            query = command.removeprefix("google search ").strip()
            fun = asyncio.to_thread(GoogleSearch, query)
            funcs.append(fun)
        elif command.startswith("Youtube "):
            query = command.removeprefix("Youtube ").strip()
            fun = asyncio.to_thread(YouTubeSearch, query)
            funcs.append(fun)
        # === MODIFICATION START: Connecting To-Do List commands ===
        elif command.startswith("add to todolist"):
             item = command.removeprefix("add to todolist").strip()
             fun = asyncio.to_thread(add_to_todolist, item)
             funcs.append(fun)
        elif command.startswith("show todolist"):
             # Pass a dummy argument as the function signature requires one
             fun = asyncio.to_thread(show_todolist, "dummy")
             funcs.append(fun)
        elif command.startswith("clear todolist"):
             # Pass a dummy argument as the function signature requires one
             fun = asyncio.to_thread(clear_todolist, "dummy")
             funcs.append(fun)
        # === MODIFICATION END ===
        elif command.startswith("system "):
            sys_command = command.removeprefix("system ").strip()
            fun = asyncio.to_thread(System, sys_command)
            funcs.append(fun)
        else:
            print(f"No function found for command: {command}")

    if funcs:
        results = await asyncio.gather(*funcs, return_exceptions=True)
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"Command {i+1} failed with exception: {result}")
            else:
                print(f"Command {i+1} result: {result}")
            yield result
    else:
        print("No valid commands to execute")


async def Automation(commands: list[str]):
    print(f"Starting automation with commands: {commands}")
    results = []
    async for result in TranslateAndExecute(commands):
        results.append(result)
    print(f"Automation completed. Results: {results}")
    return True