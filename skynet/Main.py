from Frontend.GUI import (
    GraphicalUserInterface,
    SetAsssistantStatus,
    ShowTextToScreen,
    TempDirectoryPath,
    SetMicrophoneStatus,
    AnswerModifier,
    QueryModifier,
    GetMicrophoneStatus,
    GetAssistantStatus,
)
from Backend.Model import FirstLayerDMM
from Backend.RealtimeSearchEngine import RealtimeSearchEngine
from Backend.Automation import Automation
from Backend.SpeechToText import SpeechRecognition
from Backend.Chatbot import ChatBot
from Backend.TextToSpeech import TextToSpeech
from dotenv import dotenv_values
from asyncio import run
from time import sleep
import subprocess
import threading
import json
import os

# Load environment variables
env_vars = dotenv_values(".env")
Username = env_vars.get("Username", "User")
Assistantname = env_vars.get("Assistantname", "Assistant")

DefaultMessage = f""" {Username}: Hello {Assistantname}, How are you?
{Assistantname}: Welcome {Username}. I am doing well. How may I help you? """

# === MODIFICATION START ===
# Updated the list to include our new to-do list commands
functions = [
    "open", "close", "play", "system", "content", "google search",
    "Youtube", "add to todolist", "show todolist", "clear todolist"
]
# === MODIFICATION END ===

subprocess_list = []

def ShowDefaultChatIfNoChats():
    try:
        with open(r'Data\ChatLog.json', "r", encoding='utf-8') as file:
            if len(file.read()) < 5:
                with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as temp_file:
                    temp_file.write("")
                with open(TempDirectoryPath('Responses.data'), 'w', encoding='utf-8') as response_file:
                    response_file.write(DefaultMessage)
    except FileNotFoundError:
        print("ChatLog.json file not found. Creating default response.")
        os.makedirs("Data", exist_ok=True)
        with open(r'Data\ChatLog.json', "w", encoding='utf-8') as file:
            file.write("[]")
        with open(TempDirectoryPath('Responses.data'), 'w', encoding='utf-8') as response_file:
            response_file.write(DefaultMessage)

def ReadChatLogJson():
    try:
        with open(r'Data\ChatLog.json', 'r', encoding='utf-8') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def ChatLogIntegration():
    json_data = ReadChatLogJson()
    formatted_chatlog = ""
    for entry in json_data:
        if entry["role"] == "user":
            formatted_chatlog += f"{Username}: {entry['content']}\n"
        elif entry["role"] == "assistant":
            formatted_chatlog += f"{Assistantname}: {entry['content']}\n"
    temp_dir_path = TempDirectoryPath('')
    if not os.path.exists(temp_dir_path):
        os.makedirs(temp_dir_path)
    with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as file:
        file.write(AnswerModifier(formatted_chatlog))

def ShowChatOnGUI():
    try:
        with open(TempDirectoryPath('Database.data'), 'r', encoding='utf-8') as file:
            data = file.read()
        if len(str(data)) > 0:
            with open(TempDirectoryPath('Responses.data'), 'w', encoding='utf-8') as response_file:
                response_file.write(data)
    except FileNotFoundError:
        print("Database.data file not found.")

def InitialExecution():
    SetMicrophoneStatus("False")
    ShowTextToScreen("")
    ShowDefaultChatIfNoChats()
    ChatLogIntegration()
    ShowChatOnGUI()

def MainExecution():
    try:
        SetAsssistantStatus("Listening...")
        Query = SpeechRecognition()
        ShowTextToScreen(f"{Username}: {Query}")
        SetAsssistantStatus("Thinking...")
        Decision = FirstLayerDMM(Query)
        print(f"\nDecision: {Decision}\n")

        # === MODIFICATION START ===
        # Improved logic to handle automation tasks more efficiently
        is_automation_task = any(
            any(decision.startswith(func) for func in functions)
            for decision in Decision
        )

        if is_automation_task:
            # If any command is an automation task, run the automation script with all commands
            run(Automation(Decision))
        else:
            # Otherwise, handle it as a conversational query
            G = any(i.startswith("general") for i in Decision)
            R = any(i.startswith("realtime") for i in Decision)

            Merged_query = " and ".join(
                [" ".join(i.split()[1:]) for i in Decision if i.startswith("general") or i.startswith("realtime")]
            )

            if G and R or R:
                SetAsssistantStatus("Searching...")
                Answer = RealtimeSearchEngine(QueryModifier(Merged_query))
                ShowTextToScreen(f"{Assistantname}: {Answer}")
                SetAsssistantStatus("Answering...")
                TextToSpeech(Answer)
            else:
                for queries in Decision:
                    if "general" in queries:
                        SetAsssistantStatus("Thinking...")
                        QueryFinal = queries.replace("general", "")
                        Answer = ChatBot(QueryModifier(QueryFinal))
                        ShowTextToScreen(f"{Assistantname}: {Answer}")
                        SetAsssistantStatus("Answering...")
                        TextToSpeech(Answer)
                    elif "exit" in queries:
                        Answer = "Goodbye!"
                        ShowTextToScreen(f"{Assistantname}: {Answer}")
                        SetAsssistantStatus("Answering...")
                        TextToSpeech(Answer)
                        os._exit(1)
        # === MODIFICATION END ===
    except Exception as e:
        print(f"Error in MainExecution: {e}")

def FirstThread():
    while True:
        try:
            CurrentStatus = GetMicrophoneStatus()
            if CurrentStatus.lower() == "true":
                MainExecution()
            else:
                AIStatus = GetAssistantStatus()
                if "Available..." not in AIStatus:
                    SetAsssistantStatus("Available...")
            sleep(0.5) # Check status every half a second
        except Exception as e:
            print(f"Error in FirstThread: {e}")
            sleep(1)

def SecondThread():
    try:
        GraphicalUserInterface()
    except Exception as e:
        print(f"Error in SecondThread: {e}")

if __name__ == "__main__":
    InitialExecution()
    thread1 = threading.Thread(target=FirstThread, daemon=True)
    thread1.start()
    SecondThread()