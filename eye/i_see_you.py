import logging
import os
import sched
import threading
import time

import cv2
import face_recognition
import numpy as np

import repl


def setup_logger(name, log_file, formatter, log):
    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)

    if log:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.CRITICAL)

    logger.addHandler(handler)

    return logger


def min_to_sec(minute):
    return minute * 60


def cleanup():
    open("attendance.txt", "w").close()

    for i in os.listdir("snapshots"):
        if not i.startswith("."):
            os.unlink("snapshots/" + i)


def load_encodings(valid_filetypes=(".jpg", ".png")):
    encoded = []
    names = []

    for name in os.listdir():
        if not name.lower().endswith(valid_filetypes):
            continue

        names.append(name.split(".")[0])
        image = face_recognition.load_image_file(name)
        loc = face_recognition.face_locations(image, 0)
        encoded.append(face_recognition.face_encodings(image, loc, 1)[0])

    return encoded, names


def average_pixel_color(frame):
    return np.average(frame)


def proccess_data(known_encoded, known_names, frame):
    small_frame = setter(frame)
    face_locations, face_encodings = features(small_frame)

    names = []
    for face_encode in face_encodings:
        name = detection(known_encoded, face_encode, known_names)
        names.append(name)
    return names


def setter(frame):
    return cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)[:, :, ::-1]


def features(frame):
    face_locations = face_recognition.face_locations(frame)
    face_encodings = face_recognition.face_encodings(frame, face_locations, 0)
    return face_locations, face_encodings


def detection(known_encoded, face_encode, known_names):
    print(known_encoded, face_encode)
    result = face_recognition.compare_faces(known_encoded, face_encode)
    name = "Unknown"

    dif_vals = face_recognition.face_distance(known_encoded, face_encode)

    best_match_index = np.argmin(dif_vals)
    dif_val = dif_vals[best_match_index]

    if result[best_match_index] and dif_val < 0.7:
        name = known_names[best_match_index]

    recorder.debug(f"{name} with {1 - dif_val} confidence")
    # print(f"Name      : {name}")
    # print(f"Confidence: {1 - dif_val}")
    return name


def avg_names(all_names, scan_time=5):
    everyname = [val for sublist in all_names for val in sublist]
    main_names = []

    for name in set(everyname):
        if everyname.count(name) > int(scan_time / 2):
            main_names.append(name)
    return main_names


def write(all_names, img):
    f = open("attendance.txt", "r+")

    lines = f.readlines()
    already_in = []

    for line in lines:
        if not line.startswith("\n#"):
            already_in.append(line.strip().split(":")[0])
            continue
        break

    for name in all_names:
        if already_in.count(name) <= 0:
            current_time = str(time.ctime())
            f.write(f"{name}:{current_time}\n")
            already_in.append(name)
            already_in = remove_dupe(already_in)
            cv2.imwrite(f"snapshots/{name}:{current_time}.jpg", img)

            print(f"Recorded and saved picture of {name} at {current_time}")

            recorder.info(
                f"Recorded and saved picture of {name} at {current_time}\n")

            logger.info(
                f"Recorded and saved picture of {name} at {current_time}")


def remove_dupe(head):
    return list(set(head))


def write_not_here(known_names):
    f = open("attendance.txt", "r+")
    lines = f.readlines()
    already_in = []
    not_here = []
    for line in lines:
        if not line.startswith("\n#"):
            already_in.append(line.strip().split(":")[0])
            continue
        break

    set_known_names = set(known_names)
    f.write("\n##########\nNot here\n")

    for name in list(set_known_names.symmetric_difference(already_in)):
        f.write(name + "\n")
        not_here.append(name)

    logger.debug(
        f"Names that have been recorded {set_known_names}\n"
        f"Names that have not been recorded {not_here}")


