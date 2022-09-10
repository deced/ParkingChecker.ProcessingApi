import numpy
import numpy as np
import math
from spotMath import intersection
import pixellib.instance
from os import listdir

import db
from pixellib.instance import instance_segmentation
from pixellib.instance.mask_rcnn import MaskRCNN

#---------CONFIG--------------

# Совпадение при котором считаем что это одна и та же машина
min_intersection = 0.99
MODEL_CONFIG_PATH = "mask_rcnn_coco.h5"
pixellib.instance.coco_config = pixellib.instance.configuration(BACKBONE = "resnet101",  NUM_CLASSES =  81,  class_names = ["BG"], IMAGES_PER_GPU = 1,
DETECTION_MIN_CONFIDENCE = 0.5,IMAGE_MAX_DIM = 1024, IMAGE_MIN_DIM = 800,IMAGE_RESIZE_MODE ="square",  GPU_COUNT = 1)
#-----------------------------



segment_image = instance_segmentation()
segment_image.load_model(MODEL_CONFIG_PATH)
target_classes = segment_image.select_target_classes(car=True, truck=True)

#путь к папке где лежат все картинк
imagesDirectory = "/home/deced/Desktop/parking/"
photos = listdir(imagesDirectory)
counter = 0
for photo in photos:
    counter += 1
    print(counter)
    segmask, output = segment_image.segmentImage(imagesDirectory + photo, segment_target_classes=target_classes, show_bboxes=True, output_image_name = "output-"+photo)
    cars = segmask['rois'].tolist()
    parking_spots = db.getSpots()
    isFound = False
    for parking_spot in parking_spots:
        for car in cars:
            if intersection(parking_spot, car) >= min_intersection:
                db.incVerificationCount(parking_spot)
                cars.remove(car)
                isFound = True
                break

        if isFound == False:
             db.decVerificationCount(parking_spot)

    for car in cars:
        db.createParking(int(car[0]), int(car[1]), int(car[2]), int(car[3]))
