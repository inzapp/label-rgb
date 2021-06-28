import os
import sys
from glob import glob

import cv2
import numpy as np

win_size = (768, 768)
win_name = 'Label RGB v1.0 by Inzapp'


def mouse_callback(event, cur_x, cur_y, flag, _):
    global raw

    # no click mouse moving
    if event == 0 and flag == 0:
        radius = 100
        raw_height, raw_width = raw.shape[0], raw.shape[1]
        bgr = raw[cur_y][cur_x]
        x = cur_x + radius
        y = cur_y - radius
        if cur_x > raw_width - radius:
            x = cur_x - radius
        if cur_y < radius:
            y = cur_y + radius
        raw_copy = raw.copy()
        raw_copy = cv2.circle(raw_copy, (x, y), radius, (int(bgr[0]), int(bgr[1]), int(bgr[2])), thickness=-1)
        cv2.imshow(win_name, raw_copy)

    # end click
    elif event == 4 and flag == 0:
        bgr = raw[cur_y][cur_x] / 255.0
        with open(label_path, 'wt') as label_file:
            label_file.writelines(f'{bgr[2]:6f} {bgr[1]:6f} {bgr[0]:6f}\n')
        raw = set_circle_to_side_pan(raw, [bgr[2], bgr[1], bgr[0]])
        cv2.imshow(win_name, raw)


def side_pan():
    pan = [[84, 168],
            [168, 84]]

    pan = np.concatenate((pan, pan), axis=1)
    pan = np.concatenate((pan, pan), axis=1)

    pan = np.concatenate((pan, pan), axis=0)
    pan = np.concatenate((pan, pan), axis=0)
    pan = np.concatenate((pan, pan), axis=0)
    pan = np.concatenate((pan, pan), axis=0)

    pan = np.asarray(pan).astype('uint8')
    pan = cv2.resize(pan, (int(win_size[0] / 5), win_size[1]), interpolation=cv2.INTER_NEAREST)
    pan = cv2.cvtColor(pan, cv2.COLOR_GRAY2BGR)
    return pan


def load_saved_rbg(label_path):
    if os.path.exists(label_path) and os.path.isfile(label_path):
        with open(label_path, 'rt') as f:
            line = f.readline()
        return list(map(float, line.split(' ')))
    else:
        return None


def set_circle_to_side_pan(img, rgb):
    r, g, b = rgb
    r = int(r * 255)
    g = int(g * 255)
    b = int(b * 255)
    radius = int(side_pan_width / 2)
    pan_x = win_size[0] + int((win_size[0] / 5) / 2)

    pan_y = int(win_size[1] * 0.2)
    img = cv2.circle(img, (pan_x, pan_y), radius, (b, g, r), thickness=-1)

    pan_y = int(win_size[1] * 0.5)
    img = cv2.circle(img, (pan_x, pan_y), radius, (b, g, r), thickness=-1)

    pan_y = int(win_size[1] * 0.8)
    img = cv2.circle(img, (pan_x, pan_y), radius, (b, g, r), thickness=-1)
    return img


path = ''
if len(sys.argv) > 1:
    path = sys.argv[1].replace('\\', '/') + '/'

jpg_file_paths = glob(f'{path}*.jpg')
png_file_paths = glob(f'{path}*.png')
img_paths = jpg_file_paths + png_file_paths
if len(img_paths) == 0:
    print('No image files in path. run label.py with path argument')
    sys.exit(0)

side_pan = side_pan()
side_pan_height = side_pan.shape[0]
side_pan_width = side_pan.shape[1]

index = 0
while True:
    file_path = img_paths[index]
    label_path = f'{file_path[:-4]}.txt'
    raw = cv2.imread(file_path, cv2.IMREAD_COLOR)
    raw = cv2.resize(raw, win_size)
    raw = np.concatenate((raw, side_pan), axis=1)
    rgb = load_saved_rbg(label_path)
    if rgb is not None:
        raw = set_circle_to_side_pan(raw, rgb)
    cv2.namedWindow(win_name)
    cv2.imshow(win_name, raw)
    cv2.setMouseCallback(win_name, mouse_callback)
    res = cv2.waitKey(0)

    # go to next if input key was 'd'
    if res == ord('d'):
        if index == len(img_paths) - 1:
            print('Current image is last image')
        else:
            index += 1

    # go to previous image if input key was 'a'
    elif res == ord('a'):
        if index == 0:
            print('Current image is first image')
        else:
            index -= 1

    # exit if input key was ESC
    elif res == 27:
        sys.exit()
