from time import sleep
import difflib
import os
# import cmd
# TODO: Cry
class Reader:
    # Name template
    # Aryam_S:Wed Mar 25 04:06:13 2020
    # Edge case (extra space)
    # Aryam_S:Fri Apr  3 17:58:04 2020

    def help():
        path = "help_docs/help.txt"
        file_path = path if __name__ == "__main__" else "../../eye/" + path

        with open(file_path) as f:
            for i in f:
                print("\33[32m", i.rstrip(), "\33[0m")

    def help_list():
        path = "help_docs/list.txt"
        file_path = path if __name__ == "__main__" else "../../eye/" + path

        with open(file_path) as f:
            for i in f:
                print("\33[32m", i.rstrip(), "\33[0m")

    def help_commands():
        path = "help_docs/commands.txt"
        file_path = path if __name__ == "__main__" else "../../eye/" + path

        print("\n\33[32m" + "Possible commands are:")
        with open(file_path) as f:
            for i in f:
                print(i.rstrip())
        print("\33[0m", end="")

    def attendance_data(period_no: int):
        if period_no > 4:
            print("\33[32m", "No such period no", "\33[0m")
            return None

        abs_path = f"../periods/period_{period_no}/attendance.txt"
        rel_path = f"../period_{period_no}/attendance.txt"
        file_path = abs_path if __name__ == "__main__" else rel_path

        with open(file_path) as f:
            # lnl = longest name length
            lnl = -1
            for line in f:
                info = line.strip().split(":", 1)
                name = info[0]
                if len(name) > lnl:
                    lnl = len(name)

            if lnl == -1:
                print("No attendace data")
                return None

            lnl += 1

            print("+" + ("-" * lnl) + "-------------------" + "+")
            print("|" + "Name".center(lnl + 4) + "|" + "Info".center(14) + "|")
            print("+" + ("-" * lnl) + "-------------------" + "+")

            f.seek(0)
            a = True

            for line in f:
                sep = "━" if a else "-"
                info = line.strip().split(":", 1)
                name = info[0]
                info = [i for i in info[1].split(" ") if i not in [" ", ""]]
                day, time = info[0], info[3]

                print("|" + (name + " ").ljust(lnl + 2, sep), end="> | ")
                print(time, day + " ", end="|\n")
                a = not a

            print("+" + "-" * lnl + "-------------------" + "+")
            f.close()


def accuracy(command):
    if command in [" ", ""]:
        return None

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


def main(sleep_time=3):
    sleep(sleep_time)
    PS = ">> "
    last_command = "help"

    while True:
        command = input(PS).lower().lstrip()

        if command == "p":
            command = last_command

        if command.startswith("list"):
            option = command.split(" ", 1)[-1]
            if option.split(" ")[0] == "period":
                try:
                    Reader.attendance_data(int(option.split(" ")[1]))

                except (ValueError, IndexError, FileNotFoundError):
                    print("\33[32m", "Invalid number, try again", "\33[0m")

        elif command.startswith("set"):
            option = command.split(" ", 2)
            if option[-2] == "prompt":
                PS = option[-1]
                PS = PS if PS.endswith(" ") else PS + " "

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

        last_command = command


if __name__ == "__main__":
    main(sleep_time=0)
