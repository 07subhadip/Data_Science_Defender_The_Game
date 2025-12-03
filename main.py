# ==============================================================================
#  DATA SCIENCE DEFENDER: THE GAME
# ==============================================================================
#
#  Creator     : Subhadip Hensh
#  Date        : 2025-12-03
#  GitHub      : https://github.com/07subhadip
#  LinkedIn    : https://www.linkedin.com/in/subhadip-hensh/
#  License     : MIT License (Open Source)
#  
#  Description :
#  A retro-style space shooter built with Python (pygame-ce).
#  Defend the server against data viruses in this WebAssembly-powered game.
#  
#  (c) 2025 Subhadip Hensh. All rights reserved.
# ==============================================================================

import pygame
import random
import array
import math
import asyncio 
import sys

WIDTH = 800
HEIGHT = 600
FPS = 60

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
NEON_GREEN = (57, 255, 20)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 100, 255)
DARK_GREY = (40, 40, 40)
CYAN = (0, 255, 255)

pygame.init()
pygame.mixer.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Data Science Defender | By Subhadip Hensh")
clock = pygame.time.Clock()

font_small = pygame.font.SysFont("monospace", 24)
font_mid = pygame.font.SysFont("monospace", 36, bold=True)
font_big = pygame.font.SysFont("monospace", 50, bold=True)

def generate_laser_sound():
    sample_rate = 44100
    duration = 0.15
    n_samples = int(sample_rate * duration)
    buf = array.array('h')
    for i in range(n_samples):
        t = float(i) / sample_rate
        freq = 1000 - (t / duration) * 800
        val = int(32767 * 0.5 * math.sin(2 * math.pi * freq * t))
        buf.append(val)
    return pygame.mixer.Sound(buffer=buf)

def generate_explosion_sound():
    sample_rate = 44100
    duration = 0.3
    n_samples = int(sample_rate * duration)
    buf = array.array('h')
    for i in range(n_samples):
        decay = 1.0 - (i / n_samples)
        val = int(random.uniform(-1, 1) * 32767 * 0.5 * decay)
        buf.append(val)
    return pygame.mixer.Sound(buffer=buf)

laser_snd = generate_laser_sound()
explosion_snd = generate_explosion_sound()
laser_snd.set_volume(0.3)
explosion_snd.set_volume(0.3)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 40))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        points = [(25, 0), (50, 40), (0, 40)]
        pygame.draw.polygon(self.image, NEON_GREEN, points)
        pygame.draw.circle(self.image, BLUE, (25, 25), 5)
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.centerx = WIDTH // 2
        self.rect.bottom = HEIGHT - 10
        self.speed_x = 0

    def update(self):
        self.speed_x = 0
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_LEFT]:
            self.speed_x = -8
        if keystate[pygame.K_RIGHT]:
            self.speed_x = 8
        self.rect.x += self.speed_x
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0

    def shoot(self):
        bullet = Bullet(self.rect.centerx, self.rect.top)
        all_sprites.add(bullet)
        bullets.add(bullet)
        laser_snd.play()

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.size = 45
        self.image = pygame.Surface((self.size, self.size))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        radius = self.size // 2
        pygame.draw.line(self.image, RED, (0, 0), (self.size, self.size), 4)
        pygame.draw.line(self.image, RED, (0, self.size), (self.size, 0), 4)
        pygame.draw.line(self.image, RED, (radius, 0), (radius, self.size), 4)
        pygame.draw.line(self.image, RED, (0, radius), (self.size, radius), 4)
        pygame.draw.circle(self.image, (200, 0, 0), (radius, radius), radius - 8)
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speed_y = random.randrange(2, 5)
        self.speed_x = random.randrange(-2, 2)

    def update(self):
        self.rect.y += self.speed_y
        self.rect.x += self.speed_x
        if self.rect.top > HEIGHT + 10 or self.rect.left < -50 or self.rect.right > WIDTH + 50:
            self.rect.x = random.randrange(WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speed_y = random.randrange(2, 5)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((10, 20))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speed_y = -10
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.bottom < 0:
            self.kill()

def draw_text(surf, text, font_obj, color, x, y):
    text_surface = font_obj.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)

