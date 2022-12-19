import pygame
import os
import cv2
import random
import PySimpleGUI as pg
from cvzone import HandTrackingModule

pg.theme('SystemDefaultForReal')
layout=[[pg.Checkbox('Show the view of the Camera', False, key='check')],
        [pg.Button('Launch Game')]]

win=pg.Window('Game Settings', layout)

HEIGHT=600
WIDTH=800
pygame.init()
pygame.font.init()
pygame.mixer.init()

SCORE_FONT=pygame.font.SysFont('Cascadia Code', 40)
SCORE_FONT_ENDSCREEN=pygame.font.SysFont('Cooper', 160)

detector=HandTrackingModule.HandDetector(maxHands=1)
cap=cv2.VideoCapture(0)
showcam=False

screen=pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hand Controlled Space Wars")
clock=pygame.time.Clock()
player=pygame.image.load(os.path.join('assets', 'player.png'))
player=pygame.transform.scale(player, (40, 40))
player=pygame.transform.rotate(player, -90)

enemy_img=pygame.image.load(os.path.join('assets', 'enemy.png'))
enemy_img=pygame.transform.scale(enemy_img, (25, 25))
enemy_img=pygame.transform.rotate(enemy_img, -90)

class Enemy:
    def __init__(self):
        self.rect=0
        self.vel=0

bg=pygame.image.load(os.path.join('assets', 'bg.jpg'))
go=pygame.image.load(os.path.join('assets', 'go.jpg'))
menu=pygame.image.load(os.path.join('assets', 'menu.png'))
pygame.mixer.music.load(os.path.join('assets', 'music.mp3'))
pygame.mixer.music.set_volume(0.2)

def main():
    game_start=True
    score=0
    GAME_OVER=False
    running=True
    send_enemy=True
    global showcam
    enemies_list=[]
    player_rect=pygame.Rect(100, 100, 40, 40)
    if not pygame.mixer.music.get_busy():
        pygame.mixer.music.play()
    while running:
        clock.tick(60)
        if game_start:
            screen.blit(menu, (0, 0))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running=False
            keys_pressed=pygame.key.get_pressed()
            if keys_pressed[pygame.K_ESCAPE]:
                game_start=False
        else:
            succ, img=cap.read()
            img=cv2.resize(img, (WIDTH, HEIGHT))
            hands, img=detector.findHands(img)

            keys_pressed=pygame.key.get_pressed()

            if hands:
                player_rect.x, player_rect.y=hands[0]["center"]
            else:
                if keys_pressed[pygame.K_w] and player_rect.y>0:
                    player_rect.y-=5
                elif keys_pressed[pygame.K_s] and player_rect.y<560:
                    player_rect.y+=5
                elif keys_pressed[pygame.K_a] and player_rect.x>0:
                    player_rect.x-=5
                elif keys_pressed[pygame.K_d] and player_rect.x<760:
                    player_rect.x+=5
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running=False
            if send_enemy:
                enemy=Enemy()
                enemy.rect=pygame.Rect(WIDTH, random.choice([i for i in range(600) if i%60==0]), 25, 25)
                if score<20:
                    enemy.vel=random.choice([2, 5, 10])
                else:
                    enemy.vel=random.choice([10, 13, 15])
                enemies_list.append(enemy)
                if len(enemies_list)>=6:
                    send_enemy=False
            if showcam:
                cv2.imshow('img', img)
            screen.blit(bg, (0,0))
            screen.blit(player, (player_rect.x, player_rect.y))
            for e in enemies_list:
                e.rect.x-=e.vel
                if e.rect.colliderect(player_rect):
                    GAME_OVER=True
                if e.rect.x<=5 and not GAME_OVER:
                    enemies_list.remove(e)
                    send_enemy=True
                    score+=1
                screen.blit(enemy_img, (e.rect.x, e.rect.y))
            score_text=SCORE_FONT.render(f"Score: {score}", 1, (0, 0, 0))
            screen.blit(score_text, (660, 10))
            if GAME_OVER:
                screen.blit(go, (0, 0))
                score_text_go=SCORE_FONT_ENDSCREEN.render(f"Score: {score}", 1, (255, 0, 0))
                screen.blit(score_text_go, (190, 400))
    
        pygame.display.update()
    
    cv2.destroyAllWindows()
    pygame.quit()
    cap.release()

while True:
    event, values=win.read()
    if event==pg.WIN_CLOSED:
        win.close()
        break
    if event=='Launch Game':
        showcam=values['check']
        win.close()
        main()
        break