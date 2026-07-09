import speech_recognition as sr
import pyttsx3
import ollama
import webbrowser
import os
import urllib.parse
import requests  
import threading
import customtkinter as ctk
from datetime import datetime
from ddgs import DDGS

# ==========================================
# 1. INITIALIZE HARDWARE
# ==========================================
engine = pyttsx3.init()
engine.setProperty('rate', 170)
recognizer = sr.Recognizer()

# ==========================================
# 2. DEFINE YOUR PYTHON TOOLS
# ==========================================
def create_file_tool(filename):
    if "." not in filename:
        filename += ".txt"
    try:
        # Save it right in your active project folder
        with open(filename, 'w') as f:
            pass
        # Get the exact absolute path where Windows put it
        absolute_path = os.path.abspath(filename)
        return f"Successfully created the file. Boss, you can find it at {absolute_path}."
    except Exception as e:
        return f"Failed to create file. Error: {str(e)}"

def open_website_tool(url):
    if not url.startswith("http"):
        url = "https://" + url
    try:
        webbrowser.open(url)
        return "I have opened the website for you, Boss."
    except Exception as e:
        return f"Failed to open website. Error: {str(e)}"

def search_youtube_tool(query):
    try:
        encoded_query = urllib.parse.quote(query)
        url = f"https://www.youtube.com/results?search_query={encoded_query}"
        webbrowser.open(url)
        return f"I have pulled up the YouTube search results for {query}, Boss."
    except Exception as e:
        return "Failed to search YouTube."

def open_application_tool(app_name):
    # Only these specific local programs are allowed
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
    
    # THE FAILSAFE: If she tries to open a website as an app, block her!
    if app_name.lower() not in apps:
        return f"Boss, {app_name} is a website or unrecognized program, not a local desktop application. Please use the open_website tool instead."
        
    exe_name = apps[app_name.lower()]
    try:
        os.system(f"start {exe_name}")
        return f"I have launched {app_name} for you."
    except Exception as e:
        return f"I encountered an error trying to open {app_name}."

def get_github_stats_tool(username):
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
    if " " in username or "code" in username.lower() or "league" in username.lower():
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

# NEW TOOL: Breaking News Search (Renamed to prevent hallucination)
def get_breaking_news_tool(query):
    """Silently searches the web for current events."""
    
    # THE PYTHON FAILSAFE: If the AI tries to cheat and look up a fact, Python blocks it.
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

