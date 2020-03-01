import os
from time import sleep

import schedule

import cropper
import i_see_you
from text_animator import Animation


def job():
    if bool([i for i in os.listdir("data/tocrop") if not i.startswith(".")]):
        should_crop = True if input("There are images in the to_crop file, would you like to add new students? (y/n)").lower() == "y" else False

        if should_crop:
            cropper.main(int(input("Class_no: ")))
        
    else:
        Animation.to_animate(text=Animation.standard_text, to_sleep=0.001)

        print("Running main Script")
        i_see_you.main()

if __name__ == "__main__":
    job()
    """
    schedule.every().day.at("08:15").do(job)

    while True:
        schedule.run_pending()
        sleep(10)
    """
