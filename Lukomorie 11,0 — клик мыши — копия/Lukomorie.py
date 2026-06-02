import pygame
import sys
from Wheel_Aprons import DiceWheel
from player_logic import PlayerLogic
from mini_games import MiniGames

# ============================================
# ИНИЦИАЛИЗАЦИЯ PYGAME
# ============================================
pygame.init()

SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1030
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Лукоморье")

# ============================================
# ЦВЕТА
# ============================================
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
GRAY = (200, 200, 200)
PURPLE = (100, 0, 200)
BLUE = (0, 153, 255)
LIGHT_GREEN = (144, 238, 144)
GOLD = (255, 215, 0)

# ============================================
# ШРИФТЫ
# ============================================
font_small = pygame.font.SysFont('Arial', 24)
font_medium = pygame.font.SysFont('Arial', 36)
font_large = pygame.font.SysFont('Arial', 48)
font_huge = pygame.font.SysFont('Arial', 72)

# ============================================
# ЗАГРУЗКА ФОНА
# ============================================
try:
    board_image = pygame.image.load("lukomorie_board1.jpg")
    board_image = pygame.transform.rotate(board_image, 0)
    board_image = pygame.transform.scale(board_image, (SCREEN_WIDTH - 300, SCREEN_HEIGHT))
except FileNotFoundError:
    print("️ Файл 'lukomorie_board1.jpg' не найден. Используется заглушка.")
    board_image = pygame.Surface((SCREEN_WIDTH - 300, SCREEN_HEIGHT))
    board_image.fill((34, 139, 34))
    pygame.draw.rect(board_image, BLACK, (0, 0, SCREEN_WIDTH - 300, SCREEN_HEIGHT), 2)
    text = font_medium.render("Доска Лукоморья", True, WHITE)
    board_image.blit(text, (50, 50))

