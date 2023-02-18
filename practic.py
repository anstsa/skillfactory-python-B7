from random import randint

# Исключения
class Exceptions(Exception):
    pass

class BoardOutException(Exceptions):
    def __str__(self):
        return "\033[31mОШИБКА!\033[0mВыход за пределы поля!"

class BuzyException(Exceptions):
    def __str__(self):
        return "\033[31mОШИБКА!\033[0mЗанято! Клетка уже открыта:"

class BadBoarException(Exceptions):
    pass

# Точки на поле
class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, n):
        return self.x == n.x and self.y == n.y
    def __repr__(self):
        return f"({self.x}, {self.y})"

#Корабли
class Ship:
    def __init__(self, nose, long, v_g):
        self.nose = nose
        self.long = long
        self.v_g = v_g
        self.live = long

    @property
    def dots(self):
        dots_ship = []
        for i in range(self.long):
            x_nose = self.nose.x
            y_nose = self.nose.y
            if self.v_g == 0:
                x_nose += i
            elif self.v_g == 1:
                y_nose += i
            dots_ship.append(Dot(x_nose, y_nose))
        return dots_ship


class Board:
    def __init__(self, hid=False):
        self.field = [['O']*6, ['O']*6, ['O']*6, ['O']*6, ['O']*6, ['O']*6]
        self.ships = []
        self.hid = hid
        self.live = 0
        self.busy = []
        self.kill = 0

    def add_ship(self, ship):
        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise BadBoarException()
        for d in ship.dots:
            self.field[d.x][d.y] = "\033[34m■\033[0m"
            self.busy.append(d)
        self.ships.append(ship)
        self.contour(ship)

    def contour(self, ship, b = False):
        around = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in around:
                coord = Dot(d.x + dx, d.y + dy)
                if not (self.out(coord)) and coord not in self.busy:
                    if b:
                       self.field[coord.x][coord.y] = "\033[34m.\033[0m"
                    self.busy.append(coord)

    def __str__(self):
        f = ""
        f += "\t\033[4m\033[35m  | 1 | 2 | 3 | 4 | 5 | 6 |\033[0m"
        for i, row in enumerate(self.field):
            f += "\n\t\033[35m" + str(i + 1) + " | \033[0m" + " | ".join(row) + " |"
        if self.hid:
            f = f.replace("■", "\033[0mO")
        return f


    def out(self, d):
        b = False if 0 <= d.x < 6 and 0 <= d.y < 6 else True
        return b

    def shot(self, d):
        if self.out(d):
            raise BoardOutException()
        if d in self.busy:
            raise BuzyException()
        self.busy.append(d)
        for ship in self.ships:
            if d in ship.dots:
                ship.live -= 1
                self.field[d.x][d.y] = "\033[31mX\033[0m"
                if ship.live == 0:
                    self.kill += 1
                    self.contour(ship, b = True)
                    print(f"\033[31m{ship.long}-палубный корабль убит!\033[0m")
                    return True
                else:
                    print("\033[31mКорабль ранен!\033[0m")
                    return True
        self.field[d.x][d.y] = "\033[34m.\033[0m"
        print("\033[34mМимо!\033[0m")
        return False

class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        pass

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except Exceptions as e:
                print(e)

class AI(Player):
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5))
        print(f"Координаты компьютера: {d.y + 1} {d.x + 1}")
        return d

class User(Player):
    def ask(self):
        while True:
            coord = input("Введите координаты через пробел: ").split()
            if len(coord) != 2:
                print("_______\n\033[31mОШИБКА!\033[0m Введите ДВЕ координаты. Например:2 2")
                continue
            if not ((coord[0].isdigit()) and (coord[1].isdigit())):
                print("_______\n\033[31mОШИБКА! Вы ввели символы.\033[0m Попробуйте числа.")
                continue
            y, x = map(int, coord)
            return Dot(x - 1, y - 1)
#класс игра
class Game:
    def __init__(self):
        self.long_ship = [3, 2, 2, 1, 1, 1, 1]
        pl = self.random_board()
        co = self.random_board()
        co.hid = True
        self.ai = AI(co, pl)
        self.us = User(pl, co)

    def random_board(self):
        board = None
        while board is None:
            board = Board()
            с = 0
            for l in self.long_ship:
                while True:
                    с += 1
                    if с > 3000:
                        return None
                    ship = Ship(Dot(randint(0, 6), randint(0, 6)), l, randint(0, 1))
                    try:
                        board.add_ship(ship)
                        break
                    except BadBoarException:
                        pass
            board.busy = []
        return board

    def greet(self):
        print('\n\t \033[34mИгра "Морской бой" \033[0m\n')
        print(" формат ввода координат: x y")
        print(" где x - номер строки  ")
        print("     y - номер столбца ")
        print("Количество короблей: 1 - 3х палубный, 2 - 2х палубные, 4 - однопалубные ")

    def loop(self):
        num = 0
        print("\033[35mДоска пользователя:\033[0m")
        print(self.us.board)
        print("\033[35mДоска компьютера:\033[0m")
        print(self.ai.board)
        while True:
            if num % 2 == 0:
                print("-" * 20)
                print("\n\033[032mВаш ход\033[0m")
                print("\033[35mДоска компьютера:\033[0m")
                print(self.ai.board)
                repeat = self.us.move()

            else:
                print("-" * 20)
                print("\n\033[032mХодит компьютер\033[0m")
                print("\033[35mДоска пользователя:\033[0m")
                print(self.us.board)
                repeat = self.ai.move()


            if repeat:
                num -= 1
            if self.ai.board.kill == 7:
                print("-" * 20)
                print("ПОБЕДА!!! Пользователь выиграл!")
                break
            if self.us.board.kill == 7:
                print("-" * 20)
                print("ПОБЕДА!!! Компьютер выиграл!")
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()

g = Game()
g.start()