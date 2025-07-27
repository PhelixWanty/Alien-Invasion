import pygame
import random
import sys
import os

# Initialize pygame
pygame.init()
pygame.mixer.init()

# Load and play background music (.mp3)
pygame.mixer.music.load("background_music.mp3")
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)

# Screen settings
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = screen.get_size()
pygame.display.set_caption("Alien Invasion")

# Load and scale background image
background_image = pygame.image.load("background.jpg").convert()
background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)

# Fonts
FONT = pygame.font.SysFont("arial", 24)

# Sounds
shoot_sound = pygame.mixer.Sound("laser.wav")
hit_sound = pygame.mixer.Sound("explosion.wav")
life_gain_sound = pygame.mixer.Sound("life_gain.wav")
life_lost_sound = pygame.mixer.Sound("life_lost.wav")
player_death_sound = pygame.mixer.Sound("player_death.wav")
powerup_other_sound = pygame.mixer.Sound("powerup_other.wav")  # New sound for other powerups

# Game settings
FPS = 60
SPACESHIP_SPEED = 5
BULLET_SPEED = 7
ALIEN_SPEED = 1
ALIEN_DROP = 20
POWERUP_SPEED = 3
ENEMY_BULLET_SPEED = 5

# Updated sizes - doubled
BULLET_WIDTH, BULLET_HEIGHT = 8, 20
ALIEN_WIDTH, ALIEN_HEIGHT = 80, 60
SPACESHIP_WIDTH, SPACESHIP_HEIGHT = 100, 60

clock = pygame.time.Clock()

# Load heart image
heart_image = pygame.image.load("heart.png").convert_alpha()
heart_image = pygame.transform.scale(heart_image, (30, 30))

# High score file path
HIGHSCORE_FILE = "highscore.txt"

def load_highscore():
    if os.path.exists(HIGHSCORE_FILE):
        with open(HIGHSCORE_FILE, "r") as f:
            try:
                return int(f.read())
            except:
                return 0
    else:
        return 0

def save_highscore(score):
    with open(HIGHSCORE_FILE, "w") as f:
        f.write(str(score))

