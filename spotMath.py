import shapely.geometry as sg

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