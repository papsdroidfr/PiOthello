#!/usr/bin/env python3
########################################################################
# Filename    : ledMatrixBicolor.py
# Description : jeux Othello sur une matrice leds bicolor 8*8 Adafruit
# auther      : papsdroid.fr
# modification: 2019/12/18
########################################################################

import time, board, busio
from adafruit_ht16k33 import matrix

class ledMatrix:
    def __init__(self):
        self.i2c = busio.I2C(board.SCL, board.SDA)  #i2c interface
        self.bicolor = matrix.Matrix8x8x2(self.i2c) #Led bargraph class
        self.OFF = 0
        self.GREEN = 1
        self.RED = 2
        self.YELLOW = 3
        self.col_max = 8
        self.row_max = 8

    #turn off all the leds
    def off(self):
        self.bicolor.fill(self.OFF)

    #fill with color
    def fill(self, color):
        self.bicolor.fill(color)
                
    #set pixel[row, col] with color
    def set_led(self,row, col, color):
        self.bicolor[row, col] = color

    #set pixel from othello board[lc] range
    def set_led_lc(self, lc, color):
        self.bicolor[lc//10-1, lc%10-1] = color
        #self.bicolor[8-lc%10, lc//10-1] = color #45° rotation on the left

    #draw rectangle
    def draw_rec(self, lc0, lc1, color):
        for n in range( lc1%10 - lc0%10 + 1):
            self.set_led_lc(lc0+n, color)       #top line
            self.set_led_lc(lc1-n, color)       #bottom line
        for n in range( lc1//10 - lc0//10 - 1):
            self.set_led_lc(lc0+10*n+10, color) #left line
            self.set_led_lc(lc1-10*n-10, color) #rigth line

    #animation rectangle growth
    def anim_rect_growth(self, color):
        self.off()
        self.set_led_lc(11, self.RED)       #left  up pixel
        self.set_led_lc(18, self.YELLOW)    #right up pixel
        self.set_led_lc(88, self.RED)       #right bottom pixel
        self.set_led_lc(81, self.YELLOW)    #left  bottom pixel
        lc0, lc1 = 44,55        # small square in the center
        for n in range(self.col_max//2):
            self.draw_rec(lc0-11*n,lc1+11*n,color)  #draw green rect
            time.sleep(0.05)
            self.draw_rec(lc0-11*n,lc1+11*n,self.OFF)    #erase the rect

            
        
            
        
        
        
