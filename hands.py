import datetime
import webbrowser

def execute_command(command):
    command = command.lower()

    if "time" in command:
        current_time = datetime.datetime.now().strftime("%I:%M %p")
        print(f"The current time is {current_time}")

    elif "youtube" in command:
        print("Opening Youtube...")
        webbrowser.open("https://www.youtube.com")

    else:
        print("I don't know ho to do that yet.")


print("Testing command 1 :")
execute_command("Hey jarvis what time it is")

print("\nTesting command 2 :")
execute_command("can you open youtube please")

print("\nTesting command 3 :")
execute_command("make me a sandwich")
