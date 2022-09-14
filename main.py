from PIL import Image, ImageDraw
from spotMath import intersection,inner_cars_intersection
import pixellib.instance
from os import listdir
import drawing
import db
from pixellib.instance import instance_segmentation
import os
from dotenv import load_dotenv


# ---------CONFIG--------------


load_dotenv("properties.env")
# Совпадение при котором считаем что это одна и та же машина
min_intersection = float(os.getenv("MIN_INTERSECTION"))
min_valid_intersection = float(os.getenv("MIN_VALID_INTERSECTION"))
MODEL_CONFIG_PATH = os.getenv("MODEL_CONFIG_PATH")
pixellib.instance.coco_config = pixellib.instance.configuration(BACKBONE=os.getenv("BACKBONE"),
                                                                NUM_CLASSES=int(os.getenv("NUM_CLASSES")),
                                                                class_names=[os.getenv("CLASS_NAMES")],
                                                                IMAGES_PER_GPU=int(os.getenv("IMAGES_PER_GPU")),
                                                                DETECTION_MIN_CONFIDENCE=float(os.getenv("DETECTION_MIN_CONFIDENCE")),
                                                                IMAGE_MAX_DIM=int(os.getenv("IMAGE_MAX_DIM")),
                                                                IMAGE_MIN_DIM=int(os.getenv("IMAGE_MIN_DIM")),
                                                                IMAGE_RESIZE_MODE=os.getenv("IMAGE_RESIZE_MODE"),
                                                                GPU_COUNT=int(os.getenv("GPU_COUNT")))
# -----------------------------


def draw_cars(cars):
    for car in cars:
        drawing.draw_car(car, image_draw, 'blue')


def create_spots(cars):
    for car in cars:
        db.create_parking(int(car[1]), int(car[0]), int(car[3]), int(car[2]))


def update_available_flag_and_trim_cars_and_draw_spots(spots, cars):
    for parking_spot in spots:
        is_available = True
        for car in cars:
            if intersection(parking_spot, car) >= min_valid_intersection:
                is_available = False
                cars.remove(car)
                break
        if is_available:
            db.set_available(parking_spot)
            drawing.draw_spot(parking_spot, image_draw, 'green')
        else:
            drawing.draw_spot(parking_spot, image_draw, 'red')


def update_verification_count_and_trim_cars(spots, cars):
    for parking_spot in spots:
        is_found = False
        for car in cars:
            if intersection(parking_spot, car) >= min_intersection:
                db.inc_verification_count(parking_spot)
                cars.remove(car)
                is_found = True
                break
        if not is_found:
            db.dec_verification_count(parking_spot)


def delete_car_duplicates(cars):
    # удаляем дубликаты, по типу как тут https://i.imgur.com/Ocm3tHm.jpg
    for car1 in cars:
        for car2 in cars:
            if car1[0] != car2[0] and car1[1] != car2[1] and car1[2] != car2[2] and car1[3] != car2[3]:
                if inner_cars_intersection(car1, car2) > min_intersection:
                    cars.remove(car2)


segment_image = instance_segmentation()
segment_image.load_model(MODEL_CONFIG_PATH)
target_classes = segment_image.select_target_classes(car=True, truck=True)

# путь к папке где лежат все картинки
images_directory = os.getenv("IMAGES_DIRECTORY")
# photos = ["1.jpg", "2.jpg","3.jpg","4.jpg","5.jpg","6.jpg","7.jpg","8.jpg","9.jpg","10.jpg"]
i = 1
while True:
    segmask, output = segment_image.segmentImage(images_directory + "Screenshot_"+str(i)+".png", segment_target_classes=target_classes,
                                                 show_bboxes=True, verbose=True,output_image_name="out/"+str(i)+".png")
    # segmask, output = segment_image.segmentImage(imagesDirectory + photo, segment_target_classes=target_classes)
    image = Image.open(images_directory + "Screenshot_"+str(i)+".png")
    image_draw = ImageDraw.Draw(image)
    cars_from_image = segmask['rois'].tolist()

    delete_car_duplicates(cars_from_image)

    draw_cars(cars_from_image)

    parking_spots = db.get_approved_spots()

    update_available_flag_and_trim_cars_and_draw_spots(parking_spots, cars_from_image)

    unverified_parking_spots = db.get_not_approved_spots()

    update_verification_count_and_trim_cars(unverified_parking_spots, cars_from_image)

    create_spots(cars_from_image)

    image.save("output/" + str(i)+".png")
    i = i + 1
