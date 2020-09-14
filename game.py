import pygame
import random
import os
import time
import math
pygame.font.init()

WIDTH,HEIGHT = 800,600
SCREEN = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("space invaders")


# load images
BACKGROUND = pygame.transform.scale( pygame.image.load(os.path.join( "assets","background-black.png" )), (WIDTH,HEIGHT) )
PLAYER_SHIP = pygame.image.load(os.path.join( "assets", "player_ship.png"))
ENEMY_SHIP_RED = pygame.image.load(os.path.join("assets","enemy_ship_red.png"))
ENEMY_SHIP_BLUE = pygame.image.load(os.path.join( "assets", "enemy_ship_blue.png"))
RED_LASER = pygame.image.load(os.path.join( "assets", "red_laser.png"))
BLUE_LASER = pygame.image.load(os.path.join("assets","blue_laser.png"))


class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw_laser(self, screen):
        screen.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel
    
    def off_screen(self, height):
        return not (self.y <= height and self.y >=0)

    def collision(self, obj):
        return collide(self, obj)

class Ship:
    COOLDOWN = 30

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.image = None
        self.laser_image = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw_function(self, window):
        window.blit(self.image, (self.x, self.y))
        for laser in self.lasers:
            laser.draw_laser(window)

    def move_lasers(self, vel, obj):
        self.cool_down()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 20
                if laser in self.lasers:
                    self.lasers.remove(laser)

    def cool_down(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter +=  1  

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x+20, self.y, self.laser_image)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def get_width(self):
        return self.image.get_width()

    def get_height(self):
        return self.image.get_height()
    

class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health=100)
        self.image = PLAYER_SHIP
        self.laser_image = BLUE_LASER
        self.mask = pygame.mask.from_surface(self.image)
        self.max_health = health

    def move_lasers(self,vel,objs):
        self.cool_down()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        self.lasers.remove(laser)
             

class Enemy(Ship):
    COLOR_MAP ={
                "red": (ENEMY_SHIP_RED, RED_LASER),
                "blue": (ENEMY_SHIP_BLUE, BLUE_LASER)
    }

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health=100)
        self.image, self.laser_image = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.image)
    
    def move(self, vel):
        self.y += vel

def collide(obj1, obj2):
    offset_x = int(obj2.x - obj1.x)
    offset_y = int(obj2.y - obj1.y)
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

def main():
    running = True
    FPS = 60
    main_font = pygame.font.SysFont("comicsans", 40)
    menu_font = pygame.font.SysFont("comicsans", 80)

    level = 1
    lives = 3
    enemies=[]
    enemy_number = 4
    enemy_vel = 0.7
    laser_vel = 4
    player_vel = 3.3
    lost = True

    Player_ship = Player(380,450)
    clock = pygame.time.Clock()

    

    def redraw_screen():
        SCREEN.blit( BACKGROUND, (0,0))
        lives_label = main_font.render(f"Lives: {lives}",1,(255,255,255))
        level_label = main_font.render(f"Level: {level}",1,(255,255,255))
        SCREEN.blit(level_label, (WIDTH - level_label.get_width()-10, 10))
        SCREEN.blit(lives_label, (10,10))

        Player_ship.draw_function(SCREEN)    

        for enemy in enemies:
            enemy.draw_function(SCREEN)

        if lives <= 0 or Player_ship.health <=0:
            lost_label = menu_font.render("Game Over",1,(255,255,255))
            SCREEN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, HEIGHT/2))
            lost = False
        

    
        pygame.display.update() 
   
   

    while running:
        
        redraw_screen()
                  
        
        if len(enemies) == 0:
            level += 1
            enemy_number += 2
            for i in range(enemy_number):
                enemy = Enemy(random.randrange(0, WIDTH-100), random.randrange(-1500,-100), random.choice(["red","blue"]))
                enemies.append(enemy)


        

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        if lives >= 0 or Player_ship.health >=0:
            keys = pygame.key.get_pressed()
            if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and Player_ship.x > 0:
                Player_ship.x -= player_vel
            if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and Player_ship.x + Player_ship.get_width() <= WIDTH:
                Player_ship.x += player_vel
            if (keys[pygame.K_UP] or keys[pygame.K_w]) and Player_ship.y > 0:
                Player_ship.y -= player_vel
            if (keys[pygame.K_DOWN] or keys[pygame.K_s]) and Player_ship.y + Player_ship.get_height() < HEIGHT:
                Player_ship.y += player_vel
            if (keys[pygame.K_SPACE]):
                Player_ship.shoot()
            
        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, Player_ship )
            
            if random.randrange(0,240) == 1:
                enemy.shoot()
            
            if enemy.y >= HEIGHT:
                if lives != 0:
                    lives -= 1
                    enemies.remove(enemy)
                

            

        Player_ship.move_lasers( -laser_vel, enemies)
        

        
main()