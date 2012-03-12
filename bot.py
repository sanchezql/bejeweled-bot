#!/usr/bin/python2.7

# Bejeweled Bot for Facebook v.0.1 
# Author: Marco Vanotti
# License: MIT (See LICENSE file)
#
# Bot for the Bejeweled Blitz game from facebook. Top High-Score: 500k w/o bonuses
# Usage: Start a new game, put your mouse on the top left corner of the board, 
# and run the script, press enter to quit the alert
# 
# It uses autopy.screen.get_color to get the pixel color at the center of each 
# cell and then compares the distance between said color and the ones precomputed
# on this script. It fails in a lot of cases, a better approach would be to
# take the average color from a 2x2 block of pixels and compare it with our 2x2 block
# also, the precomputed colors should be a list, because there are special blocks
# that relate to the same color block but have different RGB components 
# (x2 bonuses, special block-bombs and money)
# 
# The script runs a Scan - Move each SLEEP_TIME seconds (float number). 
# Suggested value is 0.5
import autopy, sys, math, time, random

SLEEP_TIME = 0.2
CELL_WIDTH = 40
START_PIXEL_COLOR = 0x53393a
START_PIXEL_COLOR_RIGHT = 0x352016

class Colors:
    YELLOW = (254, 245, 35, "A")
    GRAY = (245, 245, 245, "G")
    GREEN = (38,187,67, "V")
    PURPLE = (235, 13, 235, "P")
    RED = (247,26,54, "R")
    ORANGE = (229,149,62, "N")
    BLUE = (13,116,235, "C")
    MONEY = (203,165,40, "M")
    OTHER = [0]

COLORS = [Colors.YELLOW, Colors.GRAY, Colors.GREEN, Colors.PURPLE, Colors.RED, Colors.ORANGE, Colors.BLUE]

class Orientation:
    RIGHT = 1
    DOWN = -2

ORIENTATIONS = [Orientation.RIGHT, Orientation.DOWN]

def initialize_board():
    board = []
    for i in range (0, 8):
        c = [0,0,0,0,0,0,0,0]
        board.append(c)

    return board

