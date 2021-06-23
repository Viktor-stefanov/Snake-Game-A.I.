from game import *

class HelpMeGame(Game):

    def __init__(self):
        super().__init__()

    def ai_game(self, genome, config):
        rows, columns = self.grid_size[0], self.grid_size[1]
        self.screen = GameScreen(self.screen_w, self.screen_h, rows, columns)
        sw, sh = self.screen.square_width, self.screen.square_height
        # create the neural network from the genome and the configuration file
        genome = genome[0][1]
        genome.fitness = 0
        nn = neat.nn.feed_forward.FeedForwardNetwork.create(genome, config)
        snake = Snake(rows // 2, columns // 2, rows, columns, sw, sh)
        snack = Snack(rows, columns, sw, sh, snake.body[0][0], snake.body[0][1])
        self.generation += 1

        while True:
            self.surface.fill(BLACK)
            pygame.time.delay(100)

            for event in pygame.event.get():
                self.terminate_event_check(event)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_m:
                        self.main_menu()

            ### THIS IS THE ARE I NEED HELP IN
            # move the snake and check if it 'ate' (collides with) a snack if so add a part to the snake and generate a new snack
            snake.move()
            if (snake.body[0][0], snake.body[0][1]) == (snack.x_square, snack.y_square):
                genome.fitness += 5
                snake.add_part()
                snack.generate_snack(snake.body[0][0], snake.body[0][1])

            x_distance = (snake.body[0][0] - snack.x_square)
            y_distance = (snake.body[0][1] - snack.y_square)

            x_direction, y_direction = nn.activate((x_distance, y_distance))

            print(x_direction, y_direction)
            if x_direction > 0.5:
                snake.direction = (1, 0)
            elif x_direction < -0.5:
                snake.direction = (-1, 0)
            if y_direction > 0.5:
                snake.direction = (0, 1)
            elif y_direction < 0.5:
                snake.direction = (0, -1)

            ### UP TO HERE ###

            snake.draw(self.surface)
            snack.draw(self.surface)
            self.screen.draw(self.surface)
            pygame.display.update()


    def run_ai(self):
        local_dir = os.path.dirname(__file__)
        config_path = os.path.join(local_dir, "config")
        config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                             neat.DefaultSpeciesSet, neat.DefaultStagnation,
                             config_path)

        pop = neat.Population(config)
        stats = neat.StatisticsReporter()
        pop.add_reporter(stats)
        pop.add_reporter(neat.StdOutReporter(True))

        pop.run(self.ai_game, 50)