import os

class Reader:
    # Name template
    # Aryam_S:Wed Mar 25 04:06:13 2020

    def help_list():
        print("")

    def help():
        print("""
        The template for each command is as follows
        <definer> <sub-class> <option>

        Definer call:
        \tThe definer parameter defines what action is to be done. For example

        \tlist ... (Will list whatever is is in the following options) {list period 1}
        \tset ...  (Will set the sub-class object as the option)       {set prompt <><>}

        Sub-Class:
        \tThe sub-class parameter explains what command is to be run. For example

        \tlist period ... (List period table)
        \tset prompt ...  (Set prompt)

        Option:
        \tThe option parameter allows arguments to be passed to the sub-class option. For example

        \t>> set prompt <><><> 
        \t... (Changes prompt)

        \t<><><> set prompt <._.>
        \t... (Changes prompt)

        \t<._.> list period 1
        \t... (Prints out table)
        """)

    def commands():
        print("Possible commands are:")
        current_commands = ["list period <val>", "set prompt <val>", ""]
        for i in current_commands:
            print(i)

    def attendance_data(period_no: int):
        if period_no > 4:
            print("No such period no")
            return 
        
        with open(f"../periods/period{period_no}/attendance.txt") as f:
            highest = -1
            for line in f:
                info = line.strip().split(":", 1)
                name = info[0]
                if len(name) > highest:
                    highest = len(name)
            
            if highest == -1:
                print("No attendace data")
                return

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

def accuracy(word):
    pass

if __name__ == "__main__":
    PS = ">> "

    while True:
        command = input(PS).lower().lstrip()

        if command.startswith("list"):
            option = command.split(" ", 1)[-1]

            if option.split(" ")[0] == "period":
                Reader.attendance_data(int(option.split(" ")[1]))

        elif command.startswith("set"):
            option = command.split(" ", 2)
            if option[-2] == "prompt":
                PS = option[-1] if option[-1].endswith(" ") else option[-1] + " "
        
        elif command.startswith("help"):
            option = command.split(" ")
            if option[-1] == "help":
                Reader.help()
            
            elif option[-1] == "list":
                pass

            elif option[-1] == "set":
                pass

        
        elif command == "clear":
            os.system("clear")