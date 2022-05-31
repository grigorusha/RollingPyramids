# Импортируем библиотеку pygame
import pygame
from pygame import *
import pygame_widgets
from pygame_widgets.button import Button

import random
import math

from tkinter import Tk
from tkinter import filedialog as fd
import os

# Объявляем базовые переменные
SIZE_X_START = 5
SIZE_Y_START = 4
SIZE_X = SIZE_X_START
SIZE_Y = SIZE_Y_START

BORDER = 5
PANEL = 100

TG60 = math.sqrt(3)
TG30 = TG60/3

EDGE_PYRAMID = 100
HEIGHT_PYRAMID = int(EDGE_PYRAMID*TG60/2)
EDGE_PYRAMIDka = int(EDGE_PYRAMID-2*BORDER*TG60)
HEIGHT_PYRAMIDka = int((EDGE_PYRAMID*TG60/2)-BORDER*3)

BACKGROUND_COLOR = "#000000"
GRAY_COLOR = "#808080"
GRAY_COLOR2 = "#C0CCB0"
PYRAMID_COLOR = [("W","#FFFFFF"),("B","#0000FF"),("G","#008000"),("R","#FF0000")]

PYRAMID_STATE = [["WB","GR"],["WG","RB"],["WR","BG"],
                 ["BW","RG"],["BG","WR"],["BR","GW"],
                 ["GW","BR"],["GB","RW"],["GR","WB"],
                 ["RB","WG"],["RW","GB"],["RG","BW"]]

level = []
TYPE_ORIENT = 1  # 1 - наверх, 2 - налево, 3 - вниз, 4 - направо
TYPE_COLOR  = 1  # 1 - грани, 2 - углы

BTN_CLICK = False
BTN_CLICK_STR = ""

def pyram_rotate(pyram,vek, orient):
    pyram_new = []
    if vek == 1:
        pyram_new = [pyram[1], pyram[0]]
    else:
        state = pyram[0] + pyram[1]
        state_new = ""
        for pos in PYRAMID_STATE:
            if pos[0] == state:
                state_new = pos[1]
                break
        if vek == 0:
            pyram_new = [state_new[0], state_new[1]]
        elif orient:
            if vek == 2:
                pyram_new = [state_new[0], state_new[1]]
            elif vek == 3:
                pyram_new = [state_new[1], state_new[0]]
        else:
            if vek == 2:
                pyram_new = [state_new[1], state_new[0]]
            elif vek == 3:
                pyram_new = [state_new[0], state_new[1]]

    return pyram_new

def pyram_pos(level, y,x):
    pyram_epty = []

    if (y % 2 == 0)==(x % 2 == 0):  # уголок наверх
        if y < SIZE_Y - 1:
            pyram = level[y+1][x]
            if (pyram[0] == " "):
                pyram_epty.append((y+1, x, 1))
    else:  # уголок вниз
        if y > 0:
            pyram = level[y-1][x]
            if (pyram[0] == " "):
                pyram_epty.append((y-1, x, 1))
    if x>0:
        pyram = level[y][x-1]
        if (pyram[0] == " "):
            pyram_epty.append((y, x-1, 2))
    if x<SIZE_X-1:
        pyram = level[y][x+1]
        if (pyram[0] == " "):
            pyram_epty.append((y,x+1, 3))

    return pyram_epty

def init_level(y,x):
    level = []
    for ny in range(y):
        str = []
        for nx in range(x):
            str.append(["W","B"])
        level.append(str)
    ny = y // 2
    nx = x // 2
    level[ny][nx] = [" "," "]

    return level

def button_Type_click():
    global TYPE_ORIENT, BTN_CLICK, BTN_CLICK_STR
    # TYPE_ORIENT = (TYPE_ORIENT+1)%4
    BTN_CLICK_STR = "type"
    BTN_CLICK = True

def button_Color_click():
    global TYPE_COLOR, BTN_CLICK, BTN_CLICK_STR
    # TYPE_COLOR = 3-TYPE_COLOR
    BTN_CLICK_STR = "color"
    BTN_CLICK = True

