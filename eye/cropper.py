from PIL import Image
import face_recognition
import os


def setter(name):
    while True:
        im = Image.open(name)
        try:
            img = face_recognition.load_image_file(name)
            loc = face_recognition.face_locations(
                img,
                number_of_times_to_upsample=0,
                model="hog")[0]
            break
        except IndexError:
            # If no face is detected then the list will be empty
            im.rotate(90).save(name)
    return img, loc


def getcropped(img, loc):
    top, right, bottom, left = loc
    cropped = img[top:bottom, left:right]
    return Image.fromarray(cropped)


def main(Class_no):
    """
    Class_no is just asking what period number student is in,
    You may ignore it if there are no new extra students being added
    """
    image_path = "../to_crop"
    names = os.listdir(image_path)
    names = [name for name in names if name.lower().endswith((".jpg", ".png"))]
    os.chdir(image_path)

    for name in names:
        img, loc = setter(name)
        image = getcropped(img, loc)

        os.chdir(f"../periods/period_{Class_no}")
        image.save(name.split(".")[0] + ".jpg")
        os.chdir("../../to_crop")
        os.remove(name)

    os.chdir("../eye")


if __name__ == "__main__":
    main(input("Which class is this student in?\n"))
