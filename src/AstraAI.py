import speech_recognition as sr
import pyttsx3
import ollama
import webbrowser
import os
import asyncio
import edge_tts
import pygame
import uuid
import urllib.parse
import requests  
import threading
import customtkinter as ctk
from datetime import datetime
from ddgs import DDGS
import math
import tkinter as tk
import time
import pystray
from pystray import MenuItem as item
from PIL import Image, ImageDraw


astra_memory = [
    {"role": "system", "content": "You are Astra, a highly advanced, witty, and concise AI assistant. Keep your answers brief and natural."}
]

pygame.mixer.init()


engine = pyttsx3.init()
engine.setProperty('rate', 170)
recognizer = sr.Recognizer()


def create_file_tool(filename):
    if "." not in filename:
        filename += ".txt"
    try:
        with open(filename, 'w') as f:
            pass
        absolute_path = os.path.abspath(filename)
        return f"Successfully created the file. Boss, you can find it at {absolute_path}."
    except Exception as e:
        return f"Failed to create file. Error: {str(e)}"

def open_website_tool(website_name):
    website_name = website_name.lower().replace(" ", "")
    
    urls = {
        "github": "https://github.com/AkshatSingh-90056",
        "leetcode": "https://leetcode.com/u/Akshat_singh22/",
        "linkedin": "https://www.linkedin.com/in/akshat-singh-811641317/",
        "youtube": "https://www.youtube.com"
    }
    
    if website_name in urls:
        webbrowser.open(urls[website_name])
        return f"I have opened {website_name} for you, Boss."
    else:
        webbrowser.open(f"https://www.{website_name}.com")
        return f"I have opened {website_name}, Boss."

def search_youtube_tool(query):
    try:
        encoded_query = urllib.parse.quote(query)
        url = f"https://www.youtube.com/results?search_query={encoded_query}"
        webbrowser.open(url)
        return f"I have pulled up the YouTube search results for {query}, Boss."
    except Exception as e:
        return "Failed to search YouTube."

def open_application_tool(app_name):
    apps = {
        "notepad": "notepad",
        "calculator": "calc",
        "vs code": "code",
        "vscode": "code",
        "command prompt": "cmd",
        "terminal": "cmd",
        "explorer": "explorer",
        "paint": "mspaint"
    }
    
    if app_name.lower() not in apps:
        return f"Boss, {app_name} is a website or unrecognized program, not a local desktop application. Please use the open_website tool instead."
        
    exe_name = apps[app_name.lower()]
    try:
        os.system(f"start {exe_name}")
        return f"I have launched {app_name} for you."
    except Exception as e:
        return f"I encountered an error trying to open {app_name}."

def get_github_stats_tool(username="AkshatSingh-90056"):
    if not username or username.lower() in ["my", "me", "boss"]:
        username = "AkshatSingh-90056"
        
    try:
        user_url = f"https://api.github.com/users/{username}"
        user_response = requests.get(user_url)
        if user_response.status_code == 200:
            user_data = user_response.json()
            repos_count = user_data.get('public_repos', 0)
            repos_url = f"https://api.github.com/users/{username}/repos"
            repos_response = requests.get(repos_url)
            if repos_response.status_code == 200:
                repos_data = repos_response.json()
                repo_names = [repo['name'] for repo in repos_data]
                if repo_names:
                    names_list = ", ".join(repo_names)
                    return f"Boss, your GitHub account has {repos_count} public projects. The projects are named: {names_list}."
                else:
                    return f"Boss, you have {repos_count} public projects, but they appear to be empty."
            else:
                return f"Boss, you have {repos_count} projects, but I couldn't fetch their specific names."
        else:
            return f"I am sorry, Boss. I could not find a GitHub profile with the username {username}."
    except Exception as e:
        return "I encountered a network error while trying to reach the GitHub servers."