def button_Reset_click():
    global BTN_CLICK, BTN_CLICK_STR
    BTN_CLICK_STR = "reset"
    BTN_CLICK = True

def button_Scramble_click():
    global BTN_CLICK, BTN_CLICK_STR
    BTN_CLICK_STR = "scramble"
    BTN_CLICK = True

def button_Edit_click(but):
    global BTN_CLICK, BTN_CLICK_STR
    if but==0:
        BTN_CLICK_STR = "edit"
    elif but == 1:
        BTN_CLICK_STR = "editpyr"
    elif but==2:
        BTN_CLICK_STR = "editblk"
    elif but==3:
        BTN_CLICK_STR = "editemp"
    BTN_CLICK = True

def button_Size_click(y,x):
    global SIZE_X,SIZE_Y,BTN_CLICK, BTN_CLICK_STR
    if (SIZE_X>3)and(x<0):
        SIZE_X = SIZE_X + x
        BTN_CLICK_STR = "minusx"
    if (SIZE_X<9)and(x>0):
        SIZE_X = SIZE_X + x
        BTN_CLICK_STR = "plusx"
    if (SIZE_Y>2)and(y<0):
        SIZE_Y = SIZE_Y + y
        BTN_CLICK_STR = "minusy"
    if (SIZE_Y<8)and(y>0):
        SIZE_Y = SIZE_Y + y
        BTN_CLICK_STR = "plusy"
    BTN_CLICK = True

