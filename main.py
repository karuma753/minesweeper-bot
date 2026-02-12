import cv2
import numpy as np
import pyautogui
import time
from PIL import Image
from itertools import combinations,product
from collections import deque
import copy

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
    
    return size_y,size_x,coords_board

def image_to_board(H,W,coords_board,mine_board):
    x,y = coords_board[0][0]
    pyautogui.moveTo(x-16,y-16)
    cells_image = ["cell.png","bomb.png","flag.png","empty.png","1.png","2.png","3.png","4.png","5.png","6.png"]
    cells = ["?","bomb","x","-","1","2","3","4","5","6"]
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
            if mine_board[r][c] == "?":
                x,y = coords_board[r][c]
                cell_image = current_image[y:y+16,x:x+16]
                for i,img in enumerate(images):
                    result = cv2.matchTemplate(img,cell_image,cv2.TM_CCOEFF_NORMED)
                    minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(result)
                    if maxVal >= 0.9:
                        mine_board[r][c] = cells[i]
                        break
    return mine_board

H,W,coords_board = get_board()
center_x,center_y = coords_board[(H//2)][(W//2)]
pyautogui.click(center_x+8,center_y+8)

def is_inside(pos,board):
    r,c = pos
    H = len(board)
    W = len(board[0])
    if 0 <= r < H and 0<= c < W:
        return True
    else:
        return False
    
def get_neighbers(pos,board):
    r,c = pos
    H = len(board)
    W = len(board[0])
    move = [[-1,0],[-1,1],[0,1],[1,1],[1,0],[1,-1],[0,-1],[-1,-1]]
    neighbers_list = []
    for vec in move:
        next_r = r + vec[0]
        next_c = c + vec[1]
        if is_inside((next_r,next_c),board):
            neighbers_list.append((next_r,next_c))
    return neighbers_list

def get_num(pos,board): #周囲8マスにある"?"の座標のsetと、"x"の座標のsetを返す
    qtn_set = set()
    bom_set = set()
    for y,x in get_neighbers(pos,board):
        if board[y][x] == "?":
            qtn_set.add((y,x))
        elif board[y][x] == "x":
            bom_set.add((y,x))
    return [qtn_set,bom_set]

def update_cells(kinds,cells,board,que):
    open_set = set()
    for r,c in cells:
        if kinds == "open":
            board[r][c] = "-"
        elif kinds == "flag":
            board[r][c] = "x"
        open_set.update(get_neighbers((r,c),board))

    degi_set = set()
    for r,c in open_set:
        if str(board[r][c]).isdigit() and (r,c) not in que:
            degi_set.add((r,c))
    return degi_set

def semi_backtrack(dic_list):
    search_dict = {}
    for i,item in enumerate(dic_list):
        for cell in item["cells"]:
            if cell in search_dict:
                search_dict[cell].append(i)
            else:
                search_dict[cell] = [i]

    survive_list = [()]
    questions_from_dict = set()
    for dct in dic_list:
        questions_from_dict.update(dct["cells"])
        current_list = [valve for valve in combinations(dct["cells"],dct["bombs"])]
        bombs_list = [prev + item for prev, item in product(survive_list,current_list)]
        index_of_isdict = set()
        for cell in dct["cells"]:
            index_of_isdict.update(search_dict[cell])
        current_bombs = []
        for bombs in bombs_list:
            is_just_count = True
            if len(bombs) > 1:
                bombs = set(bombs)
                for i in index_of_isdict:
                    bomb_count = len(dic_list[i]["cells"] & bombs)
                    if bomb_count > dic_list[i]["bombs"]:
                        is_just_count = False
            if is_just_count:
                if n >= len(bombs):
                    current_bombs.append(tuple(bombs))
        survive_list = current_bombs
        survive_list = list(set(survive_list))
        # print(survive_list)

    survive_question = set()
    for survive in survive_list:
        survive_question.update(survive)
    
    safe = questions_from_dict - survive_question
    if survive_list:
        bomb = set(survive_list[0]).intersection(survive_list[1:])
    else:
        bomb = set(survive_list)

    
    return {"safe":safe,"bomb":bomb}

def solve_one_frame():
    global n,mine_board
    mine_board = image_to_board(H,W,coords_board,mine_board)
    virtual_board = copy.deepcopy(mine_board)
    open_set = set()
    flag_set = set()
    queue = deque([(r,c) for r in range(H) for c in range(W) if virtual_board[r][c].isdigit()])
    in_queue = set(queue)
    if any("bomb" in row for row in mine_board):
        return "BOMB"

    while True: #思考ループ
        change_this_round = False
        while queue: #自明整理
            r,c = queue.popleft()
            if not virtual_board[r][c].isdigit():
                continue
            in_queue.remove((r,c))
            N = int(virtual_board[r][c])
            qtn, bom = get_num((r,c),virtual_board)
            if len(qtn) == 0:
                continue
            if len(bom) == N:
                change_this_round = True
                open_set.update(qtn)
                degi_set = update_cells("open",qtn,virtual_board,in_queue)
                queue.extend(degi_set)
                in_queue.update(degi_set)
                # for r,c in qtn:
                #     x,y = coords_board[r][c]
                #     open_set.add(x,y)
                #     virtual_board[r][c] = "-"
                #     Flag = True
            elif len(qtn | bom) == N:
                change_this_round = True
                flag_set.update(qtn)
                degi_set = update_cells("flag",qtn,virtual_board,in_queue)
                queue.extend(degi_set)
                in_queue.update(degi_set)
                # for r,c in qtn:
                #     x,y = coords_board[r][c]
                    
                #     n -= 1
                #     Flag = True
        
        #ここでバックトラック
        all_num_pos = [(r,c) for r in range(H) for c in range(W) if virtual_board[r][c].isdigit()]
        num_dict = []
        for r,c in all_num_pos:
            qtn_set,bom_set = get_num((r,c),virtual_board)
            if qtn_set:
                for dict in num_dict:
                    if qtn_set == dict["cells"]:
                        continue
                num_dict.append({
                    "cells": qtn_set,
                    "bombs": int(virtual_board[r][c]) - len(bom_set)
                })

        results = semi_backtrack(num_dict)
        if len(results["safe"]) != 0 or len(results["bomb"]) != 0:
            open_cells = results["safe"]
            change_this_round = True
            open_set.update(open_cells)
            degi_set = update_cells("open",open_cells,virtual_board,in_queue)
            queue.extend(degi_set)
            in_queue.update(degi_set)
            
            bomb_cells = results["bomb"]
            change_this_round = True
            flag_set.update(bomb_cells)
            degi_set = update_cells("flag",bomb_cells,virtual_board,in_queue)
            queue.extend(degi_set)
            in_queue.update(degi_set)

        if not change_this_round:
            break
    
    if len(open_set) == 0 and len(flag_set) == 0:
        if n != 0: 
            return "STUCK"
        else:
            return "CLEARED"
        
    for right_click_cell in flag_set:
        r,c = right_click_cell
        x,y = coords_board[r][c]
        pyautogui.rightClick(x+8,y+8)
        n -= 1
        print(n)
    for click_cell in open_set:
        r,c = click_cell
        x,y = coords_board[r][c]
        pyautogui.click(x+8,y+8)
    return "SUCCESS"

    # open_list = get_open(results["safe"])
    # for y,x,number in open_list:
    #     map_list[y][x] = number
    # degi_list = after_open(open_list,map_list,in_queue)
    # queue.extend(degi_list)
    # in_queue.update(degi_list)

    # for y,x in results["bomb"]:
    #     map_list[y][x] = "x"
    #     n -= 1
    # degi_list = after_open(results["bomb"],map_list,in_queue)
    # queue.extend(degi_list)
    # in_queue.update(degi_list)
    # print("semi_backtrack")

n = 99
mine_board = [["?" for _ in range(W)] for _ in range(H)]
while True:
    if solve_one_frame() == "CLEARED":
        print("クリア")
        break
    elif solve_one_frame() == "STUCK":
        print("詰み")
        pyautogui.moveTo(500,500)
        break
    elif solve_one_frame() == "BOMB":
        print("ミス！")
        break