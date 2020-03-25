import os
import sched
import threading
import time

import cv2
import face_recognition
import numpy as np

import repl_sys

print(f"Time taken to import all libraries: {time.perf_counter()}")

def cleanup():
    open("attendance.txt", "w").close()

    contents = os.listdir("snapshots")

    for i in contents:
        if not i.startswith("."):
            os.unlink("snapshots/" + i)

def load_encodings(include_filetypes=(".jpg", ".png")):
    encoded = []
    names = os.listdir()
    names = [name for name in names if name.lower().endswith(include_filetypes)]

    for name in names:
        image = face_recognition.load_image_file(name)
        loc = face_recognition.face_locations(image, 0)
        encoded.append(face_recognition.face_encodings(image, loc, 1)[0])
    
    names = [name.split(".")[0] for name in names]
    return encoded, names

def setter(frame):
    return cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)[:, :, ::-1]

def detection(known_encoded, face_encode, known_names):
    result = face_recognition.compare_faces(known_encoded, face_encode)
    name = "Unknown"

    dif_vals = face_recognition.face_distance(known_encoded, face_encode)

    best_match_index = np.argmin(dif_vals)
    dif_val = dif_vals[best_match_index]

    if result[best_match_index] and dif_val < 0.7:
        name = known_names[best_match_index]
    
    print(f"Name      : {name}")
    print(f"Confidence: {1 - dif_val}")
    return name

def features(frame):
    face_locations = face_recognition.face_locations(frame)
    face_encodings = face_recognition.face_encodings(frame, face_locations, 0)
    return face_locations, face_encodings

def proccess_data(known_encoded, known_names, frame):
    small_frame = setter(frame)
    face_locations, face_encodings = features(small_frame)

    names = []
    for face_encode in face_encodings:
        name = detection(known_encoded, face_encode, known_names)
        names.append(name)
    return names

def average_pixel_color(frame):
    return np.average(frame)

def remove_dupe(head):
    return list(set(head))

def write(all_names, img):
    r = open("attendance.txt", "r+")
    
    lines = r.readlines()
    already_in = []

    for line in lines:
        if not line.startswith("\n#"):
            already_in.append(line.strip().split(":")[0])
            continue
        break

    for name in all_names:
        if already_in.count(name) <= 0:
            current_time = str(time.ctime())
            r.write(f"{name}:{current_time}\n")
            already_in.append(name)
            already_in = remove_dupe(already_in)
            cv2.imwrite(f"snapshots/{name}:{current_time}.jpg", img)
            print(f"Recorded {name} at {current_time}")

def avg_names(all_names, scan_time=5):
    everyname = [val for sublist in all_names for val in sublist]
    main_names = []

    for name in set(everyname):
        if everyname.count(name) > int(scan_time / 2):
            main_names.append(name)    
    return main_names

def write_not_here(known_names):
    r = open("attendance.txt", "r+")
    lines = r.readlines()
    already_in = []
    for line in lines:
        if not line.startswith("\n#"):
            already_in.append(line.strip().split(":")[0])
            continue
        break

    set_known_names = set(known_names)
    r.write("\n##########\nNot here\n")

    for name in list(set_known_names.symmetric_difference(already_in)):
        r.write(name + "\n")

def start(cap, file_no, delay):
    print(f"Starting for Period {file_no}")

    os.chdir(f"../periods/period{file_no}")
    cleanup()
    print("Cleanup finished")

    known_encoded, known_names = load_encodings()
    print("Encodings loaded")
    
    if len(known_names) == 0:
        print("Skipping period as no photos are in file")
        cap.release()
        return

    rigidness_motion = 3.2
    scan_time = 20
    start = time.time()

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
            
            for i in range(scan_time):
                ret, frame = cap.read()
                all_names.append(proccess_data(known_encoded, known_names, frame))

            names = avg_names(all_names, scan_time)
            write(names, frame)
            frame_gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

        last_frame_gray = frame_gray
        
        if time.time() - start > delay:
            write_not_here(known_names=known_names)
            break

    print(os.getcwd())
    os.chdir("../../eye")
    print(os.getcwd())
    print(f"Done with Period {file_no}")

def REPL():
    interperter = repl_sys.Reader(">> ")
    #TODO Deal with this

def main():
    s = sched.scheduler(time.time, time.sleep)
    #TODO Deal with this \/
    # Thread = threading.Thread(target=REPL, daemon=True)

    cap = cv2.VideoCapture(0)

    if int(time.localtime()[2]) % 2 == 1:
        s.enter(0, 1, start, argument=(cap, "1", 4920,))
        s.enter(4925, 1, start, argument=(cap, "2", 7975,))
        s.enter(7980, 1, start, argument=(cap, "3", 4495,))
        s.enter(4500, 1, start, argument=(cap, "4", 3600,))
    
    else:
        s.enter(0, 1, start, argument=(cap, "2", 4920,))
        s.enter(4925, 1, start, argument=(cap, "1", 7975,))
        s.enter(7980, 1, start, argument=(cap, "4", 4495,))
        s.enter(4500, 1, start, argument=(cap, "3", 3600,))
    
    s.run()

if __name__ == "__main__":
    s = sched.scheduler(time.time, time.sleep)
    cap = cv2.VideoCapture(0)

    if int(time.localtime()[2]) % 2 == 1:
        s.enter(0, 1, start, argument=(cap, "1", 5,))
        s.enter(10, 1, start, argument=(cap, "2", 7975,))
        s.enter(7980, 1, start, argument=(cap, "3", 4495,))
        s.enter(4500, 1, start, argument=(cap, "4", 3600,))
    
    else:
        s.enter(0, 1, start, argument=(cap, "2", 4920,))
        s.enter(4925, 1, start, argument=(cap, "1", 7975,))
        s.enter(7980, 1, start, argument=(cap, "4", 4495,))
        s.enter(4500, 1, start, argument=(cap, "3", 3600,))
    
    s.run()
