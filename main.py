
import sys
import math
import pygame
from pygame.time import Clock
from pygame import font, display, event, init, image
from pygame.locals import *
from pygame.gfxdraw import filled_circle
from socket import socket, AF_INET, SOCK_STREAM
import random

MAX_V = 7
SOCKET = 32512
SERVER_IP = '127.0.0.1'
PORT = 12345
size = width, height = 800, 600
data = []
class Player:
    volume, vx, vy, r = 0.0, 0.0, 0.0, 0.0
    screen = None
    def __init__(self, x=150, y =150, r =20, vx=0, vy=0, screen = None):
        self.x = x
        self.y = y
        self.r = r
        self.screen = screen
        self.volume = r**2 * math.pi
        self.vx, self.vy, = vx, vy

    def drawNPC(self, player):
        SMALLER = (80, 100, 80, 140)
        BIGGER = (200, 200, 240, 120)

        CURRENT_COLOR = SMALLER if player.r > self.r else BIGGER

        filled_circle(screen, self.getX(), self.getY(), self.getR(), CURRENT_COLOR)

    def drawOpponent(self, player):

        SMALLER = (200, 40, 40, 140)
        BIGGER = (200, 40, 240, 120)

        CURRENT_COLOR = SMALLER if player.r > self.r else BIGGER

        filled_circle(screen, self.getX(), self.getY(), self.getR(), CURRENT_COLOR)


    def drawPlayer(self):
        CURRENT_COLOR = (40, 180, 40, 100)

        filled_circle(screen, self.getX(), self.getY(), self.getR(), CURRENT_COLOR)

    def getX(self):
        return int(round(self.x))
    def getY(self):
        return int(round(self.y))
    def getR(self):
        return int(round(self.r))

def distance(Apos, Bpos):
    distance = 1.0 * (Apos[0] - Bpos[0])**2
    distance += (Apos[1] - Bpos[1])**2
    return distance ** 0.5

def colision(player, enemy):
    d = distance((player.x, player.y), (enemy.x, enemy.y))
    if d < player.r + enemy.r:
        if player.getR() < enemy.getR():
            diferrence = min(player.r ** 2 * math.pi - (player.r - 1)**2 * math.pi, player.volume)
            player.volume -= diferrence
            enemy.volume += diferrence
        else:
            diferrence = min(enemy.r**2 * math.pi - (enemy.r - 1)**2 * math.pi, enemy.volume)
            player.volume += diferrence
            enemy.volume -= diferrence

if __name__ == '__main__':

    if len(sys.argv) > 2:
        SERVER_IP = sys.argv[1]
        PORT = sys.argv[2]
    else:
        print("No valid arguments found, Proper arguments looks like: IP PORT")

    print("IP= " + str(SERVER_IP) + " PORT: " + str(PORT))

    SERVER_IP = "192.168.0.10"
    PORT = 16696

    init()
    random.seed(Clock())
    client_id = random.randint(1,1000)
    client_index = -1
    main_clock = Clock()
    background = image.load('a.jpg')
    myfont = font.Font("Windsong.ttf", 90)

    screen = display.set_mode(size)
    while 1:

        screen.blit(background, (0, 0))
        label = myfont.render("Wait for conection...", 1, (255,255,0))
        screen.blit(label, (300, 200))
        display.flip()

        from_server = socket(AF_INET, SOCK_STREAM)
        try:
            from_server.connect((SERVER_IP, int(float(PORT))))
        except:
            pass
        a = from_server.recv(10)
        a = a[:9]

        #invalid format: go to next phase: game
        try:
            g = float(a)
        except:
            break

        print g

        from_server.send(str(client_id) + ' ') #send your id as registration request
        if g == 12345678:  #no one registred yet
            print('Registration in progress...\n')
            client_index = 0
            continue

        if g == 12345678 - client_id:  #this client is registred now, this client is a player no 1.
            print('Get response from server (a)...\n')
            from_server.send(str(client_id) + ' ') #send your id as registration request
            continue
        if g == 12312312 and client_index == -1:  #this client is registred now, this player in no. 2
            print('Get response from server (b)...\n')
            client_index = 1
            from_server.send(str(0) + 'X')
            continue
        if g == 0:  #both client registred
            break

        from_server.close()

    while 1:#player or opponent r < 1 go to last while with result

        from_server = socket(AF_INET, SOCK_STREAM)
        try:
            from_server.connect((SERVER_IP, int(float(PORT))))
        except:
            pass
        try:
            a = from_server.recv(71*5*8).split(' ')[1:-2]
        except:
            print("Server is down. Please, try later.")

        if(a[0] == '123456789'):
            print('Reggg\n')
            continue

        g = []
        for e in a:
            try:
                g.append(float(e))
            except:
                continue

        for ev in pygame.event.get():
            if ev.type == QUIT: sys.exit()

            if ev.type == MOUSEBUTTONUP:
                message = str(str(client_id) + ' ' + str(ev.pos[0])) + ' ' + str(ev.pos[1]) + '\0'
                from_server.send(message)
        main_clock.tick(60)
        screen.blit(background, (0, 0))

        if client_index == 0:
            player = Player(g[0], g[1], g[2], g[3], g[4])
            opponent = Player(g[5], g[6], g[7], g[8], g[9])
        else:
            opponent = Player(g[0], g[1], g[2], g[3], g[4])
            player = Player(g[5], g[6], g[7], g[8], g[9])

        npc = []
        for d in range(2, len(g)/5):
            p = Player(g[5*d], g[1 + 5*d], g[2 + 5*d], g[3 + 5*d], g[4 + 5*d])
            npc += [p]

        player.drawPlayer()
        opponent.drawOpponent(player)
        for n in npc:
            n.drawNPC(player)

        display.flip()
        from_server.close()
        if player.getR() < 5 or opponent.getR() < 5:#end of game
            break
    if player.getR() > 5:
        screen.blit(background, (0, 0))
        label = myfont.render("You won!", 1, (255,255,0))
        screen.blit(label, (300, 200))
        display.flip()
    else:
        screen.blit(background, (0, 0))
        label = myfont.render("You lose!", 1, (255,255,0))
        screen.blit(label, (300, 200))
        display.flip()
    while 1:
        for ev in event.get():
            if ev.type == QUIT: sys.exit()

