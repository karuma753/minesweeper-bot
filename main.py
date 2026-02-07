import cv2
import numpy as np
import pyautogui
import time
from PIL import Image

def get_board():
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

    coords_board = []
    for r in range(size_y):
        row = []
        for c in range(size_x):
            row.append(coords[r * size_x + c])
        coords_board.append(row)

    mine_board = [["o" for _ in range(size_x)] for _ in range(size_y)]
    
    return size_y,size_x,coords_board,mine_board

def image_to_board(H,W,coords_board,mine_board):
    cells_image = ["cell.png","flag.png","empty.png","1.png","2.png","3.png","4.png"]
    cells = ["?","x","-","1","2","3","4"]
    images = [cv2.imread(cell) for cell in cells_image]

    # board_image = cv2.cvtColor(np.array(pyautogui.screenshot()), cv2.COLOR_RGB2BGR)
    # debug_image = board_image.copy()
    # for r in range(H):
    #     for c in range(W):
    #         x,y = coords_board[r][c]
    #         cv2.rectangle(debug_image,(x,y),(x+16, y+16),(0,0,255),1)
    # cv2.imwrite("debug_board.png", debug_image)
    # どこをマスとして認識しているかチェックするやつ。チェックした結果、cell.pngの切り取り範囲が１つずれてた。

    # start_x,start_y = coords_board[0][0]
    # x,y = start_x.item(),start_y.item()
    # current_image = cv2.cvtColor(np.array(pyautogui.screenshot(region=(x,y,16*W,16*H))), cv2.COLOR_RGB2BGR)
    # これだと、coords_boardに入っている座標とずれるから、offsetが必要なんだけど、全体のスクリーンショットをとってもそこまで負荷にならないからボツ

    # img1 = current_image[0:30,0:30]
    # cv2.imwrite("img1.png",img1)
    # 切り出し方のメモ

    current_image = cv2.cvtColor(np.array(pyautogui.screenshot()), cv2.COLOR_RGB2BGR)
    for r in range(H):
        for c in range(W):
            x,y = coords_board[r][c]
            cell_image = current_image[y:y+16,x:x+16]
            for i,img in enumerate(images):
                result = cv2.matchTemplate(img,cell_image,cv2.TM_CCOEFF_NORMED)
                minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(result)
                if maxVal >= 0.9:
                    mine_board[r][c] = cells[i]
                    break
    print(mine_board)
    return mine_board

H,W,coords_board, mine_board = get_board()
center_x,center_y = coords_board[(H//2)][(W//2)]
pyautogui.click(center_x+8,center_y+8)
mine_board = image_to_board(H,W,coords_board,mine_board)

