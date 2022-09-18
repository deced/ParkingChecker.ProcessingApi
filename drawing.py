from PIL import Image, ImageDraw, ImageFont


def draw_car(car, idraw, color):
    list = (car[1], car[0], car[3], car[2])
    idraw.rectangle(list, outline=color, width=5)


def draw_spot(spot, idraw, color):
    list = (spot['x1'], spot['y1'], spot['x2'], spot['y2'])
    idraw.rectangle(list, outline=color, width=3)
    # font = ImageFont.truetype("arial.ttf", 25)
    # idraw.text((spot['x1'], spot['y1'] - 75), "vc: " + str(spot['verificationCount']), (255, 0, 0), font=font)
    # idraw.text((spot['x1'], spot['y1'] - 50), "av: " + str(spot['available']), (255, 0, 0), font=font)
    # idraw.text((spot['x1'], spot['y1'] - 25), "ap: " + str(spot['approved']), (255, 0, 0), font=font)
