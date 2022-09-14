import shapely.geometry as sg

def inner_cars_intersection(car1, car2):
    xmin = car1[1]
    xmax = car1[3]
    ymin = car1[0]
    ymax = car1[2]
    car1_area = sg.box(xmin, ymin, xmax, ymax)
    xmin = car2[1]
    ymin = car2[0]
    xmax = car2[3]
    ymax = car2[2]
    car2_spot = sg.box(xmin, ymin, xmax, ymax)
    intr = car1_area.intersection(car2_spot)
    return max(intr.area / car1_area.area, intr.area / car2_spot.area)

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
    return intr.area / (parking_spot.area + car_spot.area - intr.area)