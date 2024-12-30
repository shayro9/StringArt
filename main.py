import PIL.Image as Image
import PIL.ImageDraw as ImageDraw
import PIL.ImageChops as ImageChops
import PIL.ImageFilter as ImageFilter
import PIL.ImageMath as ImageMath
import math
import json

CANVAS_SIZE = (390, 390)
NAILS = 222
FACTOR = 0.2


def draw_circle(radius, nails, image):
    c_draw = ImageDraw.Draw(image)
    pnt_list = []
    c_draw.ellipse((0, 0, CANVAS_SIZE[0], CANVAS_SIZE[1]), 'white')
    for i in range(0, nails):
        x = CANVAS_SIZE[0] / 2 + radius * math.cos((2 * math.pi * i) / nails)
        y = CANVAS_SIZE[1] / 2 + radius * math.sin((2 * math.pi * i) / nails)
        pnt_list.append((x, y))
    return pnt_list


def conv_bw(image):
    bw_img = image.convert('L')
    bw_img.save('test.jpg')
    return bw_img


def ipart(x):
    return math.floor(x)


def fpart(x):
    return x - ipart(x)


def rfpart(x):
    return 1 - fpart(x)


def write_point(x, y, b, flag, file):
    if not flag:
        file.write('"' + f"{x},{y}" + '"' + " : " + str(b))
    else:
        file.write(", " + '"' + f"{x},{y}" + '"' + " : " + str(b))


def drawLine(x0, y0, x1, y1, file):
    flag = 0
    steep = abs(y1 - y0) > abs(x1 - x0)

    if steep:
        x0, y0 = y0, x0
        x1, y1 = y1, x1

    if x0 > x1:
        x0, x1 = x1, x0
        y0, y1 = y1, y0

    dx = x1 - x0
    dy = y1 - y0

    if dx == 0.0:
        gradient = 1.0
    else:
        gradient = dy / dx

    # handle first endpoint
    xend = ipart(x0 + 0.5)
    yend = y0 + gradient * (xend - x0)
    xgap = rfpart(x0 + 0.5)
    xpxl1 = xend
    ypxl1 = ipart(yend)

    if steep:
        write_point(ypxl1, xpxl1, rfpart(yend) * xgap * FACTOR, flag, file)
        flag = 1
        if ypxl1 + 1 < CANVAS_SIZE[0]:
            write_point(ypxl1 + 1, xpxl1, fpart(yend) * xgap * FACTOR, flag, file)
    else:
        write_point(xpxl1, ypxl1, rfpart(yend) * xgap * FACTOR, flag, file)
        flag = 1
        if ypxl1 + 1 < CANVAS_SIZE[1]:
            write_point(xpxl1, ypxl1 + 1, fpart(yend) * xgap * FACTOR, flag, file)

    intery = yend + gradient

    # handle second endpoint
    xend = ipart(x1 + 0.5)
    yend = y1 + gradient * (xend - x1)
    xgap = fpart(x1 + 0.5)
    xpxl2 = xend
    ypxl2 = ipart(yend)
    if steep:
        write_point(ypxl2, xpxl2, rfpart(yend) * xgap * FACTOR, flag, file)
        if ypxl2 + 1 < CANVAS_SIZE[0]:
            write_point(ypxl2 + 1, xpxl2, fpart(yend) * xgap * FACTOR, flag, file)
    else:
        write_point(xpxl2, ypxl2, rfpart(yend) * xgap * FACTOR, flag, file)
        if ypxl2 + 1 < CANVAS_SIZE[1]:
            write_point(xpxl2, ypxl2 + 1, fpart(yend) * xgap * FACTOR, flag, file)

    if steep:
        for x in range(xpxl1 + 1, xpxl2):
            write_point(ipart(intery), x, rfpart(intery) * FACTOR, flag, file)
            write_point(ipart(intery) + 1, x, fpart(intery) * FACTOR, flag, file)
            intery = intery + gradient
    else:
        for x in range(xpxl1 + 1, xpxl2):
            write_point(x, ipart(intery), rfpart(intery) * FACTOR, flag, file)
            write_point(x, ipart(intery) + 1, fpart(intery) * FACTOR, flag, file)
            intery = intery + gradient


