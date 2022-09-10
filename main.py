import numpy
import numpy as np
import math
import db
import shapely.geometry as sg
from pixellib.instance import instance_segmentation
from pixellib.instance.mask_rcnn import MaskRCNN

def intersection(spot, car):
    xmin = spot['x1']
    xmax = spot['x2']
    ymin = spot['y1']
    ymax = spot['y2']
    parking_spot = sg.box(xmin, ymin, xmax, ymax)
    xmin = car[0]
    xmax = car[2]
    ymin = car[1]
    ymax = car[3]
    car_spot = sg.box(xmin, ymin, xmax, ymax)
    intr = parking_spot.intersection(car_spot)
    return max(intr.area / parking_spot.area, intr.area / car_spot.area)


segment_image = instance_segmentation()
segment_image.load_model("mask_rcnn_coco.h5")
target_classes = segment_image.select_target_classes(car=True, truck=True)
segmask, output = segment_image.segmentImage("17.jpg", segment_target_classes=target_classes, show_bboxes=True, output_image_name = "output.jpg")
car_coords = segmask['rois']
cars = list(car_coords)
parking_spots = db.getSpots()
max_intersec = 0.99
isFound = False;
for parking_spot in parking_spots:
    for car in cars:
        if (intersection(parking_spot, car) >= max_intersec) :
            db.incVerificationCount(parking_spot)
            cars.remove(car)
            isFound = True
            break
    # if (isFound == False) :
    #     db.CreateParking(parking_spot['x1'], parking_spot['y1'], parking_spot['x2'], parking_spot['y2'])

for car in cars :
    db.createParking(int(car[0]), int(car[1]), int(car[2]), int(car[3]))
