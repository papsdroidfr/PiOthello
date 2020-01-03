#!/usr/bin/env python3
########################################################################
# Filename    : piOthello.py
# Description : jeux Othello sur une matrice leds bicolor 8*8 Adafruit
# auther      : papsdroid.fr
# modification: 2019/12/10
########################################################################

import time, os
from game import Game
from ledMatrixBicolor import ledMatrix
import RPi.GPIO as GPIO

class Application:
    def __init__(self):
        print('Démarrage piOthello. CTRL+C pour interrompre, ou appuyer sur le bouton Off.')
        self.off = False                                                # True: switching off the raspberry
        self.game=Game()
        self.plateau=ledMatrix()
        self.PLAYER_COLORS = {self.game.BLACK: self.plateau.RED,        # black player is: RED
                              self.game.WHITE: self.plateau.GREEN,      # white player is: GREEN
                              self.game.EMPTY: self.plateau.OFF}        # empty case: led OFF
        self.MOVE_COLOR = self.plateau.YELLOW                           # possible move: YELLOW

        #strategy setup: human or 3 level with increasing IA skills
        self.PLAYER_ITEMS = ['humain', 'IA0', 'IA1', 'IA2']
        self.PLAYERS_STRATEGY = {self.PLAYER_ITEMS[0]: self.human_strategy,              # played by human using push button
                                 self.PLAYER_ITEMS[1]: self.game.random_strategy ,       # random play
                                 self.PLAYER_ITEMS[2]: self.game.maximizer(),            # simple IA: best move without any anticipation
                                 self.PLAYER_ITEMS[3]: self.game.alphabeta_searcher(5)}  # IA brute force anticipating 5 next turns.
                
        #raspberry GPIO pin setup 
        self.ledRpin = 20                   # Red led PIN
        self.ledGpin = 21                   # Green led PIN
        GPIO.setup(self.ledRpin, GPIO.OUT)
        GPIO.setup(self.ledGpin, GPIO.OUT)
        self.pushOFFpin = 26                # push button OFF(black): switch off the Raspberry
        self.pushCHXpin = 17                # push button CHOICE(yellow): to let the user choose an item above x items
        self.pushVALpin = 12                # push button VALIDATION(green): confirm choice validation by the user
        GPIO.setup(self.pushOFFpin, GPIO.IN, pull_up_down=GPIO.PUD_UP)        # mode INPUT, pull_up=high
        GPIO.add_event_detect(self.pushOFFpin,GPIO.FALLING,callback=self.buttonOFFEvent, bouncetime=300)
        GPIO.setup(self.pushCHXpin, GPIO.IN, pull_up_down=GPIO.PUD_UP)        # mode INPUT, pull_up=high
        GPIO.add_event_detect(self.pushCHXpin,GPIO.FALLING,callback=self.buttonCHXEvent, bouncetime=300)
        GPIO.setup(self.pushVALpin, GPIO.IN, pull_up_down=GPIO.PUD_UP)        # mode INPUT, pull_up=high
        GPIO.add_event_detect(self.pushVALpin,GPIO.FALLING,callback=self.buttonVALEvent, bouncetime=500)
        self.button_CHX_pressed = False  # True if CHX button is pressed
        self.button_VAL_pressed = False  # True if VALID button is pressed
        self.waitingChoice      = False  # True: a choice above x items must be done by the user by pressing CHX button
        self.waitingValidation  = False  # True: a choice must be validated by the user by pressing VAL button


        #some static drawings specified as [[GREENS lc] [RED lc] [YELLOW lc]]
        #                                 l = line from 1 to 8, c = column from 1 to 8

        self.icon = [ [], [33,34,35,36,37,44,46,54,56,64,66,],[]]         # red pi symbol

        self.logo1_GRY  = [ [64,75],                                      # green Othello plays
                            [65,74],                                      # red Othello plays
                            [12,13,14,16,22,24,32,33,34,36,42,46,52,56] ] # PI in yellow
        
        self.logo2_GRY  = [ [75],                                         # green Othello plays
                            [54,64,65,74],                                # red Othello plays
                            [12,13,14,16,22,24,32,33,34,36,42,46,52,56] ] # PI in yellow

        self.logo3_GRY  = [ [73,74,75],                                   # green Othello plays
                            [54,64,65],                                   # red Othello plays
                            [12,13,14,16,22,24,32,33,34,36,42,46,52,56] ] # PI in yellow

        self.logo4_GRY  = [ [74,75],                                      # green Othello plays
                            [54,64,65,73,82],                             # red Othello plays
                            [12,13,14,16,22,24,32,33,34,36,42,46,52,56] ] # PI in yellow

        self.logo5_GRY  = [ [53,64,74,75],                                # green Othello plays
                            [54,65,73,82],                                # red Othello plays
                            [12,13,14,16,22,24,32,33,34,36,42,46,52,56] ] # PI in yellow

        self.logo_anim_GRY = [self.logo1_GRY, self.logo2_GRY, self.logo3_GRY, self.logo4_GRY, self.logo5_GRY]  #animated logo
        
        self.human_GRY = [ [13,14,15,16,22,27,31,38,41,48,51,53,56,58,61,64,65,68,72,77,83,84,85,86], # green smiley
                           [],             # no red
                           [33,36] ]       # yellow eyes
        
        self.IA0_GRY  = [ [11,12,13,14,15,16,17,21,27,31,37,41,47,51,53,54,57,61,67,71,72,73,74,75,76,77], # green robot, stupid face
                          [],             # no red
                          [33,35,78,88] ] # yellow eyes + yellow level bar graph
        
        self.IA1_GRY  = [ [11,12,13,14,15,16,17,21,27,31,37,41,47,51,53,54,55,57,61,67,71,72,73,74,75,76,77], # green robot more agressive face
                          [33, 35],        # red eyes
                          [58, 68,78,88] ] # yellow level bar graph

        
        self.IA2_GRY  = [ [11,12,13,14,15,16,17,21,27,31,33, 37,41,47,51,57,61,67,71,72,73,74,75,76,77],  # same green robot face
                          [53,54,55, 33, 35, 18,28,38,48,58,68,78,88], # red eyes, red mouth and red level bar graph
                          [] ]                                         # no yellow
        
        self.P1_GRY = [ [],[21,22,23,27,31,34,36,37,41,44,47,51,52,53,57,61,67,71,76,77,78],[] ]      # red P1 
        self.P2_GRY = [ [21,22,23,26,27,31,34,38,41,44,48,51,52,53,56,57,61,66,71,76,77,78], [], [] ] # green P2 
    
           
        #menu strategy choice items
        self.PLAYER_MENU = {self.PLAYER_ITEMS[0]: self.human_GRY,
                            self.PLAYER_ITEMS[1]: self.IA0_GRY,
                            self.PLAYER_ITEMS[2]: self.IA1_GRY,
                            self.PLAYER_ITEMS[3]: self.IA2_GRY }
        self.PLAYER_ICONS = {self.game.BLACK: self.P1_GRY, self.game.WHITE: self.P2_GRY}
        

    #executed when OFF is pressed
    #-----------------------------------------------------------
    def buttonOFFEvent(self,channel):
        self.off = True
        print('Extinction Raspberry...')
        time.sleep(1)
        self.plateau.off()      # switch led matrix Off
        self.switch_off_leds()  # switch off all leds
        os.system('sudo halt')        


    #executed when CHX is pressed
    #-----------------------------------------------------------
    def buttonCHXEvent(self,channel):
        if self.waitingChoice:
            self.button_CHX_pressed = True

    
    #executed when VALID is pressed
    #-----------------------------------------------------------
    def buttonVALEvent(self,channel):
        if self.waitingValidation:
            self.button_VAL_pressed = True

    #drawing a pic_GRY [ [Green lc], [Red lc], [Yellow lc] ]  l = line from 1 to 8, c=column from 1 to 8
    def draw_picGRY(self, pic_GRY):
        for lc in pic_GRY[0]:
            self.plateau.set_led_lc(lc, self.plateau.GREEN)
        for lc in pic_GRY[1]:
            self.plateau.set_led_lc(lc, self.plateau.RED)
        for lc in pic_GRY[2]:
            self.plateau.set_led_lc(lc, self.plateau.YELLOW)
                            

    #principal loop
    #-----------------------------------------------
    def loop(self):
        #draw animation start
        self.plateau.off()                 # switch off all the matrix
        for pic_GRY in self.logo_anim_GRY: #animated logo
            self.draw_picGRY(pic_GRY)  # draw one pic from animation list
            time.sleep(0.5)
        #keep on playing, until off button is pressed, or CTRL+C is pressed
        while not(self.off) :
            black, white = self.get_players()   #chose level of players above items: human, IA0, IA1, IA2, IA3
            print('black payer:', black)
            print('white player:', white)
            board, score = self.play(black, white)
            self.switch_off_leds()
            print('Final score:', score)
            print('%s wins!' % ('Black' if score > 0 else 'White'))
            self.draw_board(board)
            print(self.game.print_board(board))
            self.blink_led(self.game.BLACK if score >0 else self.game.WHITE)
            

    #destroy method
    #---------------------------------------------
    def destroy(self):
        print ('bye')
        self.plateau.off()      # switch led matrix Off
        self.switch_off_leds()  # switch off all leds

    #Play a game of Othello and return the final board and score
    #Each round consists of:
    # + Get a move from the current player.
    # + Apply it to the board.
    # + Switch players. If the game is over, get the final score.
    #------------------------------------------------------------
    def play(self, black_strategy, white_strategy):
        print('Starting a new game')
        board = self.game.initial_board()
        player = self.game.BLACK    #black player always starts
        strategy = lambda who: black_strategy if who == self.game.BLACK else white_strategy
        while player is not None and not(self.off):
            self.switch_on_led(player)
            print(self.game.print_board(board))
            self.draw_board(board)
            self.draw_all_possible_moves(player, board)
            move = self.game.get_move(strategy(player), player, board)
            print(self.game.PLAYERS[player], "plays", move)
            self.draw_move(move, player)
            self.game.make_move(move, player, board)
            player = self.game.next_player(board, player)
        return board, self.game.score(self.game.BLACK, board)    

    #get strategy players
    #-----------------------------------------
    def get_players(self):
        self.waitingChoice, self.waitingValidation = True, True
        for player in [self.game.BLACK, self.game.WHITE]:
            print('define ', player, 'strategy')
            self.switch_on_led(player)                      # swhitch on leds regards to player
            self.plateau.off()                              # switch off all the matrix
            self.draw_picGRY(self.PLAYER_ICONS[player])     # draw player icon
            time.sleep(1)                                   # waiting for 1s
            self.plateau.off()                              # switch off all the matrix
            item=0
            while not(self.button_VAL_pressed) and not self.off:            # VALID button must be pressed for each player
                self.draw_picGRY(self.PLAYER_MENU[self.PLAYER_ITEMS[item]]) # draw a strategy icon
                if self.button_CHX_pressed:
                    self.button_CHX_pressed = False
                    item+=1
                    if item == len(self.PLAYER_ITEMS):
                        item=0
                    self.plateau.off() # switch off all Matrix
                time.sleep(0.3)        # to prevent CPU from overwhelming 
            #button validation is pressed
            self.button_VAL_pressed = False
            player_strategy = self.PLAYERS_STRATEGY[self.PLAYER_ITEMS[item]]
            if player==self.game.BLACK:
                black = player_strategy
            else:
                white = player_strategy
            time.sleep(0.3)
        self.waitingChoice, self.waitingValidation = False, False
        return black, white

    #human strategy played with push button
    #-----------------------------------------------------------------
    def human_strategy (self, player, board):
        print('Your move?')
        moves = self.game.legal_moves(player, board)
        id_move = 0
        self.waitingChoice, self.waitingValidation = True, True
        while not(self.button_VAL_pressed) and not self.off:             # VALID button must be pressed
            self.plateau.set_led_lc(moves[id_move], self.plateau.YELLOW) #current possible move in yellow
            if self.button_CHX_pressed:
                self.button_CHX_pressed = False
                self.plateau.set_led_lc(moves[id_move], self.plateau.OFF) #switch off current possible move
                id_move += 1                # next move
                if id_move == len(moves):
                        id_move=0
            time.sleep(0.3)     # to prevent CPU from overwhelming
        #button validation is pressed
        self.button_VAL_pressed = False
        self.waitingChoice, self.waitingValidation = False, False
        return moves[id_move]
        

    #draw the board on the led Matrix
    #---------------------------------------------------------
    def draw_board(self, board):
        for lc in self.game.valid_squares:
            self.plateau.set_led_lc(lc, self.PLAYER_COLORS[board[lc]]) #that simple !

    #draw move chosen by a player
    #--------------------------------------------------------
    def draw_move(self, move, player):
        for n in range(3): #blinking from player color to MOVE_COLOR 3 times
            self.plateau.set_led_lc(move, self.PLAYER_COLORS[player])
            time.sleep(0.2)
            self.plateau.set_led_lc(move, self.PLAYER_COLORS[self.game.EMPTY])
            time.sleep(0.2)    

    #draw all possible moves by a player given a board
    #-------------------------------------------------
    def draw_all_possible_moves(self, player, board):
        moves = self.game.legal_moves(player, board)
        for n in range(3):
            for move in moves:
                self.plateau.set_led_lc(move, self.MOVE_COLOR)
            time.sleep(0.2)
            for move in moves:
                self.plateau.set_led_lc(move, self.PLAYER_COLORS[self.game.EMPTY])
            time.sleep(0.2)

    #switch on/off leds regards to current player
    #---------------------------------------------
    def switch_on_led(self, player):
        GPIO.output(self.ledRpin, player == self.game.BLACK and GPIO.HIGH or GPIO.LOW) 
        GPIO.output(self.ledGpin, player == self.game.WHITE and GPIO.HIGH or GPIO.LOW) 

    def switch_off_leds(self):
            GPIO.output(self.ledRpin, GPIO.LOW)  #switch off red led
            GPIO.output(self.ledGpin, GPIO.LOW)  #switch off green led

    def blink_led(self, player):
        for n in range(30):
            self.switch_on_led(player)
            time.sleep(0.1)
            self.switch_off_leds()
            time.sleep(0.1)
      
    
if __name__ == '__main__':
    appl=Application()
    try:
        appl.loop()
    except KeyboardInterrupt:  # interruption clavier CTRL-C: appel à la méthode destroy() de appl.
        appl.destroy()
