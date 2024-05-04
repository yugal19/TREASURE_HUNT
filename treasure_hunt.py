import tkinter as tk
import random
from queue import Queue

EMPTY = 0
OBSTACLE = 1
TREASURE = 2
PLAYER = 3
VISITED_TREASURE = 4

class TreasureHuntGame:
    def __init__(self, size=10, num_treasures=3):
        self.size = size
        self.num_treasures = num_treasures
        self.grid = [[EMPTY] * size for _ in range(size)]
        self.generate_obstacles()
        self.place_treasures()
        self.place_player()
        self.treasures_found = 0
        self.visited_treasures = set()

    def generate_obstacles(self):
        num_obstacles = self.size ** 2 // 10
        for _ in range(num_obstacles):
            x, y = random.randint(0, self.size - 1), random.randint(0, self.size - 1)
            self.grid[x][y] = OBSTACLE

    def place_treasures(self):
        for _ in range(self.num_treasures):
            x, y = random.randint(0, self.size - 1), random.randint(0, self.size - 1)
            while self.grid[x][y] != EMPTY:
                x, y = random.randint(0, self.size - 1), random.randint(0, self.size - 1)
            self.grid[x][y] = TREASURE

    def place_player(self):
        x, y = random.randint(0, self.size - 1), random.randint(0, self.size - 1)
        while self.grid[x][y] != EMPTY:
            x, y = random.randint(0, self.size - 1), random.randint(0, self.size - 1)
        self.grid[x][y] = PLAYER
        self.player_x, self.player_y = x, y

    def bfs(self, start_x, start_y, target_treasures):
        visited = [[False] * self.size for _ in range(self.size)]
        q = Queue()
        q.put((start_x, start_y))
        visited[start_x][start_y] = True
        parent = {}
        parent[(start_x, start_y)] = None

        while not q.empty():
            x, y = q.get()
            if (x, y) in target_treasures:
                path = self.get_path(parent, (start_x, start_y), (x, y))
                return path
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.size and 0 <= ny < self.size and not visited[nx][ny] and self.grid[nx][ny] != OBSTACLE:
                    q.put((nx, ny))
                    visited[nx][ny] = True
                    parent[(nx, ny)] = (x, y)
        return None

    def find_shortest_path_to_treasures(self):
        target_treasures = set([(i, j) for i in range(self.size) for j in range(self.size) if self.grid[i][j] == TREASURE])
        return self.bfs(self.player_x, self.player_y, target_treasures)

    def get_path(self, parent, start, end):
        path = []
        while end != start:
            path.append(end)
            end = parent[end]
        path.append(start)
        return path[::-1]

    def move_player(self, direction):
        new_x, new_y = self.player_x, self.player_y
        if direction == "Up":
            new_x -= 1
        elif direction == "Down":
            new_x += 1
        elif direction == "Left":
            new_y -= 1
        elif direction == "Right":
            new_y += 1

        if 0 <= new_x < self.size and 0 <= new_y < self.size and self.grid[new_x][new_y] != OBSTACLE:
            if (new_x, new_y) in self.visited_treasures:
                self.grid[new_x][new_y] = EMPTY
                self.visited_treasures.remove((new_x, new_y))
            else:
                if self.grid[new_x][new_y] == TREASURE:
                    self.visited_treasures.add((new_x, new_y))
                    self.treasures_found += 1
                    if self.treasures_found == self.num_treasures:
                        return True  # All treasures found
                    self.grid[new_x][new_y] = VISITED_TREASURE
            self.grid[self.player_x][self.player_y] = EMPTY
            self.player_x, self.player_y = new_x, new_y
            self.grid[self.player_x][self.player_y] = PLAYER
        return False  

class GUI(tk.Tk):
    def __init__(self, game):
        super().__init__()
        self.game = game
        self.cell_width = 500 // self.game.size
        self.canvas = tk.Canvas(self, width=500, height=500, bg="white")
        self.canvas.pack()
        self.draw_grid()
        self.draw_elements()

        self.bind("<Up>", lambda event: self.move_player("Up"))
        self.bind("<Down>", lambda event: self.move_player("Down"))
        self.bind("<Left>", lambda event: self.move_player("Left"))
        self.bind("<Right>", lambda event: self.move_player("Right"))

    def draw_grid(self):
        for i in range(self.game.size):
            for j in range(self.game.size):
                color = "black"
                if self.game.grid[i][j] == OBSTACLE:
                    color = "gray"
                elif self.game.grid[i][j] == VISITED_TREASURE:
                    color = "black"
                self.canvas.create_rectangle(j * self.cell_width, i * self.cell_width,
                                             (j + 1) * self.cell_width, (i + 1) * self.cell_width,
                                             fill=color, outline="white")

    def draw_elements(self):
        for i in range(self.game.size):
            for j in range(self.game.size):
                if self.game.grid[i][j] == TREASURE:
                    self.canvas.create_rectangle(j * self.cell_width, i * self.cell_width,
                                                 (j + 1) * self.cell_width, (i + 1) * self.cell_width,
                                                 fill="yellow", outline="white")
        self.draw_player()

    def draw_player(self):
        i, j = self.game.player_x, self.game.player_y
        self.player = self.canvas.create_oval(j * self.cell_width, i * self.cell_width,
                                               (j + 1) * self.cell_width, (i + 1) * self.cell_width,
                                               fill="blue", outline="white")

    def move_player(self, direction):
        if self.game.move_player(direction):
            print("All treasures found! Game over.")
            self.destroy()
        else:
            self.canvas.delete(self.player)
            self.draw_player()

            shortest_path = self.game.find_shortest_path_to_treasures()
            if shortest_path:
                self.visualize_shortest_path(shortest_path)

    def visualize_shortest_path(self, path):
        self.canvas.delete("shortest_path")  
        x, y = path[0]
        i, j = self.game.player_x, self.game.player_y
        if (x, y) == (i, j):  
            for i in range(len(path) - 1):
                x1, y1 = path[i]
                x2, y2 = path[i + 1]
                self.canvas.create_line(y1 * self.cell_width + self.cell_width // 2,
                                         x1 * self.cell_width + self.cell_width // 2,
                                         y2 * self.cell_width + self.cell_width // 2,
                                         x2 * self.cell_width + self.cell_width // 2,
                                         fill="green", width=3, tags="shortest_path")

if __name__ == "__main__":
    game = TreasureHuntGame()
    gui = GUI(game)
    gui.mainloop()