# ==========================================
# 3. DEFINE THE LLM TOOL MENU
# ==========================================
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
            'description': 'Opens a website in the browser. Use this whenever the user wants to go to LeetCode, GitHub, or LinkedIn.',
            'parameters': {
                'type': 'object',
                'properties': {
                    'url': {
                        'type': 'string', 
                        'description': 'CRITICAL URLS: "github" -> "https://github.com/AkshatSingh-90056". "linkedin" -> "https://www.linkedin.com/in/akshat-singh-811641317/". "leetcode" or "lead code" -> "https://leetcode.com/u/Akshat_singh22/".'
                    },
                },
                'required': ['url'],
            },
        },
    },
    {
        'type': 'function',
        'function': {
            'name': 'search_youtube',
            'description': 'Opens YouTube. ONLY use this if the user explicitly says "search youtube", "play", or "watch a video". Do NOT use this for general questions.',
            'parameters': {
                'type': 'object',
                'properties': {'query': {'type': 'string'}},
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
            'description': 'Fetches live statistics and repository names from a GitHub profile.',
            'parameters': {
                'type': 'object',
                'properties': {
                    'username': {
                        'type': 'string',
                        'description': 'CRITICAL: If the user asks about "my github", use exactly "AkshatSingh-90056".'
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
            'description': 'Fetches the number of solved programming questions from a LeetCode profile.',
            'parameters': {
                'type': 'object',
                'properties': {
                    'username': {
                        'type': 'string',
                        'description': 'CRITICAL: If the user asks about "my leetcode", "league code", "lead code", use exactly "Akshat_singh22".'
                    },
                },
                'required': ['username'],
            },
        },
    }
]


# ==========================================
# 4. THE BRAIN
# ==========================================
def ask_brain(user_input):
    current_time = datetime.now().strftime("%I:%M %p")
    system_prompt = (
        "You are Astra, a highly intelligent, fast, and concise AI assistant. "
        "Never use markdown formatting. "
        f"The current time is {current_time}. "
        "Always refer to the user as Boss."
    )
    
    # THE WHITELIST ROUTER: Python checks if tools are actually needed
    # THE WHITELIST ROUTER: Added file creation keywords!
    tool_keywords = ["weather", "temperature", "open", "youtube", "github", "leetcode", "news", "launch", "play", "file", "create", "make"]
    needs_tools = any(keyword in user_input.lower() for keyword in tool_keywords)
    
    try:
        if needs_tools:
            # Give her the tools, she actually needs them
            print("[System] Action words detected. Granting Astra tool access...")
            response = ollama.chat(
                model='llama3.1',
                messages=[
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': user_input}
                ],
                tools=astra_tools 
            )
        else:
            # Hide the tools completely! She physically has no choice but to use her brain.
            print("[System] Basic chat detected. Unplugging tools for instant speed...")
            response = ollama.chat(
                model='llama3.1',
                messages=[
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': user_input}
                ]
            )
        
        message = response.get('message', {})
        
        # Process tool calls ONLY if she made one
        if message.get('tool_calls'):
            for tool in message['tool_calls']:
                function_name = tool['function']['name']
                arguments = tool['function']['arguments']
                
                if function_name in available_functions:
                    function_to_call = available_functions[function_name]
                    
                    if function_name == 'create_file':
                        return function_to_call(arguments.get('filename'))
                    elif function_name == 'open_website':
                        return function_to_call(arguments.get('url'))
                    elif function_name == 'search_youtube':
                        return function_to_call(arguments.get('query'))
                    elif function_name == 'open_application':
                        return function_to_call(arguments.get('app_name'))
                    elif function_name == 'get_github_stats':
                        return function_to_call(arguments.get('username'))
                    elif function_name == 'get_leetcode_stats':
                        return function_to_call(arguments.get('username'))
                    elif function_name == 'get_weather':
                        return function_to_call(arguments.get('location', 'Lucknow'))
                    elif function_name == 'get_breaking_news':
                        return function_to_call(arguments.get('query'))
                        
        return message.get('content', "I am processing that, Boss.")
        
    except Exception as e:
        print(f"\n[SYSTEM ERROR]: {str(e)}\n")
        return "I am sorry Boss, my core just crashed."


# ==========================================
# 5. THE GRAPHICAL INTERFACE (GUI)
# ==========================================
class AstraGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Setup the Window
        self.title("AstraAI - Core System")
        self.geometry("600x500")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # UI Layout
        self.title_label = ctk.CTkLabel(self, text="Astra AI Offline Engine", font=ctk.CTkFont(size=24, weight="bold"))
        self.title_label.pack(pady=20)

        self.status_label = ctk.CTkLabel(self, text="Status: Booting Up...", text_color="gray", font=ctk.CTkFont(size=14))
        self.status_label.pack(pady=5)

        self.console_box = ctk.CTkTextbox(self, width=500, height=300, font=ctk.CTkFont(size=14))
        self.console_box.pack(pady=10)
        self.console_box.insert("0.0", "System Initializing...\n")
        self.console_box.configure(state="disabled") # Make it read-only

        # STATE VARIABLE: Controls the live countdown
        self.is_listening = False

        # Start Astra's brain in a background thread so the UI doesn't freeze
        self.is_running = True
        self.astra_thread = threading.Thread(target=self.run_astra)
        self.astra_thread.daemon = True
        self.astra_thread.start()

    def update_console(self, text):
        """Safely pushes text to the UI console"""
        self.console_box.configure(state="normal")
        self.console_box.insert("end", text + "\n")
        self.console_box.see("end") # Auto-scroll to bottom
        self.console_box.configure(state="disabled")

    def update_status(self, text, color="white"):
        """Changes the status indicator text"""
        self.status_label.configure(text=f"Status: {text}", text_color=color)

    def speak(self, text):
        """Custom speak function that updates the UI before talking"""
        self.update_console(f"Astra: {text}\n")
        engine.say(text)
        engine.runAndWait()

    # --- NEW LIVE COUNTDOWN LOGIC ---
    def start_countdown(self, seconds):
        """Starts the live ticking clock on the UI"""
        self.is_listening = True
        self.tick_timer(seconds)

    def tick_timer(self, seconds):
        """The loop that visually updates the UI every single second"""
        if not self.is_listening:
            return # The kill switch: Stop ticking if the user stops talking early
        
        if seconds > 0:
            self.update_status(f"Listening... [{seconds}s remaining]", color="#00ffcc")
            # Schedule the next tick in exactly 1 second (1000 milliseconds)
            self.after(1000, self.tick_timer, seconds - 1)
        else:
            self.update_status("Listening Timed Out", color="orange")
            
    def stop_countdown(self):
        """Instantly kills the clock"""
        self.is_listening = False
    # --------------------------------

    def listen(self):
        """Custom listen function linked to the UI and live timer"""
        with sr.Microphone() as source:
            
            # Start the 15-second live countdown!
            self.start_countdown(15) 
            
            try:
                audio = recognizer.listen(source, timeout=10, phrase_time_limit=15)
                
                # Instantly stop the clock the moment you finish your sentence
                self.stop_countdown() 
                self.update_status("Processing audio...", color="yellow")
                
                text = recognizer.recognize_google(audio).lower()
                
                # CLEANUP: Remove accidental microphone mistakes
                mistakes = ["astra", "extra", "straw", "service", "welding service", "abstract", "astro", "a star"]
                for word in mistakes:
                    if text.startswith(word):
                        text = text.replace(word, "", 1).strip()
                
                self.update_console(f"Boss: {text}")
                return text
                
            except sr.WaitTimeoutError:
                self.stop_countdown()
                self.update_status("Listening Timed Out (No speech detected)", color="orange")
                return ""
            except sr.UnknownValueError:
                self.stop_countdown()
                return ""
            except sr.RequestError:
                self.stop_countdown()
                self.update_console("[Error] Microphone network error.")
                return ""

    def run_astra(self):
        """The main loop running in the background thread"""
        self.update_status("Calibrating Microphone...", color="yellow")
        self.speak("Calibrating audio. Please wait.")
        
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=2)
            recognizer.dynamic_energy_threshold = True
            recognizer.energy_threshold = 300 
            
        self.update_status("Online & Ready", color="#00ffcc")
        self.speak("Astra architecture online. I am ready, Boss.")
        
        while self.is_running:
            self.update_status("Waiting for command...", color="gray")
            command = self.listen()
            
            if command:
                if "go to sleep" in command or "shutdown" in command or "exit" in command:
                    self.update_status("Shutting Down", color="red")
                    self.speak("Shutting down protocols. Goodbye!")
                    self.is_running = False
                    self.quit() # Close the window
                    break
                
                self.update_status("Astra is thinking...", color="#ff00ff")
                self.speak("Right away.") 
                
                astra_reply = ask_brain(command)
                
                if astra_reply:
                    self.speak(astra_reply)

if __name__ == "__main__":
    app = AstraGUI()
    app.mainloop()