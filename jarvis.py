import speech_recognition as sr
import pyttsx3
import ollama
import webbrowser
import os  # NEW: For file creation and absolute paths
import re  # NEW: For extracting the file name from your voice command
from datetime import datetime

# Initialize the Text-to-Speech Engine
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
        except sr.WaitTimeoutError:
            return ""
        except sr.UnknownValueError:
            return ""
        except sr.RequestError:
            print("Network error.")
            return ""

def ask_brain(user_input):
    try:
        current_time = datetime.now().strftime("%I:%M %p")
        system_prompt = (
            "You are Jarvis, a brilliant and concise AI assistant. "
            "Never use markdown symbols like asterisks, bullet points, or bold text. "
            f"The absolute correct current time is {current_time}. Use this exact time if the user asks. "
            "Always respond in clean, plain paragraphs and refer to the user as Boss."
        )
        
        response = ollama.chat(
            model='llama3',
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_input}
            ]
        )
        return response['message']['content']
    except Exception as e:
        return "I am sorry Boss, I am having trouble communicating with my core."

def run_jarvis():
    print("Initializing systems...")
    speak("Calibrating audio systems. Please wait.")
    
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=2)
        recognizer.dynamic_energy_threshold = True
        recognizer.energy_threshold = 300 
        
    speak("System is online. I am ready, Boss.")
    
    while True:
        command = listen()
        
        if command:
            # 1. Check for shutdown
            if "go to sleep" in command or "shutdown" in command or "exit" in command:
                speak("Shutting down protocols. Goodbye!")
                break
                
            # 2. NEW ACTION: Create a file
           # 2. NEW ACTION: Create a file
            elif "create a file" in command or "make a file" in command:
                print("Jarvis: Processing file creation request...")
                
                # UPDATE: Now looks for "named", "called", OR "name"
                match = re.search(r'(?:named|called|name)\s+(\S+)', command)
                
                if match:
                    filename = match.group(1)
                    
                    if "." not in filename:
                        filename += ".txt"
                        
                    try:
                        with open(filename, 'w') as f:
                            pass
                            
                        abs_path = os.path.abspath(filename)
                        # Prints the success path to your terminal
                        print(f"Jarvis: File created successfully at {abs_path}") 
                        speak(f"File created successfully. It is saved as {filename}.")
                        
                    except Exception as e:
                        print(f"Error: {e}")
                        speak("I encountered a system error while trying to write the file.")
                else:
                    # UPDATE: Added a print statement so you can see if it fails
                    error_msg = "I didn't catch the exact name. Please say 'create a file named' followed by your desired name."
                    print(f"Jarvis: {error_msg}")
                    speak(error_msg)
                
                continue
                
            # 3. HARDCODED ACTION: Open YouTube
            elif "open youtube" in command:
                speak("Opening YouTube right away, Boss.")
                print("Jarvis: Opening YouTube...")
                webbrowser.open("https://www.youtube.com")
                continue
                
            # 4. HARDCODED ACTION: Open Google
            elif "open google" in command:
                speak("Opening Google, Boss.")
                print("Jarvis: Opening Google...")
                webbrowser.open("https://www.google.com")
                continue

            # 5. General conversation via Llama 3
            print("Jarvis is thinking...")
            jarvis_reply = ask_brain(command)
            print(f"Jarvis: {jarvis_reply}")
            speak(jarvis_reply)

if __name__ == "__main__":
    run_jarvis()