def reset_game():
    all_sprites.empty()
    mobs.empty()
    bullets.empty()
    player_new = Player()
    all_sprites.add(player_new)
    for i in range(8):
        m = Enemy()
        all_sprites.add(m)
        mobs.add(m)
    return player_new, 0

all_sprites = pygame.sprite.Group()
mobs = pygame.sprite.Group()
bullets = pygame.sprite.Group()

async def main():
    player, score = reset_game()
    running = True
    game_state = 'WAITING'
    print("Game Engine Started...")

    while running:
        clock.tick(FPS)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

            if game_state == 'WAITING':
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        game_state = 'RUNNING'
                    elif event.key == pygame.K_q:
                        running = False
                    
            elif game_state == 'RUNNING':
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        player.shoot()
                        
            elif game_state == 'GAME_OVER':
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        player, score = reset_game()
                        game_state = 'RUNNING'
                    elif event.key == pygame.K_q:
                        running = False

        screen.fill(BLACK)
        
        if game_state == 'WAITING':
            draw_text(screen, "DATA SCIENCE DEFENDER", font_big, CYAN, WIDTH // 2, HEIGHT // 4)
            draw_text(screen, "By Subhadip Hensh", font_small, NEON_GREEN, WIDTH // 2, HEIGHT // 4 + 80)
            
            draw_text(screen, "Instructions:", font_mid, WHITE, WIDTH // 2, HEIGHT // 2 - 30)
            draw_text(screen, "Arrow Keys -> Move", font_small, WHITE, WIDTH // 2, HEIGHT // 2 + 20)
            draw_text(screen, "Spacebar   -> Shoot", font_small, WHITE, WIDTH // 2, HEIGHT // 2 + 50)
            draw_text(screen, "Shoot the Red Viruses!", font_small, RED, WIDTH // 2, HEIGHT // 2 + 80)
            draw_text(screen, "Press SPACE To Start", font_mid, NEON_GREEN, WIDTH // 2, HEIGHT * 3/4)
            draw_text(screen, "[Press Q or ESC to Quit]", font_small, DARK_GREY, WIDTH // 2, HEIGHT - 30)

        elif game_state == 'RUNNING':
            all_sprites.update()
            
            hits = pygame.sprite.groupcollide(mobs, bullets, True, True)
            for hit in hits:
                score += 10
                explosion_snd.play()
                m = Enemy()
                all_sprites.add(m)
                mobs.add(m)
                
            hits = pygame.sprite.spritecollide(player, mobs, False, pygame.sprite.collide_mask)
            if hits:
                explosion_snd.play()
                game_state = 'GAME_OVER'

            for x in range(0, WIDTH, 50):
                pygame.draw.line(screen, DARK_GREY, (x, 0), (x, HEIGHT))
            for y in range(0, HEIGHT, 50):
                pygame.draw.line(screen, DARK_GREY, (0, y), (WIDTH, y))
                
            all_sprites.draw(screen)
            draw_text(screen, f"Score: {score}", font_small, WHITE, WIDTH // 2, 10)

        elif game_state == 'GAME_OVER':
            draw_text(screen, "GAME OVER", font_big, RED, WIDTH // 2, HEIGHT // 4)
            draw_text(screen, f"Final Score: {score}", font_mid, WHITE, WIDTH // 2, HEIGHT // 2)
            draw_text(screen, "Press 'R' to Restart", font_small, WHITE, WIDTH // 2, HEIGHT * 3/4)
            draw_text(screen, "Press 'Q' or 'ESC' to Quit", font_small, WHITE, WIDTH // 2, HEIGHT * 3/4 + 40)

        pygame.display.flip()
        
        await asyncio.sleep(0)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    asyncio.run(main())