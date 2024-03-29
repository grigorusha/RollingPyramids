# Импортируем библиотеку pygame
import pygame
from pygame import *
import pygame_widgets
from pygame_widgets.button import Button

import random
import math
import copy

import webbrowser
from tkinter import Tk
from tkinter import filedialog as fd
import os

# Объявляем базовые переменные
SIZE_X_START = 5
SIZE_Y_START = 4
SIZE_X = SIZE_X_START
SIZE_Y = SIZE_Y_START

BORDER = 5
PANEL = 33*5

TG60 = math.sqrt(3)
TG30 = TG60/3

EDGE_PYRAMID = 100
HEIGHT_PYRAMID = int(EDGE_PYRAMID*TG60/2)
EDGE_PYRAMIDka = int(EDGE_PYRAMID-2*BORDER*TG60)
HEIGHT_PYRAMIDka = int((EDGE_PYRAMID*TG60/2)-BORDER*3)

BACKGROUND_COLOR = "#000000"
GRAY_COLOR = "#808080"
GRAY_COLOR2 = "#C0CCB0"
RED_COLOR = "#FF0000"
PYRAMID_COLOR = [("W","#FFFFFF"),("B","#0000FF"),("G","#008000"),("R","#FF0000")] # "R","800080"

PYRAMID_STATE = [["WB","GR"],["WG","RB"],["WR","BG"],
                 ["BW","RG"],["BG","WR"],["BR","GW"],
                 ["GW","BR"],["GB","RW"],["GR","WB"],
                 ["RB","WG"],["RW","GB"],["RG","BW"]]

level = []
solved_level = []
TYPE_COLOR  = 2  # 1 - грани, 2 - углы

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

