import pygame
import time
from queue import PriorityQueue
from colorama import init, Fore, Style
from TreeNode import TreeNode

pygame.init()

# Your original global variables and setup
y = 0
x = 0

eventos = {
    '1': 55, '2': 60, '3': 65, '4': 70, '5': 75, '6': 90, '7': 95,
    '8': 120, '9': 125, '0': 130, 'B': 135, 'C': 150, 'E': 155,
    'G': 160, 'H': 170, 'J': 180
}

runas = {
    '1': {'poder': 1.6, 'usos': 5},
    '2': {'poder': 1.4, 'usos': 5},
    '3': {'poder': 1.3, 'usos': 5},
    '4': {'poder': 1.2, 'usos': 5},
    '5': {'poder': 1.0, 'usos': 5}
}

# Pygame window settings
CELL_SIZE = 5  # Size of each cell in pixels
WINDOW_WIDTH = 0  # Will be set based on map size
WINDOW_HEIGHT = 0  # Will be set based on map size
screen = None  # Pygame screen, initialized later

# Colors for different terrain types
COLORS = {
    '.': (200, 200, 200),  # Light gray for path
    'A': (0, 0, 255),      # Blue for water
    'M': (139, 69, 19),    # Brown for mountain
    'N': (255, 255, 255),  # White for snow
    'F': (0, 255, 0),      # Green for forest
    'D': (255, 0, 0),      # Red for desert
    'R': (100, 100, 100),  # Gray for rock
    'I': (0, 255, 255),    # Cyan for start
    'Z': (255, 255, 0),    # Yellow for end
    'EVENT': (255, 165, 0),  # Orange for events (1-9, 0, B, C, E, G, H, J)
    'CURRENT': (255, 0, 255),  # Magenta for current node
    'VISITED': (128, 0, 128),  # Purple for visited nodes
    'PATH': (0, 0, 0)       # Black for final path
}

# curr_cost should be a local bound passed into busca_a_estrela via max_cost;
# avoid module-level globals for pruning

def read_file(filename):
    global x, y, WINDOW_WIDTH, WINDOW_HEIGHT, screen
    with open(filename) as file:
        lines = [line.strip('\n') for line in file.readlines()]
    y = len(lines)
    x = len(lines[0]) if y > 0 else 0
    start = None
    end = None
    for j in range(y):
        for i in range(x):
            if lines[j][i] in ('I', 'i'):
                start = (i, j)
            if lines[j][i] in ('Z', 'z'):
                end = (i, j)
    if not start or not end:
        raise ValueError("Start ('I'/'i') or end ('Z'/'z') not found in map")

    # Initialize Pygame window
    WINDOW_WIDTH = x * CELL_SIZE
    WINDOW_HEIGHT = y * CELL_SIZE
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("A* Pathfinding Visualization")

    return lines, start, end

def get_coord_from_map(mapa, char):
    for j in range(y):
        for i in range(x):
            if mapa[j][i] == char:
                return (i, j)
    return None


def draw_map(mapa, current_node=None, visited=None, path=None):
    screen.fill((255, 255, 255))
    for j in range(y):
        for i in range(x):
            char = mapa[j][i]
            color = COLORS.get(char, COLORS['EVENT'] if char in eventos else (0, 0, 0))
            if path and (i, j) in path:
                color = COLORS['PATH']
            elif visited and (i, j) in visited and (i, j) != start and (i, j) != end:
                color = COLORS['VISITED']
            elif current_node and (i, j) == current_node.get_coord():
                color = COLORS['CURRENT']
            pygame.draw.rect(screen, color, (i * CELL_SIZE, j * CELL_SIZE, CELL_SIZE, CELL_SIZE))
            # Draw grid lines
            #pygame.draw.rect(screen, (50, 50, 50), (i * CELL_SIZE, j * CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)
    pygame.display.flip()

