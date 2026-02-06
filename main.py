import cv2
import numpy as np
import pyautogui
import time
from PIL import Image

time.sleep(3)
board_image = cv2.cvtColor(np.array(pyautogui.screenshot()), cv2.COLOR_RGB2BGR)
template = cv2.imread("cell.png")

result = cv2.matchTemplate(board_image,template,cv2.TM_CCOEFF_NORMED)

ys, xs = np.where(result >= 0.9)
coords = sorted(zip(xs,ys),key=lambda p:(p[1],p[0]))
top_left_x,top_left_y = (coords[0])
bottom_right_x,bottom_right_y = (coords[-1])
size_y = int((bottom_right_y - top_left_y) / 16 + 1)
size_x = int((bottom_right_x - top_left_x) / 16 + 1)

board = []
for r in range(size_y):
    row = []
    for c in range(size_x):
        row.append(coords[r * size_x + c])
    board.append(row)

pyautogui.moveTo(board[4][4])

