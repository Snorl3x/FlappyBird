import pygame
import random

# Initialize Pygame
pygame.init()

# Initialize clock and screen
clock = pygame.time.Clock()
fps = 60
screen_width = 864
screen_height = 936
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Flappy Bird')

# Define game variables
ground_scroll = 0
scroll_speed = 4
flying = False
game_over = False
pipe_gap = 150
pipe_frequency = 1500  # milliseconds
last_pipe = pygame.time.get_ticks() - pipe_frequency
score = 0
pass_pipe = False

# Load images
bg = pygame.image.load('/home/kali/img/bg.png')
ground_img = pygame.image.load('/home/kali/img/ground.png')

# Load custom Daydream font
font = pygame.font.Font('/home/kali/Daydream.ttf', 60)

# Define color
white = (255, 255, 255)

# Define function to draw text
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

class Bird(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        self.index = 0
        self.counter = 0
        for num in range(1, 4):
            img = pygame.image.load(f'/home/kali/img/bird{num}.png')
            self.images.append(img)
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.vel = 0

    def update(self, jumping):
        global game_over
        # Animation logic
        self.counter += 1
        flap_cooldown = 5
        if self.counter > flap_cooldown:
            self.counter = 0
            self.index += 1
            if self.index >= len(self.images):
                self.index = 0
            self.image = self.images[self.index]

        if game_over:
            # Make the bird fall with -90° rotation
            if self.rect.bottom < 768:  # Fall until hitting the ground
                self.rect.y += int(self.vel)
                self.vel += 0.5  # Gravity effect during fall
            self.image = pygame.transform.rotate(self.images[self.index], -90)
        elif flying:
            # Apply gravity and movement only when flying
            self.vel += 0.5
            if self.vel > 8:
                self.vel = 8
            if self.rect.bottom < 768:
                self.rect.y += int(self.vel)

            # Jump when spacebar is pressed
            if jumping:
                self.vel = -10

            # Rotate the bird based on its velocity
            self.image = pygame.transform.rotate(self.images[self.index], self.vel * -2)
        else:
            # Keep the bird stationary with slight rotation
            self.image = pygame.transform.rotate(self.images[self.index], 0)


class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, position):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('/home/kali/img/pipe.png')
        self.rect = self.image.get_rect()
        if position == 1:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x, y - int(pipe_gap / 2)]
        if position == -1:
            self.rect.topleft = [x, y + int(pipe_gap / 2)]

    def update(self):
        if not game_over:
            self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill()


# Create bird sprite group
bird_group = pygame.sprite.Group()
pipe_group = pygame.sprite.Group()
flappy = Bird(100, int(screen_height / 2))
bird_group.add(flappy)

# Main game loop
run = True
while run:
    clock.tick(fps)

    # Draw the background image
    screen.blit(bg, (0, 0))

    # Get key states
    keys = pygame.key.get_pressed()
    jumping = keys[pygame.K_SPACE]

    # Check if the bird hit the ground
    if flappy.rect.bottom > 768:
        game_over = True
        flying = False

    # Start or restart the game
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            if not flying and not game_over:
                flying = True
            elif game_over:
                game_over = False
                flying = False
                flappy.rect.center = [100, int(screen_height / 2)]
                flappy.vel = 0
                ground_scroll = 0
                pipe_group.empty()
                last_pipe = pygame.time.get_ticks() - pipe_frequency
                score = 0  # Reset the score to 0

    # Update and draw bird
    bird_group.update(jumping)
    bird_group.draw(screen)
              
    
    # Collision
    if pygame.sprite.groupcollide(bird_group, pipe_group, False, False) or flappy.rect.top < 0:
        game_over = True
        flying = False

    if flying and not game_over:
        # Generate new pipes
        time_now = pygame.time.get_ticks()
        if time_now - last_pipe > pipe_frequency:
            pipe_height = random.randint(-100, 100)
            btm_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, -1)
            top_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, 1)
            pipe_group.add(btm_pipe)
            pipe_group.add(top_pipe)
            last_pipe = time_now
    
    pipe_group.update()
    pipe_group.draw(screen)
    
    if len(pipe_group) > 0:
        if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left\
    	and bird_group.sprites()[0].rect.right < pipe_group.sprites()[0].rect.right\
    	and pass_pipe == False:
    	    pass_pipe = True
    if pass_pipe == True:
       if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.right:
            score += 1
            pass_pipe = False
    
    draw_text(str(score), font, white, int(screen_width / 2), 20)  

    # Draw the ground and update scroll
    screen.blit(ground_img, (ground_scroll, 768))
    if not game_over:
        ground_scroll -= scroll_speed
    if abs(ground_scroll) > 35:  # Reset ground scroll for a looping effect
        ground_scroll = 0

    # Display instructions based on the game state
    if not flying:
        font = pygame.font.Font('/home/kali/Daydream.ttf', 25)
        if not game_over:
            text = font.render('Press SPACE to Start', True, (255, 0, 0))
        else:
            text = font.render('Press SPACE to Restart', True, (255, 0, 0))
        screen.blit(text, (screen_width // 2 - text.get_width() // 2, screen_height // 2))

    pygame.display.update()

pygame.quit()
