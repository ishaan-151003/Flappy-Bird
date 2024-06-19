import pygame
import random
import os
import neat
import visualize

pygame.font.init()
pygame.display.init()

WIN_WIDTH = 600
WIN_HEIGHT = 800
FLOOR = 730
STAT_FONT = pygame.font.SysFont("comicsans", 50)
END_FONT = pygame.font.SysFont("comicsans", 70)
DRAW_LINES = False

WIN = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pygame.display.set_caption("Flappy Bird")

pipe_img = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe.png")).convert_alpha())
bg_img = pygame.transform.scale(pygame.image.load(os.path.join("imgs", "bg.png")).convert_alpha(), (600, 900))
bird_images = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", f"bird{x}.png"))) for x in range(1, 4)]
base_img = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")).convert_alpha())

gen = 0

class Bird:
    MAX_ROTATION = 25
    IMGS = bird_images
    ROT_VEL = 20
    ANIMATION_TIME = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tilt = 0
        self.tick_count = 0
        self.vel = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMGS[0]

    def jump(self):
        self.vel = -10.5
        self.tick_count = 0
        self.height = self.y

    def move(self):
        self.tick_count += 1
        displacement = self.vel * self.tick_count + 0.5 * 3 * self.tick_count ** 2
        if displacement >= 16:
            displacement = (displacement / abs(displacement)) * 16
        if displacement < 0:
            displacement -= 2
        self.y += displacement
        if displacement < 0 or self.y < self.height + 50:
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL

    def draw(self, win):
        self.img_count += 1
        if self.img_count <= self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count <= self.ANIMATION_TIME * 2:
            self.img = self.IMGS[1]
        elif self.img_count <= self.ANIMATION_TIME * 3:
            self.img = self.IMGS[2]
        elif self.img_count <= self.ANIMATION_TIME * 4:
            self.img = self.IMGS[1]
        elif self.img_count == self.ANIMATION_TIME * 4 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0
        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME * 2
        blit_rotate_center(win, self.img, (self.x, self.y), self.tilt)

    def get_mask(self):
        return pygame.mask.from_surface(self.img)

class Pipe:
    GAP = 200
    VEL = 5

    def __init__(self, x):
        self.x = x
        self.height = 0
        self.top = 0
        self.bottom = 0
        self.PIPE_TOP = pygame.transform.flip(pipe_img, False, True)
        self.PIPE_BOTTOM = pipe_img
        self.passed = False
        self.set_height()

    def set_height(self):
        self.height = random.randrange(50, 450)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    def move(self):
        self.x -= self.VEL

    def draw(self, win):
        win.blit(self.PIPE_TOP, (self.x, self.top))
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    def collide(self, bird):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)
        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))
        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        t_point = bird_mask.overlap(top_mask, top_offset)
        if b_point or t_point:
            return True
        return False

class Base:
    VEL = 5
    WIDTH = base_img.get_width()
    IMG = base_img

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL
        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win):
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))

def blit_rotate_center(surf, image, topleft, angle):
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center=image.get_rect(topleft=topleft).center)
    surf.blit(rotated_image, new_rect.topleft)

def draw_window(win, birds, pipes, base, score, gen, pipe_ind):
    if gen == 0:
        gen = 1
    win.blit(bg_img, (0, 0))
    for pipe in pipes:
        pipe.draw(win)
    base.draw(win)
    for bird in birds:
        if DRAW_LINES:
            try:
                pygame.draw.line(win, (255, 0, 0), (bird.x + bird.img.get_width() / 2, bird.y + bird.img.get_height() / 2),
                                 (pipes[pipe_ind].x + pipes[pipe_ind].PIPE_TOP.get_width() / 2, pipes[pipe_ind].height), 5)
                pygame.draw.line(win, (255, 0, 0), (bird.x + bird.img.get_width() / 2, bird.y + bird.img.get_height() / 2),
                                 (pipes[pipe_ind].x + pipes[pipe_ind].PIPE_BOTTOM.get_width() / 2, pipes[pipe_ind].bottom), 5)
            except:
                pass
        bird.draw(win)

    score_label = STAT_FONT.render("Score: " + str(score), 1, (255, 255, 255))
    win.blit(score_label, (WIN_WIDTH - score_label.get_width() - 15, 10))
    gens_label = STAT_FONT.render("Gens: " + str(gen - 1), 1, (255, 255, 255))
    win.blit(gens_label, (10, 10))
    alive_label = STAT_FONT.render("Alive: " + str(len(birds)), 1, (255, 255, 255))
    win.blit(alive_label, (10, 50))
    pygame.display.update()

