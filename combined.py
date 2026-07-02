import pyttsx3
import datetime
import webbrowser


engine = pyttsx3.init('sapi5')

def speak(text):
    
    print(f"Jarvis: {text}")
    engine.say(text)
    engine.runAndWait()



def execute_command(command):
    command = command.lower()

    if "time" in command:
        
        current_time = datetime.datetime.now().strftime("%I:%M %p")
        speak(f"The current time is {current_time}")
        
    elif "youtube" in command:
        speak("Opening YouTube now.")
        webbrowser.open("https://www.youtube.com")
        
    else:
        speak("I don't know how to do that yet.")



speak("Systems online. Testing combined protocols.")

execute_command("hey jarvis what time is it")
execute_command("open youtube please")