from random import randint
import time


class Points:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"Координаты:({self.x}, {self.y})"


# ______________________________________________________________________________
# Классы исключений

class BoardException(Exception):
    pass


class BoardOutException(BoardException):
    def __str__(self):
        return "Вы пытаетесь выстрелить за пределы поля!"


class BoardRepeatException(BoardException):
    def __str__(self):
        return "Вы уже стреляли в эту клетку!"


class BoardWrongShipException(BoardException):
    pass


# __________________________________________________________________________________

class Ship:
    def __init__(self, ship_start, ship_size, ship_direct):
        self.ship_start = ship_start
        self.ship_size = ship_size
        self.ship_direct = ship_direct
        self.lives = ship_size

    @property
    def points(self):
        ship_points = []
        for i in range(self.ship_size):
            cur_x = self.ship_start.x
            cur_y = self.ship_start.y

            if self.ship_direct == 0:
                cur_x += i

            elif self.ship_direct == 1:
                cur_y += i
            ship_points.append(Points(cur_x, cur_y))

        return ship_points

    def shooten(self, shoot):
        return shoot in self.points


class Board:

    def __init__(self, hiden=False, size=6):
        self.hiden = hiden
        self.size = size

        self.count = 0  # кол -во подбитых кораблей
        self.field = [['0' for _ in range(size)] for _ in range(size)]
        self.busy = []  # занятые клетки (либо размещен корабль, либо туда стреляли)
        self.ships = []  # список кораблей доски

    def __str__(self):
        res = ""
        res += "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.field):
            res += f"\n{i + 1} | " + " | ".join(row) + " |"

        if self.hiden:
            res = res.replace('■', '0')
        return res

    def out(self, d):  # Проверка не выходит ли точка за границу доски
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    def contour(self, ship, verb=False):  # контур корабля
        near = [  # в списке указываются все сдвиги относительно нашей точки
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.points:
            for dx, dy in near:
                cur = Points(d.x + dx, d.y + dy)

                if not (self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = "."
                    self.busy.append(cur)

    def add_ship(self, ship):

        for d in ship.points:
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException()
        for d in ship.points:
            self.field[d.x][d.y] = "■"
            self.busy.append(d)

        self.ships.append(ship)
        self.contour(ship)

    def shot(self, d):
        if self.out(d):
            raise BoardOutException()

        if d in self.busy:
            raise BoardRepeatException()

        self.busy.append(d)

        for ship in self.ships:
            if d in ship.points:
                ship.lives -= 1
                self.field[d.x][d.y] = "X"
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    print("Корабль уничтожен!")
                    return True
                else:
                    print("Корабль ранен!")
                    return True

        self.field[d.x][d.y] = "."
        print("Мимо!")
        return False

    def begin(self):
        self.busy = []

    def destroy(self):
        return self.count == len(self.ships)


class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)


class Comp(Player):
    def ask(self):
        d = Points(randint(0, 5), randint(0, 5))
        print(f"Ход компьютера: {d.x + 1} {d.y + 1}")
        return d


class User(Player):

    def ask(self):
        while True:
            cords = input("Ваш ход: ").split()

            if len(cords) != 2:
                print(" Введите 2 координаты! ")
                continue

            x, y = cords

            if not (x.isdigit()) or not (y.isdigit()):
                print(" Введите числа! ")
                continue

            x, y = int(x), int(y)

            return Points(x - 1, y - 1)


class Game:
    def __init__(self, size=6):
        self.lens = [3, 2, 2, 1, 1, 1, 1]
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        co.hiden = True

        self.ai = Comp(co, pl)
        self.us = User(pl, co)

    def try_board(self):
        board = Board(size=self.size)
        attempts = 0
        for i in self.lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Points(randint(0, self.size), randint(0, self.size)), i, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def random_board(self):
        board = None
        while board is None:
            board = self.try_board()
        return board

    @staticmethod
    def greet():
        print("-------------------")
        print("  Приветствуем вас  ")
        print("      в игре       ")
        print("    морской бой    ")
        print("-------------------")
        print(" формат ввода: x y ")
        print(" x - номер строки  ")
        print(" y - номер столбца ")

    def print_boards(self):
        print("-" * 20)
        print("Доска пользователя:")
        print(self.us.board)
        print("-" * 20)
        print("Доска компьютера:")
        print(self.ai.board)

    def loop(self):
        num = 0
        while True:
            self.print_boards()
            if num % 2 == 0:
                print("-" * 20)
                print("Ходит пользователь!")
                repeat = self.us.move()
            else:
                print("-" * 20)
                print("Ходит компьютер!")
                time.sleep(randint(1, 10))
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.board.destroy():
                self.print_boards()
                print("-" * 20)
                print("Пользователь выиграл!")
                break

            if self.us.board.destroy():
                self.print_boards()
                print("-" * 20)
                print("Компьютер выиграл!")
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()


g = Game()
g.start()
