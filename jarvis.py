import speech_recognition as sr
import pyttsx3
import ollama
import webbrowser
import os
import urllib.parse
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
    """Launches standard Windows applications."""
   
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

available_functions = {
    'create_file': create_file_tool,
    'open_website': open_website_tool,
    'search_youtube': search_youtube_tool,
    'open_application': open_application_tool 
}


jarvis_tools = [
    {
        'type': 'function',
        'function': {
            'name': 'create_file',
            'description': 'Creates a new empty text file or document on the computer.',
            'parameters': {
                'type': 'object',
                'properties': {
                    'filename': {'type': 'string', 'description': 'The name of the file to create.'},
                },
                'required': ['filename'],
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
                        'description': 'The URL of the website. If the user says a brand name, format it as www.[name].com. CRITICAL: If the user says "my github", "my profile", or "my repository", the URL MUST be exactly "https://github.com/AkshatSingh-90056".'
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
            'description': 'Searches YouTube for a specific video, topic, song, or channel.',
            'parameters': {
                'type': 'object',
                'properties': {
                    'query': {'type': 'string', 'description': 'The exact search term to look for on YouTube.'},
                },
                'required': ['query'],
            },
        },
    },

    {
        'type': 'function',
        'function': {
            'name': 'open_application',
            'description': 'Opens a local desktop application or program on the Windows computer.',
            'parameters': {
                'type': 'object',
                'properties': {
                    'app_name': {
                        'type': 'string', 
                        'description': 'The name of the application to open (e.g., notepad, calculator, vs code, terminal).'
                    },
                },
                'required': ['app_name'],
            },
        },
    }
]

def ask_brain(user_input):
    current_time = datetime.now().strftime("%I:%M %p")
    system_prompt = (
        "You are Jarvis, a brilliant and concise AI assistant. "
        "Never use markdown symbols like asterisks, bullet points, or bold text. "
        f"The current time is {current_time}. "
        "CRITICAL INSTRUCTION: ONLY use a tool if the user EXPLICITLY asks you to open a website, "
        "search YouTube, create a file, or open an application. "
        "If the user is just chatting, praising you, or asking general questions, DO NOT use tools. "
        "If the user asks you to read, count, or extract data from a website, politely explain that you can "
        "open the website for them, but you do not have screen-reading capabilities yet. "
        "NEVER output your internal JSON thoughts or tool formats in your spoken text. "
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
                        return function_to_call(arguments['filename'])
                    elif function_name == 'open_website':
                        return function_to_call(arguments['url'])
                    elif function_name == 'search_youtube':
                        return function_to_call(arguments['query'])
                    elif function_name == 'open_application':
                        return function_to_call(arguments['app_name'])
                        
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