def drawLine2(x0, y0, x1, y1, draw1):
    steep = abs(y1 - y0) > abs(x1 - x0)

    if steep:
        x0, y0 = y0, x0
        x1, y1 = y1, x1

    if x0 > x1:
        x0, x1 = x1, x0
        y0, y1 = y1, y0

    dx = x1 - x0
    dy = y1 - y0

    if dx == 0.0:
        gradient = 1.0
    else:
        gradient = dy / dx

    # handle first endpoint
    xend = ipart(x0 + 0.5)
    yend = y0 + gradient * (xend - x0)
    xgap = rfpart(x0 + 0.5)
    xpxl1 = xend
    ypxl1 = ipart(yend)

    if steep:
        draw1.point((ypxl1, xpxl1), ipart(unnormalize(rfpart(yend) * xgap * FACTOR)))
        if ypxl1 + 1 < CANVAS_SIZE[0]:
            draw1.point((ypxl1 + 1, xpxl1), ipart(unnormalize(fpart(yend) * xgap * FACTOR)))
    else:
        draw1.point((xpxl1, ypxl1), ipart(unnormalize(rfpart(yend) * xgap * FACTOR)))
        if ypxl1 + 1 < CANVAS_SIZE[1]:
            draw1.point((xpxl1, ypxl1 + 1), ipart(unnormalize(fpart(yend) * xgap * FACTOR)))

    intery = yend + gradient

    # handle second endpoint
    xend = ipart(x1 + 0.5)
    yend = y1 + gradient * (xend - x1)
    xgap = fpart(x1 + 0.5)
    xpxl2 = xend
    ypxl2 = ipart(yend)
    if steep:
        draw1.point((ypxl2, xpxl2), ipart(unnormalize(rfpart(yend) * xgap * FACTOR)))
        if ypxl2 + 1 < CANVAS_SIZE[0]:
            draw1.point((ypxl2 + 1, xpxl2), ipart(unnormalize(fpart(yend) * xgap * FACTOR)))
    else:
        draw1.point((xpxl2, ypxl2), ipart(unnormalize(rfpart(yend) * xgap * FACTOR)))
        if ypxl2 + 1 < CANVAS_SIZE[1]:
            draw1.point((xpxl2, ypxl2), ipart(unnormalize(fpart(yend) * xgap * FACTOR)))

    if steep:
        for x in range(xpxl1 + 1, xpxl2):
            draw1.point((ipart(intery), x), ipart(unnormalize(rfpart(intery))) * FACTOR)
            draw1.point((ipart(intery) + 1, x), ipart(unnormalize(fpart(intery))) * FACTOR)
            intery = intery + gradient
    else:
        for x in range(xpxl1 + 1, xpxl2):
            draw1.point((x, ipart(intery)), ipart(unnormalize(rfpart(intery))) * FACTOR)
            draw1.point((x, ipart(intery) + 1), ipart(unnormalize(fpart(intery))) * FACTOR)
            intery = intery + gradient


def create_strings_file(curr_nail):
    strings_file = open(f"Strings/strings{curr_nail}.txt", "w")
    canvas = Image.new('L', CANVAS_SIZE)
    nails = draw_circle(min(CANVAS_SIZE) / 2 - 1, NAILS, canvas)
    for n in range(0, NAILS):
        if curr_nail != n:
            strings_file.write(f"{curr_nail} : {n} - \n{{")
            x1, y1 = nails[curr_nail][0], nails[curr_nail][1]
            x2, y2 = nails[n][0], nails[n][1]
            drawLine(x1, y1, x2, y2, strings_file)
            strings_file.write("}\n")


def normalize_data(data):
    idx = 0
    for pixel in data:
        data[idx] = normalize(pixel)
        idx += 1


def normalize(x):
    return 1 - x / 255


def unnormalize_data(data):
    idx = 0
    for pixel in data:
        data[idx] = unnormalize(pixel)
        idx += 1


def unnormalize(x):
    return 255 - x * 255


def euclidean_distance(img1, img2):
    i = 0
    sum_p = 0
    for pix in img1:
        x = float(pix)
        y = float(img2[i])
        if x != y:
            sum_p += x - y
        i += 1
    return sum_p


if __name__ == '__main__':

    for i in range(0, NAILS):
        create_strings_file(i)
        print(i)

    result = Image.new('L', CANVAS_SIZE)

    input_img = Image.open('Inbar.png')
    input_img = input_img.resize(CANVAS_SIZE)
    bw_input = conv_bw(input_img)
    input_img.close()

    points = draw_circle(min(CANVAS_SIZE) / 2 - 1, NAILS, result)
    draw = ImageDraw.Draw(result)

    curr_nail = 0
    next_nail = 0
    chosen_line = None
    connections = []
    file = open("result.txt", "w")
    for m in range(0, 1500):
        file.write(f"{curr_nail}, ")
        if m % 250 == 0:
            result.save(f"inbar-{m}.jpg")
        print(m)
        most_black = -math.inf
        # min_dist = math.inf
        s_file = open(f"Strings/strings{curr_nail}.txt")
        lines = list(s_file)
        for n in range(0, NAILS):
            if abs(n-curr_nail) <= NAILS/8 or abs((NAILS - n)-curr_nail) <= NAILS/8 or {curr_nail, n} in connections:
                continue
            curr_line = json.loads(lines[n * 2 + 1 if n < curr_nail else n * 2 - 1])

            blackness = 0
            for pixl in curr_line.keys():
                p = pixl.split(",")
                blackness = blackness + normalize(bw_input.getpixel((int(p[0]), int(p[1]))))

            avg_black = blackness / len(curr_line.keys())
            if most_black < avg_black:
                most_black = avg_black
                next_nail = n
                chosen_line = curr_line

        for pxl in chosen_line.keys():
            p = pxl.split(",")
            curr_pxl = normalize(result.getpixel((int(p[0]), int(p[1]))))
            added_pxl = chosen_line[pxl]
            new_pxl = min(curr_pxl + added_pxl, 1)
            t1 = ipart(unnormalize(new_pxl))

            result.putpixel((int(p[0]), int(p[1])), t1)

            curr_bw_pxl = normalize(bw_input.getpixel((int(p[0]), int(p[1]))))
            r_new_pxl = max(curr_bw_pxl - added_pxl, 0)
            t2 = ipart(unnormalize(r_new_pxl))

            bw_input.putpixel((int(p[0]), int(p[1])), t2)
        connections.append({curr_nail, next_nail})
        curr_nail = next_nail
        s_file.close()
    result.save('result.jpg')
    bw_input.save('diff.jpg')
    file.close()
