import pyttsx3
import speech_recognition as sr
import datetime
import webbrowser


engine = pyttsx3.init('sapi5')
def speak(text):
    print(f"Jarvis: {text}")
    engine.say(text)
    engine.runAndWait()


def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("\nListening...")
      
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=7)
            text = recognizer.recognize_google(audio).lower()
            print(f"You said: {text}")
            return text
        except sr.UnknownValueError:
           
            return ""
        except Exception as e:
            return ""


def run_jarvis():
    speak("System is online. I am ready.")
    
    while True:
        command = listen()
        
        
        if command == "":
            continue
            

        if "time" in command:
            current_time = datetime.datetime.now().strftime("%I:%M %p")
            speak(f"The time is {current_time}")
            
        elif "youtube" in command:
            speak("Opening YouTube")
            webbrowser.open("https://www.youtube.com")
            
        elif "stop" in command or "sleep" in command:
            speak("Shutting down protocols. Goodbye!")
            break 
        else:
            speak("I heard you, but I don't know how to do that yet.")


run_jarvis()