import speech_recognition as sr

def listen():
    recoginzer = sr.Recognizer()

    with sr.Microphone() as source:
        print("Calibrating background niose... please wait a second.")
        recoginzer.adjust_for_ambient_noise(source,duration= 1)

        