class Spaceship(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        image = pygame.image.load("ship.png").convert_alpha()
        self.image = pygame.transform.scale(image, (SPACESHIP_WIDTH, SPACESHIP_HEIGHT))
        self.rect = self.image.get_rect(midbottom=(WIDTH // 2, HEIGHT - 30))
        self.health = 3
        self.shield = False
        self.shield_timer = 0

    def update(self, keys):
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= SPACESHIP_SPEED
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += SPACESHIP_SPEED
        if self.shield:
            self.shield_timer -= 1
            if self.shield_timer <= 0:
                self.shield = False

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction=-1, color=(255, 0, 0)):
        super().__init__()
        self.image = pygame.Surface((BULLET_WIDTH, BULLET_HEIGHT))
        self.image.fill(color)
        self.rect = self.image.get_rect(center=(x, y))
        self.direction = direction

    def update(self):
        self.rect.y += BULLET_SPEED * self.direction
        if self.rect.bottom < 0 or self.rect.top > HEIGHT:
            self.kill()

class Alien(pygame.sprite.Sprite):
    def __init__(self, x, y, alien_type):
        super().__init__()
        self.type = alien_type
        self.points = {0: 10, 1: 20, 2: 30}[alien_type]
        image_file = {0: "alien1.png", 1: "alien2.png", 2: "alien3.png"}[alien_type]
        image = pygame.image.load(image_file).convert_alpha()
        self.image = pygame.transform.scale(image, (ALIEN_WIDTH, ALIEN_HEIGHT))
        self.rect = self.image.get_rect(topleft=(x, y))

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        image_files = [
            "powerup_star.png",
            "powerup_speed.png",
            "powerup_health.png",
            "powerup_upgrade.png",
            "powerup_shield.png"
        ]
        self.type = random.choice(image_files)
        image = pygame.image.load(self.type).convert_alpha()
        self.image = pygame.transform.scale(image, (24, 24))
        self.rect = self.image.get_rect(center=(x, y))

    def update(self):
        self.rect.y += POWERUP_SPEED
        if self.rect.top > HEIGHT:
            self.kill()

def create_alien_fleet(rows, cols):
    aliens = pygame.sprite.Group()
    for row in range(rows):
        for col in range(cols):
            x = col * (ALIEN_WIDTH + 20) + 50
            y = row * (ALIEN_HEIGHT + 20) + 50
            alien_type = random.choice([0, 1, 2])
            alien = Alien(x, y, alien_type)
            aliens.add(alien)
    return aliens

def draw_text(text, size, x, y, color=WHITE):
    font = pygame.font.SysFont("arial", size)
    label = font.render(text, True, color)
    screen.blit(label, (x, y))

def draw_hearts(health):
    for i in range(health):
        x = WIDTH - (i + 1) * 35 - 10
        y = 10
        screen.blit(heart_image, (x, y))

# 🔴 Rounded Button Drawing
def draw_button(text, x, y, width, height, inactive_color, active_color, radius=20):
    mouse_pos = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    rect = pygame.Rect(x, y, width, height)
    hovered = rect.collidepoint(mouse_pos)

    color = active_color if hovered else inactive_color
    pygame.draw.rect(screen, color, rect, border_radius=radius)

    font = pygame.font.SysFont("arial", 32, bold=True)
    label = font.render(text, True, BLACK)
    label_rect = label.get_rect(center=rect.center)
    screen.blit(label, label_rect)

    if hovered and click[0] == 1:
        return True
    return False

def draw_outlined_text(text, font_size, center_x, center_y, text_color, outline_color, outline_width=2):
    font = pygame.font.SysFont("arial", font_size, bold=True)
    base = font.render(text, True, text_color)
    outline = font.render(text, True, outline_color)
    x = center_x - base.get_width() // 2
    y = center_y - base.get_height() // 2

    for dx in range(-outline_width, outline_width + 1):
        for dy in range(-outline_width, outline_width + 1):
            if dx != 0 or dy != 0:
                screen.blit(outline, (x + dx, y + dy))
    screen.blit(base, (x, y))

def draw_text_with_shadow(text, font_size, center_x, center_y, text_color, shadow_color, shadow_offset=2, bold=True):
    font = pygame.font.SysFont("arial", font_size, bold=bold)
    shadow_label = font.render(text, True, shadow_color)
    shadow_rect = shadow_label.get_rect(center=(center_x + shadow_offset, center_y + shadow_offset))
    screen.blit(shadow_label, shadow_rect)
    text_label = font.render(text, True, text_color)
    text_rect = text_label.get_rect(center=(center_x, center_y))
    screen.blit(text_label, text_rect)

def pause_menu():
    while True:
        screen.fill(BLACK)
        center_x = WIDTH // 2
        center_y = HEIGHT // 2

        draw_outlined_text("PAUSED", 80, center_x, center_y - 150, WHITE, BLACK, outline_width=2)
        resume_clicked = draw_button("Resume", center_x - 100, center_y - 30, 200, 60, (100, 200, 100), (150, 255, 150))
        quit_clicked = draw_button("Quit", center_x - 100, center_y + 50, 200, 60, (200, 100, 100), (255, 150, 150))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        if resume_clicked:
            return
        if quit_clicked:
            pygame.quit()
            sys.exit()

def game_menu(highscore):
    while True:
        screen.blit(background_image, (0, 0))
        center_x = WIDTH // 2
        center_y = HEIGHT // 2

        draw_text_with_shadow("ALIEN INVASION", 72, center_x, center_y - 150, WHITE, BLACK, shadow_offset=3)
        draw_text_with_shadow(f"High Score: {highscore}", 36, center_x, center_y - 90, YELLOW, BLACK, shadow_offset=2)

        start_clicked = draw_button("Start Game", center_x - 100, center_y - 30, 200, 60, (100, 200, 100), (150, 255, 150))
        quit_clicked = draw_button("Quit", center_x - 100, center_y + 50, 200, 60, (200, 100, 100), (255, 150, 150))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        if start_clicked:
            return
        if quit_clicked:
            pygame.quit()
            sys.exit()

def main(level=1, highscore=0):
    spaceship = Spaceship()
    spaceship_group = pygame.sprite.GroupSingle(spaceship)

    bullets = pygame.sprite.Group()
    enemy_bullets = pygame.sprite.Group()
    aliens = create_alien_fleet(3 + level, 6 + level)
    powerups = pygame.sprite.Group()

    alien_direction = 1
    score = 0
    powerup_timer = 0
    double_bullets = False
    powerup_duration = 300

    pause_rect = pygame.Rect(10, 10, 100, 40)

    running = True
    while running:
        clock.tick(FPS)
        screen.blit(background_image, (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if pause_rect.collidepoint(event.pos):
                    pause_menu()

        keys = pygame.key.get_pressed()
        spaceship.update(keys)

        if keys[pygame.K_SPACE]:
            if len(bullets) < 5:
                shoot_sound.play()
                bullets.add(Bullet(spaceship.rect.centerx, spaceship.rect.top))
                if double_bullets:
                    bullets.add(Bullet(spaceship.rect.centerx - 10, spaceship.rect.top))
                    bullets.add(Bullet(spaceship.rect.centerx + 10, spaceship.rect.top))

        bullets.update()
        powerups.update()
        enemy_bullets.update()

        move_down = False
        for alien in aliens:
            alien.rect.x += ALIEN_SPEED * alien_direction
            if alien.rect.right >= WIDTH or alien.rect.left <= 0:
                move_down = True
            if alien.type == 2 and random.random() < 0.002:
                enemy_bullets.add(Bullet(alien.rect.centerx, alien.rect.bottom, direction=1, color=(0, 255, 255)))

        if move_down:
            alien_direction *= -1
            for alien in aliens:
                alien.rect.y += ALIEN_DROP

        collisions = pygame.sprite.groupcollide(bullets, aliens, True, True)
        for bullet, hit_aliens in collisions.items():
            for alien in hit_aliens:
                hit_sound.play()
                score += alien.points
                if random.random() < 0.1:
                    powerup = PowerUp(alien.rect.centerx, alien.rect.centery)
                    powerups.add(powerup)

        for p in powerups:
            if spaceship.rect.colliderect(p.rect):
                if "shield" in p.type:
                    spaceship.shield = True
                    spaceship.shield_timer = 600
                    powerup_other_sound.play()
                elif "health" in p.type and spaceship.health < 5:
                    spaceship.health += 1
                    life_gain_sound.play()
                else:
                    double_bullets = True
                    powerup_timer = powerup_duration
                    powerup_other_sound.play()
                p.kill()

        if double_bullets:
            powerup_timer -= 1
            if powerup_timer <= 0:
                double_bullets = False

        for bullet in enemy_bullets:
            if spaceship.rect.colliderect(bullet.rect):
                bullet.kill()
                if not spaceship.shield:
                    spaceship.health -= 1
                    if spaceship.health > 0:
                        life_lost_sound.play()
                    else:
                        player_death_sound.play()
                        if score > highscore:
                            save_highscore(score)
                            highscore = score
                        draw_text("You were destroyed! Game Over!", 48, WIDTH // 3, HEIGHT // 2, (255, 0, 0))
                        pygame.display.flip()
                        pygame.time.wait(2000)
                        return highscore

        for alien in aliens:
            if alien.rect.bottom >= HEIGHT:
                if score > highscore:
                    save_highscore(score)
                    highscore = score
                draw_text("Game Over!", 48, WIDTH // 3, HEIGHT // 2, (255, 0, 0))
                pygame.display.flip()
                pygame.time.wait(2000)
                return highscore

        if not aliens:
            score += 50
            if score > highscore:
                save_highscore(score)
                highscore = score
            draw_text("Level Cleared!", 48, WIDTH // 3, HEIGHT // 2, (0, 255, 0))
            pygame.display.flip()
            pygame.time.wait(2000)
            return main(level + 1, highscore)

        pygame.draw.rect(screen, (200, 200, 0), pause_rect)
        pause_label = pygame.font.SysFont("arial", 24).render("Pause", True, BLACK)
        pause_label_rect = pause_label.get_rect(center=pause_rect.center)
        screen.blit(pause_label, pause_label_rect)

        spaceship_group.draw(screen)
        bullets.draw(screen)
        aliens.draw(screen)
        powerups.draw(screen)
        enemy_bullets.draw(screen)

        score_text = f"Score: {score}"
        score_font = pygame.font.SysFont("arial", 24)
        score_label = score_font.render(score_text, True, WHITE)
        score_rect = score_label.get_rect(midtop=(WIDTH // 2, 10))
        screen.blit(score_label, score_rect)

        draw_hearts(spaceship.health)
        if spaceship.shield:
            draw_text("Shield: ON", 24, WIDTH - 150, 50, YELLOW)

        pygame.display.flip()

if __name__ == "__main__":
    highscore = load_highscore()
    game_menu(highscore)
    while True:
        highscore = main(highscore=highscore)
        game_menu(highscore)
