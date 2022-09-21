import shapely.geometry as sg

def cars_intersection(car1, car2):
    xmin = car1[1]
    xmax = car1[3]
    ymin = car1[0]
    ymax = car1[2]
    car1_box = sg.box(xmin, ymin, xmax, ymax)
    xmin = car2[1]
    ymin = car2[0]
    xmax = car2[3]
    ymax = car2[2]
    car2_box = sg.box(xmin, ymin, xmax, ymax)
    intr_box = car1_box.intersection(car2_box)
    intersection = max(intr_box.area/car1_box.area,intr_box.area/car2_box.area)
    if car1_box.area > car2_box.area:
        return intersection, car2
    else:
        return intersection, car1


def spot_intersection(spot1, spot2):
    xmin = spot1['x1']
    xmax = spot1['x2']
    ymin = spot1['y1']
    ymax = spot1['y2']
    spot1_box = sg.box(xmin, ymin, xmax, ymax)
    xmin = spot2['x1']
    ymin = spot2['y1']
    xmax = spot2['x2']
    ymax = spot2['y2']
    spot2_box = sg.box(xmin, ymin, xmax, ymax)
    intr_box = spot1_box.intersection(spot2_box)
    intersection = max(intr_box.area/spot1_box.area,intr_box.area/spot2_box.area)
    if spot1_box.area > spot2_box.area:
        return intersection, spot2
    else:
        return intersection, spot1

def intersection(spot, car):
    xmin = spot['x1']
    xmax = spot['x2']
    ymin = spot['y1']
    ymax = spot['y2']
    parking_spot = sg.box(xmin, ymin, xmax, ymax)
    xmin = car[1]
    ymin = car[0]
    xmax = car[3]
    ymax = car[2]
    car_spot = sg.box(xmin, ymin, xmax, ymax)
    intr = parking_spot.intersection(car_spot)
    return max(intr.area / parking_spot.area, intr.area / car_spot.area)