# Scans the board and get the RGB Component of each cell. 
def scan_board(board, x, y):
    y0 = y + CELL_WIDTH / 2
    x0 = x + CELL_WIDTH / 2

    screen = autopy.bitmap.capture_screen()
    for i in range (0, 8):
        for j in range (0, 8):
            r = g = b = 0
            for k in range (-2, 3):
                values = autopy.color.hex_to_rgb(screen.get_color(x0 + (j * CELL_WIDTH) + k, y0 + (i * CELL_WIDTH) + k))
                r += values[0]
                g += values[1]
                b += values[2]
            board[i][j] = get_color2((r//5, g//5, b//5 ))
             

def test_movement(x, y):
    x0 = x + CELL_WIDTH/2
    y0 = y + CELL_WIDTH / 2

    for i in range(0, 8):
        autopy.mouse.move(x0 + i * 40, y0)
        autopy.alert.alert("a")

# Basic make_move strategy, checks for all the 3-block matches available and
# chooses one randomly. 
def make_move(board, x, y):
    x0 = x + CELL_WIDTH / 2
    y0 = y + CELL_WIDTH / 2

    results = []
    for i in range(0, 8):
        for j in range (0, 8):
            for k in ORIENTATIONS:
                if (test_swap(board, i, j, k)):
                    results.append( (i, j, k))

    
    if (len(results) > 0):
        s = random.choice(results)
        i = s[0]
        j = s[1]
        k = s[2]
    else:
        i = random.choice(range(0, 7)) # As we only can swap to DOWN and RIGHT, 
        j = random.choice(range(0, 7)) # avoid the last column/row
        k = random.choice(ORIENTATIONS)

    swap_real(x0 + j * CELL_WIDTH, y0 + i * CELL_WIDTH, k)

# Swap the blocks in the real life, using autopy.mouse.click() function
def swap_real(x, y, orientation):
    autopy.mouse.move(x, y)
    autopy.mouse.click()
    if orientation == Orientation.RIGHT:
        autopy.mouse.move(x + CELL_WIDTH, y)
        autopy.mouse.click()
    elif orientation == Orientation.DOWN:
        autopy.mouse.move(x, y + CELL_WIDTH)
        autopy.mouse.click()

# Swap the blocks in our internal board
def swap(board, i, j, orientation):
    tmp = board[i][j]
    if orientation == Orientation.RIGHT:
        board[i][j] = board[i][j + 1]
        board[i][j + 1] = tmp
    elif orientation == Orientation.DOWN:
        board[i][j] = board[i + 1][j]
        board[i + 1][j] = tmp

# Try swapping the block in the desired orientation and see if there is a match
def test_swap(board, y, x, orientation):
    result = False
    if orientation == Orientation.RIGHT:
        if (x == 7):
            return False
        swap(board, y, x, orientation)
        if (is_match(board, y, x + 1) or is_match(board, y, x)):
            result = True
    elif orientation == Orientation.DOWN:
        if (y == 7):
            return False
        swap(board, y, x, orientation)
        if (is_match(board, y + 1, x) or is_match(board, y, x)):
            result = True

    swap(board, y, x, orientation)
    return result

# Tells you if it is a 3-block match in the position x, y
def is_match(board, y, x):
    color = get_color(board, y, x)

    if (y >= 0 and y < 6):
        if (color == get_color(board, y + 1, x) and color == get_color(board, y + 2, x)):
            return True
    if (y > 0 and y < 7):
        if (color == get_color(board, y - 1, x) and color == get_color(board, y + 1, x)):
            return True
    if (y > 1 and y < 8):
        if (color == get_color(board, y - 1, x) and color == get_color(board, y - 2, x)):
            return True

    if (x >= 0 and x < 6):
        if (color == get_color(board, y, x + 2) and color == get_color(board, y, x + 1)):
            return True

    if (x > 0 and x < 7):
        if (color == get_color(board, y, x - 1) and color == get_color(board, y, x + 1)):
            return True

    if (x > 1 and x < 8):
        if (color == get_color(board, y, x - 1) and color == get_color(board, y, x - 2)):
            return True

    return False


def get_color(board, y, x):
    color = board[y][x]

    result = get_color2(color)
    return result 

# To calculate the block that corresponds to a desired R G B value
# we get the shortest distance between this rgb component and the precalculated
# rgb components
def get_color2(color):
    minDist = 1000000
    minColor = 0
    for i in COLORS:
        a = math.pow(i[0] - color[0], 2)
        b = math.pow(i[1] - color[1], 2)
        c = math.pow(i[2] - color[2], 2)
        distance = math.sqrt(a + b +c)
        if (distance < minDist):
            minDist = distance
            minColor = i

    if (minColor == Colors.MONEY):
        minColor = Colors.YELLOW

    return minColor

# Try to find the leftmost top pixel from the board
# Calculating from two pixels that are next to each other 
# (START_PIXEL_COLOR and START_PIXEL_COLOR_RIGHT)
def calibrate_vertically(x, y):
    screen = autopy.bitmap.capture_screen()
    for i in range (0, 100):
        for j in range (-10, 10):
            if (hex(screen.get_color(x + j, y - i)) == hex(START_PIXEL_COLOR)):
                if (hex(screen.get_color(x + j + 1, y - i)) == hex(START_PIXEL_COLOR_RIGHT)):
                    return (x + j + 1, y - i - 1)
    return (0, 0)

def main():
    board = initialize_board()

    autopy.alert.alert("Please get your mouse on the top left corner and press ENTER")
    (xTmp, yTmp) = autopy.mouse.get_pos()
    (x, y) = calibrate_vertically(xTmp, yTmp)
    if ( (x, y) == (0, 0)):
        print ("Couldn't find initial pixel for calibrate")
        return
    else:
        print ("Found starting pixel at (%d, %d)" % (x, y))

    for i in range (1, 10000):
        scan_board(board, x, y)
        make_move(board, x, y)
        time.sleep(SLEEP_TIME)
    

# This is the standar boilerplate that calls the main() function
if __name__ == '__main__':
    main()
