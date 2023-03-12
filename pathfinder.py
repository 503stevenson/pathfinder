from ast import Lambda
import sys
import time
import pygame
import math
from queue import PriorityQueue

WIDTH = 800
WIN = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("Path Finding Algorithm")

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 255, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165 ,0)
GREY = (128, 128, 128)
TURQUOISE = (64, 224, 208)

class Box:
    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.x = row * width
        self.y = col * width
        self.color = WHITE
        self.neighbors = []
        self.width = width
        self.total_rows = total_rows

    def getPosition(self):
        return self.row, self.col
    
    def isClosed(self):
        return self.color == RED
    
    def isOpen(self):
        return self.color == GREEN
    
    def isWall(self):
        return self.color == BLACK
    
    def isStart(self):
        return self.color == ORANGE
    
    def isEnd(self):
        return self.color == TURQUOISE
    
    def isBarrier(self):
        return self.color == BLACK
    
    def isPath(self):
        return self.color == PURPLE
    
    def reset(self):
        self.color = WHITE

    def makeClosed(self):
        self.color = RED
    
    def makeOpen(self):
        self.color = GREEN
    
    def makeBarrier(self):
        self.color = BLACK
    
    def makeStart(self):
        self.color = ORANGE

    def makeEnd(self):
        self.color = TURQUOISE

    def makePath(self):
        self.color = PURPLE

    def draw(self,win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

    def updateNeighbors(self, grid):
        self.neighbors = []
        #down
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].isBarrier():
            self.neighbors.append(grid[self.row + 1][self.col])
        #up
        if self.row > 0 and not grid[self.row - 1][self.col].isBarrier():
            self.neighbors.append(grid[self.row - 1][self.col])
        #left
        if self.col > 0 and not grid[self.row][self.col - 1].isBarrier():
            self.neighbors.append(grid[self.row][self.col - 1])
        #right
        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].isBarrier():
            self.neighbors.append(grid[self.row][self.col + 1])

    def __lt__(self, other):
        return False
    
def h(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)

def showClearPath(draw, grid):
    for row in grid:
        for box in row:
            if not(box.isStart() or box.isEnd() or box.isPath()):
                box.reset()
    draw()

def reconstructPath(cameFrom, start, current, draw):
    end = current
    while current in cameFrom:
        current = cameFrom[current]
        if current != start and current != end:
            current.makePath()
            draw()

def algorithm(draw, grid, start, end):
    count = 0
    openSet = PriorityQueue()
    openSet.put((0, count, start))
    cameFrom = {}
    gScore = {box: float("inf") for row in grid for box in row}
    gScore[start] = 0
    fScore = {box: float("inf") for row in grid for box in row}
    fScore[start] = h(start.getPosition(), end.getPosition())
    openSetHash = {start}
    while not openSet.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        current = openSet.get()[2]
        openSetHash.remove(current)
        if current == end:
            reconstructPath(cameFrom, start, end, draw)
            return True
        for neighbor in current.neighbors:
            temp_g_score = gScore[current] + 1
            if temp_g_score < gScore[neighbor]:
                cameFrom[neighbor] = current
                gScore[neighbor] = temp_g_score
                fScore[neighbor] = temp_g_score + h(neighbor.getPosition(), end.getPosition())
                if neighbor not in openSetHash:
                    count += 1
                    openSet.put((fScore[neighbor], count, neighbor))
                    openSetHash.add(neighbor)
                    if neighbor != end:    
                        neighbor.makeOpen()

        draw()
        if current != start:
            current.makeClosed() 
    return False

def makeGrid(rows, width):
    grid = []
    gap = width // rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            box = Box(i, j, gap, rows)
            grid[i].append(box)
    return grid

def drawGrid(win, rows, width):
    gap = width // rows
    for i in range(rows):
        pygame.draw.line(win, GREY, (0, i * gap), (width, i * gap))
    for i in range(rows):
        pygame.draw.line(win, GREY, (i * gap, 0), (i * gap, width))

def draw(win, grid, rows, width):
    win.fill(WHITE)
    for row in grid:
        for box in row:
            box.draw(win)

    drawGrid(win, rows, width)
    pygame.display.update()

def getClickedPos(pos, rows, width):
    gap = width // rows
    y, x = pos
    row = y // gap
    col = x // gap
    return row, col

def main(win, width):
    ROWS = 50
    grid = makeGrid(ROWS, width)
    start = None
    end = None
    run = True
    started = False

    while run:
        draw(win, grid, ROWS, width)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if started:
                continue
            if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()
                row, col = getClickedPos(pos, ROWS, width)
                box = grid[row][col]
                if not start and box != end:
                    start = box
                    start.makeStart()
                elif not end and box != start:
                    end = box
                    box.makeEnd()
                elif box != start and box != end:
                    box.makeBarrier()

            elif pygame.mouse.get_pressed()[2]:
                pos = pygame.mouse.get_pos()
                row, col = getClickedPos(pos, ROWS, width)
                box = grid[row][col]
                box.reset()
                if box == start:
                    start = None
                if box == end:
                    end = None
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not started:
                    for row in grid:
                        for box in row:
                            box.updateNeighbors(grid)
                    algorithm(lambda: draw(win, grid, ROWS, width), grid, start, end)
                    time.sleep(1)
                    showClearPath(lambda: draw(win, grid, ROWS, width), grid)
            
                if event.key == pygame.K_BACKSPACE:
                    sys.exit()

                if event.key == pygame.K_RETURN:
                    for row in grid:
                        for box in row:
                            box.reset()
                    start = None
                    end = None

    pygame.quit()

main(WIN, WIDTH)