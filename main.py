import os
os.system("clear")
import time
import schedule

import cropper
import i_see_you
from text_animator import Animation

def job():
    if bool([i for i in os.listdir("data/tocrop") if not i.startswith(".")]):
        if input("There are images in the to_crop file, would you like to add new students? (y/n): ").lower() == "y":
            cropper.main(int(input("Class_no: ")))
        
    Animation.to_animate(text=Animation.standard_text)

    print("Running main Script")
    i_see_you.main()

if __name__ == "__main__":
    job()
    # schedule.every().day.at("08:15").do(job)

    # while True:
    #     if time.localtime()[6] > 5:
    #         time.sleep()
    #     schedule.run_pending()
    #     time.sleep(10)