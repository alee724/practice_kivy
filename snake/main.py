"""
My attempt at using the kivy module to make a simple snake game
"""

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ObjectProperty
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.core.window import Window
from random import randint

WIN_HEIGHT = 500
WIN_WIDTH = 500


class Grid:
    """
    Class for keeping track of where the snake is on a virtual grid and checking for overlaps
    """

    def __init__(self, side, width, height):
        self.side = side
        self.width = width
        self.height = height
        self.g_width = width // side
        self.g_height = height // side
        self.grid = [[0 for j in range(height // side)] for i in range(width // side)]

    def occupy(self, x, y):
        self.grid[x][y] = 1

    def unoccupy(self, x, y):
        self.grid[x][y] = 0

    def reset(self):
        self.grid = [
            [0 for j in range(self.height // self.side)]
            for i in range(self.width // self.side)
        ]


def point_to_grid(lst, width):
    return list(map(lambda x: (x - 15) // width // 2, list(lst)))


def grid_to_point(lst, width):
    return list(map(lambda x: ((x * width) + 15) * 2, list(lst)))


class Snake(Widget):
    """
    The snake widget that will represent the player
    """

    points = ObjectProperty([])
    direction = 0
    head = Vector(0, 0)

    def move(self, g):
        new = None
        if self.direction == 0:
            new = Vector(0, 1)
        elif self.direction == 1:
            new = Vector(1, 0)
        elif self.direction == 2:
            new = Vector(0, -1)
        else:
            new = Vector(-1, 0)
        self.head += new

        # game over
        if g.g_width <= self.head[0] or self.head[0] < 0:
            return True  # cross border
        if g.g_height <= self.head[1] or self.head[1] < 0:
            return True  # cross border
        if g.grid[self.head[0]][self.head[1]] == 1:
            return True  # there is a collision

        g.occupy(*self.head)
        g.unoccupy(*point_to_grid(self.points[-2:], self.width))
        point = grid_to_point(self.head, self.width)
        self.points = list(point) + self.points[:-2]
        return False

    def reset(self, g):
        g_width = g.g_width // 2
        g_height = g.g_height // 2

        self.head = Vector(g_width, g_height)
        tmp = []
        for i in range(3):
            g.occupy(g_width, g_height - i)
            tmp += [g_width, (g_height - i)]
        self.points = grid_to_point(tmp, self.width)

    def getTail(self):
        return self.points[-2:]

    def getHead(self):
        return self.points[0:2]


class SnakeFood(Widget):
    def generate(self, gx, gy):
        rx = randint(0, gx-1) * self.size[0] * 2
        ry = randint(0, gy-1) * self.size[0] * 2
        self.pos = rx, ry


class SnakeGame(Widget):
    snake = ObjectProperty(None)
    food = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.size = (WIN_WIDTH, WIN_HEIGHT)
        self.timer = Clock.schedule_interval(self.update, 1.0 / 5.0)
        self.grid = Grid(self.snake.width + 2, WIN_WIDTH, WIN_HEIGHT)
        self.snake.reset(self.grid)
        self.food.generate(self.grid.g_width, self.grid.g_height)

        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if keycode[1] == "left":
            self.snake.direction -= 1
        if keycode[1] == "right":
            self.snake.direction += 1
        self.snake.direction = self.snake.direction % 4

    def update(self, dt):
        tail = self.snake.getTail()
        if self.snake.move(self.grid):
            self.timer.cancel()
        if self.snake.getHead() == list(self.food.pos):
            self.snake.points += tail
            self.food.generate(self.grid.g_width, self.grid.g_height)


class SnakeApp(App):
    def build(self):
        game = SnakeGame()
        return game


if __name__ == "__main__":
    SnakeApp().run()