def get_leetcode_stats_tool(username="Akshat_singh22"):
    if not username or " " in username or username.lower() in ["my", "me", "boss", "league", "code", "leadcode", "leetcode"]:
        username = "Akshat_singh22"
        
    try:
        url = "https://leetcode.com/graphql"
        query = """
        query getUserProfile($username: String!) {
            matchedUser(username: $username) {
                submitStats {
                    acSubmissionNum {
                        difficulty
                        count
                    }
                }
            }
        }
        """
        variables = {"username": username}
        headers = {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}
        response = requests.post(url, json={"query": query, "variables": variables}, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            if "errors" in data or data.get("data", {}).get("matchedUser") is None:
                return f"Boss, I couldn't find the stats for the LeetCode user {username}."
            stats = data["data"]["matchedUser"]["submitStats"]["acSubmissionNum"]
            counts = {item['difficulty']: item['count'] for item in stats}
            total, easy, medium, hard = counts.get('All', 0), counts.get('Easy', 0), counts.get('Medium', 0), counts.get('Hard', 0)
            return f"Boss, your LeetCode account has solved a total of {total} questions. This includes {easy} easy, {medium} medium, and {hard} hard questions."
        else:
            return "I am sorry, Boss. The LeetCode servers are currently unreachable."
    except Exception as e:
        return "I encountered a network error while trying to fetch your LeetCode stats."

def get_weather_tool(location="Lucknow"):
    try:
        url = f"https://wttr.in/{location}?format=j1"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            temp_c = data['current_condition'][0]['temp_C']
            description = data['current_condition'][0]['weatherDesc'][0]['value']
            return f"Boss, the current weather in {location} is {temp_c} degrees Celsius with {description}."
        else:
            return f"I am sorry, Boss. I couldn't fetch the weather for {location} right now."
    except Exception as e:
        return "I encountered a network error while trying to reach the weather servers."

def get_breaking_news_tool(query):
    """Silently searches the web for current events."""
    
    static_words = ["capital", "history", "what is", "where is", "who was"]
    if any(word in query.lower() for word in static_words):
        return "Internal Error: You used a news tool for a static fact. DO NOT READ THIS ALOUD. Just answer the Boss's question directly using your own brain."
        
    try:
        results = DDGS().text(query, max_results=1)
        if not results:
            return f"Boss, I couldn't find any recent news on {query}."
            
        snippet = results[0]['body']
        clean_snippet = snippet[:150] + "..." if len(snippet) > 150 else snippet
        return f"Boss, I checked the live web. {clean_snippet}"
    except Exception as e:
        return "I encountered a network error while trying to search the web."

available_functions = {
    'create_file': create_file_tool,
    'open_website': open_website_tool,
    'search_youtube': search_youtube_tool,
    'open_application': open_application_tool,
    'get_github_stats': get_github_stats_tool,
    'get_leetcode_stats': get_leetcode_stats_tool,
    'get_weather': get_weather_tool,
    'get_breaking_news': get_breaking_news_tool 
}

astra_tools = [
   {
        'type': 'function',
        'function': {
            'name': 'get_breaking_news',
            'description': 'Searches the web for LIVE NEWS, CURRENT EVENTS, or REAL-TIME updates ONLY (e.g., live scores, current president). Do NOT use for static facts or geography.',
            'parameters': {
                'type': 'object',
                'properties': {
                    'query': {'type': 'string', 'description': 'The exact news topic to look up.'}
                },
                'required': ['query'],
            },
        },
    },
    {
        'type': 'function',
        'function': {
            'name': 'create_file',
            'description': 'Creates a new empty text file.',
            'parameters': {
                'type': 'object',
                'properties': {'filename': {'type': 'string'}},
                'required': ['filename'],
            },
        },
    },
    {
        'type': 'function',
        'function': {
            'name': 'get_weather',
            'description': 'Fetches the current live weather and temperature.',
            'parameters': {
                'type': 'object',
                'properties': {
                    'location': {
                        'type': 'string',
                        'description': 'The city to get the weather for. Default to "Lucknow".'
                    },
                },
                'required': ['location'],
            },
        },
    },
   {
        'type': 'function',
        'function': {
            'name': 'open_website',
            'description': 'Opens a specific website. Use this whenever the user wants to go to LeetCode, GitHub, LinkedIn, etc.',
            'parameters': {
                'type': 'object',
                'properties': {
                    'website_name': {
                        'type': 'string', 
                        'description': 'The simple name of the website to open, e.g., "leetcode", "github", "linkedin".'
                    },
                },
                'required': ['website_name'],
            },
        },
    },
    {
        'type': 'function',
        'function': {
            'name': 'search_youtube',
            'description': 'Searches YouTube for a video. Only use this if the user specifically asks to play a song, watch a video, or search YouTube.',
            'parameters': {
                'type': 'object',
                'properties': {
                    'query': {
                        'type': 'string', 
                        'description': 'The specific topic, song, or video name to search for.'
                    }
                },
                'required': ['query'],
            },
        },
    },
    {
        'type': 'function',
        'function': {
            'name': 'open_application',
            'description': 'Opens a LOCAL Windows desktop application (like Notepad, Calculator, Paint). DO NOT use this for websites like LeetCode, GitHub, or LinkedIn.',
            'parameters': {
                'type': 'object',
                'properties': {'app_name': {'type': 'string'}},
                'required': ['app_name'],
            },
        },
    },
    {
        'type': 'function',
        'function': {
            'name': 'get_github_stats',
            'description': 'Fetches REAL live statistics from GitHub. Trigger this IMMEDIATELY if the user asks "how many repositories do I have", "what are my github stats", or anything about projects.',
            'parameters': {
                'type': 'object',
                'properties': {
                    'username': {
                        'type': 'string',
                        'description': 'The GitHub username. If the user asks about "my" account or doesn\'t specify, use "AkshatSingh-90056".'
                    },
                },
                'required': ['username'],
            },
        },
    },
    {
        'type': 'function',
        'function': {
            'name': 'get_leetcode_stats',
            'description': 'Fetches REAL solved question counts from LeetCode. Trigger this IMMEDIATELY if the user asks "how many questions have I solved", "lead code stats", or anything about LeetCode.',
            'parameters': {
                'type': 'object',
                'properties': {
                    'username': {
                        'type': 'string',
                        'description': 'The LeetCode username. If the user asks about "my" account or doesn\'t specify, use "Akshat_singh22".'
                    },
                },
                'required': ['username'],
            },
        },
    }
]



astra_memory = []

def ask_brain(user_input):
    global astra_memory 
    
    from datetime import datetime 
    current_time = datetime.now().strftime("%I:%M %p on %A, %B %d, %Y")
    
    system_prompt = (
        "You are Astra, a highly intelligent, fast, and concise AI assistant. "
        "Never use markdown formatting. "
        f"The current time is {current_time}. "
        "Always refer to the user as Boss. "
        "CRITICAL RULES: "
        "1. If asked to open a website, strictly use the open_website tool. "
        "2. NEVER guess, invent, or make up statistics for GitHub or LeetCode. "
        "3. You MUST use the get_github_stats tool if asked about repositories or projects. "
        "4. You MUST use the get_leetcode_stats tool if asked about solved questions or coding stats."
    )
    
    tool_keywords = [
        "weather", "temperature", "open", "youtube", "github", "leetcode", 
        "news", "launch", "play", "file", "create", "make", 
        "repositories", "depositories", "repo", "project", 
        "stats", "question", "solved", "how many"
    ]
    needs_tools = any(keyword in user_input.lower() for keyword in tool_keywords)
    
    astra_memory.append({'role': 'user', 'content': user_input})
    
    if len(astra_memory) > 10:
        astra_memory = astra_memory[-10:]
        
    messages_to_send = [{'role': 'system', 'content': system_prompt}] + astra_memory
    
    try:
        if needs_tools:
            print("[System] Action words detected. Granting Astra tool access...")
            response = ollama.chat(
                model='llama3.1',
                messages=messages_to_send,
                tools=astra_tools 
            )
        else:
            print("[System] Basic chat detected. Unplugging tools for instant speed...")
            response = ollama.chat(
                model='llama3.1',
                messages=messages_to_send, 
            )
        
        message = response.get('message', {})
        
        if message.get('tool_calls'):
            for tool in message['tool_calls']:
                function_name = tool['function']['name']
                arguments = tool['function']['arguments']
                
                if function_name in available_functions:
                    function_to_call = available_functions[function_name]
                    
                    tool_reply = ""
                    if function_name == 'create_file':
                        tool_reply = function_to_call(arguments.get('filename'))
                    elif function_name == 'open_website':
                        url_target = arguments.get('website_name', arguments.get('url', ''))
                        tool_reply = function_to_call(url_target)
                    elif function_name == 'search_youtube':
                        tool_reply = function_to_call(arguments.get('query'))
                    elif function_name == 'open_application':
                        tool_reply = function_to_call(arguments.get('app_name'))
                    elif function_name == 'get_github_stats':
                        tool_reply = function_to_call(arguments.get('username'))
                    elif function_name == 'get_leetcode_stats':
                        tool_reply = function_to_call(arguments.get('username'))
                    elif function_name == 'get_weather':
                        tool_reply = function_to_call(arguments.get('location', 'Lucknow'))
                    elif function_name == 'get_breaking_news':
                        tool_reply = function_to_call(arguments.get('query'))
                    
                    if tool_reply:
                        astra_memory.append({'role': 'assistant', 'content': f"Action completed: {tool_reply}"})
                        return tool_reply
                    
        final_reply = message.get('content', "I am processing that, Boss.")
        
        if final_reply:
            astra_memory.append({'role': 'assistant', 'content': final_reply})
            
        return final_reply
        
    except Exception as e:
        print(f"\n[SYSTEM ERROR]: {str(e)}\n")
        return "I am sorry Boss, my core just crashed."




class AstraGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("AstraAI - Core System")
        self.geometry("700x650")
        self.minsize(500, 500)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.protocol("WM_DELETE_WINDOW", self.hide_window)

        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.title_label = ctk.CTkLabel(self, text="ASTRA AI ENGINE", font=ctk.CTkFont(size=28, weight="bold", family="Courier"))
        self.title_label.grid(row=0, column=0, pady=(20, 0))

        self.status_label = ctk.CTkLabel(self, text="Status: Booting Up...", text_color="gray", font=ctk.CTkFont(size=14))
        self.status_label.grid(row=1, column=0, pady=5)

        self.orb_canvas = tk.Canvas(self, width=200, height=200, bg="#242424", highlightthickness=0)
        self.orb_canvas.grid(row=2, column=0, pady=10)

        self.console_box = ctk.CTkTextbox(self, font=ctk.CTkFont(size=14), fg_color="#1e1e1e", border_width=1, border_color="#333333")
        self.console_box.grid(row=3, column=0, padx=20, pady=10, sticky="nsew")
        self.console_box.insert("0.0", "System Initializing...\n")
        self.console_box.configure(state="disabled")

        self.controls_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.controls_frame.grid(row=4, column=0, padx=20, pady=(0, 20), sticky="ew")
        self.controls_frame.grid_columnconfigure(1, weight=1)

        self.voice_switch = ctk.CTkSwitch(self.controls_frame, text="Voice Mode", font=ctk.CTkFont(size=12))
        self.voice_switch.select() 
        self.voice_switch.grid(row=0, column=0, padx=(0, 10))

        self.input_entry = ctk.CTkEntry(self.controls_frame, placeholder_text="Type a command...", font=ctk.CTkFont(size=14))
        self.input_entry.grid(row=0, column=1, sticky="ew", padx=5)
        self.input_entry.bind("<Return>", lambda event: self.handle_text_input())

        self.send_button = ctk.CTkButton(self.controls_frame, text="Send", width=60, command=self.handle_text_input)
        self.send_button.grid(row=0, column=2, padx=(5, 0))

        self.orb_angle = 0.0
        self.orb_speed = 0.05
        self.orb_color = "#0077ff" 
        self.orb_vibration = 0
        self.is_listening = False
        self.is_running = True 
        
        self.animate_orb() 

        self.astra_thread = threading.Thread(target=self.run_astra)
        self.astra_thread.daemon = True
        self.astra_thread.start()

    def set_orb_state(self, state):
        if state == "idle":
            self.orb_color = "#0077ff" 
            self.orb_speed = 3         
            self.orb_vibration = 0
        elif state == "listening":
            self.orb_color = "#00ffcc" 
            self.orb_speed = 8         
            self.orb_vibration = 10    
        elif state == "thinking":
            self.orb_color = "#b200ff" 
            self.orb_speed = 15        
            self.orb_vibration = 20    

    def animate_orb(self):
        if getattr(self, 'is_running', False):
            self.orb_canvas.delete("all")
            cx, cy, base_r = 100, 100, 40 
            pulse = math.sin(math.radians(self.orb_angle * 2)) * self.orb_vibration
            
            r1 = base_r + 5 + (pulse * 0.2)
            self.orb_canvas.create_arc(cx - r1, cy - r1, cx + r1, cy + r1, start=self.orb_angle, extent=280, outline=self.orb_color, width=3, style=tk.ARC)

            r2 = base_r + 20 + (pulse * 0.5)
            self.orb_canvas.create_arc(cx - r2, cy - r2, cx + r2, cy + r2, start=-self.orb_angle * 1.2, extent=180, outline=self.orb_color, width=4, style=tk.ARC, dash=(4, 4))
            self.orb_canvas.create_arc(cx - r2, cy - r2, cx + r2, cy + r2, start=(-self.orb_angle * 1.2) + 200, extent=100, outline=self.orb_color, width=4, style=tk.ARC, dash=(4, 4))

            r3 = base_r + 35 + pulse
            self.orb_canvas.create_arc(cx - r3, cy - r3, cx + r3, cy + r3, start=self.orb_angle * 1.5, extent=80, outline=self.orb_color, width=2, style=tk.ARC)
            self.orb_canvas.create_arc(cx - r3, cy - r3, cx + r3, cy + r3, start=(self.orb_angle * 1.5) + 180, extent=80, outline=self.orb_color, width=2, style=tk.ARC)

            self.orb_angle = (self.orb_angle + self.orb_speed) % 360
            self.after(30, self.animate_orb)

    def update_console(self, text):
        self.console_box.configure(state="normal")
        self.console_box.insert("end", text + "\n\n")
        self.console_box.see("end") 
        self.console_box.configure(state="disabled")

    def update_status(self, text, color="white"):
        self.status_label.configure(text=f"Status: {text}", text_color=color)

    def speak(self, text):
        """Generates hyper-realistic AI speech and plays it dynamically"""
        self.update_console(f"Astra: {text}")
        
        if self.voice_switch.get() == 1:
            threading.Thread(target=self._async_speak_worker, args=(text,), daemon=True).start()

    def _async_speak_worker(self, text):
        """Background worker to handle the async voice generation"""
        voice = "en-IN-NeerjaNeural"
        
        unique_id = str(uuid.uuid4().hex)
        audio_file = f"temp_astra_{unique_id}.mp3"
        
        try:
            communicate = edge_tts.Communicate(text, voice, rate="+15%")
            asyncio.run(communicate.save(audio_file))
            
            pygame.mixer.music.load(audio_file)
            pygame.mixer.music.play()
            
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
                
        except Exception as e:
            print(f"[Audio Error]: {e}")
            
        finally:
            pygame.mixer.music.unload()
            try:
                if os.path.exists(audio_file):
                    os.remove(audio_file)
            except Exception:
                pass

    def execute_command(self, command):
        if "go to sleep" in command or "shutdown" in command or "exit" in command:
            self.update_status("Shutting Down", color="red")
            self.set_orb_state("idle")
            self.speak("Shutting down protocols. Goodbye!")
            self.is_running = False
            self.quit() 
            return
        
        self.update_status("Astra is thinking...", color="#ff00ff")
        self.set_orb_state("thinking")
        self.speak("Right away.") 
        
        astra_reply = ask_brain(command)
        
        self.update_status("Online & Ready", color="#00ffcc")
        self.set_orb_state("idle")
        
        if astra_reply:
            self.speak(astra_reply)

    def handle_text_input(self):
        text = self.input_entry.get().strip()
        if not text: return
        self.input_entry.delete(0, "end")
        self.update_console(f"Boss (Typed): {text}")
        threading.Thread(target=self.execute_command, args=(text,), daemon=True).start()


    def start_countdown(self, seconds):
        self.is_listening = True
        self.set_orb_state("listening") 
        self.tick_timer(seconds)

    def tick_timer(self, seconds):
        if not self.is_listening or self.voice_switch.get() == 0: return 
        if seconds > 0:
            self.update_status(f"Listening... [{seconds}s remaining]", color="#00ffcc")
            self.after(1000, self.tick_timer, seconds - 1)
        else:
            self.update_status("Listening Timed Out", color="orange")
            self.set_orb_state("idle")
            
    def stop_countdown(self):
        self.is_listening = False

    def listen(self):
        with sr.Microphone() as source:
            self.start_countdown(15) 
            try:
                audio = recognizer.listen(source, timeout=10, phrase_time_limit=15)
                self.stop_countdown() 
                self.update_status("Processing audio...", color="yellow")
                
                text = recognizer.recognize_google(audio).lower()
                for word in ["astra", "extra", "straw", "service", "welding service", "abstract", "astro", "a star"]:
                    if text.startswith(word):
                        text = text.replace(word, "", 1).strip()
                
                self.update_console(f"Boss: {text}")
                return text
            except (sr.WaitTimeoutError, sr.UnknownValueError, sr.RequestError):
                self.stop_countdown()
                self.set_orb_state("idle")
                return ""

    def run_astra(self):
        import time
        self.update_status("Calibrating Microphone...", color="yellow")
        self.set_orb_state("idle")
        self.speak("Calibrating audio. Please wait.")
        
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=2)
            recognizer.dynamic_energy_threshold = True
            recognizer.energy_threshold = 300 
            
        self.update_status("Online & Ready", color="#00ffcc")
        self.speak("Astra Core Engine initialized. Local neural sub-systems online and standby.")
        
        while self.is_running:
            if self.voice_switch.get() == 1:
                self.update_status("Waiting for voice command...", color="gray")
                self.set_orb_state("idle")
                command = self.listen()
                if command:
                    self.execute_command(command)
            else:
                self.update_status("Text Mode Active (Mic Muted)", color="gray")
                self.set_orb_state("idle")
                time.sleep(1)


    def create_tray_image(self):
        """Generates a sleek blue dot icon for the system tray via code"""
        image = Image.new('RGB', (64, 64), color=(36, 36, 36))
        dc = ImageDraw.Draw(image)
        dc.ellipse((16, 16, 48, 48), fill=(0, 119, 255))
        return image

    def hide_window(self):
        """Hides the UI and spawns the tray icon"""
        self.withdraw() 
        
        image = self.create_tray_image()
        menu = (item('Show Astra', self.show_window), item('Quit', self.quit_window))
        
        self.tray_icon = pystray.Icon("AstraAI", image, "Astra AI Engine", menu)
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def show_window(self, icon, item):
        """Brings the UI back from the dead"""
        self.tray_icon.stop() 
        self.after(0, self.deiconify) 

    def quit_window(self, icon, item):
        """The TRUE shutdown command"""
        self.tray_icon.stop()
        self.is_running = False
        self.quit()


if __name__ == "__main__":
    app = AstraGUI()
    app.mainloop()
    
  