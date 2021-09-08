import argparse
import logging
import os
import time

import schedule

import cropper
import i_see_you
from text_animator import Animation


def job(log):
    if bool([i for i in os.listdir("../to_crop") if i[0] != "."]):
        logger.debug("Photos are in the to_crop folder")

        if input("There are images in the to_crop file, would you like to "
                 "add new students? (y/n): ").strip()[0].lower() == "y":

            logger.debug("User wanted to crop photos")
            class_no = int(input("Class_no: "))

            if class_no in [i for i in range(1, 5)]:
                cropper.main(class_no)

            else:
                print("Invalid number executing main folder")
                logger.debug(
                    "User entered invalid number, executing main folder")

        else:
            logger.debug("User did not want to crop photos")

    Animation.to_animate(text=Animation.standard_text)
    print("Running main Script")
    logger.info("Running main Script")
    i_see_you.main(log)


def flags():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()

    group.add_argument(
        "-nl", "--no_logging",
        help="When this flag is selected NO LOGGING will occur",
        action="store_true")

    # group.add_argument(
    #     "-l", "--logging",
    #     help="When this flag is selected LOGGING will occur",
    #     action="store_true")

    args = parser.parse_args()
    return not args.no_logging


if __name__ == "__main__":
    os.system("clear")
    print(f"Time taken to import all libraries: {time.perf_counter()}")
    log = flags()

    logger = logging.getLogger(__name__)

    if log:
        logger.setLevel(logging.DEBUG)

    else:
        logger.setLevel(logging.CRITICAL)

    formatter = logging.Formatter(
        "%(asctime)s.%(msecs).03d\n"
        "%(levelname)s\t\t%(filename)s\t\t%(funcName)s\n"
        "%(message)s\n", datefmt="%Y/%m/%d | %H:%M:%S")

    file_handler = logging.FileHandler("log_files/main.log")
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    logger.debug(
        "|==============|\n"
        "| N E W  D A Y |\n"
        "|==============|")

    job(log)
    # schedule.every().day.at("08:15").do(job)

    # while True:
    #     if time.localtime()[6] > 5:
    #         time.sleep()
    #     schedule.run_pending()
    #     time.sleep(10)
