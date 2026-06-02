import pygame
import random
import sys

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 153, 255)
YELLOW = (255, 255, 0)
PURPLE = (100, 0, 200)
GRAY = (200, 200, 200)
BROWN = (139, 69, 19)
SKY_BLUE = (135, 206, 235)
PIPE_GREEN = (34, 139, 34)
GOLD = (255, 215, 0)


class MiniGames:
    def __init__(self, screen, font_medium, font_large, font_huge):
        self.screen = screen
        self.font_medium = font_medium
        self.font_large = font_large
        self.font_huge = font_huge
        self.SCREEN_WIDTH = 1920
        self.SCREEN_HEIGHT = 1030

        # Для мини-игры №3 (Кот Учёный)
        self.maze_buttons = []
        self.maze_result = None

        # Для мини-игры №5 (Царевна Лягушка - Flappy Bird)
        self.bird_y = 0
        self.bird_velocity = 0
        self.pipes = []
        self.flappy_score = 0
        self.flappy_running = False
        self.flappy_game_over = False

        # Для мини-игры №13 (Баба Яга)
        self.player_coins = 0  # Будет обновляться из основной игры

    def set_player_coins(self, coins):
        """Устанавливает количество монет игрока"""
        self.player_coins = coins

    # ============================================
    # МИНИ-ИГРА №3: КОТ УЧЁНЫЙ (Лабиринт + кнопки)
    # ============================================
    def mini_game_3_kot_ucheny(self, dice_roll):
        """
        Кот Учёный - лабиринт с 6 кнопками
        Возвращает индекс координаты для телепортации
        """
        clock = pygame.time.Clock()
        running = True
        result_index = None

        # Координаты для каждой кнопки (индексы в path_points)
        button_destinations = {
            1: 15,  # Кнопка 1 -> координата 15
            2: 20,  # Кнопка 2 -> координата 20
            3: 25,  # Кнопка 3 -> координата 25
            4: 30,  # Кнопка 4 -> координата 30
            5: 35,  # Кнопка 5 -> координата 35
            6: 40  # Кнопка 6 -> координата 40
        }

        # Создаём кнопки справа
        button_rects = []
        button_y_start = 200
        button_height = 80
        button_width = 200
        button_x = self.SCREEN_WIDTH - 250

        for i in range(6):
            rect = pygame.Rect(button_x, button_y_start + i * (button_height + 20),
                               button_width, button_height)
            button_rects.append(rect)

        # Загружаем или создаём фон лабиринта
        try:
            maze_bg = pygame.image.load("maze_background.jpg")
            maze_bg = pygame.transform.scale(maze_bg, (self.SCREEN_WIDTH - 300, self.SCREEN_HEIGHT))
        except:
            maze_bg = pygame.Surface((self.SCREEN_WIDTH - 300, self.SCREEN_HEIGHT))
            maze_bg.fill((100, 100, 150))
            # Рисуем простой лабиринт
            for i in range(0, self.SCREEN_WIDTH - 300, 100):
                pygame.draw.rect(maze_bg, GRAY, (i, 0, 10, self.SCREEN_HEIGHT))
            for i in range(0, self.SCREEN_HEIGHT, 100):
                pygame.draw.rect(maze_bg, GRAY, (0, i, self.SCREEN_WIDTH - 300, 10))

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = event.pos
                    for i, rect in enumerate(button_rects):
                        if rect.collidepoint(mouse_x, mouse_y):
                            result_index = button_destinations[i + 1]
                            running = False
                            break

            # Отрисовка
            self.screen.fill(BLACK)
            self.screen.blit(maze_bg, (0, 0))

            # Заголовок
            title = self.font_huge.render("КОТ УЧЁНЫЙ", True, YELLOW)
            self.screen.blit(title, (50, 50))

            # Инструкция
            instruction = self.font_medium.render(f"Выпало: {dice_roll}. Выберите кнопку!", True, WHITE)
            self.screen.blit(instruction, (50, 120))

            # Кнопки
            colors = [RED, BLUE, GREEN, YELLOW, PURPLE, BROWN]
            for i, rect in enumerate(button_rects):
                pygame.draw.rect(self.screen, colors[i], rect, border_radius=10)
                pygame.draw.rect(self.screen, WHITE, rect, 3, border_radius=10)
                btn_text = self.font_large.render(f"Путь {i + 1}", True, WHITE)
                text_rect = btn_text.get_rect(center=rect.center)
                self.screen.blit(btn_text, text_rect)

            pygame.display.flip()
            clock.tick(60)

        return result_index

    # ============================================
    # МИНИ-ИГРА №5: ЦАРЕВНА ЛЯГУШКА (Flappy Bird)
    # ============================================
    def mini_game_5_flappy_bird(self):
        """
        Царевна Лягушка - Flappy Bird с простыми фигурами
        Нужно пролететь через 10 труб
        Возвращает индекс координаты для телепортации (например, 50)
        """
        clock = pygame.time.Clock()
        running = True
        game_complete = False

        # Параметры птицы
        bird_x = 200
        self.bird_y = self.SCREEN_HEIGHT // 2
        self.bird_velocity = 0
        bird_radius = 20
        gravity = 0.5
        jump_strength = -10

        # Параметры труб
        self.pipes = []
        pipe_width = 80
        pipe_gap = 200
        pipe_speed = 5
        self.flappy_score = 0
        pipes_needed = 10

        # Создаём начальные трубы
        for i in range(3):
            pipe_x = 600 + i * 400
            gap_y = random.randint(200, self.SCREEN_HEIGHT - 200 - pipe_gap)
            self.pipes.append({'x': pipe_x, 'gap_y': gap_y, 'passed': False})

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN:
                    if not game_complete:
                        self.bird_velocity = jump_strength

            if not game_complete:
                # Физика птицы
                self.bird_velocity += gravity
                self.bird_y += self.bird_velocity

                # Движение труб
                for pipe in self.pipes:
                    pipe['x'] -= pipe_speed

                # Удаляем ушедшие трубы и добавляем новые
                if self.pipes and self.pipes[0]['x'] < -pipe_width:
                    self.pipes.pop(0)

                if self.pipes and self.pipes[-1]['x'] < self.SCREEN_WIDTH - 400:
                    gap_y = random.randint(200, self.SCREEN_HEIGHT - 200 - pipe_gap)
                    self.pipes.append({'x': self.SCREEN_WIDTH, 'gap_y': gap_y, 'passed': False})

                # Проверка прохождения труб
                for pipe in self.pipes:
                    if not pipe['passed'] and pipe['x'] + pipe_width < bird_x:
                        pipe['passed'] = True
                        self.flappy_score += 1

                # Проверка столкновений
                # С полом/потолком
                if self.bird_y < 0 or self.bird_y > self.SCREEN_HEIGHT:
                    game_complete = True

                # С трубами
                for pipe in self.pipes:
                    if bird_x + bird_radius > pipe['x'] and bird_x - bird_radius < pipe['x'] + pipe_width:
                        if self.bird_y - bird_radius < pipe['gap_y'] or self.bird_y + bird_radius > pipe[
                            'gap_y'] + pipe_gap:
                            game_complete = True

                # Проверка победы
                if self.flappy_score >= pipes_needed:
                    game_complete = True

            # Отрисовка
            self.screen.fill(SKY_BLUE)

            # Трубы
            for pipe in self.pipes:
                # Верхняя труба
                pygame.draw.rect(self.screen, PIPE_GREEN,
                                 (pipe['x'], 0, pipe_width, pipe['gap_y']))
                pygame.draw.rect(self.screen, BLACK,
                                 (pipe['x'], 0, pipe_width, pipe['gap_y']), 2)
                # Нижняя труба
                pygame.draw.rect(self.screen, PIPE_GREEN,
                                 (pipe['x'], pipe['gap_y'] + pipe_gap, pipe_width,
                                  self.SCREEN_HEIGHT - pipe['gap_y'] - pipe_gap))
                pygame.draw.rect(self.screen, BLACK,
                                 (pipe['x'], pipe['gap_y'] + pipe_gap, pipe_width,
                                  self.SCREEN_HEIGHT - pipe['gap_y'] - pipe_gap), 2)

            # Птица (круг)
            pygame.draw.circle(self.screen, YELLOW, (int(bird_x), int(self.bird_y)), bird_radius)
            pygame.draw.circle(self.screen, BLACK, (int(bird_x), int(self.bird_y)), bird_radius, 2)

            # Счёт
            score_text = self.font_huge.render(f"Трубы: {self.flappy_score}/{pipes_needed}", True, WHITE)
            self.screen.blit(score_text, (50, 50))

            # Инструкция
            if game_complete:
                if self.flappy_score >= pipes_needed:
                    result_text = self.font_huge.render("ПОБЕДА! Телепортация...", True, GREEN)
                else:
                    result_text = self.font_huge.render("ИГРА ОКОНЧЕНА! Попробуйте снова", True, RED)
                result_rect = result_text.get_rect(center=(self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2 + 100))
                self.screen.blit(result_text, result_rect)
                pygame.display.flip()
                pygame.time.wait(2000)
                running = False

            pygame.display.flip()
            clock.tick(60)

        # Возвращаем индекс координаты (например, 50)
        return 50 if self.flappy_score >= pipes_needed else 0

    # ============================================
    # МИНИ-ИГРА №11: ГУСИ-ЛЕБЕДИ (Кубик + рандом)
    # ============================================
    def mini_game_11_gusi_lebedi(self, dice_roll):
        """
        Гуси-Лебеди - бросок кубика, телепортация на случайную координату
        Возвращает индекс координаты для телепортации
        """
        clock = pygame.time.Clock()
        running = True
        result_index = None

        # Случайные координаты для каждого числа кубика
        dice_destinations = {
            1: 55,
            2: 60,
            3: 65,
            4: 70,
            5: 75,
            6: 80
        }

        # Загружаем или создаём фон
        try:
            bg = pygame.image.load("geese_background.jpg")
            bg = pygame.transform.scale(bg, (self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        except:
            bg = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
            bg.fill((100, 150, 100))
            # Рисуем гусей (простые фигуры)
            for i in range(5):
                pygame.draw.ellipse(bg, WHITE, (200 + i * 150, 300 + i * 50, 80, 50))
                pygame.draw.circle(bg, ORANGE := (255, 165, 0), (280 + i * 150, 320 + i * 50), 15)

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN:
                    result_index = dice_destinations.get(dice_roll, 55)
                    running = False

            # Отрисовка
            self.screen.blit(bg, (0, 0))

            # Заголовок
            title = self.font_huge.render("ГУСИ-ЛЕБЕДИ", True, WHITE)
            title_rect = title.get_rect(center=(self.SCREEN_WIDTH // 2, 100))
            self.screen.blit(title, title_rect)

            # Кубик
            dice_text = self.font_huge.render(f"Выпало: {dice_roll}", True, YELLOW)
            dice_rect = dice_text.get_rect(center=(self.SCREEN_WIDTH // 2, 300))
            self.screen.blit(dice_text, dice_rect)

            # Инструкция
            instruction = self.font_large.render("Нажмите любую кнопку для телепортации", True, WHITE)
            instruction_rect = instruction.get_rect(center=(self.SCREEN_WIDTH // 2, 500))
            self.screen.blit(instruction, instruction_rect)

            # Куда телепортирует
            dest_text = self.font_medium.render(f"Координата: {dice_destinations.get(dice_roll, 55)}", True, GREEN)
            dest_rect = dest_text.get_rect(center=(self.SCREEN_WIDTH // 2, 600))
            self.screen.blit(dest_text, dest_rect)

            pygame.display.flip()
            clock.tick(60)

        return result_index

    # ============================================
    # МИНИ-ИГРА №12: РЕПКА (Викторина)
    # ============================================
    def mini_game_12_repka(self):
        """
        Репка - вопрос о количестве героев в сказке
        Возвращает индекс координаты в зависимости от ответа
        """
        clock = pygame.time.Clock()
        running = True
        result_index = None

        # Правильный ответ: 6 (дедка, бабка, внучка, жучка, кошка, мышка)
        correct_answer = 6

        # Варианты ответов с координатами
        answers = [
            {"text": "4", "index": 10, "correct": False},
            {"text": "5", "index": 20, "correct": False},
            {"text": "6", "index": 70, "correct": True},  # Правильный -> дальше
            {"text": "7", "index": 5, "correct": False},
            {"text": "8", "index": 1, "correct": False},
        ]

        # Создаём кнопки
        button_rects = []
        button_y_start = 400
        button_height = 80
        button_width = 250
        button_x_start = (self.SCREEN_WIDTH - (button_width * 3 + 40)) // 2

        for i in range(len(answers)):
            x = button_x_start + (i % 3) * (button_width + 20)
            y = button_y_start + (i // 3) * (button_height + 20)
            rect = pygame.Rect(x, y, button_width, button_height)
            button_rects.append(rect)

        # Загружаем или создаём фон
        try:
            bg = pygame.image.load("repka_background.jpg")
            bg = pygame.transform.scale(bg, (self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        except:
            bg = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
            bg.fill((139, 119, 101))
            # Рисуем репку
            pygame.draw.ellipse(bg, ORANGE := (255, 165, 0), (self.SCREEN_WIDTH // 2 - 50, 300, 100, 150))
            pygame.draw.polygon(bg, GREEN, [(self.SCREEN_WIDTH // 2, 250),
                                            (self.SCREEN_WIDTH // 2 - 30, 300),
                                            (self.SCREEN_WIDTH // 2 + 30, 300)])

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = event.pos
                    for i, rect in enumerate(button_rects):
                        if rect.collidepoint(mouse_x, mouse_y):
                            result_index = answers[i]["index"]
                            running = False
                            break

            # Отрисовка
            self.screen.blit(bg, (0, 0))

            # Вопрос
            question = self.font_large.render("Сколько действующих героев в сказке РЕПКА?", True, WHITE)
            question_rect = question.get_rect(center=(self.SCREEN_WIDTH // 2, 150))
            self.screen.blit(question, question_rect)

            # Кнопки с ответами
            for i, rect in enumerate(button_rects):
                color = GREEN if answers[i]["correct"] else RED
                pygame.draw.rect(self.screen, color, rect, border_radius=10)
                pygame.draw.rect(self.screen, WHITE, rect, 3, border_radius=10)
                ans_text = self.font_huge.render(answers[i]["text"], True, WHITE)
                text_rect = ans_text.get_rect(center=rect.center)
                self.screen.blit(ans_text, text_rect)

            # Подсказка
            hint = self.font_medium.render("Правильный ответ телепортирует дальше!", True, YELLOW)
            hint_rect = hint.get_rect(center=(self.SCREEN_WIDTH // 2, 650))
            self.screen.blit(hint, hint_rect)

            pygame.display.flip()
            clock.tick(60)

        return result_index

    # ============================================
    # МИНИ-ИГРА №13: БАБА ЯГА (Монетки)
    # ============================================
    def mini_game_13_baba_yaga(self, player_coins):
        """
        Баба Яга - нужно 20 монеток
        Если есть - забирают, игрок идёт дальше
        Если нет - телепорт на координату 1
        Возвращает индекс координаты для телепортации
        """
        clock = pygame.time.Clock()
        running = True
        result_index = None

        coins_needed = 20

        # Загружаем или создаём фон
        try:
            bg = pygame.image.load("baba_yaga_background.jpg")
            bg = pygame.transform.scale(bg, (self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        except:
            bg = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
            bg.fill((50, 30, 20))
            # Рисуем избушку
            pygame.draw.rect(bg, BROWN, (self.SCREEN_WIDTH // 2 - 150, 400, 300, 200))
            pygame.draw.polygon(bg, BROWN, [(self.SCREEN_WIDTH // 2 - 170, 400),
                                            (self.SCREEN_WIDTH // 2, 250),
                                            (self.SCREEN_WIDTH // 2 + 170, 400)])
            # Куриные ножки
            pygame.draw.rect(bg, BROWN, (self.SCREEN_WIDTH // 2 - 100, 600, 30, 150))
            pygame.draw.rect(bg, BROWN, (self.SCREEN_WIDTH // 2 + 70, 600, 30, 150))

        has_enough = player_coins >= coins_needed

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN:
                    if has_enough:
                        result_index = 80  # Дальше по пути
                    else:
                        result_index = 1  # На начало
                    running = False

            # Отрисовка
            self.screen.blit(bg, (0, 0))

            # Заголовок
            title = self.font_huge.render("БАБА ЯГА", True, WHITE)
            title_rect = title.get_rect(center=(self.SCREEN_WIDTH // 2, 100))
            self.screen.blit(title, title_rect)

            # Информация о монетах
            coins_text = self.font_large.render(f"У вас монет: {player_coins}", True, GOLD)
            coins_rect = coins_text.get_rect(center=(self.SCREEN_WIDTH // 2, 250))
            self.screen.blit(coins_text, coins_rect)

            needed_text = self.font_large.render(f"Нужно монет: {coins_needed}", True, WHITE)
            needed_rect = needed_text.get_rect(center=(self.SCREEN_WIDTH // 2, 320))
            self.screen.blit(needed_text, needed_rect)

            # Результат
            if has_enough:
                result_msg = self.font_huge.render("Достаточно! Баба Яга довольна", True, GREEN)
                dest_msg = self.font_medium.render("Вы идёте дальше...", True, WHITE)
            else:
                result_msg = self.font_huge.render("Недостаточно монет!", True, RED)
                dest_msg = self.font_medium.render("Вас отправляют на начало пути...", True, WHITE)

            result_rect = result_msg.get_rect(center=(self.SCREEN_WIDTH // 2, 450))
            dest_rect = dest_msg.get_rect(center=(self.SCREEN_WIDTH // 2, 550))
            self.screen.blit(result_msg, result_rect)
            self.screen.blit(dest_msg, dest_rect)

            # Инструкция
            instruction = self.font_medium.render("Нажмите любую кнопку", True, YELLOW)
            instruction_rect = instruction.get_rect(center=(self.SCREEN_WIDTH // 2, 700))
            self.screen.blit(instruction, instruction_rect)

            pygame.display.flip()
            clock.tick(60)

        return result_index

    # ============================================
    # УНИВЕРСАЛЬНЫЙ МЕТОД ЗАПУСКА МИНИ-ИГРЫ
    # ============================================
    def start_mini_game(self, mini_id, dice_roll=0, player_coins=0):
        """
        Универсальный метод для запуска любой мини-игры по ID
        Возвращает индекс координаты для телепортации
        """
        self.set_player_coins(player_coins)

        if mini_id == 3:
            return self.mini_game_3_kot_ucheny(dice_roll)
        elif mini_id == 5:
            return self.mini_game_5_flappy_bird()
        elif mini_id == 11:
            return self.mini_game_11_gusi_lebedi(dice_roll)
        elif mini_id == 12:
            return self.mini_game_12_repka()
        elif mini_id == 13:
            return self.mini_game_13_baba_yaga(player_coins)
        else:
            print(f"Мини-игра #{mini_id} не реализована")
            return None