import pygame
import pygame_menu
import random

pygame.init()

# цвета

BLACK = (21, 24, 29)
BLUE = (31, 25, 76)
RED = (252, 91, 122)
WHITE = (255, 255, 255)

# картиночки

img1 = pygame.image.load('1.png')
img2 = pygame.image.load('2.png')
img3 = pygame.image.load('3.png')
img4 = pygame.image.load('4.png')

Assets = {
	1 : img1,
	2 : img2,
	3 : img3,
	4 : img4
}

# счёт

score = [0, 0, 0]

# менюшка
display_width = 300
display_height = 480
win = pygame.display.set_mode((display_width,display_height))
pygame.display.set_caption('game by Liza')
default_player_name = True

def set_player_name(name):
    global player_name
    global default_player_name
    player_name = name
    default_player_name = False

def set_default_player_name():
    global player_name
    global default_player_name
    player_name = "Guest"
    default_player_name = False 


def show_start_screen():
    start_menu = pygame_menu.Menu(width=display_width, height=display_height, title='Привета!', theme=pygame_menu.themes.THEME_BLUE)
    start_menu.add.text_input("Your Name: ", default="Guest", onchange=set_player_name)
    start_menu.add.button("Play", game_loop)
    start_menu.add.button("Quit", pygame_menu.events.EXIT)
    if default_player_name:
        set_default_player_name()
    start_menu.mainloop(win)

def replay_game(): 
    game_loop()

def show_end_screen(game_score):
    end_menu = pygame_menu.Menu(width=display_width, height=display_height, title='Game Over', theme=pygame_menu.themes.THEME_BLUE)
    end_menu.add.label("Your Score:" + str(game_score))
    end_menu.add.button("Score menu", show_score_screen)
    end_menu.add.button("Replay Game", replay_game)
    end_menu.add.button("Quit Game", pygame_menu.events.EXIT)
    end_menu.mainloop(win)
    
def show_score_screen():
    score_menu = pygame_menu.Menu(width=display_width, height=display_height, title='Score', theme=pygame_menu.themes.THEME_BLUE)
    score_menu.add.label("1:" + str(sorted(score)[-1]))
    score_menu.add.label("2:" + str(sorted(score)[-2]))
    score_menu.add.label("3:" + str(sorted(score)[-3]))
    score_menu.add.button("Replay Game", replay_game)
    score_menu.add.button("Quit Game", pygame_menu.events.EXIT)
    score_menu.mainloop(win)

# фигурочки

class Figures:

	FIGURES = {
		'Palka' : [[1, 5, 9, 13], [4, 5, 6, 7]],
        'ZigZag' : [[4, 5, 9, 10], [2, 6, 5, 9]],
        'ZigZig' : [[6, 7, 9, 10], [1, 5, 6, 10]],
        'Ugol_1' : [[1, 2, 5, 9], [0, 4, 5, 6], [1, 5, 9, 8], [4, 5, 6, 10]],
        'Ugol_2' : [[1, 2, 6, 10], [5, 6, 7, 9], [2, 6, 10, 11], [3, 5, 6, 7]],
        'Zontik' : [[1, 4, 5, 6], [1, 4, 5, 9], [4, 5, 6, 9], [1, 5, 6, 9]],
        'Kvadrat' : [[1, 2, 5, 6]]
	}

	TYPES = ['Palka', 'ZigZag', 'ZigZig', 'Ugol_1', 'Ugol_2', 'Zontik', 'Kvadrat']

	def __init__(self, x, y):
		self.x = x
		self.y = y
		self.type = random.choice(self.TYPES)
		self.shape = self.FIGURES[self.type]
		self.color = random.randint(1, 4)
		self.rotation = 0

	def image(self):
		return self.shape[self.rotation]

	def rotate(self):
		self.rotation = (self.rotation + 1) % len(self.shape)


# сама игрулька
SCREEN = WIDTH, HEIGHT = 300, 480
SIZE = 20
ROWS = (HEIGHT-120) // SIZE
COLS = WIDTH // SIZE