def pyram_find_empty(level, y,x):
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
    global TYPE_COLOR
    level = []
    for ny in range(y):
        str = []
        for nx in range(x):
            if TYPE_COLOR==1:
                str.append(["W","B"])
            else:
                if nx % 3 == 0:
                    col = "R"
                else:
                    if (nx//3)%2 == 0:
                        if ny % 2 == 0:
                            col = "G"
                        else:
                            col = "B"
                    else:
                        if ny % 2 == 1:
                            col = "G"
                        else:
                            col = "B"
                str.append(["W", col])
        level.append(str)
    solved_level = copy.deepcopy(level)

    ny = y // 2
    nx = x // 2
    level[ny][nx] = [" "," "]

    return level,solved_level

def button_Button_click(button_str):
    global BTN_CLICK, BTN_CLICK_STR
    BTN_CLICK_STR = button_str
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

def read_file():
    dir = os.path.abspath(os.curdir)
    filetypes = (("Text file", "*.txt"),("Any file", "*"))
    filename = fd.askopenfilename(title="Open Level", initialdir=dir,filetypes=filetypes)
    if filename=="":
        return ""

    x = y = type = 0
    level = []
    with open(filename,'r') as f:
        lines = f.readlines()
        for nom,str in enumerate(lines):
            str = str.replace('\n','')
            if nom == 0:
                type = int(str)
                continue

            str_mas = []
            while len(str)>=2:
                sim1 = str[0]
                sim2 = str[1]
                str = str[3:]
                str_mas.append([sim1,sim2])
            level.append(str_mas)
            y += 1
            x = max(x,len(str_mas))
    return level, y, x, type

def save_file(level,type):
    dir = os.path.abspath(os.curdir)
    filetypes = (("Text file", "*.txt"),("Any file", "*"))
    filename = fd.asksaveasfile("w", title="Save Level as...", initialdir=dir,filetypes=filetypes)
    if filename==None:
        return ""

    with open(filename.name, 'w') as f:
        f.write(str(type) + "\n")
        for string in level:
            line = ""
            for pyr in string:
                line += pyr[0]+pyr[1]+" "
            f.write(line+"\n")

def main():
    global SIZE_X,SIZE_Y,BTN_CLICK,BTN_CLICK_STR,TYPE_COLOR

    # основные константы
    SIZE_X = SIZE_X_START
    SIZE_Y = SIZE_Y_START
    file_ext = False

    # основная инициализация
    random.seed()
    pygame.init()  # Инициация PyGame
    font = pygame.font.SysFont('Verdana', 18)
    font_button = pygame.font.SysFont("ArialB",18)
    timer = pygame.time.Clock()
    Tk().withdraw()

    icon = os.path.abspath(os.curdir) + "\\RollingPyramids.ico"
    if os.path.isfile(icon):
        pygame.display.set_icon(pygame.image.load(icon))

    ################################################################################
    ################################################################################
    # перезапуск программы при смене параметров
    while True:
        # дополнительные константы
        WIN_WIDTH = int(EDGE_PYRAMID * (SIZE_X/2+0.5))+BORDER*2  # Ширина создаваемого окна
        WIN_HEIGHT = SIZE_Y * HEIGHT_PYRAMID+BORDER*2  # Высота

        if file_ext:
            file_ext = False
            solved_level = []
        else:
            level,solved_level = init_level(SIZE_Y, SIZE_X)
        edit_mode = False
        edit_mode_str = ""
        scramble_move = 0

        moves_stack = []
        moves = 0
        solved = True
        bad_state = False # нет пустых ячеек после радактора

        # инициализация окна
        screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT+PANEL))  # Создаем окошко
        pygame.display.set_caption("Rolling Pyramids")  # Пишем в шапку

        screen.fill(BACKGROUND_COLOR) # Заливаем поверхность сплошным цветом

        # инициализация кнопок
        if True:
            button_y1 = WIN_HEIGHT + BORDER + 10
            button_Reset = Button(screen, 10, button_y1, 45, 20, text='Reset', fontSize=20, font=font_button, margin=5, radius=3,
                            inactiveColour="#008000", hoverColour="#008000", pressedColour=(0, 200, 20),
                            onClick = lambda: button_Button_click("reset"))
            button_Scramble = Button(screen, button_Reset.textRect.right+10, button_y1, 70, 20, text='Scramble', fontSize=20, font=font_button, margin=5, radius=3,
                            inactiveColour="#008000", hoverColour="#008000", pressedColour=(0, 200, 20),
                            onClick = lambda: button_Button_click("scramble"))
            button_Undo = Button(screen, button_Scramble.textRect.right+10, button_y1, 40, 20, text='Undo', fontSize=20, font=font_button, margin=5, radius=3,
                            inactiveColour="#008000", hoverColour="#008000", pressedColour=(0, 200, 20),
                            onClick = lambda: button_Button_click("undo"))

            button_y2 = button_y1 + 30
            button_Open = Button(screen, 10, button_y2, 45, 20, text='Open', fontSize=20, font=font_button, margin=5, radius=3,
                            inactiveColour="#008000", hoverColour="#008000", pressedColour=(0, 200, 20),
                            onClick=lambda: button_Button_click("open"))
            button_Save = Button(screen, button_Open.textRect.right+10, button_y2, 45, 20, text='Save', fontSize=20, font=font_button, margin=5, radius=3,
                            inactiveColour="#008000", hoverColour="#008000", pressedColour=(0, 200, 20),
                            onClick=lambda: button_Button_click("save"))
            button_MinusX = Button(screen, button_Save.textRect.right+15, button_y2, 20, 20, text='-', fontSize=20, font=font_button, margin=5, radius=3,
                            inactiveColour="#008000", hoverColour="#008000", pressedColour=(0, 200, 20),
                            onClick=lambda: button_Size_click(0,-1))
            textx = font.render(str(SIZE_X), True, "#008000")
            textx_place = textx.get_rect(topleft=(button_MinusX.textRect.right+15, button_y2 - 3))
            button_PlusX =  Button(screen, textx_place.right+7, button_y2, 20, 20, text='+', fontSize=20, font=font_button, margin=5, radius=3,
                            inactiveColour="#008000", hoverColour="#008000", pressedColour=(0, 200, 20),
                            onClick=lambda: button_Size_click(0,1))

            button_MinusY = Button(screen, button_PlusX.textRect.right+15, button_y2, 20, 20, text='-', fontSize=20, font=font_button, margin=5, radius=3,
                            inactiveColour="#008000", hoverColour="#008000", pressedColour=(0, 200, 20),
                            onClick=lambda: button_Size_click(-1,0))
            texty = font.render(str(SIZE_Y), True, "#008000")
            texty_place = texty.get_rect(topleft=(button_MinusY.textRect.right+15, button_y2 - 3))
            button_PlusY = Button(screen, texty_place.right+7, button_y2, 20, 20, text='+', fontSize=20, font=font_button, margin=5, radius=3,
                            inactiveColour="#008000", hoverColour="#008000", pressedColour=(0, 200, 20),
                            onClick=lambda: button_Size_click(1,0))

            button_y3 = button_y2 + 30
            button_Color = Button(screen, 10, button_y3, 65, 20, text='Color: Δ', fontSize=20, font=font_button, margin=5, radius=3,
                            inactiveColour="#008000", hoverColour="#008000", pressedColour=(0, 200, 20),
                            onClick=lambda: button_Button_click("color"))
            button_Edit = Button(screen, button_Color.textRect.right+15, button_y3, 50, 20, text='Edit', fontSize=20, font=font_button, margin=5, radius=3,
                            inactiveColour="#008000", hoverColour="#008000", pressedColour=(0, 200, 20),
                            onClick=lambda: button_Edit_click(0))
            button_EditPyr = Button(screen, button_Edit.textRect.right+25, button_y3, 20, 20, text='Δ', fontSize=20, font=font_button, margin=5, radius=3,
                            inactiveColour="#008000", hoverColour="#008000", pressedColour=(0, 200, 20),
                            onClick=lambda: button_Edit_click(1))
            button_EditBlk = Button(screen, button_EditPyr.textRect.right+7, button_y3, 20, 20, text='*', fontSize=20, font=font_button, margin=5, radius=3,
                            inactiveColour="#008000", hoverColour="#008000", pressedColour=(0, 200, 20),
                            onClick=lambda: button_Edit_click(2))
            button_EditEmp = Button(screen, button_EditBlk.textRect.right+10, button_y3, 20, 20, text='x', fontSize=20, font=font_button, margin=5, radius=3,
                            inactiveColour="#008000", hoverColour="#008000", pressedColour=(0, 200, 20),
                            onClick=lambda: button_Edit_click(3))

            button_y4 = button_y3 + 30
            button_Info = Button(screen, 10, button_y4, 95, 20, text='Puzzle Photo ->', fontSize=20, font=font_button, margin=5, radius=3,
                            inactiveColour="#0000FF", hoverColour="#0000FF", pressedColour=(0, 200, 20),
                            onClick=lambda: button_Button_click("info"))
            button_About = Button(screen, button_Info.textRect.right+10, button_y4, 60, 20, text='About ->', fontSize=20, font=font_button, margin=5, radius=3,
                            inactiveColour="#0000FF", hoverColour="#0000FF", pressedColour=(0, 200, 20),
                            onClick=lambda: button_Button_click("about"))

            button_y5 = button_y4 + 30
        button_set = [button_Reset, button_Scramble, button_Undo, button_Color, button_Edit, button_Open, button_Save,
                      button_MinusX, button_PlusX, button_MinusY, button_PlusY, button_EditPyr, button_EditBlk, button_EditEmp, button_Info, button_About]

        ################################################################################
        ################################################################################
        # Основной цикл программы
        while True:
            mouse_x = mouse_y = face = 0
            pyramid_pos_x = pyramid_pos_y = -1
            undo = False

            ################################################################################
            # обработка событий
            if scramble_move == 0:
                timer.tick(10)

                events = pygame.event.get()
                for ev in events:  # Обрабатываем события
                    if (ev.type == QUIT):
                        return SystemExit, "QUIT"
                    if ev.type == MOUSEBUTTONDOWN and ev.button == 1:
                        mouse_x = ev.pos[0]
                        mouse_y = ev.pos[1]
                    if ev.type == MOUSEBUTTONDOWN and ev.button == 5:
                        BTN_CLICK = True
                        BTN_CLICK_STR = "undo"

                ################################################################################
                # обработка нажатия на кнопки
                if BTN_CLICK:
                    fl_break = True
                    if BTN_CLICK_STR=="reset":
                        fl_break = True
                    if BTN_CLICK_STR=="open":
                        fl_break = False
                        fil = read_file()
                        if fil != "":
                            fl_break = True
                            level, SIZE_Y, SIZE_X, TYPE_COLOR = fil
                            file_ext = True
                    if BTN_CLICK_STR=="save":
                        fl_break = False
                        save_file(level,TYPE_COLOR)
                    if BTN_CLICK_STR=="scramble" and not edit_mode:
                        fl_break = False
                        scramble_move = SIZE_X * SIZE_Y * 500
                    if BTN_CLICK_STR=="undo":
                        fl_break = False
                        if len(moves_stack) > 0:
                            vek,pyramid_pos_y,pyramid_pos_x = moves_stack.pop()
                            vek = (vek + 1) % 4 + 1
                            moves -= 1
                            undo = True

                    if BTN_CLICK_STR=="info":
                        webbrowser.open("https://twistypuzzles.com/forum/viewtopic.php?p=414460#p414460", new=2, autoraise=True)
                        webbrowser.open("https://twistypuzzles.com/app/museum/museum_showitem.php?pkey=9766", new=2, autoraise=True)
                        webbrowser.open("https://twistypuzzles.com/app/museum/museum_showitem.php?pkey=10961", new=2, autoraise=True)

                    if BTN_CLICK_STR == "about":
                        webbrowser.open("https://github.com/grigorusha/RollingPyramids", new=2, autoraise=True)
                        webbrowser.open("https://twistypuzzles.com/forum/viewtopic.php?t=38581", new=2, autoraise=True)
                        webbrowser.open("https://twistypuzzles.com/forum/viewtopic.php?p=417361#p417361", new=2, autoraise=True)

                    if BTN_CLICK_STR=="color":
                        fl_break = True
                        TYPE_COLOR = 3-TYPE_COLOR
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
                            button_Edit.inactiveColour = button_Edit.hoverColour = "#0000F0"
                        else:
                            edit_mode_str = ""
                            button_Edit.inactiveColour = button_Edit.hoverColour = button_EditPyr.inactiveColour = button_EditPyr.hoverColour = "#008000"
                            button_EditBlk.inactiveColour = button_EditBlk.hoverColour = button_EditEmp.inactiveColour = button_EditEmp.hoverColour = "#008000"
                    if BTN_CLICK_STR == "editpyr":
                        fl_break = False
                        if edit_mode:
                            if edit_mode_str != "pyram":
                                edit_mode_str = "pyram"
                                button_EditPyr.inactiveColour = button_EditPyr.hoverColour = "#0000F0"
                                button_EditBlk.inactiveColour = button_EditBlk.hoverColour = button_EditEmp.inactiveColour = button_EditEmp.hoverColour = "#008000"
                    elif BTN_CLICK_STR == "editblk":
                        fl_break = False
                        if edit_mode:
                            if edit_mode_str != "block":
                                edit_mode_str = "block"
                                button_EditBlk.inactiveColour = button_EditBlk.hoverColour = "#0000F0"
                                button_EditPyr.inactiveColour = button_EditPyr.hoverColour = button_EditEmp.inactiveColour = button_EditEmp.hoverColour = "#008000"
                    elif BTN_CLICK_STR == "editemp":
                        fl_break = False
                        if edit_mode:
                            if edit_mode_str != "empty":
                                edit_mode_str = "empty"
                                button_EditEmp.inactiveColour = button_EditEmp.hoverColour = "#0000F0"
                                button_EditPyr.inactiveColour = button_EditPyr.hoverColour = button_EditBlk.inactiveColour = button_EditBlk.hoverColour = "#008000"

                    if edit_mode:
                        moves_stack = []
                        moves = 0
                    else:
                        bad_state = False
                        count_empty = 0
                        for row in level:
                            for pyramid in row:
                                if (pyramid[0] == " "):
                                    count_empty += 1
                        if count_empty == 0:
                            bad_state = True

                    BTN_CLICK = False
                    BTN_CLICK_STR = ""
                    if fl_break: break

            else:
                # обработка рандома для Скрамбла
                if not bad_state:
                    while True:
                        # ищем пирамидку, которую можно повернуть
                        pyramid_pos_x = random.randint(0,SIZE_X-1)
                        pyramid_pos_y = random.randint(0,SIZE_Y-1)

                        pyramid = level[pyramid_pos_y][pyramid_pos_x]
                        if (pyramid[0] != " ") and (pyramid[0] != "X"):
                            pyram_empty = pyram_find_empty(level, pyramid_pos_y, pyramid_pos_x)
                            if len(pyram_empty)>0:
                                vek = random.randint(1,4)
                                break

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
                    try: tg11 = (HEIGHT_PYRAMID-y2)/(EDGE_PYRAMID/2-x2)
                    except: tg11 = y2

                    try: tg2 = y2/(EDGE_PYRAMID/2-x2)
                    except: tg2 = y2
                    try: tg22 = (HEIGHT_PYRAMID-y2)/x2
                    except: tg22 = y2

                    # разбор прямоугольных блоков шириной в пирамидку
                    if (yy % 2 == 0) == (xx % 2 == 0):  # 1 ряд, четные с 0 или 2 ряд, нечетные с 1
                        if tg2>TG60:
                            pyramid_pos_x = xx
                        else:
                            pyramid_pos_x = xx-1

                        orient = (pyramid_pos_y % 2 == 0) == (pyramid_pos_x % 2 == 0)  # уголок вверх
                        if tg2 < TG30 or tg22<TG30:
                            face = 1
                        elif orient:
                            face = 2
                        else:
                            face = 3
                    else: # elif (yy % 2 == 0) and (xx % 2 == 1):  # 1 ряд, нечетные с 1 или 2 ряд, четные с 0
                        if tg1>TG60:
                            pyramid_pos_x = xx-1
                        else:
                            pyramid_pos_x = xx

                        orient = (pyramid_pos_y % 2 == 0) == (pyramid_pos_x % 2 == 0)  # уголок вверх
                        if tg1<TG30 or tg11<TG30:
                            face = 1
                        elif orient:
                            face = 3
                        else:
                            face = 2

                    if pyramid_pos_x >= SIZE_X : pyramid_pos_x = -1

            ################################################################################
            ################################################################################
            # режим редактора
            if edit_mode and len(edit_mode_str)>0 and (pyramid_pos_x>=0) and (pyramid_pos_y>=0):
                if edit_mode_str=="pyram":
                    sol_pyram = solved_level[pyramid_pos_y][pyramid_pos_x]
                    level[pyramid_pos_y][pyramid_pos_x] = [sol_pyram[0],sol_pyram[1]]
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
                    pyram_empty = pyram_find_empty(level, pyramid_pos_y, pyramid_pos_x)
                    if len(pyram_empty) > 0:
                        if len(pyram_empty)==1:
                            pos = 0
                            vek = pyram_empty[0][2]
                        else:
                            vek = 0
                            for pos,epmty_pos in enumerate(pyram_empty):
                                if epmty_pos[2] == face:
                                    vek = face
                                    break

                        if vek != 0:
                            orient = (pyramid_pos_y % 2 == 0) == (pyramid_pos_x % 2 == 0) # уголок вверх
                            pyram_new = pyram_rotate(pyram, vek, orient)

                            level[pyram_empty[pos][0]][pyram_empty[pos][1]] = pyram_new
                            level[pyramid_pos_y][pyramid_pos_x] = [" "," "]

                            if not undo:
                                moves += 1
                                moves_stack.append([vek,pyram_empty[0][0],pyram_empty[0][1]])

            if scramble_move != 0:
                scramble_move -= 1
                moves_stack = []
                moves = 0
                continue
                # отрисовка не нужна

            # проверка на решенное состояние
            solved = True
            if not edit_mode:
                #TYPE_COLOR
                if len(solved_level) > 0:
                    for ny, row in enumerate(level):
                        for nx, pyramid in enumerate(row):
                            if (pyramid[0]!="X") and (pyramid[0]!=" "):
                                sol_pyram = solved_level[ny][nx]
                                if (pyramid[0]!=sol_pyram[0]) or (pyramid[1]!=sol_pyram[1]):
                                    solved = False

            ################################################################################
            ################################################################################
            # отрисовка игрового поля
            screen.fill(BACKGROUND_COLOR)
            screen.blit(textx, textx_place)
            screen.blit(texty, texty_place)
            pf = Surface((WIN_WIDTH, BORDER))
            pf.fill(Color("#B88800"))
            screen.blit(pf, (0, WIN_HEIGHT + BORDER))

            ################################################################################
            # text
            text_moves = font.render('Moves: ' + str(moves), True, PYRAMID_COLOR[2][1])
            text_moves_place = text_moves.get_rect(topleft=(10, button_y5))
            screen.blit(text_moves, text_moves_place)
            if solved:
                text_solved = font.render('Solved', True, PYRAMID_COLOR[0][1])
            else:
                text_solved = font.render('not solved', True, RED_COLOR)
            if bad_state:
                text_solved = font.render('BAD', True, RED_COLOR)
            text_solved_place = text_solved.get_rect(topleft=(text_moves_place.right + 10, button_y5))
            screen.blit(text_solved, text_solved_place)

            ############################################
            # отрисовка сетки и пирамидок
            for ny,row in enumerate(level):
                for nx,pyramid in enumerate(row):
                    orient = (ny % 2 == 0) == (nx % 2 == 0) # уголок вверх

                    ############################################
                    # расчет всех координат
                    if orient: # уголок вверх
                        fl_or = 1
                        if (ny % 2 == 0) and (nx % 2 == 0):  # 1 ряд, наверх
                            x1 = int(EDGE_PYRAMID / 2) + (nx // 2) * EDGE_PYRAMID + BORDER
                        elif (ny % 2 == 1) and (nx % 2 == 1):  # 2 ряд, наверх
                            x1 = (nx // 2 + nx % 2) * EDGE_PYRAMID + BORDER
                        y1 = ny * HEIGHT_PYRAMID + BORDER + (2 * BORDER)
                        yy = y1 + HEIGHT_PYRAMIDka
                        y1_grid = ny * HEIGHT_PYRAMID + BORDER
                        yy_grid = y1_grid + HEIGHT_PYRAMID
                    else:  # уголок вниз
                        fl_or = -1
                        if (ny % 2 == 0) and (nx % 2 == 1):  # 1 ряд, вниз
                            x1 = (nx // 2 + nx % 2) * EDGE_PYRAMID + BORDER
                        elif (ny % 2 == 1) and (nx % 2 == 0):  # 2 ряд, вниз
                            x1 = int(EDGE_PYRAMID / 2) + (nx // 2) * EDGE_PYRAMID + BORDER
                        yy = ny * HEIGHT_PYRAMID + BORDER + (BORDER)
                        y1 = yy + HEIGHT_PYRAMIDka
                        yy_grid = ny * HEIGHT_PYRAMID + BORDER
                        y1_grid = yy_grid + HEIGHT_PYRAMID

                    x2  = x1 + int(EDGE_PYRAMIDka / 2) * fl_or
                    x3  = x1 - int(EDGE_PYRAMIDka / 2) * fl_or
                    y0  = y1 + int(2 * HEIGHT_PYRAMIDka / 3) * fl_or

                    y10 = y1 + int(HEIGHT_PYRAMIDka / 3) * fl_or
                    x20 = x1 + int(EDGE_PYRAMIDka / 4) * fl_or
                    x30 = x1 - int(EDGE_PYRAMIDka / 4) * fl_or
                    yy0 = y1 + int(5 * HEIGHT_PYRAMIDka / 6) * fl_or
                    y11 = y1 + int(HEIGHT_PYRAMIDka / 2) * fl_or

                    yc  = y1 + int(8 * HEIGHT_PYRAMIDka / 9) * fl_or
                    xc2 = x1 + int(EDGE_PYRAMIDka / 6) * fl_or
                    xc3 = x1 - int(EDGE_PYRAMIDka / 6) * fl_or
                    yc2 = y1 + int(5 * HEIGHT_PYRAMIDka / 9) * fl_or

                    x2_grid  = x1 + int(EDGE_PYRAMID / 2) * fl_or
                    x3_grid  = x1 - int(EDGE_PYRAMID / 2) * fl_or

                    ############################################
                    # отрисовка сетки
                    if pyramid[0]!="X":
                        draw.line(screen, GRAY_COLOR2, [x2_grid, yy_grid], [x3_grid, yy_grid], 2)
                        draw.line(screen, GRAY_COLOR2, [x1, y1_grid], [x2_grid, yy_grid], 2)
                        draw.line(screen, GRAY_COLOR2, [x1, y1_grid], [x3_grid, yy_grid], 2)

                    # отрисовка пирамидок

                    if pyramid[0]==" ": # пустая ячейка
                        draw.polygon(screen, BACKGROUND_COLOR, [[x1, y1], [x2, yy], [x3, yy]])
                    elif pyramid[0] == "X":  # блок
                        delta = int(HEIGHT_PYRAMIDka / 5)
                        delta2 = int(delta * TG60 / 2)
                        draw.line(screen, GRAY_COLOR, [x1, y0 - delta], [x1, y0 + delta], 3)
                        draw.line(screen, GRAY_COLOR, [x1 - delta2, y0 - delta / 2], [x1 + delta2, y0 + delta / 2], 3)
                        draw.line(screen, GRAY_COLOR, [x1 - delta2, y0 + delta / 2], [x1 + delta2, y0 - delta / 2], 3)

                    else: # пирамидка
                        pyramid2 = pyram_rotate(pyramid, 0, orient)
                        for color in PYRAMID_COLOR:
                            if TYPE_COLOR == 1:
                                if pyramid[1]==color[0]: # перед
                                    draw.polygon(screen,color[1], [[x1, y0], [x2, yy], [x3, yy]] )
                                elif pyramid2[0] == color[0]: # лево
                                    draw.polygon(screen,color[1], [[x1, y0], [x1, y1], [x3, yy]] )
                                elif pyramid2[1] == color[0]: # право
                                    draw.polygon(screen,color[1], [[x1, y0], [x1, y1], [x2, yy]] )
                            else:
                                if pyramid[0]==color[0]: # верх
                                    draw.polygon(screen,color[1], [[x1, y10], [xc2, yc2], [x20, yy0], [x1, yc], [x30, yy0], [xc3, yc2]] )
                                elif pyramid[1]==color[0]: # перед
                                    draw.polygon(screen,color[1], [[x1, y1], [x20, y11], [xc2, yc2], [x1, y10], [xc3, yc2], [x30, y11]] )
                                elif pyramid2[0] == color[0]: # лево
                                    draw.polygon(screen,color[1], [[x2, yy], [x1, yy], [x1, yc], [x20, yy0], [xc2, yc2], [x20, y11]] )
                                elif pyramid2[1] == color[0]:  # право
                                    draw.polygon(screen, color[1], [[x3, yy], [x30, y11], [xc3, yc2], [x30, yy0], [x1, yc], [x1, yy]])

                            draw.aaline(screen, GRAY_COLOR, [x1, y0], [x1, y1])
                            draw.aaline(screen, GRAY_COLOR, [x1, y0], [x2, yy])
                            draw.aaline(screen, GRAY_COLOR, [x1, y0], [x3, yy])
                            draw.aaline(screen, GRAY_COLOR, [x1, y1], [x2, yy])
                            draw.aaline(screen, GRAY_COLOR, [x1, y1], [x3, yy])
                            draw.aaline(screen, GRAY_COLOR, [x3, yy], [x2, yy])

            #####################################################################################
            pygame_widgets.update(events)
            pygame.display.update()  # обновление и вывод всех изменений на экран

        # удаляем кнопки
        for btn in button_set:
            btn.hide()

main()