# ============================================
# СОЗДАНИЕ ОБЪЕКТОВ ИГРЫ
# ============================================
player = PlayerLogic("Игрок 1")
wheel = DiceWheel(SCREEN_WIDTH - 160, SCREEN_HEIGHT // 2, 150, font_large, font_huge)
mini_games = MiniGames(screen, font_medium, font_large, font_huge)

# ============================================
# ФЛАГИ СОСТОЯНИЯ
# ============================================
dice_result_handled = False
waiting_for_second_roll = False
message_text = "Нажмите START для броска кубика"
message_color = WHITE

# ============================================
# UI ПРЯМОУГОЛЬНИКИ
# ============================================
INVENTORY_RECT = pygame.Rect(SCREEN_WIDTH - 280, 100, 260, 120)
COINS_RECT = pygame.Rect(SCREEN_WIDTH - 280, 250, 260, 60)
MESSAGE_RECT = pygame.Rect(10, SCREEN_HEIGHT - 60, SCREEN_WIDTH - 320, 50)

# ============================================
# СПИСОК РЕАЛИЗОВАННЫХ МИНИ-ИГР
# ============================================
IMPLEMENTED_MINI_GAMES = [3, 5, 11, 12, 13]  # Кот, Лягушка, Гуси, Репка, Баба Яга

# ============================================
# ОСНОВНОЙ ЦИКЛ ИГРЫ
# ============================================
clock = pygame.time.Clock()
running = True

while running:
    # --- ОБРАБОТКА СОБЫТИЙ ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos

            # 1. Клик по колесу (бросок кубика)
            dist_sq = (mouse_x - wheel.center_x) ** 2 + (mouse_y - wheel.center_y) ** 2
            if dist_sq <= wheel.radius ** 2 and not wheel.is_spinning():
                if not player.in_mini_game and not player.waiting_for_branch_decision:
                    if not player.waiting_for_click_move:
                        wheel.spin()
                        dice_result_handled = False
                        waiting_for_second_roll = False
                        message_text = "Кубик крутится..."
                        message_color = YELLOW
                    elif waiting_for_second_roll:
                        wheel.spin()
                        message_text = "Бросок для количества шагов..."
                        message_color = YELLOW

            # 2. Клик по игровому полю (перемещение фишки)
            elif mouse_x < SCREEN_WIDTH - 300 and player.waiting_for_click_move:
                best_index = -1
                min_dist = float('inf')

                for i, point in enumerate(player.path_points):
                    if i <= player.current_path_index:
                        continue
                    dist = ((point[0] - mouse_x) ** 2 + (point[1] - mouse_y) ** 2) ** 0.5
                    if dist < 50 and dist < min_dist:
                        min_dist = dist
                        best_index = i

                if best_index != -1:
                    success, result = player.try_move_to_point(best_index)
                    if success:
                        if result == "branch":
                            message_text = "РАЗВИЛКА! Нажмите любую клавишу"
                            message_color = PURPLE
                        elif result == "mini_game":
                            message_text = "Мини-игра активирована!"
                            message_color = YELLOW
                        elif result == "turn_end":
                            message_text = "Ход завершён. Нажмите START"
                            message_color = GREEN
                        else:
                            if player.branch_2_passed:
                                message_text = "Свободное перемещение"
                            else:
                                message_text = f"Осталось шагов: {player.steps_remaining}"
                            message_color = LIGHT_GREEN
                    else:
                        message_text = result
                        message_color = RED

        # 3. Обработка клавиш (для развилок и мини-игр)
        if event.type == pygame.KEYDOWN:
            if player.waiting_for_branch_decision:
                wheel.spin()
                dice_result_handled = False
                message_text = "Кубик крутится для выбора пути..."
                message_color = YELLOW

            elif player.in_mini_game:
                _, _, _, mini_id = player.get_current_cell_info()

                # ✅ ПРОВЕРКА: Реализована ли мини-игра в mini_games.py?
                if mini_id in IMPLEMENTED_MINI_GAMES:
                    # Запуск полноценной мини-игры
                    dice_roll = player.dice_roll_value
                    target_index = mini_games.start_mini_game(mini_id, dice_roll, player.bon)

                    # Обработка результатов конкретных мини-игр
                    if mini_id == 13 and target_index == 80:
                        player.bon -= 20  # Баба Яга забирает 20 бонусов
                        if player.bon < 0:
                            player.bon = 0

                    player.complete_mini_game(target_index)
                    message_text = "Мини-игра завершена!"
                    message_color = GREEN
                else:
                    # Заглушка для нереализованных мини-игр
                    player.complete_mini_game(None)
                    message_text = "Мини-игра (заглушка) завершена!"
                    message_color = GRAY

    # --- ОБНОВЛЕНИЕ КОЛЕСА ---
    wheel.update()

    # --- ОБРАБОТКА РЕЗУЛЬТАТОВ БРОСКА ---
    if not wheel.is_spinning() and not dice_result_handled and not player.in_mini_game:
        # 1. Обычный ход
        if not player.waiting_for_branch_decision and not waiting_for_second_roll and not player.waiting_for_click_move:
            dice_roll = wheel.get_dice_result()
            if dice_roll != 0:
                print(f" Выпало: {dice_roll}")
                player.start_click_movement(dice_roll)
                dice_result_handled = True
                message_text = f"Выпало {dice_roll}! Кликайте на точки"
                message_color = BLUE

        # 2. Первый бросок на развилке (выбор пути)
        elif player.waiting_for_branch_decision and not waiting_for_second_roll:
            dice_roll = wheel.get_dice_result()
            if dice_roll != 0:
                if player.choose_path_from_dice(dice_roll):
                    waiting_for_second_roll = True
                    dice_result_handled = True
                    message_text = "Бросьте кубик для количества шагов"
                    message_color = PURPLE

        # 3. Второй бросок на развилке (количество шагов)
        elif waiting_for_second_roll:
            dice_roll = wheel.get_dice_result()
            if dice_roll != 0:
                player.move_along_selected_path(dice_roll)
                waiting_for_second_roll = False
                dice_result_handled = True
                message_text = "Ход завершён. Нажмите START"
                message_color = WHITE

    # --- ОТРИСОВКА ---
    screen.fill(WHITE)
    screen.blit(board_image, (0, 0))

    # 1. Отрисовка точек пути
    for i, point in enumerate(player.path_points):
        if i == player.current_path_index:
            color = RED  # Текущая позиция
        else:
            color = GRAY  # Все остальные серые

        pygame.draw.circle(screen, color, (int(point[0]), int(point[1])), 10)

        # Номер точки (каждую 5-ю)
        if i % 5 == 0:
            num_text = font_small.render(str(i + 1), True, WHITE)
            screen.blit(num_text, (int(point[0]) - 5, int(point[1]) - 15))

    # 2. Отрисовка фишки игрока
    if player.path_points and 0 <= player.current_path_index < len(player.path_points):
        x, y = player.path_points[player.current_path_index]
        pygame.draw.circle(screen, RED, (int(x), int(y)), 20)
        pygame.draw.circle(screen, WHITE, (int(x), int(y)), 16)
        point_number = player.current_path_index + 1
        token_label = font_small.render(str(point_number), True, BLACK)
        screen.blit(token_label, (int(x) - 8, int(y) - 10))

    # 3. Отрисовка колеса
    wheel.draw(screen)

    # 4. UI: Инвентарь
    pygame.draw.rect(screen, GRAY, INVENTORY_RECT, border_radius=10)
    pygame.draw.rect(screen, BLACK, INVENTORY_RECT, 2, border_radius=10)
    inv_text = font_small.render("Инвентарь:", True, BLACK)
    screen.blit(inv_text, (INVENTORY_RECT.x + 10, INVENTORY_RECT.y + 10))
    for i, item in enumerate(player.inventory):
        item_text = font_small.render(item or "—", True, BLACK)
        screen.blit(item_text, (INVENTORY_RECT.x + 10, INVENTORY_RECT.y + 40 + i * 25))

    # 5. UI: БОНЫ (монеты)
    pygame.draw.rect(screen, GOLD, COINS_RECT, border_radius=10)
    pygame.draw.rect(screen, BLACK, COINS_RECT, 2, border_radius=10)
    coins_text = font_medium.render(f"Боны: {player.bon}", True, BLACK)
    screen.blit(coins_text, (COINS_RECT.x + 15, COINS_RECT.y + 15))

    # 6. UI: Сообщение
    pygame.draw.rect(screen, (50, 50, 50), MESSAGE_RECT, border_radius=5)
    msg_surface = font_small.render(message_text, True, message_color)
    screen.blit(msg_surface, (MESSAGE_RECT.x + 10, MESSAGE_RECT.y + 10))

    # 7. Оверлей развилки
    if player.waiting_for_branch_decision:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))

        panel_width = 600
        panel_height = 250
        panel_x = (SCREEN_WIDTH - panel_width) // 2
        panel_y = (SCREEN_HEIGHT - panel_height) // 2

        pygame.draw.rect(screen, PURPLE, (panel_x, panel_y, panel_width, panel_height), border_radius=20)
        pygame.draw.rect(screen, WHITE, (panel_x, panel_y, panel_width, panel_height), 3, border_radius=20)

        title = font_large.render("РАЗВИЛКА!", True, YELLOW)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, panel_y + 50))
        screen.blit(title, title_rect)

        subtitle = font_medium.render("Нажмите ЛЮБУЮ клавишу для броска", True, WHITE)
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, panel_y + 100))
        screen.blit(subtitle, subtitle_rect)

        rules = ["1-2 → Путь 1", "3-4 → Путь 2", "5-6 → Путь 3"]
        for i, rule in enumerate(rules):
            rule_text = font_small.render(rule, True, WHITE)
            rule_rect = rule_text.get_rect(center=(SCREEN_WIDTH // 2 - 100 + i * 200, panel_y + 150))
            screen.blit(rule_text, rule_rect)

    # 8. Оверлей второго броска
    if waiting_for_second_roll:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))

        panel_width = 600
        panel_height = 150
        panel_x = (SCREEN_WIDTH - panel_width) // 2
        panel_y = (SCREEN_HEIGHT - panel_height) // 2

        pygame.draw.rect(screen, BLUE, (panel_x, panel_y, panel_width, panel_height), border_radius=20)
        pygame.draw.rect(screen, WHITE, (panel_x, panel_y, panel_width, panel_height), 3, border_radius=20)

        title = font_large.render("ВЫБРАНО НАПРАВЛЕНИЕ!", True, YELLOW)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, panel_y + 40))
        screen.blit(title, title_rect)

        subtitle = font_medium.render("Бросьте кубик для количества шагов", True, WHITE)
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, panel_y + 90))
        screen.blit(subtitle, subtitle_rect)

    # 9. Оверлей мини-игры
    if player.in_mini_game:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))

        _, _, _, mini_id = player.get_current_cell_info()

        # ✅ ПРОВЕРКА: Реализована ли мини-игра?
        if mini_id in IMPLEMENTED_MINI_GAMES:
            mini_names = {
                3: "Кот Учёный",
                5: "Царевна Лягушка",
                11: "Гуси-Лебеди",
                12: "Репка",
                13: "Баба Яга"
            }
            title = mini_names.get(mini_id, f"Мини-игра #{mini_id}")
            prompt = "Нажмите ЛЮБУЮ клавишу для старта..."
        else:
            # Заглушка для нереализованных мини-игр
            mini_names = {
                4: "Сундук", 6: "Леший", 7: "Леший 2",
                8: "Гуси-Лебеди 2", 9: "Царевна-Лягушка 2",
                60: "Леший 60", 61: "Леший 61"
            }
            title = mini_names.get(mini_id, f"Мини-игра #{mini_id}") + " (заглушка)"
            prompt = "Нажмите ЛЮБУЮ клавишу, чтобы продолжить..."

        text = font_large.render(title, True, WHITE)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        screen.blit(text, text_rect)

        prompt_text = font_small.render(prompt, True, YELLOW)
        prompt_rect = prompt_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        screen.blit(prompt_text, prompt_rect)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()