import speech_recognition as sr
import pyttsx3
import ollama
import webbrowser
import os
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
    """Physically creates a file on the hard drive."""
    if "." not in filename:
        filename += ".txt"
    try:
        with open(filename, 'w') as f:
            pass
        abs_path = os.path.abspath(filename)
        print(f"System: File created at {abs_path}")
        return f"Successfully created the file named {filename}."
    except Exception as e:
        return f"Failed to create file. Error: {str(e)}"

def open_website_tool(url):
    """Opens a URL in the default browser."""
    if not url.startswith("http"):
        url = "https://" + url
    try:
        webbrowser.open(url)
        print(f"System: Opening browser to {url}")
        return f"I have opened the website for you, Boss."
    except Exception as e:
        return f"Failed to open website. Error: {str(e)}"


available_functions = {
    'create_file': create_file_tool,
    'open_website': open_website_tool
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
                    'filename': {
                        'type': 'string',
                        'description': 'The name of the file to create, including the extension (e.g., notes.txt, data.csv)',
                    },
                },
                'required': ['filename'],
            },
        },
    },
    {
        'type': 'function',
        'function': {
            'name': 'open_website',
            'description': 'Opens a specific website in the computer browser.',
            'parameters': {
                'type': 'object',
                'properties': {
                    'url': {
                        'type': 'string',
                        'description': 'The full URL of the website to open, such as www.youtube.com or www.google.com',
                    },
                },
                'required': ['url'],
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
        "If the user asks you to do something, use your tools if applicable. "
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
            print("Jarvis decided to use a tool...")
            

            for tool in message['tool_calls']:
                function_name = tool['function']['name']
                arguments = tool['function']['arguments']
                
          
                if function_name in available_functions:
                    function_to_call = available_functions[function_name]
                    
              
                    if function_name == 'create_file':
                        result_speech = function_to_call(arguments['filename'])
                    elif function_name == 'open_website':
                        result_speech = function_to_call(arguments['url'])
                        
                    return result_speech
                    
        
        return message.get('content', "I am processing that, Boss.")
        
    except Exception as e:
        print(f"Brain Error: {e}")
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
            jarvis_reply = ask_brain(command)
            
            if jarvis_reply:
                print(f"Jarvis: {jarvis_reply}")
                speak(jarvis_reply)

if __name__ == "__main__":
    run_jarvis()