def start(cap, file_no, delay):
    logger.debug(
        "Current folder before changing directory\n"
        f"{os.getcwd()}")

    os.chdir(f"../periods/period_{file_no}")
    print(f"Starting for Period {file_no}")
    cleanup()
    print("Cleanup finished")

    known_encoded, known_names = load_encodings()
    # known = {k: v for (k, v) in zip(known_names, known_encoded)}
    print("Encodings loaded")

    rigidness_motion = 3.2
    scan_time = 20

    logger.debug(
        f"Period no ------------> {file_no}\n"
        f"Number of students ---> {len(known_names)}\n"
        f"Tolerance level ------> {rigidness_motion}\n"
        f"Motion capture time --> {scan_time}")

    if len(known_names) == 0:
        print("Skipping period as no photos are in file")
        logger.warning(
            "No student images in located folder\n"
            f"Current folder being checked is {os.getcwd()}")
        cap.release()
        return None

    start = time.time()
    # Why in christ's name is this being so badly shown to the user, Christ.
    print(f"Tolerance level ------------------------> {rigidness_motion}")
    print(f"Frames taken when motion is detected ---> {scan_time}")

    ret, last_frame = cap.read()
    last_frame_gray = cv2.cvtColor(last_frame, cv2.COLOR_RGB2GRAY)
    print("Camera now on")

    while True:
        ret, frame = cap.read()
        frame_gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

        diff_frame = cv2.absdiff(last_frame_gray, frame_gray)
        average_intensity = average_pixel_color(diff_frame)

        if average_intensity > rigidness_motion:
            all_names = []
            recorder.info(f"Movement detected\nTol = {average_intensity}\n")
            for i in range(scan_time):
                ret, frame = cap.read()
                all_names.append(
                    proccess_data(known_encoded, known_names, frame))

            recorder.debug(f"Names detected were {all_names}")
            names = avg_names(all_names, scan_time)
            write(names, frame)
            frame_gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

        last_frame_gray = frame_gray

        if time.time() - start > delay:
            write_not_here(known_names)
            break

    os.chdir("../../eye")
    print(f"Done with Period {file_no}")


def REPL():
    repl.main()


def main(log):
    global logger, recorder
    s = sched.scheduler(time.time, time.sleep)
    repl_thread = threading.Thread(target=REPL, daemon=True)

    # Main
    formatter = logging.Formatter(
        "%(asctime)s.%(msecs).03d\n"
        "%(levelname)s\t\t%(filename)s\t\t%(funcName)s\n"
        "%(message)s\n", datefmt="%Y/%m/%d | %H:%M:%S")

    logger = setup_logger(
        "main_logger", "log_files/i_see_you.log", formatter, log)

    # Recorder
    formatter = logging.Formatter(
        "%(asctime)s.%(msecs).03d\t%(levelname)s\n"
        "%(message)s", datefmt="%Y/%m/%d | %H:%M:%S")

    recorder = setup_logger(
        "recorder_logger", "log_files/recordings.log", formatter, log)

    cap = cv2.VideoCapture(0)

    # Period lengths (Delay)
    period_length = min_to_sec(1 * 60 + 15)

    # Period 1 to period 4 start times from period 1 start time
    period_start_times = [
        min_to_sec(0 * 60 + 00),
        min_to_sec(1 * 60 + 22),
        min_to_sec(3 * 60 + 35),
        min_to_sec(4 * 60 - 5)]

    if int(time.localtime()[2]) % 2 == 1:
        for period_stats in zip(period_start_times, ["1", "2", "3", "4"]):
            s.enter(period_stats[0], 1, start,
                    argument=(cap, period_stats[1], period_length - 5,))
    else:
        for period_stats in zip(period_start_times, ["2", "1", "4", "3"]):
            s.enter(period_stats[0], 1, start,
                    argument=(cap, period_stats[1], period_length - 5,))

    print("starting")
    repl_thread.start()
    s.run()


if __name__ == "__main__":
    # If you're trying to understand this code. Don't. Even I don't.
    log = False
    print(f"Logging state: {log}")
    s = sched.scheduler(time.time, time.sleep)
    cap = cv2.VideoCapture(0)
    # Main
    formatter = logging.Formatter(
        "%(asctime)s.%(msecs).03d\n"
        "%(levelname)s\t\t%(filename)s\t\t%(funcName)s\n"
        "%(message)s\n", datefmt="%Y/%m/%d | %H:%M:%S")

    logger = setup_logger(
        "main_logger", "log_files/i_see_you.log", formatter, log)

    # Recorder
    formatter = logging.Formatter(
        "%(asctime)s.%(msecs).03d\t%(levelname)s\n"
        "%(message)s", datefmt="%Y/%m/%d | %H:%M:%S")

    recorder = setup_logger(
        "recorder_logger", "log_files/recordings.log", formatter, log)

    # Period lengths (Delay)
    period_length = min_to_sec(1 * 60 + 15)

    # Period 1 to Period 4 start times from period 1 start time
    period_start_times = [
        min_to_sec(0 * 60 + 00),
        min_to_sec(1 * 60 + 22),
        min_to_sec(3 * 60 + 35),
        min_to_sec(4 * 60 - 5)]

    if int(time.localtime()[2]) % 2 == 1:
        for period_stats in zip(period_start_times, ["1", "2", "3", "4"]):
            s.enter(period_stats[0], 1, start,
                    argument=(cap, period_stats[1], period_length - 5,))
    else:
        for period_stats in zip(period_start_times, ["2", "1", "4", "3"]):
            s.enter(period_stats[0], 1, start,
                    argument=(cap, period_stats[1], period_length - 5,))

    s.run()
