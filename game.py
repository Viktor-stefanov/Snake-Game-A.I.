import pygame
import random
import sys
import os
from pathfinding import find_path

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SNAKE_RED = (207, 4, 4)
SNACK_GREEN = (73, 235, 52)
HOVER_COLOR = (227, 255, 196)
CHOSEN_COLOR = (255, 0, 0)


class Game:
    def __init__(self):
        pygame.init()
        self.fps = 10
        self.surface = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.screen_w = self.surface.get_width()
        self.screen_h = self.surface.get_height()
        self.big_font = pygame.font.SysFont("ComicSansMS", 70)
        self.medium_font = pygame.font.SysFont("ComicSansMS", 55)
        self.small_font = pygame.font.SysFont("ComicSansMS", 25)
        self.grid_size = None
        self.generation = 0
        self.main_menu()

    def terminate_event_check(self, event):
        if event.type == pygame.QUIT:
            pygame.quit(), sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_q, pygame.K_ESCAPE):
                pygame.quit(), sys.exit()

    def pause(self):
        flag = True
        while flag:
            for event in pygame.event.get():
                self.terminate_event_check(event)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        flag = False

    def player_event_loop(self, snake):
        for event in pygame.event.get():
            self.terminate_event_check(event)
            if event.type == pygame.QUIT:
                pygame.quit(), sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_q, pygame.K_ESCAPE):
                    pygame.quit(), sys.exit()
                if event.key == pygame.K_RIGHT:
                    snake.direction = (1, 0)
                elif event.key == pygame.K_LEFT:
                    snake.direction = (-1, 0)
                elif event.key == pygame.K_UP:
                    snake.direction = (0, 1)
                elif event.key == pygame.K_DOWN:
                    snake.direction = (0, -1)
                elif event.key == pygame.K_m:
                    self.main_menu()
                elif event.key == pygame.K_p:
                    self.pause()

    def ai_event_loop(self): # think about what input values are you going to give ( distance from snake to snack, distance from head to tail? )
        for event in pygame.event.get():
            self.terminate_event_check(event)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m:
                    self.main_menu()
                elif event.key == pygame.K_RETURN:
                    return 20
                elif event.key == pygame.K_t:
                    return 1

    def menu_event_loop(self):
        enter, mouse_pos = None, None
        for event in pygame.event.get():
            self.terminate_event_check(event)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    enter = True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == pygame.BUTTON_LEFT:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    mouse_pos = (mouse_x, mouse_y)
        return mouse_pos, enter

    def player_game(self):
        self.screen = GameScreen(self.screen_w, self.screen_h, self.grid_size[0], self.grid_size[1])
        rows, columns = self.grid_size[0], self.grid_size[1]
        sw, sh = self.screen.square_width, self.screen.square_height

        snake = Snake(10, 10, rows, columns, sw, sh)
        snack = Snack(rows, columns, sw, sh, snake.body)
        while True:
            pause = True
            self.surface.fill(BLACK)
            pygame.time.delay(115)
            ret = self.player_event_loop(snake)
            if ret is True:
                pause = not pause

            if pause is False:
                # move the snake and check if it 'ate' (collides with) a snack if so add a part to the snake and generate a new snack
                snake.move()
                if (snake.body[0][0], snake.body[0][1]) == (snack.x_square, snack.y_square):
                    snake.add_part()
                    snack.generate_snack(snake.body)

                # check for snake collision with itself
                # snake.hits_self()
                if snake.hits_self():
                    self.main_menu()

                # redraw all the objects on the screen (snake, snack, grid) and update the display
                snake.draw(self.surface)
                snack.draw(self.surface)
                self.screen.draw(self.surface)
                pygame.display.update()

    def ai_game(self):
        rows, columns = self.grid_size[0], self.grid_size[1]
        self.screen = GameScreen(self.screen_w, self.screen_h, rows, columns)
        sw, sh = self.screen.square_width, self.screen.square_height

        snake = Snake(rows // 2, columns // 2, rows, columns, sw, sh)
        snack = Snack(rows, columns, sw, sh, snake.body)
        path = find_path((snack.x_square, snack.y_square), rows, columns, snake.body)
        path_index = 1

        delay = 20
        while True:
            self.surface.fill(BLACK)
            pygame.time.delay(delay)
            ret = self.ai_event_loop()
            if ret is not None:
                delay = 20 * ret

            if path is not None and path_index >= len(path):
                path = find_path((snack.x_square, snack.y_square), rows, columns, snake.body)
                path_index = 1

            if path is not None:
                next_move = path[path_index]
                if isinstance(next_move, int):
                    print(path)

            if snake.body[0][0] - next_move[0] == 1:
                snake.direction = (-1, 0)
            elif snake.body[0][0] - next_move[0] == -1:
                snake.direction = (1, 0)
            elif snake.body[0][1] - next_move[1] == 1:
                snake.direction = (0, 1)
            elif snake.body[0][1] - next_move[1] == -1:
                snake.direction = (0, -1)
            elif snake.body[0][0] == rows-1 and next_move[0] == 0: # if the snake is at the edge and the next position is at the other edge
                snake.direction = (1, 0)         # change the direction to make the snake appear at the other side of the screen
            elif snake.body[0][0] == 0 and next_move[0] == rows-1:
                snake.direction = (-1, 0)
            elif snake.body[0][1] == columns-1 and next_move[1] == 0:
                snake.direction = (0, -1)
            elif snake.body[0][1] == 0 and next_move[1] == columns-1:
                snake.direction = (0, 1)
            path_index += 1

            snake.move()
            if (snake.body[0][0], snake.body[0][1]) == (snack.x_square, snack.y_square):
                snake.add_part()
                snack.generate_snack(snake.body)

            snake.draw(self.surface)
            snack.draw(self.surface)
            self.screen.draw(self.surface)
            pygame.display.update()

    def show_text(self, surface, text, pos, font, color):
        render_object = font.render(text, False, color)
        return surface.blit(render_object, pos)

    def main_menu(self):
        hovered_check = [] # list to check for overlap between mouse position and text on the screen
        colors = [WHITE] * 5 # colors list - hovered, chosen, normal state
        # create variables to hold the text and it's position on the screen
        header = ("Snake Game & A.I.", (self.screen_w * 0.3, self.screen_h * 0.08))
        author = ("by Viktor Stefanov", (self.screen_w * 0.5, self.screen_h * 0.16))
        grid_size_text = ("Choose your grid size:", (self.screen_w * 0.31, self.screen_h * 0.5))
        small_grid = ("SMALL", (self.screen_w * 0.32, self.screen_h * 0.6))
        medium_grid = ("MEDIUM", (self.screen_w * 0.427, self.screen_h * 0.6))
        large_grid = ("LARGE", (self.screen_w * 0.555, self.screen_h * 0.6))
        play_game = ("Play Game", (self.screen_w * 0.2, self.screen_h * 0.3))
        ai_play_game = ("Watch A.I. Play", (self.screen_w * 0.6, self.screen_h * 0.3))
        # iterate over the grid size options and the game options and add their rect objects to the hovered check list.
        # We do this outside the main loop because I append the rects to a list, and I don't want to clear that list and append anew every iteration of the mainloop
        for text, pos in (small_grid, medium_grid, large_grid):
            rect = self.show_text(self.surface, text, pos, self.small_font, WHITE)
            hovered_check.append(rect)
        for text, pos in (play_game, ai_play_game):
            rect = self.show_text(self.surface, text, pos, self.medium_font, WHITE)
            hovered_check.append(rect)

        while True:
            self.surface.fill(BLACK)
            click, enter = self.menu_event_loop() # check for click events inside the event loop with the click_pos argument

            # blit the text on the screen using the show_text method
            self.show_text(self.surface, header[0], header[1], self.big_font, WHITE)
            self.show_text(self.surface, author[0], author[1], self.small_font, WHITE)
            self.show_text(self.surface, grid_size_text[0], grid_size_text[1], self.medium_font, WHITE)
            self.show_text(self.surface, play_game[0], play_game[1], self.medium_font, colors[3])
            self.show_text(self.surface, ai_play_game[0], ai_play_game[1], self.medium_font, colors[4])
            for (small_text, position), color in zip((small_grid, medium_grid, large_grid), colors): # use a for loop to spare a few lines of code
                self.show_text(self.surface, small_text, position, self.small_font, color)

            # check if the user has pressed ENTER if so begin the actual game if possible
            if enter is not None:
                chosen_game = [1 for color in colors if color == CHOSEN_COLOR]
                if len(chosen_game) == 2: # if the user chose the grid size AND the game mode
                    chosen_game_mode = colors[3:].index(CHOSEN_COLOR)
                    chosen_grid_size = colors[:3].index(CHOSEN_COLOR)
                    self.grid_size = (15, 15) if chosen_grid_size == 0 else (25, 25) if chosen_grid_size == 1 else (40, 40)
                    if chosen_game_mode == 0: # Single player self.snake game
                        self.player_game()
                    else: # A.I. game mode chosen
                        self.ai_game()

            # check for clicks on the screen and if there are any check for overlap of the click and the clickable text
            if click is not None:
                mouse_x, mouse_y = click[0], click[1] # get the mouse position
                click = [rect.collidepoint(mouse_x, mouse_y) for rect in hovered_check] # hovered_check[3:] is just the game mode text (AI, or player controlled)
                # click_index is the index of the rectangle that was clicked on IF the user clicked on a clickable text otherwise it is set to -1, so if the user clicks anywhere else the chosen text will be unchosen
                click_index = click.index(1) if 1 in click else -1
                if 0 <= click_index < 3:
                    for index in range(3):
                        colors[index] = CHOSEN_COLOR if index == click_index else WHITE
                if 3 <= click_index < 5:
                    for index in range(3, 5):
                        colors[index] = CHOSEN_COLOR if index == click_index else WHITE

            # get the mouse position and check if it overlaps with ANY text. If the text the hover color
            mouse_x, mouse_y = pygame.mouse.get_pos()
            hovers = [rect.collidepoint(mouse_x, mouse_y) for rect in hovered_check]
            for index in range(len(hovers)):
                if hovers[index] == 1 and colors[index] != CHOSEN_COLOR: # the and statement is here as to not give a chose text the hover effect
                    colors[index] = HOVER_COLOR
                elif hovers[index] == 0 and colors[index] != CHOSEN_COLOR:
                    colors[index] = WHITE

            pygame.display.update()


class GameScreen:
    def __init__(self, width, height, rows, columns):
        self.width = width
        self.height = height
        self.rows = rows
        self.columns = columns # if you want perfect squares multiply the number of columns by the width/height ratio of your monitor
        self.square_height = self.height / self.rows - (1 / 1000)
        self.square_width = self.width / self.columns - (1 / 1000) # the (1 / 1000) constant adds the last row and column I don't know why

    def draw(self, surface):
        for column in range(self.columns+1):
            pygame.draw.line(surface, WHITE, (self.square_width * column, 0),
                             (self.square_width * column, self.height), 1)
        for row in range(self.rows + 1):
            pygame.draw.line(surface, WHITE, (0, self.square_height * row), (self.width, self.square_height * row), 1)


class Snake:
    body = []
    def __init__(self, x, y, rows, cols, sw, sh):
        self.x_square = x
        self.y_square = y
        self.rows = rows
        self.columns = cols
        self.square_w = sw
        self.square_h = sh
        self.direction = (1, 0) # represent direction by (x, y) pairs. X - horizontal direction, Y - vertical direction. At all times one of the 2 is going to be 0
        self.body = self.body + [[x, y, self.direction]] # append the head of the snake to the body list

    def move(self):
        self.body[0][2] = self.direction # if there is a change in the direction apply it to the head.
        for index, part in zip(range(len(self.body)-1, -1, -1), reversed(self.body)):
            part[0] += part[2][0]
            part[1] -= part[2][1]
            if index - 1 >= 0:
                self.body[index][2] = self.body[index-1][2]
            # check if snake is out of the terrain if so make it appear out of the other side
            if part[0] >= self.rows:
                part[0] = 0
            elif part[0] < 0:
                part[0] = self.rows-1
            if part[1] >= self.columns:
                part[1] = 0
            elif part[1] < 0:
                part[1] = self.columns-1

    def hits_self(self):
        collision_list = [1 if (self.body[0][0], self.body[0][1]) == (part[0], part[1]) else 0 for part in self.body[1:]]
        if 1 in collision_list:
            # collision_index = collision_list.index(1)
            # self.body = self.body[:collision_index]
            return True

    def add_part(self):
        last_part = self.body[-1]
        if last_part[2] == (1, 0): # if going to the right append to the left of the body
            self.body.append([last_part[0] - 1, last_part[1], last_part[2]])
        elif last_part[2] == (-1, 0): # going to the left - append to right
            self.body.append([last_part[0] + 1, last_part[1], last_part[2]])
        elif last_part[2] == (0, 1): # going up - append down
            self.body.append([last_part[0], last_part[1] + 1, last_part[2]])
        elif last_part[2] == (0, -1): # going down - append up
            self.body.append([last_part[0], last_part[1] - 1, last_part[2]])

    def draw(self, surface):
        for part in self.body:
            x = part[0] * self.square_w
            y = part[1] * self.square_h
            pygame.draw.rect(surface, SNAKE_RED, (x + 1, y + 1, self.square_w, self.square_h))


class Snack:
    def __init__(self, rows, columns, sw, sh, snake_body):
        self.rows = rows
        self.columns = columns
        self.square_w = sw
        self.square_h = sh
        self.x_square = None
        self.y_square = None
        self.generate_snack(snake_body)

    def generate_snack(self, snake_body):
        snake_coords = {i: [True] * self.columns for i in range(0, self.rows)}
        for part in snake_body:
            if part[0] in snake_coords:
                if part[1] < len(snake_coords[part[0]]):
                    snake_coords[part[0]][part[1]] = False

        while True:
            possible_x = random.randint(0, self.rows-1)
            if True in snake_coords[possible_x]:
                break
        self.x_square = possible_x
        self.y_square = random.choice([index for index in range(len(snake_coords[possible_x])) if snake_coords[possible_x][index] is True])

    def draw(self, surface):
        pygame.draw.rect(surface, SNACK_GREEN, (self.x_square * self.square_w + 1, self.y_square * self.square_h + 1, self.square_w, self.square_h))


g = Game()