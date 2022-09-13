from PIL import Image, ImageDraw
from spotMath import intersection
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

segment_image = instance_segmentation()
segment_image.load_model(MODEL_CONFIG_PATH)
target_classes = segment_image.select_target_classes(car=True, truck=True)

# путь к папке где лежат все картинки
images_directory = os.getenv("IMAGES_DIRECTORY")
# photos = ["1.jpg", "2.jpg","3.jpg","4.jpg","5.jpg","6.jpg","7.jpg","8.jpg","9.jpg","10.jpg"]
i = 1
while True:
    segmask, output = segment_image.segmentImage(images_directory + "Screenshot_"+str(i)+".png", segment_target_classes=target_classes,
                                                 show_bboxes=True, verbose=True)
    # segmask, output = segment_image.segmentImage(imagesDirectory + photo, segment_target_classes=target_classes)
    image = Image.open(images_directory + "Screenshot_"+str(i)+".png")
    image_draw = ImageDraw.Draw(image)
    cars = segmask['rois'].tolist()

    for car in cars:
        drawing.draw_car(car, image_draw, 'blue')

    parking_spots = db.get_approved_spots()
    for parking_spot in parking_spots:
        isAvailable = True
        for car in cars:
            if intersection(parking_spot, car) >= min_valid_intersection:
                isAvailable = False
                cars.remove(car)
                break
        if isAvailable:
            db.set_available(parking_spot)
            drawing.draw_spot(parking_spot, image_draw, 'green')
        else:
            drawing.draw_spot(parking_spot, image_draw, 'red')

    parking_spots = db.get_not_approved_spots()

    # for car in cars:
    #     drawCar(car, idraw)
    #
    # for spot in parking_spots:
    #     drawSpot(spot, idraw, 'red')

    for parking_spot in parking_spots:
        isFound = False
        for car in cars:
            intr = intersection(parking_spot, car)
            # if intr != 0:
            #     print(intr)
            if intr >= min_intersection:
                db.inc_verification_count(parking_spot)
                cars.remove(car)
                isFound = True
                break

        if not isFound:
            db.dec_verification_count(parking_spot)

    for car in cars:
        db.create_parking(int(car[1]), int(car[0]), int(car[3]), int(car[2]))

    image.save("output\\" + str(i)+".png")
    i = i + 1
