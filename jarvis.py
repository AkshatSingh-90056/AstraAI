import speech_recognition as sr
import pyttsx3
import ollama
import webbrowser
import os
import urllib.parse
import requests  
from datetime import datetime


engine = pyttsx3.init()
engine.setProperty('rate', 170)
recognizer = sr.Recognizer()

def speak(text):
    engine.say(text)
    engine.runAndWait()

def listen():
    with sr.Microphone() as source:
        print("\nListening...")
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=8)
            text = recognizer.recognize_google(audio).lower()
            print(f"You said: {text}")
            return text
        except (sr.WaitTimeoutError, sr.UnknownValueError):
            return ""
        except sr.RequestError:
            print("Network error.")
            return ""


def create_file_tool(filename):
    if "." not in filename:
        filename += ".txt"
    try:
        with open(filename, 'w') as f:
            pass
        return f"Successfully created the file named {filename}."
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
    exe_name = apps.get(app_name.lower(), app_name.lower())
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
    """Fetches live problem-solving stats directly from LeetCode."""
    
  
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
        

        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0"
        }
        
        response = requests.post(url, json={"query": query, "variables": variables}, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            
   
            if "errors" in data or data.get("data", {}).get("matchedUser") is None:
                return f"Boss, I couldn't find the stats for the LeetCode user {username}."
            
         
            stats = data["data"]["matchedUser"]["submitStats"]["acSubmissionNum"]
            counts = {item['difficulty']: item['count'] for item in stats}
            
            total = counts.get('All', 0)
            easy = counts.get('Easy', 0)
            medium = counts.get('Medium', 0)
            hard = counts.get('Hard', 0)
            
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

available_functions = {
    'create_file': create_file_tool,
    'open_website': open_website_tool,
    'search_youtube': search_youtube_tool,
    'open_application': open_application_tool,
    'get_github_stats': get_github_stats_tool,
    'get_leetcode_stats': get_leetcode_stats_tool,
    'get_weather': get_weather_tool 
}


jarvis_tools = [
    {
        'type': 'function',
        'function': {
            'name': 'create_file',
            'description': 'Creates a new empty text file.',
            'parameters': {
                'type': 'object',
                'properties': {
                    'filename': {'type': 'string'},
                },
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
                        'description': 'The city to get the weather for. If the user does not specify a city, default to "Lucknow".'
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
            'description': 'Opens a specific website homepage in the browser.',
            'parameters': {
                'type': 'object',
                'properties': {
                    'url': {
                        'type': 'string', 
                        'description': 'The URL of the website. CRITICAL: "my github" -> "https://github.com/AkshatSingh-90056". "my linkedin" -> "https://www.linkedin.com/in/akshat-singh-811641317/". "my leetcode" or "my lead code" -> "https://leetcode.com/u/Akshat_singh22/".'
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
            'description': 'Searches YouTube for a specific video or topic.',
            'parameters': {
                'type': 'object',
                'properties': {
                    'query': {'type': 'string'},
                },
                'required': ['query'],
            },
        },
    },
    {
        'type': 'function',
        'function': {
            'name': 'open_application',
            'description': 'Opens a local desktop application.',
            'parameters': {
                'type': 'object',
                'properties': {
                    'app_name': {'type': 'string'},
                },
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
                        'description': 'The exact GitHub username. CRITICAL: If the user asks about "my github", use exactly "AkshatSingh-90056".'
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
                        'description': 'The exact LeetCode username. CRITICAL: If the user asks about "my leetcode", "league code", "lead code", or "my problem solving stats", use exactly "Akshat_singh22".'
                    },
                },
                'required': ['username'],
            },
        },
    }
]


def ask_brain(user_input):
    current_time = datetime.now().strftime("%I:%M %p")
    
  
    system_prompt = (
        "You are Jarvis, a highly intelligent and concise AI assistant. "
        "Never use markdown formatting. "
        f"The current time is {current_time}. "
        "If the user asks you to do something that matches one of your capabilities (like opening a website, checking weather, etc.), trigger the tool silently. "
        "Do NOT explain that you are going to use a tool, and NEVER write out dictionary or code formats in your spoken text. "
        "If no tool is needed, just chat naturally. "
        "If the user asks for the weather without specifying a city, always default the location to Lucknow. "
        "Always refer to the user as Boss."
    )
    
    try:
        response = ollama.chat(
            model='llama3.1',
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_input}
            ],
            tools=jarvis_tools 
        )
        
        message = response.get('message', {})
        
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
                        return function_to_call(arguments.get('location', 'Deoria'))
                        
        return message.get('content', "I am processing that, Boss.")
        
    except Exception as e:
        return "I am sorry Boss, I am having trouble communicating with my core."


def run_jarvis():
    print("Initializing systems...")
    speak("Calibrating audio. Please wait.")
    
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=2)
        recognizer.dynamic_energy_threshold = True
        recognizer.energy_threshold = 300 
        
    speak("Function calling architecture online. I am ready, Boss.")
    
    while True:
        command = listen()
        
        if command:
            if "go to sleep" in command or "shutdown" in command or "exit" in command:
                speak("Shutting down protocols. Goodbye!")
                break
            
            print("Jarvis is thinking...")
            speak("Right away.") 
            
            jarvis_reply = ask_brain(command)
            
            if jarvis_reply:
                print(f"Jarvis: {jarvis_reply}")
                speak(jarvis_reply)

if __name__ == "__main__":
    run_jarvis()