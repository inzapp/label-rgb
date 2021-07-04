import os
import sys
from glob import glob

import cv2
import numpy as np

g_max_num_circles = 2
g_win_size = (768, 768)
g_win_name = 'Label RGB v1.0 by Inzapp'


def get_next_circle_index():
    global g_max_num_circles, g_circle_index
    g_circle_index += 1
    if g_circle_index == g_max_num_circles:
        g_circle_index = 0
    return g_circle_index


def mouse_callback(event, cur_x, cur_y, flag, _):
    global g_raw

    # no click mouse moving
    if event == 0 and flag == 0:
        radius = 100
        raw_height, raw_width = g_raw.shape[0], g_raw.shape[1]
        bgr = g_raw[cur_y][cur_x]
        x = cur_x + radius
        y = cur_y - radius
        if cur_x > raw_width - radius:
            x = cur_x - radius
        if cur_y < radius:
            y = cur_y + radius
        raw_copy = g_raw.copy()
        raw_copy = cv2.circle(raw_copy, (x, y), radius, (int(bgr[0]), int(bgr[1]), int(bgr[2])), thickness=-1)
        cv2.imshow(g_win_name, raw_copy)

    # end click
    elif event == 4 and flag == 0:
        bgr = g_raw[cur_y][cur_x] / 255.0
        rgb = [bgr[2], bgr[1], bgr[0]]
        g_raw = set_circle_to_side_pan(g_raw, rgb, get_next_circle_index())
        cv2.imshow(g_win_name, g_raw)


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
    pan = cv2.resize(pan, (int(g_win_size[0] / 5), g_win_size[1]), interpolation=cv2.INTER_NEAREST)
    pan = cv2.cvtColor(pan, cv2.COLOR_GRAY2BGR)
    return pan


def load_saved_rgbs_if_exist(label_path):
    rgbs = list()
    if os.path.exists(label_path) and os.path.isfile(label_path):
        with open(label_path, 'rt') as f:
            lines = f.readlines()
        for line in lines:
            r, g, b = list(map(float, line.replace('\n', '').split()))
            rgbs.append([r, g, b])
        return rgbs
    else:
        return None


def save_label(label_path, rgb, circle_index):
    rgb_str = f'{rgb[0]:.6f} {rgb[1]:.6f} {rgb[2]:.6f}\n'
    if not (os.path.exists(label_path) and os.path.isfile(label_path)):
        with open(label_path, 'wt') as f:
            f.writelines(rgb_str)
        return

    with open(label_path, 'rt') as f:
        lines = f.readlines()

    if circle_index < len(lines):
        lines[circle_index] = rgb_str
    else:
        lines.append(rgb_str)

    with open(label_path, 'wt') as f:
        f.writelines(lines)


def set_circle_to_side_pan(img, rgb, circle_index):
    global g_label_path
    r, g, b = rgb
    r = int(r * 255)
    g = int(g * 255)
    b = int(b * 255)
    radius = int(side_pan_width / 2)
    pan_x = g_win_size[0] + int((g_win_size[0] / 5) / 2)

    if circle_index == 0:
        pan_y = int(g_win_size[1] * 0.2)
        img = cv2.circle(img, (pan_x, pan_y), radius, (b, g, r), thickness=-1)
        save_label(g_label_path, rgb, circle_index)

    if circle_index == 1:
        pan_y = int(g_win_size[1] * 0.8)
        img = cv2.circle(img, (pan_x, pan_y), radius, (b, g, r), thickness=-1)
        save_label(g_label_path, rgb, circle_index)
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
    g_circle_index = -1
    file_path = img_paths[index]
    g_label_path = f'{file_path[:-4]}.txt'
    g_raw = cv2.imread(file_path, cv2.IMREAD_COLOR)
    g_raw = cv2.resize(g_raw, g_win_size)
    g_raw = np.concatenate((g_raw, side_pan), axis=1)
    g_rgbs = load_saved_rgbs_if_exist(g_label_path)
    if g_rgbs is not None:
        for i in range(len(g_rgbs)):
            g_raw = set_circle_to_side_pan(g_raw, g_rgbs[i], i)
    cv2.namedWindow(g_win_name)
    cv2.imshow(g_win_name, g_raw)
    cv2.setMouseCallback(g_win_name, mouse_callback)
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
