from time import sleep
import difflib
import os

class Reader:
    # Name template
    # Aryam_S:Wed Mar 25 04:06:13 2020

    def help():
        with open("help_docs/help.txt") as f:
            for i in f:
                print("\33[32m", i.rstrip(), "\33[0m")

    def help_list():
        with open("help_docs/list.txt") as f:
            for i in f:
                print("\33[32m", i.rstrip(), "\33[0m")

    def help_commands():
        print("\n\33[32m" + "Possible commands are:")

        with open("help_docs/commands.txt") as f:
            for i in f:
                print(i.rstrip())
        print("\33[0m", end="")
    
    def attendance_data(period_no: int):
        if period_no > 4:
            print("No such period no")
            return None
        
        with open(f"../periods/period_{period_no}/attendance.txt") as f:
            highest = -1
            for line in f:
                info = line.strip().split(":", 1)
                name = info[0]
                if len(name) > highest:
                    highest = len(name)
            
            if highest == -1:
                print("No attendace data")
                return None

            highest += 1

            print("+" + ("-" * highest)  + "-------------------" + "+")
            print("|" +  "Name".center(highest + 4)  + "|" + "Info".center(14) + "|")
            print("+" + ("-" * highest)  + "-------------------" + "+")

            f.seek(0)
            a = True
            
            for line in f:
                sep = "━" if a else "-"
                info = line.strip().split(":", 1)
                name = info[0]
                info = info[1].split(" ")
                day, time = info[0], info[3]
                
                print("|" + (name + " ").ljust(highest + 2, sep), end="> | ")
                print(time, day + " ", end="|\n")
                
                a = not a
            
            print("+" + "-" * highest  + "-------------------" + "+")

            f.close()

def accuracy(command):
    highest = -1
    guessed = []
    for possible_command in ["help", "list", "set"]:
        seq = difflib.SequenceMatcher(None, command, possible_command)
        val = seq.ratio() * 100
        if val >= 25:
            guessed.append([possible_command, val])    
    
    if len(guessed):
        # Largest value will be the first element
        guessed = sorted(guessed, key=lambda x: x[-1], reverse=True)
        print("\33[32m", "\nThe most similar command(s)")

        for pack in guessed:
            print(pack[0])
    
    else:
        print("\33[32m", "No command found", end=" ")
    print("\33[0m")
    return None

def main():
    sleep(3)
    PS = ">> "

    while True:
        command = input(PS).lower().lstrip()

        if command.startswith("list"):
            option = command.split(" ", 1)[-1]

            if option.split(" ")[0] == "period":
                try:
                    Reader.attendance_data(int(option.split(" ")[1]))
                
                except ValueError:
                    print("\33[32m", "Invalid number, try again", "\33[0m")

        elif command.startswith("set"):
            option = command.split(" ", 2)
            if option[-2] == "prompt":
                PS = option[-1] if option[-1].endswith(" ") else option[-1] + " "
        
        elif command.startswith("help"):
            option = command.strip().split(" ")

            if option[-1] == "help":
                Reader.help()
            
            elif option[-1] == "commands":
                Reader.help_commands()
            
            elif option[-1] == "list":
                Reader.help_list()

            elif option[-1] == "set":
                pass

        elif command == "clear":
            print("\33[0m")
            os.system("clear")
        
        elif command == "exit":
            exit()
        
        else:
            accuracy(command)
