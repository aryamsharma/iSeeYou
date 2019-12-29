import cv2
import face_recognition
import os
import numpy as np
import time
import sched

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
    small = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)[:, :, ::-1]
    return small

def detection(known_encoded, face_encode, known_names):
    result = face_recognition.compare_faces(known_encoded, face_encode)
    name = "Unknown"

    dif_vals = face_recognition.face_distance(known_encoded, face_encode)
    best_match_index = np.argmin(dif_vals)

    if result[best_match_index]:
        name = known_names[best_match_index]
    return name

def features(frame):
    face_locations = face_recognition.face_locations(frame)
    face_encodings = face_recognition.face_encodings(frame, face_locations, 0)
    return face_locations, face_encodings

def render(frame, name, top, right, bottom, left):
    cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
    cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 255, 0), -1)
    cv2.putText(frame, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 1.0, (0, 0, 0), 1)

def proccess_data(known_encoded, known_names, frame):
    small_frame = setter(frame)
    face_locations, face_encodings = features(small_frame)

    names = []
    for face_encode in face_encodings:
        name = detection(known_encoded, face_encode, known_names)
        names.append(name)
    return names

def average_pixel_color(frame):
    avg_color_row = np.average(frame)
    return np.average(avg_color_row)

def remove_dupe(head):
    return list(set(head))

def write(all_names=[], known_names=None, to_input="H", img=None):
    """
    def end_write_to_file(known_names=None):
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
    """

    r = open("attendance.txt", "r+")
    
    if to_input.upper() == "H":
        lines = r.readlines()
        already_in = []

        for line in lines:
            if not line.startswith("\n#"):
                already_in.append(line.strip().split(":")[0])
                continue
            break

        for name in all_names:
            if already_in.count(name) <= 0:
                r.write(f"{name}:{time.ctime()}\n")
                already_in.append(name)
                already_in = remove_dupe(already_in)
                cv2.imwrite(f"../../snapshots/{name}:{str(time.ctime())}.jpg", img)
    
    elif to_input.upper() == "N":
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

def avg_names(all_names, scan_time=5):
    everyname = []
    main_names = []

    for names in all_names:
        for name in names:
            everyname.append(name)

    for name in set(everyname):
        if everyname.count(name) > int(scan_time / 2):
            main_names.append(name)    
    return main_names

def start(cap, file_no, delay):
    os.chdir(f"data/ready/period{file_no}")
    known_encoded, known_names = load_encodings()
    rigidness_motion = 4
    scan_time = 20
    start = time.time()

    ret, last_frame = cap.read()
    last_frame_gray = cv2.cvtColor(last_frame, cv2.COLOR_RGB2GRAY)
    
    print("Ready")
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
            write(names, img=frame, to_input="H")
            frame_gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        last_frame_gray = frame_gray
        
        if time.time() - start > delay:
            write(known_names=known_names, to_input="n")
            break

if __name__ == "__main__":
    s = sched.scheduler(time.time, time.sleep)
    cap = cv2.VideoCapture(0)


    s.enter(0, 1, start, argument=(cap, "1", 4920,))
    s.enter(4925, 1, start, argument=(cap, "2", 7975,))
    s.enter(7980, 1, start, argument=(cap, "3", 4495,))
    s.enter(4500, 1, start, argument=(cap, "4", 3600,))

    s.run()