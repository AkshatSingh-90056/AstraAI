import speech_recognition as sr

def listen():
    recoginzer = sr.Recognizer()

    with sr.Microphone() as source:
        print("Calibrating background niose... please wait a second.")
        recoginzer.adjust_for_ambient_noise(source,duration= 1)

        print("Listening... (Say something!)")

        
        try:
            audio = recoginzer.listen(source,timeout= 5 , phrase_time_limit=10)
            print("Processing your voice.... ")

            text = recoginzer.recognize_google(audio)
            print(f"You said '{text}")
            return text.lower()

        except sr.UnknownValueError:
            print("Error: I couldn't understand what you said. It sounded like bullshit.")
            return ""
        except sr.RequestError:
            print("Error: My internet connection to the speech engine is down.")
            return ""

        except Exception as e:
            print(f"A system error occurred : {e}")
            return ""

print("Testing the Ears... ")
listen()

        