class Tetris:
	def __init__(self, rows, cols):
		self.rows = rows
		self.cols = cols
		self.score = 0
		self.level = 1
		self.board = [[0 for j in range(cols)] for i in range(rows)]
		self.next = None
		self.gameover = False
		self.new_figure()

	def draw_grid(self):
		for i in range(self.rows+1):
			pygame.draw.line(win, WHITE, (0, SIZE*i), (WIDTH, SIZE*i))
		for j in range(self.cols):
			pygame.draw.line(win, WHITE, (SIZE*j, 0), (SIZE*j, HEIGHT-120))

	def new_figure(self):
		if not self.next:
			self.next = Figures(5, 0)
		self.figure = self.next
		self.next = Figures(5, 0)

	def intersects(self):
		intersection = False
		for i in range(4):
			for j in range(4):
				if i * 4 + j in self.figure.image():
					if i + self.figure.y > self.rows - 1 or \
					   j + self.figure.x > self.cols - 1 or \
					   j + self.figure.x < 0 or \
					   self.board[i + self.figure.y][j + self.figure.x] > 0:
						intersection = True
		return intersection

	def remove_line(self):
		rerun = False
		for y in range(self.rows-1, 0, -1):
			is_full = True
			for x in range(0, self.cols):
				if self.board[y][x] == 0:
					is_full = False
			if is_full:
				del self.board[y]
				self.board.insert(0, [0 for i in range(self.cols)])
				self.score += 1
				if self.score % 10 == 0:
					self.level += 1
				rerun = True

		if rerun:
			self.remove_line()

	def freeze(self):
		for i in range(4):
			for j in range(4):
				if i * 4 + j in self.figure.image():
					self.board[i + self.figure.y][j + self.figure.x] = self.figure.color
		self.remove_line()
		self.new_figure()
		if self.intersects():
			self.gameover = True

	def go_space(self):
		while not self.intersects():
			self.figure.y += 1
		self.figure.y -= 1
		self.freeze()

	def go_down(self):
		self.figure.y += 1
		if self.intersects():
			self.figure.y -= 1
			self.freeze()

	def go_side(self, dx):
		self.figure.x += dx
		if self.intersects():
			self.figure.x -= dx

	def rotate(self):
		rotation = self.figure.rotation
		self.figure.rotate()
		if self.intersects():
			self.figure.rotation = rotation


		

def game_loop():
	win = pygame.display.set_mode(SCREEN, pygame.NOFRAME)

	clock = pygame.time.Clock()
	FPS = 24

	# фон
	font = pygame.font.Font('Alternity-8w7J.ttf', 50)
	font2 = pygame.font.SysFont('cursive', 25)

	running = True
	counter = 0
	move_down = False
	can_move = True

	tetris = Tetris(ROWS, COLS)
	while running:
		win.fill(BLACK)

		counter += 1
		if counter >= 10000:
			counter = 0

		if can_move:
			if counter % (FPS // (tetris.level * 2)) == 0 or move_down:
				if not tetris.gameover:
					tetris.go_down()
        
        # кнопочки всякие
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False

			if event.type == pygame.KEYDOWN:
				if can_move and not tetris.gameover:
					if event.key == pygame.K_LEFT:
						tetris.go_side(-1)

					if event.key == pygame.K_RIGHT:
						tetris.go_side(1)

					if event.key == pygame.K_UP:
						tetris.rotate()

					if event.key == pygame.K_DOWN:
						move_down = True

					if event.key == pygame.K_SPACE:
						tetris.go_space()

				if event.key == pygame.K_r:
					tetris.__init__(ROWS, COLS)

				if event.key == pygame.K_p:
					can_move = not can_move

				if event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
					running = False

			if event.type == pygame.KEYUP:
				if event.key == pygame.K_DOWN:
					move_down = False

		# отрисовочка детальки
		for x in range(ROWS):
			for y in range(COLS):
				if tetris.board[x][y] > 0:
					val = tetris.board[x][y]
					img = Assets[val]
					win.blit(img, (y*SIZE, x*SIZE))
					pygame.draw.rect(win, WHITE, (y*SIZE, x*SIZE,
										SIZE, SIZE), 1)

		if tetris.figure:
			for i in range(4):
				for j in range(4):
					if i * 4 + j in tetris.figure.image():
						img = Assets[tetris.figure.color]
						x = SIZE * (tetris.figure.x + j)
						y = SIZE * (tetris.figure.y + i)
						win.blit(img, (x, y))
						pygame.draw.rect(win, WHITE, (x, y, SIZE, SIZE), 1)

		# конец игры

		if tetris.gameover:
			score.append(tetris.score)
			running = False
			show_end_screen(tetris.score)

	    # переотрисовка

		pygame.draw.rect(win, BLUE, (0, HEIGHT-120, WIDTH, 120))
		if tetris.next:
			for i in range(4):
				for j in range(4):
					if i * 4 + j in tetris.next.image():
						img = Assets[tetris.next.color]
						x = SIZE * (tetris.next.x + j - 4)
						y = HEIGHT - 100 + SIZE * (tetris.next.y + i)
						win.blit(img, (x, y))

		scoreimg = font.render(f'{tetris.score}', True, WHITE)
		levelimg = font2.render(f'Level : {tetris.level}', True, WHITE)
		win.blit(scoreimg, (250-scoreimg.get_width()//2, HEIGHT-110))
		win.blit(levelimg, (250-levelimg.get_width()//2, HEIGHT-30))

		pygame.draw.rect(win, BLUE, (0, 0, WIDTH, HEIGHT-120), 2)
		clock.tick(FPS)
		pygame.display.update()


show_start_screen()
