import pygame
import os
import cv2
import random
import PySimpleGUI as pg
from cvzone import HandTrackingModule

pg.theme('SystemDefaultForReal')
layout=[[pg.Checkbox('Use only WASD', False, key='wasd_only')],
        [pg.Checkbox('Show the view of the Camera', False, key='check')],
        [pg.Text('Enter Camera ID (Default is 0): '), pg.Input(key="cam")],
        [pg.Button('Launch Game')]]

win=pg.Window('Game Settings', layout)

HEIGHT=600
WIDTH=800
pygame.init()
pygame.font.init()
pygame.mixer.init()

SCORE_FONT=pygame.font.SysFont('Cascadia Code', 40)
SCORE_FONT_ENDSCREEN=pygame.font.SysFont('Cooper', 120)
HIGHSCORE_FONT=pygame.font.SysFont('cooper', 40)

detector=HandTrackingModule.HandDetector(maxHands=1)
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
icon=pygame.image.load(os.path.join('assets', 'icon.png'))

laser_sound=pygame.mixer.Sound(os.path.join('assets', 'laser.mp3'))
laser_sound.set_volume(0.1)
pygame.mixer.music.load(os.path.join('assets', 'music.mp3'))
pygame.mixer.music.set_volume(0.2)

pygame.display.set_icon(icon)

def main():
    score_previous=0
    new_highscore=False
    game_start=True
    score=0
    GAME_OVER=False
    running=True
    send_enemy=True
    global showcam
    shoot=False
    bullets_rem=0
    bullets=[]
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

            if hands and not wasd:
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
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and bullets_rem != 0 and wasd:
                        shoot=True
            if send_enemy:
                enemy=Enemy()
                enemy.rect=pygame.Rect(WIDTH, random.choice([i for i in range(600) if i%60==0]), 25, 25)
                if score<50:
                    enemy.vel=random.choice([2, 5, 10])
                else:
                    enemy.vel=random.choice([5, 10, 15])
                enemies_list.append(enemy)
                if len(enemies_list)>=difficulty:
                    send_enemy=False
            if showcam and not wasd:
                cv2.imshow('img', img)
            if shoot and len(bullets)<5 and bullets_rem:
                bullet=pygame.Rect(player_rect.x+20, player_rect.y+17, 20, 5)
                bullets.append(bullet)
                bullets_rem-=1
                laser_sound.play()
                shoot=False
            screen.blit(bg, (0,0))
            screen.blit(player, (player_rect.x, player_rect.y))
            for b in bullets:
                b.x+=10
                pygame.draw.rect(screen, (160, 252, 36), b)
            for e in enemies_list:
                e.rect.x-=e.vel
                if e.rect.colliderect(player_rect):
                    with open('highscore', 'r') as f:
                        highscore=f.read()
                        if int(highscore)<score:
                            new_highscore=True
                    if new_highscore:
                        highscore=score
                        with open('highscore', 'w') as f:
                            f.write(str(score))
                    GAME_OVER=True
                if e.rect.x<=5 and not GAME_OVER:
                    enemies_list.remove(e)
                    send_enemy=True
                    score+=1
                for b in bullets:
                    if e.rect.colliderect(b):
                        enemies_list.remove(e)
                        bullets.remove(b)
                    if b.x>800:
                        bullets.remove(b)
                screen.blit(enemy_img, (e.rect.x, e.rect.y))
            if wasd and score%5==0 and score!=score_previous:
                bullets_rem+=1
                score_previous=score
            score_text=SCORE_FONT.render(f"Score: {score}", 1, (0, 0, 0))
            screen.blit(score_text, (660, 10))
            if wasd:
                bullets_text=SCORE_FONT.render(f"Bullets: {bullets_rem}", 1, (0, 0, 0))
                screen.blit(bullets_text, (10, 10))
        
            if GAME_OVER:
                screen.blit(go, (0, 0))
                score_text_go=SCORE_FONT_ENDSCREEN.render(f"Score: {score}", 1, (255, 0, 0))
                highscore_text=HIGHSCORE_FONT.render(f"Highscore: {highscore}", 1, (255, 100, 100))
                screen.blit(score_text_go, (250, 400))
                screen.blit(highscore_text, (255, 500))
    
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
        try:
            cam=int(values['cam'])
            cap=cv2.VideoCapture(cam)
            difficulty=8
            wasd=False
            win.close()
            main()
            break
        except:
            if values['wasd_only']==True:
                cap=cv2.VideoCapture(0)
                difficulty=15
                wasd=True
                win.close()
                main()
                break
            else:
                pg.popup_error("Please Enter a valid value(0, 1, 2) or check the Only WASD option", title='ERROR')
        