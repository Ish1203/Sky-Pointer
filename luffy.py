import speech_recognition as sr
import pyttsx3
import os
import sys
import webbrowser
import datetime
import psutil
import pyautogui
import time
import requests
import subprocess
import threading

# Selenium imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager  # ✅ Auto driver manager

# ---------------- Configuration ----------------
engine = pyttsx3.init()
engine.setProperty("rate", 170)

last_opened_website = None

# ---------------- Voice Functions ----------------
def speak(text):
    print("🗣️ Luffy:", text)
    engine.say(text)
    engine.runAndWait()

def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎙️ Listening...")
        r.adjust_for_ambient_noise(source, duration=0.5)
        audio = r.listen(source, phrase_time_limit=6)
    try:
        query = r.recognize_google(audio, language="en-in")
        print("👉 You said:", query)
        return query.lower()
    except:
        return ""

# ---------------- Utility Functions ----------------
def get_weather(city="Delhi"):
    try:
        url = f"https://wttr.in/{city}?format=%t"
        temp = requests.get(url).text.strip()
        return temp
    except:
        return "I cannot fetch the weather right now"

def write_notes_to_file():
    speak("Okay master, speak to write. Say 'save note' when done.")
    notes = []
    while True:
        text = listen()
        if "save note" in text or "stop writing" in text:
            break
        elif text:
            notes.append(text)
            speak(f"Added: {text}")
    filename = "notes.txt"
    with open(filename, "w") as f:
        f.write("\n".join(notes))
    os.system("notepad.exe " + filename)
    speak("Notes saved and opened in Notepad")

def read_notes():
    filename = "notes.txt"
    if os.path.exists(filename):
        with open(filename, "r") as f:
            content = f.read().strip()
        if content:
            speak("Here are your notes.")
            speak(content)
        else:
            speak("Your notes file is empty.")
    else:
        speak("No notes found. Please create some notes first.")

def open_file(file_name):
    try:
        for root, dirs, files in os.walk("C:\\"):
            for file in files:
                if file_name.lower() in file.lower():
                    file_path = os.path.join(root, file)
                    os.startfile(file_path)
                    speak(f"Opening {file}")
                    return file
        speak(f"Sorry, I could not find {file_name}")
    except Exception as e:
        speak("Error while opening file")
        print(e)
    return None

def close_app(app_name):
    try:
        closed = False
        for proc in psutil.process_iter(['pid', 'name']):
            if app_name.lower() in proc.info['name'].lower():
                proc.kill()
                closed = True
                speak(f"Closed {app_name}")
                break
        if not closed:
            speak(f"I could not find {app_name} running.")
    except Exception as e:
        speak("Error while closing application")
        print(e)

def open_website(name):
    global last_opened_website
    url = f"https://www.{name}.com"
    try:
        webbrowser.open(url)
        last_opened_website = name
        speak(f"Opening {name}")
    except:
        speak(f"Could not open {name}")

def close_website(name):
    global last_opened_website
    if last_opened_website and name in last_opened_website:
        pyautogui.hotkey("ctrl", "w")
        speak(f"Closed {name} tab")
        last_opened_website = None
    else:
        speak(f"No tab with {name} was opened recently.")

# ---------------- Selenium YouTube Playback ----------------
def skip_ads_selenium(driver):
    while last_opened_website == "youtube":
        try:
            skip_button = driver.find_element(By.CLASS_NAME, "ytp-ad-skip-button")
            skip_button.click()
        except:
            pass
        time.sleep(2)

def play_youtube(query, is_playlist=False):
    """Play a song or playlist on YouTube using Selenium"""
    global last_opened_website
    last_opened_website = "youtube"

    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")

    # ✅ Auto-install driver with webdriver-manager
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    driver.get("https://www.youtube.com")

    search_box = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "search_query"))
    )
    search_box.clear()
    search_box.send_keys(query)
    search_box.send_keys(Keys.RETURN)

    try:
        if is_playlist:
            first_item = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//ytd-playlist-renderer//a[@id="video-title"]'))
            )
        else:
            first_item = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//a[@id="video-title"]'))
            )
        first_item.click()
        time.sleep(5)
        pyautogui.press("f")  # Fullscreen
    except:
        speak("Could not find the video or playlist to play.")
        driver.quit()
        return

    threading.Thread(target=skip_ads_selenium, args=(driver,), daemon=True).start()