def main():
    global SIZE_X,SIZE_Y,BTN_CLICK,BTN_CLICK_STR

    # основные константы
    SIZE_X = SIZE_X_START
    SIZE_Y = SIZE_Y_START

    # основная инициализация
    random.seed()
    pygame.init()  # Инициация PyGame
    font = pygame.font.SysFont('Verdana', 18)
    timer = pygame.time.Clock()
    Tk().withdraw()

    dir = os.path.abspath(os.curdir)
    icon = pygame.image.load(dir + '\RollingPyramids.ico')

    ################################################################################
    ################################################################################
    # перезапуск программы при смене параметров
    while True:
        # дополнительные константы
        WIN_WIDTH = int(EDGE_PYRAMID * (SIZE_X/2+0.5))+BORDER*2  # Ширина создаваемого окна
        WIN_HEIGHT = SIZE_Y * HEIGHT_PYRAMID+BORDER*2  # Высота

        level = init_level(SIZE_Y, SIZE_X)
        edit_mode = False
        edit_mode_str = ""
        scramble_move = 0

        # инициализация окна
        screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT+PANEL))  # Создаем окошко
        pygame.display.set_caption("Rolling Pyramids")  # Пишем в шапку
        pygame.display.set_icon(icon)

        screen.fill(BACKGROUND_COLOR) # Заливаем поверхность сплошным цветом

        # инициализация кнопок
        button_y1 = WIN_HEIGHT + BORDER + 10
        button_Reset = Button(screen, 10, button_y1, 45, 20, text='Reset', fontSize=20, margin=5, radius=3,
                        inactiveColour="#008000", hoverColour="#008000", pressedColour=(0, 200, 20),
                        onClick = lambda: button_Reset_click())
        button_Scramble = Button(screen, button_Reset.textRect.right+10, button_y1, 70, 20, text='Scramble', fontSize=20, margin=5, radius=3,
                        inactiveColour="#008000", hoverColour="#008000", pressedColour=(0, 200, 20),
                        onClick = lambda: button_Scramble_click())
        button_Undo = Button(screen, button_Scramble.textRect.right+10, button_y1, 40, 20, text='Undo', fontSize=20, margin=5, radius=3,
                        inactiveColour="#008000", hoverColour="#008000", pressedColour=(0, 200, 20))

        button_y2 = button_y1 + 30
        button_Type = Button(screen, 10, button_y2, 60, 20, text='Type: Δ', fontSize=20, margin=5, radius=3,
                        inactiveColour="#008000", hoverColour="#008000", pressedColour=(0, 200, 20),
                        onClick=lambda: button_Type_click())
        button_MinusX = Button(screen, button_Type.textRect.right+15, button_y2, 20, 20, text='-', fontSize=20, margin=5, radius=3,
                        inactiveColour="#008000", hoverColour="#008000", pressedColour=(0, 200, 20),
                        onClick=lambda: button_Size_click(0,-1))
        textx = font.render(str(SIZE_X), True, "#008000")
        textx_place = textx.get_rect(topleft=(button_MinusX.textRect.right+15, button_y2 - 3))
        button_PlusX =  Button(screen, textx_place.right+7, button_y2, 20, 20, text='+', fontSize=20, margin=5, radius=3,
                        inactiveColour="#008000", hoverColour="#008000", pressedColour=(0, 200, 20),
                        onClick=lambda: button_Size_click(0,1))

        button_MinusY = Button(screen, button_PlusX.textRect.right+15, button_y2, 20, 20, text='-', fontSize=20, margin=5, radius=3,
                        inactiveColour="#008000", hoverColour="#008000", pressedColour=(0, 200, 20),
                        onClick=lambda: button_Size_click(-1,0))
        texty = font.render(str(SIZE_Y), True, "#008000")
        texty_place = texty.get_rect(topleft=(button_MinusY.textRect.right+15, button_y2 - 3))
        button_PlusY = Button(screen, texty_place.right+7, button_y2, 20, 20, text='+', fontSize=20, margin=5, radius=3,
                        inactiveColour="#008000", hoverColour="#008000", pressedColour=(0, 200, 20),
                        onClick=lambda: button_Size_click(1,0))

        button_y3 = button_y2 + 30
        button_Color = Button(screen, 10, button_y3, 65, 20, text='Color: Δ', fontSize=20, margin=5, radius=3,
                        inactiveColour="#008000", hoverColour="#008000", pressedColour=(0, 200, 20),
                        onClick=lambda: button_Color_click())
        button_Edit = Button(screen, button_Color.textRect.right+15, button_y3, 50, 20, text='Edit', fontSize=20, margin=5, radius=3,
                        inactiveColour="#008000", hoverColour="#008000", pressedColour=(0, 200, 20),
                        onClick=lambda: button_Edit_click(0))
        button_EditPyr = Button(screen, button_Edit.textRect.right+25, button_y3, 20, 20, text='Δ', fontSize=20, margin=5, radius=3,
                        inactiveColour="#008000", hoverColour="#008000", pressedColour=(0, 200, 20),
                        onClick=lambda: button_Edit_click(1))
        button_EditBlk = Button(screen, button_EditPyr.textRect.right+7, button_y3, 20, 20, text='*', fontSize=20, margin=5, radius=3,
                        inactiveColour="#008000", hoverColour="#008000", pressedColour=(0, 200, 20),
                        onClick=lambda: button_Edit_click(2))
        button_EditEmp = Button(screen, button_EditBlk.textRect.right+10, button_y3, 20, 20, text='x', fontSize=20, margin=5, radius=3,
                        inactiveColour="#008000", hoverColour="#008000", pressedColour=(0, 200, 20),
                        onClick=lambda: button_Edit_click(3))

        button_set = [button_Reset, button_Scramble, button_Undo, button_Type, button_Color, button_Edit,
                      button_MinusX, button_PlusX, button_MinusY, button_PlusY, button_EditPyr, button_EditBlk, button_EditEmp]

        ################################################################################
        ################################################################################
        # Основной цикл программы

        while True:

            mouse_x = mouse_y = 0
            pyramid_pos_x = pyramid_pos_y = -1

            ################################################################################
            ################################################################################
            # обработка событий
            if scramble_move == 0:
                timer.tick(10)

                events = pygame.event.get()
                for ev in events:  # Обрабатываем события
                    if (ev.type == QUIT) or (ev.type == KEYDOWN and ev.key == K_ESCAPE):
                        return SystemExit, "QUIT"
                    if ev.type == MOUSEBUTTONDOWN and ev.button == 1:
                        mouse_x = ev.pos[0]
                        mouse_y = ev.pos[1]

                ################################################################################
                # обработка нажатия на кнопки
                if BTN_CLICK:
                    fl_break = True
                    if BTN_CLICK_STR=="reset":
                        fl_break = True
                    if BTN_CLICK_STR=="scramble":
                        fl_break = False
                        scramble_move = SIZE_X * SIZE_Y * 2000
                    if BTN_CLICK_STR=="minusy":
                        pos = pygame.mouse.get_pos()
                        pygame.mouse.set_pos(pos[0], pos[1] - HEIGHT_PYRAMID)
                    elif BTN_CLICK_STR=="plusy":
                        pos = pygame.mouse.get_pos()
                        pygame.mouse.set_pos(pos[0], pos[1] + HEIGHT_PYRAMID)
                    elif BTN_CLICK_STR == "edit":
                        fl_break = False
                        edit_mode = not edit_mode
                        if edit_mode:
                            BTN_CLICK_STR = "editpyr"
                            button_Edit.inactiveColour = "#0000F0"
                            button_Edit.hoverColour = "#0000F0"
                        else:
                            edit_mode_str = ""
                            button_Edit.inactiveColour = "#008000"
                            button_Edit.hoverColour = "#008000"
                            button_EditPyr.inactiveColour = "#008000"
                            button_EditPyr.hoverColour = "#008000"
                            button_EditBlk.inactiveColour = "#008000"
                            button_EditBlk.hoverColour = "#008000"
                            button_EditEmp.inactiveColour = "#008000"
                            button_EditEmp.hoverColour = "#008000"

                    if BTN_CLICK_STR == "editpyr":
                        fl_break = False
                        if edit_mode:
                            if edit_mode_str != "pyram":
                                edit_mode_str = "pyram"
                                button_EditPyr.inactiveColour = "#0000F0"
                                button_EditPyr.hoverColour = "#0000F0"
                                button_EditBlk.inactiveColour = "#008000"
                                button_EditBlk.hoverColour = "#008000"
                                button_EditEmp.inactiveColour = "#008000"
                                button_EditEmp.hoverColour = "#008000"
                    elif BTN_CLICK_STR == "editblk":
                        fl_break = False
                        if edit_mode:
                            if edit_mode_str != "block":
                                edit_mode_str = "block"
                                button_EditBlk.inactiveColour = "#0000F0"
                                button_EditBlk.hoverColour = "#0000F0"
                                button_EditPyr.inactiveColour = "#008000"
                                button_EditPyr.hoverColour = "#008000"
                                button_EditEmp.inactiveColour = "#008000"
                                button_EditEmp.hoverColour = "#008000"
                    elif BTN_CLICK_STR == "editemp":
                        fl_break = False
                        if edit_mode:
                            if edit_mode_str != "empty":
                                edit_mode_str = "empty"
                                button_EditEmp.inactiveColour = "#0000F0"
                                button_EditEmp.hoverColour = "#0000F0"
                                button_EditPyr.inactiveColour = "#008000"
                                button_EditPyr.hoverColour = "#008000"
                                button_EditBlk.inactiveColour = "#008000"
                                button_EditBlk.hoverColour = "#008000"

                    BTN_CLICK = False
                    BTN_CLICK_STR = ""
                    if fl_break: break

            else:
                # обработка рандома для Скрамбла
                pyramid_pos_x = random.randint(0,SIZE_X-1)
                pyramid_pos_y = random.randint(0,SIZE_Y-1)

                pyramid = level[pyramid_pos_y][pyramid_pos_x]
                if (pyramid[0] != " ") and (pyramid[0] != "X"):
                    vek = random.randint(1,4)
                    # mouse_x = mouse_y = 1

            ################################################################################
            # обработка нажатия на пирамидки в игровом поле

            if mouse_x+mouse_y > 0:
                if mouse_y<(WIN_HEIGHT-BORDER): # мышь внутри игрового поля
                    yy = (mouse_y-BORDER)//HEIGHT_PYRAMID # строка
                    y2 = (mouse_y-BORDER)% HEIGHT_PYRAMID # координаты в строке

                    xx = int((mouse_x-BORDER)//(EDGE_PYRAMID/2)) # номер прямоугольного блока
                    x2 = int((mouse_x-BORDER)% (EDGE_PYRAMID/2)) # координаты в блоке

                    pyramid_pos_y = yy

                    try: tg1 = y2/x2
                    except: tg1 = y2
                    try: tg2 = y2/(EDGE_PYRAMID/2-x2)
                    except: tg2 = y2

                    if (yy % 2 == 0) and (xx % 2 == 0):  # 1 ряд, четные с 0
                        if tg2>TG60:
                            pyramid_pos_x = xx
                        else:
                            pyramid_pos_x = xx-1
                    elif (yy % 2 == 0) and (xx % 2 == 1):  # 1 ряд, нечетные с 1
                        if tg1>TG60:
                            pyramid_pos_x = xx-1
                        else:
                            pyramid_pos_x = xx
                    elif (yy % 2 == 1) and (xx % 2 == 0):  # 2 ряд, четные с 0
                        if tg1>TG60:
                            pyramid_pos_x = xx-1
                        else:
                            pyramid_pos_x = xx
                    elif (yy % 2 == 1) and (xx % 2 == 1):  # 2 ряд, нечетные с 1
                        if tg2>TG60:
                            pyramid_pos_x = xx
                        else:
                            pyramid_pos_x = xx-1

                    if pyramid_pos_x >= SIZE_X : pyramid_pos_x = -1

            ################################################################################
            ################################################################################
            # режим редактора
            if edit_mode and len(edit_mode_str)>0 and (pyramid_pos_x>=0) and (pyramid_pos_y>=0):
                if edit_mode_str=="pyram":
                    level[pyramid_pos_y][pyramid_pos_x] = ["W","B"]
                if edit_mode_str=="block":
                    level[pyramid_pos_y][pyramid_pos_x] = ["X","X"]
                if edit_mode_str=="empty":
                    level[pyramid_pos_y][pyramid_pos_x] = [" "," "]

            ################################################################################
            ################################################################################
            # логика игры - выполнение перемещений
            if not edit_mode and (pyramid_pos_x>=0) and (pyramid_pos_y>=0):
                pyram = level[pyramid_pos_y][pyramid_pos_x]
                if (pyram[0] != "X")and(pyram[0] != " "):
                    pyram_empty = pyram_pos(level, pyramid_pos_y, pyramid_pos_x)
                    if len(pyram_empty)==1:
                        vek = pyram_empty[0][2]
                        orient = (pyramid_pos_y % 2 == 0) == (pyramid_pos_x % 2 == 0) # уголок вверх
                        pyram_new = pyram_rotate(pyram, vek, orient)

                        level[pyram_empty[0][0]][pyram_empty[0][1]] = pyram_new
                        level[pyramid_pos_y][pyramid_pos_x] = [" "," "]

            if scramble_move != 0:
                scramble_move -= 1
                #moves_stack = []
                #moves = 0
                continue
                # отрисовка не нужна

            ################################################################################
            ################################################################################
            # отрисовка игрового поля
            screen.fill(BACKGROUND_COLOR)
            screen.blit(textx, textx_place)
            screen.blit(texty, texty_place)
            pf = Surface((WIN_WIDTH, BORDER))
            pf.fill(Color("#B88800"))
            screen.blit(pf, (0, WIN_HEIGHT + BORDER))

            # отрисовка сетки
            if (TYPE_ORIENT==1):
                for ny in range(SIZE_Y+1):
                    if ny % 2 == 0:
                        x1 = int(EDGE_PYRAMID / 2) + BORDER
                        x2 = int(x1 + (SIZE_X // 2) * EDGE_PYRAMID)
                        x0 = BORDER
                    else:
                        x1 = BORDER
                        x2 = int(x1+(SIZE_X//2+SIZE_X%2)*EDGE_PYRAMID)
                        x0 = int(EDGE_PYRAMID / 2) + BORDER
                    y1 = ny * HEIGHT_PYRAMID + BORDER
                    draw.line(screen, GRAY_COLOR, (x1, y1), (x2, y1), 3)

                    y2 = (ny + 1) * HEIGHT_PYRAMID + BORDER
                    if ny<SIZE_Y:
                        for nn in range(SIZE_X//2+1):
                            draw.line(screen, GRAY_COLOR, (x1+nn*EDGE_PYRAMID, y1), (x0+nn*EDGE_PYRAMID, y2), 3)
                        for nn in range(SIZE_X//2+SIZE_X%2):
                            if ny % 2 == 0:
                                draw.line(screen, GRAY_COLOR, (x1+nn*EDGE_PYRAMID, y1), (x0+(nn+1)*EDGE_PYRAMID, y2), 3)
                            else:
                                draw.line(screen, GRAY_COLOR, (x1+(nn+1)*EDGE_PYRAMID, y1), (x0+nn*EDGE_PYRAMID, y2), 3)

            ############################################
            # отрисовка пирамидок
            for ny,row in enumerate(level):
                for nx,pyramid in enumerate(row):
                    ############################################
                    # расчет всех координат
                    if (ny % 2 == 0) and (nx % 2 == 0):  # 1 ряд, наверх
                        x1 = int(EDGE_PYRAMID / 2) + (nx // 2) * EDGE_PYRAMID + BORDER
                        y1 = ny * HEIGHT_PYRAMID + BORDER + (2 * BORDER)
                        x2 = x1 + int(EDGE_PYRAMIDka / 2)
                        x3 = x1 - int(EDGE_PYRAMIDka / 2)
                        yy = y1 + HEIGHT_PYRAMIDka
                        y0 = y1 + int(2 * HEIGHT_PYRAMIDka / 3)

                    elif (ny % 2 == 1) and (nx % 2 == 1):  # 2 ряд, наверх
                        x1 = (nx // 2 + nx % 2) * EDGE_PYRAMID + BORDER
                        y1 = ny * HEIGHT_PYRAMID + BORDER + (2 * BORDER)
                        x2 = x1 + int(EDGE_PYRAMIDka / 2)
                        x3 = x1 - int(EDGE_PYRAMIDka / 2)
                        yy = y1 + HEIGHT_PYRAMIDka
                        y0 = y1 + int(2 * HEIGHT_PYRAMIDka / 3)

                    elif (ny % 2 == 0) and (nx % 2 == 1):  # 1 ряд, вниз
                        yy = ny * HEIGHT_PYRAMID + BORDER + (BORDER)
                        x1 = (nx // 2 + nx % 2) * EDGE_PYRAMID + BORDER
                        y1 = yy + HEIGHT_PYRAMIDka
                        x2 = x1 - int(EDGE_PYRAMIDka / 2)
                        x3 = x1 + int(EDGE_PYRAMIDka / 2)
                        y0 = y1 - int(2 * HEIGHT_PYRAMIDka / 3)

                    elif (ny % 2 == 1) and (nx % 2 == 0):  # 2 ряд, вниз
                        yy = ny * HEIGHT_PYRAMID + BORDER + (BORDER)
                        x1 = int(EDGE_PYRAMID / 2) + (nx // 2) * EDGE_PYRAMID + BORDER
                        y1 = yy + HEIGHT_PYRAMIDka
                        x2 = x1 - int(EDGE_PYRAMIDka / 2)
                        x3 = x1 + int(EDGE_PYRAMIDka / 2)
                        y0 = y1 - int(2 * HEIGHT_PYRAMIDka / 3)

                    ############################################
                    # сама отрисовка

                    if pyramid[0]==" ": # пустая ячейка
                        draw.polygon(screen, BACKGROUND_COLOR, [[x1, y1], [x2, yy], [x3, yy]])
                    elif pyramid[0]=="X": # блок
                        draw.polygon(screen,GRAY_COLOR2, [[x1, y1], [x2, yy], [x3, yy]] )
                        draw.aaline(screen, GRAY_COLOR2, [x1, y1], [x2, yy])
                        draw.aaline(screen, GRAY_COLOR2, [x1, y1], [x3, yy])

                        delta = int(HEIGHT_PYRAMIDka/5)
                        delta2 = int(delta*TG60/2)
                        draw.line(screen, GRAY_COLOR, [x1, y0-delta], [x1, y0+delta],3)
                        draw.line(screen, GRAY_COLOR, [x1-delta2, y0-delta/2], [x1+delta2, y0+delta/2],3)
                        draw.line(screen, GRAY_COLOR, [x1-delta2, y0+delta/2], [x1+delta2, y0-delta/2],3)

                    else: # пирамидка
                        orient = (ny % 2 == 0) == (nx % 2 == 0) # уголок вверх
                        pyramid2 = pyram_rotate(pyramid, 0, orient)
                        for color in PYRAMID_COLOR:
                            if pyramid[1]==color[0]:
                                draw.polygon(screen,color[1], [[x1, y0], [x2, yy], [x3, yy]] )
                                draw.aaline(screen, color[1], [x1, y0], [x2, yy])
                                draw.aaline(screen, color[1], [x1, y0], [x3, yy])
                            elif pyramid2[0] == color[0]:
                                draw.polygon(screen,color[1], [[x1, y0], [x1, y1], [x3, yy]] )
                                draw.aaline(screen, color[1], [x1, y0], [x3, yy])
                                draw.aaline(screen, color[1], [x1, y1], [x3, yy])
                            elif pyramid2[1] == color[0]:
                                draw.polygon(screen,color[1], [[x1, y0], [x1, y1], [x2, yy]] )
                                draw.aaline(screen, color[1], [x1, y0], [x2, yy])
                                draw.aaline(screen, color[1], [x1, y1], [x2, yy])

            #####################################################################################
            pygame_widgets.update(events)
            pygame.display.update()  # обновление и вывод всех изменений на экран

        # удаляем кнопки
        for btn in button_set:
            btn.hide()

main()

"""
elif (TYPE_ORIENT == 3):
    for ny in range(SIZE_Y + 1):
        if ny % 2 == 0:
            x1 = BORDER
            x2 = int(x1 + (SIZE_X // 2 + SIZE_X % 2) * EDGE_PYRAMID)
            x0 = int(EDGE_PYRAMID / 2) + BORDER
        else:
            x1 = int(EDGE_PYRAMID / 2) + BORDER
            x2 = int(x1 + (SIZE_X // 2) * EDGE_PYRAMID)
            x0 = BORDER
        y1 = ny * HEIGHT_PYRAMID + BORDER
        draw.line(screen, GRAY_COLOR, (x1, y1), (x2, y1), 3)

        y2 = (ny + 1) * HEIGHT_PYRAMID + BORDER
        if ny<SIZE_Y:
            for nn in range(1+SIZE_X//2):
                draw.line(screen, GRAY_COLOR, (x1+nn*EDGE_PYRAMID, y1), (x0+nn*EDGE_PYRAMID, y2), 3)
            for nn in range(SIZE_X // 2 + SIZE_X % 2):
                if ny % 2 == 0:
                    draw.line(screen, GRAY_COLOR, (x1 + (nn + 1) * EDGE_PYRAMID, y1), (x0 + nn * EDGE_PYRAMID, y2), 3)
                else:
                    draw.line(screen, GRAY_COLOR, (x1+nn*EDGE_PYRAMID, y1), (x0+(nn+1)*EDGE_PYRAMID, y2), 3)
"""
