from PIL import Image, ImageDraw
from spotMath import intersection,inner_cars_intersection
import pixellib.instance
from os import listdir
import drawing
import db
from pixellib.instance import instance_segmentation
import os
from dotenv import load_dotenv
import math


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


def log(ex):
    file_object = open('1.log', 'a')
    file_object.write(str(ex))
    file_object.close()


def draw_cars(cars):
    for car in cars:
        drawing.draw_car(car, image_draw, 'blue')


def create_spots(cars, parking_id):
    for car in cars:
        db.create_parking_spot(int(car[1]), int(car[0]), int(car[3]), int(car[2]), parking_id)


def update_available_flag_and_trim_cars_and_draw_spots(spots, cars):
    for parking_spot in spots:
        is_available = True
        for car in cars:
            if intersection(parking_spot, car) >= min_valid_intersection:
                is_available = False
                parking_spot['x1'] = car[1]
                parking_spot['y1'] = car[0]
                parking_spot['x2'] = car[3]
                parking_spot['y2'] = car[2]
                cars.remove(car)
                break
        if is_available:
            db.set_available_and_update_position(parking_spot)
            drawing.draw_spot(parking_spot, image_draw, 'red')
        else:
            db.set_not_available_and_update_position(parking_spot)
            # drawing.draw_spot(parking_spot, image_draw, 'red')


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

i = 1
while True:
    try:
        parking_queue_items = db.get_parking_image_queue()
        for parking_queue_item in parking_queue_items:
            image = Image.open(parking_queue_item["fullPath"])

            image_draw = ImageDraw.Draw(image)

            segmask, output = segment_image.segmentImage(parking_queue_item["fullPath"], segment_target_classes=target_classes,
                                                         show_bboxes=True, verbose=True, output_image_name="out/" + parking_queue_item["fullPath"])
            # segmask, output = segment_image.segmentImage(imagesDirectory + photo, segment_target_classes=target_classes)
            cars_from_image = segmask['rois'].tolist()

            delete_car_duplicates(cars_from_image)

            # draw_cars(cars_from_image)

            approved_parking_spots = db.get_approved_spots(parking_queue_item["parkingId"])

            update_available_flag_and_trim_cars_and_draw_spots(approved_parking_spots, cars_from_image)

            not_approved_parking_spots = db.get_not_approved_spots(parking_queue_item["parkingId"])

            update_verification_count_and_trim_cars(not_approved_parking_spots, cars_from_image)

            create_spots(cars_from_image, parking_queue_item["parkingId"])

            x, y = image.size
            x2, y2 = math.floor(x/2), math.floor(y/2)
            image = image.resize((x2, y2), Image.ANTIALIAS)

            image.save("output/" + os.path.basename(parking_queue_item["fullPath"]),optimize=True, quality=95)

            db.remove_from_image_queue(parking_queue_item)

            db.save_image(os.path.abspath("output/" + os.path.basename(parking_queue_item["fullPath"])), parking_queue_item["parkingId"])
    except Exception as ex:
        log(ex)