def draw_menu(win):
    win.blit(bg_img, (0, 0))
    title_label = END_FONT.render("Flappy Bird", 1, (255, 255, 255))
    play_label = STAT_FONT.render("Press 1 to Play", 1, (255, 255, 255))
    ai_label = STAT_FONT.render("Press 2 for AI", 1, (255, 255, 255))

    win.blit(title_label, (WIN_WIDTH // 2 - title_label.get_width() // 2, 200))
    win.blit(play_label, (WIN_WIDTH // 2 - play_label.get_width() // 2, 400))
    win.blit(ai_label, (WIN_WIDTH // 2 - ai_label.get_width() // 2, 500))

    pygame.display.update()

def draw_pause_menu(win):
    pause_label = END_FONT.render("Paused", 1, (255, 255, 255))
    resume_label = STAT_FONT.render("Press R to Resume", 1, (255, 255, 255))
    menu_label = STAT_FONT.render("Press M for Main Menu", 1, (255, 255, 255))

    win.blit(pause_label, (WIN_WIDTH // 2 - pause_label.get_width() // 2, 300))
    win.blit(resume_label, (WIN_WIDTH // 2 - resume_label.get_width() // 2, 400))
    win.blit(menu_label, (WIN_WIDTH // 2 - menu_label.get_width() // 2, 500))

    pygame.display.update()

def main_menu():
    run = True
    while run:
        draw_menu(WIN)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    run_game()
                elif event.key == pygame.K_2:
                    config_path = os.path.join(os.path.dirname(__file__), 'config-feedforward.txt')
                    run_ai(config_path)
    pygame.quit()
    quit()

def run_game():
    bird = Bird(230, 350)
    base = Base(FLOOR)
    pipes = [Pipe(700)]
    score = 0

    clock = pygame.time.Clock()
    run = True
    paused = False

    while run:
        if not paused:
            clock.tick(30)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        bird.jump()
                    if event.key == pygame.K_ESCAPE:
                        paused = True

            bird.move()
            add_pipe = False
            rem = []
            for pipe in pipes:
                pipe.move()
                if pipe.collide(bird):
                    run = False

                if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                    rem.append(pipe)

                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True
                    add_pipe = True

            if add_pipe:
                score += 1
                pipes.append(Pipe(WIN_WIDTH))

            for r in rem:
                pipes.remove(r)

            if bird.y + bird.img.get_height() - 10 >= FLOOR or bird.y < -50:
                run = False

            base.move()
            draw_window(WIN, [bird], pipes, base, score, gen, 0)
        else:
            draw_pause_menu(WIN)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        paused = False
                    if event.key == pygame.K_m:
                        main_menu()

    main_menu()

def eval_genomes(genomes, config):
    global WIN, gen
    win = WIN
    gen += 1

    birds = []
    nets = []
    ge = []

    for genome_id, genome in genomes:
        genome.fitness = 0
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        birds.append(Bird(230, 350))
        ge.append(genome)

    base = Base(FLOOR)
    pipes = [Pipe(700)]
    score = 0
    clock = pygame.time.Clock()
    run = True
    paused = False

    while run and len(birds) > 0:
        if not paused:
            clock.tick(30)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        paused = True

            pipe_ind = 0
            if len(birds) > 0:
                if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
                    pipe_ind = 1

            for x, bird in enumerate(birds):
                bird.move()
                ge[x].fitness += 0.1

                output = nets[birds.index(bird)].activate((bird.y, abs(bird.y - pipes[pipe_ind].height),
                                                           abs(bird.y - pipes[pipe_ind].bottom)))

                if output[0] > 0.5:
                    bird.jump()

            add_pipe = False
            rem = []
            for pipe in pipes:
                pipe.move()
                for bird in birds:
                    if pipe.collide(bird):
                        ge[birds.index(bird)].fitness -= 1
                        nets.pop(birds.index(bird))
                        ge.pop(birds.index(bird))
                        birds.pop(birds.index(bird))
                if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                    rem.append(pipe)
                if not pipe.passed and pipe.x < birds[0].x:
                    pipe.passed = True
                    add_pipe = True

            if add_pipe:
                score += 1
                for genome in ge:
                    genome.fitness += 5
                pipes.append(Pipe(WIN_WIDTH))

            for r in rem:
                pipes.remove(r)

            for bird in birds:
                if bird.y + bird.img.get_height() - 10 >= FLOOR or bird.y < -50:
                    nets.pop(birds.index(bird))
                    ge.pop(birds.index(bird))
                    birds.pop(birds.index(bird))

            base.move()
            draw_window(WIN, birds, pipes, base, score, gen, pipe_ind)
        else:
            draw_pause_menu(WIN)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        paused = False
                    if event.key == pygame.K_m:
                        main_menu()

def run_ai(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)

    p = neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    p.add_reporter(neat.Checkpointer(5))

    winner = p.run(eval_genomes, 50)

    visualize.draw_net(config, winner, True)
    visualize.plot_stats(stats, ylog=False, view=True)
    visualize.plot_species(stats, view=True)

if __name__ == "__main__":
    main_menu()