def calculaTempoEvento(dificuldade_evento):
    return dificuldade_evento

def get_value(c):
    v = -1
    if c == '.' or c == 'I' or c == 'Z':
        v = 1
    elif c == 'M':
        v = 50
    elif c == 'A':
        v = 20
    elif c == 'N':
        v = 15
    elif c == 'D':
        v = 8
    elif c == 'R':
        v = 5
    elif c == 'X':
        v = -1
    elif c in eventos:
        v = calculaTempoEvento(eventos[c])
    return v

def get_char_from_map(mapa, coord):
    return mapa[coord[1]][coord[0]]

def get_value_from_map(mapa, coord):
    return get_value(get_char_from_map(mapa, coord))

def add_valid_pos(nb, mapa, coord):
    if get_value_from_map(mapa, coord) > -1:
        nb.append(coord)

def get_neighborhood(mapa, coord):
    nb = []
    if coord[0] == 0:
        add_valid_pos(nb, mapa, (coord[0] + 1, coord[1]))
    elif coord[0] == x - 1:
        add_valid_pos(nb, mapa, (coord[0] - 1, coord[1]))
    else:
        add_valid_pos(nb, mapa, (coord[0] + 1, coord[1]))
        add_valid_pos(nb, mapa, (coord[0] - 1, coord[1]))
    if coord[1] == 0:
        add_valid_pos(nb, mapa, (coord[0], coord[1] + 1))
    elif coord[1] == y - 1:
        add_valid_pos(nb, mapa, (coord[0], coord[1] - 1))
    else:
        add_valid_pos(nb, mapa, (coord[0], coord[1] + 1))
        add_valid_pos(nb, mapa, (coord[0], coord[1] - 1))
    return nb

def manhattan_distance(_from, to):
    return abs(to[0] - _from[0]) + abs(to[1] - _from[1])

def busca_a_estrela(mapa, origem, destino):
    cost = 0
    num_iter = 0
    fronteira = PriorityQueue()
    # Use your TreeNode with parent for path tracing
    start_node = TreeNode(origem, manhattan_distance(origem, destino), 0)
    fronteira.put(start_node)
    visitados = {}

    while not fronteira.empty():
        # Handle Pygame events to allow closing the window
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None, None

        num_iter += 1
        curr_node = fronteira.get()
        curr_coord = curr_node.get_coord()
        curr_dist_g = curr_node.get_value_gx()

        draw_map(mapa, curr_node, visitados)

        if curr_coord == destino:
            cost = curr_dist_g
            print(f" > Encontrei a distância em {num_iter} iteracoes até o fim e custo {cost}")
            # Reconstruct path for visualization
            path = []
            node = curr_node
            while node:
                path.append(node.get_coord())
                node = node.get_parent()
            path.reverse()
            # Draw final path
            draw_map(mapa, None, visitados, path)
            return cost, path

        if curr_coord in visitados and visitados[curr_coord] <= curr_dist_g:
            continue

        visitados[curr_coord] = curr_dist_g

        for coord_vizinho in get_neighborhood(mapa, curr_coord):
            novo_dist_g = curr_dist_g + get_value_from_map(mapa, coord_vizinho)
            if coord_vizinho not in visitados or novo_dist_g < visitados[coord_vizinho]:
                novo_h = manhattan_distance(coord_vizinho, destino)
                # Create neighbor node with current node as parent
                no_vizinho = TreeNode(coord_vizinho, novo_dist_g + novo_h, novo_dist_g)
                no_vizinho.set_parent(curr_node)
                fronteira.put(no_vizinho)

    print("Nenhuma solução encontrada")
    draw_map(mapa)
    return None, None





mapa, start, end = read_file('mapa_t1_instancia.txt')
cost, path = busca_a_estrela(mapa, get_coord_from_map(mapa, '1'), get_coord_from_map(mapa, 'Z'))


# Keep window open until closed by user
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
pygame.quit()