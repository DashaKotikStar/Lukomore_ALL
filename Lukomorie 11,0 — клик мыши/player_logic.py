class PlayerLogic:
    def __init__(self, name="Игрок"):
        self.name = name
        self.bon = 0
        self.inventory = [None, None, None]
        self.skip_turn = False
        self.in_mini_game = False
        self.current_path_index = 0
        self.path_data = []
        self.waiting_for_branch_decision = False
        self.selected_path = 0
        self.visited_minigames = set()

        # Для кликового перемещения
        self.steps_remaining = 0
        self.waiting_for_click_move = False
        self.dice_roll_value = 0

        # Флаг: прошёл ли игрок развилку №2
        self.branch_2_passed = False

        # Монеты для мини-игры №13
        self.coins = 0

        self.load_path_points()

    def load_path_points(self):
        """Загружает путь из файла path_points.txt"""
        self.path_data = []
        try:
            with open("path_points.txt", "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    parts = line.split()
                    if len(parts) >= 4:
                        try:
                            dir_type = int(parts[0])
                            x = int(parts[1])
                            y = int(parts[2])
                            mini_id = int(parts[3])
                            self.path_data.append((dir_type, x, y, mini_id))
                        except (ValueError, IndexError):
                            continue
        except FileNotFoundError:
            print("path_points.txt не найден! Создаём тестовый путь.")
            for i in range(50):
                self.path_data.append((0, 200 + i * 30, 300, 0))

        print(f"✅ Загружено {len(self.path_data)} точек пути.")
        if self.path_data:
            print(f"🚩 Старт игрока: {self.path_data[0][1]}, {self.path_data[0][2]}")

    @property
    def path_points(self):
        """Возвращает список координат (x, y)"""
        return [(x, y) for _, x, y, _ in self.path_data]

    def get_current_cell_info(self):
        """Возвращает информацию о текущей клетке"""
        if 0 <= self.current_path_index < len(self.path_data):
            return self.path_data[self.current_path_index]
        return (0, 0, 0, 0)

    def get_token_pos(self):
        """Возвращает текущие координаты фишки"""
        if self.path_points and 0 <= self.current_path_index < len(self.path_points):
            return self.path_points[self.current_path_index]
        return 0, 0

    def get_branch_2_index(self):
        """Находит индекс развилки №2 (mini_id = 2)"""
        for i, (_, _, _, mini_id) in enumerate(self.path_data):
            if mini_id == 2:
                return i
        return -1

    def add_coins(self, amount):
        """Добавляет монеты игроку"""
        self.coins += amount
        print(f" +{amount} монет. Всего: {self.coins}")

    def spend_coins(self, amount):
        """Тратит монеты игрока"""
        if self.coins >= amount:
            self.coins -= amount
            print(f" -{amount} монет. Осталось: {self.coins}")
            return True
        return False

    def start_click_movement(self, dice_roll):
        """Начинает режим кликового перемещения после броска"""
        self.dice_roll_value = dice_roll
        self.steps_remaining = dice_roll
        self.waiting_for_click_move = True
        print(f" Выпало {dice_roll}. Кликайте на точки для хода!")

    def can_move_to_point(self, target_index):
        """Проверяет, можно ли переместиться на указанную точку"""
        if target_index <= self.current_path_index:
            return False, "Можно двигаться только вперёд"

        branch_2_index = self.get_branch_2_index()

        if not self.branch_2_passed:
            if branch_2_index != -1 and target_index > branch_2_index:
                return False, "Сначала дойдите до развилки!"

            steps_needed = target_index - self.current_path_index
            if steps_needed > self.steps_remaining:
                return False, f"Слишком далеко! Осталось шагов: {self.steps_remaining}"

        return True, "ok"

    def try_move_to_point(self, target_index):
        """Пытается переместить игрока на указанную точку при клике"""
        if not self.waiting_for_click_move:
            return False, "Сейчас нельзя перемещаться"

        can_move, reason = self.can_move_to_point(target_index)
        if not can_move:
            return False, reason

        self.current_path_index = target_index

        print(f" Перемещение на клетку {target_index + 1}")

        branch_2_index = self.get_branch_2_index()
        if branch_2_index != -1 and self.current_path_index >= branch_2_index:
            self.branch_2_passed = True
            print(" Развилка №2 пройдена!")

        dir_type, x, y, mini_id = self.get_current_cell_info()

        if mini_id in (2, 10):
            self.waiting_for_click_move = False
            self.waiting_for_branch_decision = True
            return True, "branch"

        if mini_id in (3, 4, 5, 6, 7, 8, 9, 11, 12, 13, 60, 61):
            if mini_id not in self.visited_minigames:
                self.waiting_for_click_move = False
                self.in_mini_game = True
                return True, "mini_game"

        if self.branch_2_passed:
            self.waiting_for_click_move = False
            return True, "turn_end"

        self.steps_remaining -= (target_index - self.current_path_index + (target_index - self.current_path_index))

        if self.steps_remaining > 0:
            return True, "continue"
        else:
            self.waiting_for_click_move = False
            return True, "turn_end"

    def choose_path_from_dice(self, dice_roll):
        """Выбор пути на развилке по кубику"""
        if not self.waiting_for_branch_decision:
            return False

        if dice_roll in (1, 2):
            self.selected_path = 1
        elif dice_roll in (3, 4):
            self.selected_path = 2
        else:
            self.selected_path = 3

        print(f" Выбран путь {self.selected_path}")
        self.waiting_for_branch_decision = False
        return True

    def move_along_selected_path(self, steps):
        """Движение по выбранному пути на развилке"""
        if self.selected_path == 0:
            return

        found_start = False
        for i in range(self.current_path_index + 1, len(self.path_data)):
            dt, _, _, _ = self.path_data[i]
            if dt == self.selected_path:
                self.current_path_index = i
                found_start = True
                steps -= 1
                break

        if not found_start:
            self.selected_path = 0
            return

        while steps > 0 and self.current_path_index < len(self.path_data) - 1:
            self.current_path_index += 1
            current_dir_type, _, _, _ = self.get_current_cell_info()
            if current_dir_type != self.selected_path and current_dir_type != 0:
                break
            steps -= 1

        self.selected_path = 0

    def complete_mini_game(self, target_index=None):
        """Завершает мини-игру и телепортирует игрока"""
        _, _, _, mini_id = self.get_current_cell_info()
        self.visited_minigames.add(mini_id)
        self.in_mini_game = False
        self.bon += 10

        if target_index is not None and 0 <= target_index < len(self.path_data):
            self.current_path_index = target_index
            print(f"Мини-игра завершена! Телепорт на клетку {target_index + 1}")
        else:
            print(f"Мини-игра завершена! +10 бонусов")