# ---------------- Main Luffy Function ----------------
def luffy_main():
    global last_opened_website
    speak("Hi, I am Luffy. Ready for your command!")

    while True:
        query = listen()

        # --- Exit ---
        if "exit" in query or "quit" in query:
            speak("Goodbye! Luffy is closing now.")
            break

        elif "close hand gesture" in query:
            speak("Okay, closing the hand gesture program.")
            os._exit(0)

        # --- Close current tab ---
        elif "close it" in query:
            if last_opened_website:
                pyautogui.hotkey("ctrl", "w")
                speak(f"Closed {last_opened_website} tab")
                last_opened_website = None
            else:
                pyautogui.hotkey("ctrl", "w")
                speak("Closed the current tab")

        # --- File Handling ---
        elif query.startswith("open "):
            file_name = query.replace("open", "").strip()
            if file_name == "notepad":
                speak("Do you want me to write in Notepad?")
                choice = listen()
                subprocess.Popen(["notepad.exe"])
                time.sleep(1)
                if "yes" in choice:
                    speak("Start speaking. Say 'stop writing' to finish.")
                    while True:
                        text = listen()
                        if "stop writing" in text or "save note" in text:
                            speak("Finished writing in Notepad.")
                            break
                        elif text:
                            pyautogui.typewrite(text + "\n")
            elif file_name:
                if "." in file_name or "file" in file_name:
                    open_file(file_name)
                else:
                    open_website(file_name)

        elif query.startswith("close "):
            target = query.replace("close", "").strip()
            if target:
                if target == "notepad":
                    close_app("notepad")
                elif "tab" in target or "browser" in target:
                    close_website(target)
                else:
                    close_app(target)

        # --- Notes ---
        elif "write note" in query:
            write_notes_to_file()
        elif "read notes" in query:
            read_notes()

        # --- Apps ---
        elif "open calculator" in query:
            speak("Opening Calculator")
            os.system("calc.exe")
        elif "open command prompt" in query:
            speak("Opening Command Prompt")
            os.system("start cmd")

        # --- Web Searches ---
        elif "search for" in query:
            search_term = query.replace("search for", "").strip()
            if search_term:
                speak(f"Searching {search_term}")
                webbrowser.open(f"https://www.google.com/search?q={search_term}")

        elif "search youtube for" in query:
            search_term = query.replace("search youtube for", "").strip()
            if search_term:
                speak(f"Searching YouTube for {search_term}")
                webbrowser.open(f"https://www.youtube.com/results?search_query={search_term}")
                last_opened_website = "youtube"

        # --- Play YouTube (song / playlist / music) ---
        elif query.startswith("play"):
            if "playlist" in query and "on youtube" in query:
                playlist_name = query.replace("play", "").replace("playlist", "").replace("on youtube", "").strip()
                if playlist_name:
                    speak(f"Playing playlist {playlist_name} on YouTube")
                    threading.Thread(target=play_youtube, args=(playlist_name, True), daemon=True).start()
            elif "on youtube" in query:
                song_name = query.replace("play", "").replace("on youtube", "").strip()
                if song_name:
                    speak(f"Playing {song_name} on YouTube")
                    threading.Thread(target=play_youtube, args=(song_name, False), daemon=True).start()
            elif "music" in query or "song" in query:
                speak("Playing random music on YouTube")
                threading.Thread(target=play_youtube, args=("music", False), daemon=True).start()
            else:
                speak("Please tell me what you want me to play.")

        # --- Media Controls ---
        elif "play" in query or "pause" in query:
            pyautogui.press("playpause")
            speak("Toggled play/pause")
        elif "next song" in query or "skip" in query:
            pyautogui.press("nexttrack")
            speak("Next track")
        elif "previous song" in query:
            pyautogui.press("prevtrack")
            speak("Previous track")
        elif "volume up" in query:
            pyautogui.press("volumeup")
            speak("Volume up")
        elif "volume down" in query:
            pyautogui.press("volumedown")
            speak("Volume down")
        elif "mute" in query:
            pyautogui.press("volumemute")
            speak("Muted")

        # --- System ---
        elif "shutdown" in query:
            speak("Shutting down your PC")
            os.system("shutdown /s /t 5")
        elif "restart" in query:
            speak("Restarting your PC")
            os.system("shutdown /r /t 5")
        elif "lock" in query:
            speak("Locking your PC")
            os.system("rundll32.exe user32.dll,LockWorkStation")

        # --- Info ---
        elif "time" in query:
            str_time = datetime.datetime.now().strftime("%H:%M:%S")
            speak(f"The time is {str_time}")
        elif "date" in query:
            str_date = datetime.datetime.now().strftime("%A, %d %B %Y")
            speak(f"Today is {str_date}")
        elif "battery" in query:
            battery = psutil.sensors_battery()
            if battery:
                speak(f"Battery is at {battery.percent} percent")
            else:
                speak("I cannot read the battery level right now")
        elif "weather" in query or "temperature" in query:
            temp = get_weather()
            speak(f"The temperature is {temp}")

        # --- Gestures via voice ---
        elif "screenshot" in query:
            speak("Taking screenshot")
            filename = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S.png")
            pyautogui.screenshot(filename)
            speak("Screenshot saved")
        elif "change tab" in query:
            pyautogui.hotkey("ctrl", "tab")
            speak("Tab changed")
        elif "close tab" in query:
            pyautogui.hotkey("ctrl", "w")
            speak("Tab closed")
        elif "minimize all" in query:
            pyautogui.hotkey("win", "d")
            speak("Windows minimized")
        elif "maximize window" in query:
            pyautogui.hotkey("win", "up")
            speak("Window maximized")
        else:
            if query:
                speak("I did not understand. Please try again.")

if __name__ == "__main__":
    luffy_main()
