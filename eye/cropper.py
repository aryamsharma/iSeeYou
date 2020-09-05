import os

import face_recognition
from PIL import Image


def setter(name):
    while True:
        im = Image.open(name)
        try:
            img = face_recognition.load_image_file(name)
            loc = face_recognition.face_locations(
                img,
                number_of_times_to_upsample=0,
                model="hog")
            break
        except IndexError:
            # If no face is detected then the list will be empty
            im.rotate(90).save(name)

    # Why god why
    # TODO I stg if you dont get the file system working so theres no need to
    # do same calcs over and over
    # encoding = face_recognition.face_encodings(img, loc, 100)

    return getcropped(img, loc[0])


def getcropped(img, loc):
    top, right, bottom, left = loc
    cropped = img[top:bottom, left:right]
    return Image.fromarray(cropped)


def main(Class_no):
    image_path = "../to_crop"
    names = os.listdir(image_path)
    names = [name for name in names if name.lower().endswith((".jpg", ".png"))]
    os.chdir(image_path)

    for name in names:
        image = setter(name)

        os.chdir(f"../periods/period_{Class_no}")
        image.save(name.split(".")[0] + ".jpg")
        os.chdir("../../to_crop")
        os.remove(name)

    os.chdir("../eye")


if __name__ == "__main__":
    main(input("Which class are these students in?\n"))
