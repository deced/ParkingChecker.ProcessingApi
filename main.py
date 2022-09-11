from PIL import Image, ImageDraw, ImageFont
from spotMath import intersection
import pixellib.instance
from os import listdir

import db
from pixellib.instance import instance_segmentation
from pixellib.instance.mask_rcnn import MaskRCNN


def drawCar(car,idraw):
    list = (car[1], car[0], car[3], car[2])
    idraw.rectangle(list, outline='blue', width=5)

def drawSpot(spot,idraw):
    list = (spot['x1'], spot['y1'], spot['x2'], spot['y2'])
    idraw.rectangle(list, outline='red', width=3)
    font = ImageFont.truetype("arial.ttf", 25)
    idraw.text((spot['x1'],spot['y1']- 75), "vc: "+str(spot['verificationCount']), (255, 0, 0), font=font)
    idraw.text((spot['x1'], spot['y1'] - 50), "av: " + str(spot['available']), (255, 0, 0), font=font)
    idraw.text((spot['x1'], spot['y1'] - 25), "ap: " + str(spot['approved']), (255, 0, 0), font=font)

#---------CONFIG--------------

# Совпадение при котором считаем что это одна и та же машина
min_intersection = 0.9
min_valid_intersection = 0.4
MODEL_CONFIG_PATH = "mask_rcnn_coco.h5"
pixellib.instance.coco_config = pixellib.instance.configuration(BACKBONE = "resnet101",  NUM_CLASSES =  81,  class_names = ["BG"], IMAGES_PER_GPU = 1,
DETECTION_MIN_CONFIDENCE = 0.5,IMAGE_MAX_DIM = 1024, IMAGE_MIN_DIM = 800,IMAGE_RESIZE_MODE ="square",  GPU_COUNT = 1)
#-----------------------------

segment_image = instance_segmentation()
segment_image.load_model(MODEL_CONFIG_PATH)
target_classes = segment_image.select_target_classes(car=True, truck=True)

#путь к папке где лежат все картинк
imagesDirectory = "ph/"
# photos = listdir(imagesDirectory)
photos = ["1.jpg", "2.jpg","3.jpg","4.jpg","5.jpg","6.jpg","7.jpg","8.jpg","9.jpg","10.jpg"]
for photo in photos:
    print(photo)
    segmask, output = segment_image.segmentImage(imagesDirectory + photo, segment_target_classes=target_classes, show_bboxes=True, output_image_name = "test-" + photo + ".jpg")
    # segmask, output = segment_image.segmentImage(imagesDirectory + photo, segment_target_classes=target_classes)
    image = Image.open(imagesDirectory + photo)
    idraw = ImageDraw.Draw(image)
    cars = segmask['rois'].tolist()
    parking_spots = db.getSpots()
    for car in cars:
        drawCar(car, idraw)

    for spot in parking_spots:
        drawSpot(spot, idraw)

    for parking_spot in parking_spots:
        isFound = False
        for car in cars:
            intr = intersection(parking_spot, car)
            if intr != 0:
                print(intr)
            if intr >= min_intersection:
                db.incVerificationCount(parking_spot)
                cars.remove(car)
                isFound = True
                break

        if not isFound:
             db.decVerificationCount(parking_spot)

    for car in cars:
        db.createParking(int(car[1]), int(car[0]), int(car[3]), int(car[2]))

    parking_spots = db.getApprovedSpots()
    # for parking_spot in parking_spots:
    #     notFree = False
    #     for car in cars:
    #         if intersection(parking_spot, car) >= min_valid_intersection:
    #             notFree = True
    #             break
    #     if notFree == False:
    #         list = (parking_spot['x1'], parking_spot['y1'], parking_spot['x2'], parking_spot['y2'])
    #         idraw.rectangle(list, outline='red', width=5)

    image.save("output-"+photo)


