import pygame
from queue import PriorityQueue
from colorama import init, Fore, Style
from TreeNode import TreeNode
from fileHelper import read_file
from mapHelper import (
    get_value_from_map,
    get_char_from_map,
    get_coord_from_map,
    get_neighborhood,
    eventos,
)
from annealing import best_simulated


pygame.init()


eventos = {
    "1": 55,
    "2": 60,
    "3": 65,
    "4": 70,
    "5": 75,
    "6": 90,
    "7": 95,
    "8": 120,
    "9": 125,
    "0": 130,
    "B": 135,
    "C": 150,
    "E": 155,
    "G": 160,
    "H": 170,
    "J": 180,
}

runas = {1: 1.6, 2: 1.4, 3: 1.3, 4: 1.2, 5: 1.0}

num_uso_runas = [5] * len(runas)

# Pygame window settings
CELL_SIZE = 5  # Size of each cell in pixels
WINDOW_WIDTH = 0  # Will be set based on map size
WINDOW_HEIGHT = 0  # Will be set based on map size
screen = None  # Pygame screen, initialized later

# Colors for different terrain types
COLORS = {
    ".": (200, 200, 200),  # Light gray for path
    "A": (0, 0, 255),  # Blue for water
    "M": (139, 69, 19),  # Brown for mountain
    "N": (255, 255, 255),  # White for snow
    "F": (0, 255, 0),  # Green for forest
    "D": (255, 0, 0),  # Red for desert
    "R": (100, 100, 100),  # Gray for rock
    "I": (0, 255, 255),  # Cyan for start
    "Z": (255, 255, 0),  # Yellow for end
    "EVENT": (255, 165, 0),  # Orange for events (1-9, 0, B, C, E, G, H, J)
    "CURRENT": (255, 0, 255),  # Magenta for current node
    "VISITED": (128, 0, 128),  # Purple for visited nodes
    "PATH": (0, 0, 0),  # Black for final path
}


def manhattan_distance(_from, to):
    return abs(to[0] - _from[0]) + abs(to[1] - _from[1])


def draw_map(mapa, current_node=None, visited=None, path=None):
    # mapa is list of strings; compute size
    if not mapa:
        return
    h = len(mapa)
    w = len(mapa[0])
    # clear
    screen.fill((255, 255, 255))
    # visited may be a dict keyed by coords
    for j in range(h):
        for i in range(w):
            char = mapa[j][i]
            if path and (i, j) in path:
                color = COLORS["PATH"]
            elif current_node and (i, j) == current_node.get_coord():
                color = COLORS["CURRENT"]
            else:
                color = COLORS.get(
                    char, COLORS["EVENT"] if char in eventos else (0, 0, 0)
                )
            pygame.draw.rect(
                screen, color, (i * CELL_SIZE, j * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            )
    pygame.display.flip()


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

        if curr_coord == destino:
            cost = curr_dist_g
            print(
                f" > Encontrei a distância em {num_iter} iteracoes até o fim e custo {cost}"
            )
            # Reconstruct path for visualization
            path = []
            node = curr_node
            while node:
                path.append(node.get_coord())
                node = node.get_parent()
            path.reverse()
            # Draw final path
            try:
                draw_map(mapa, None, visitados, path)
                pygame.time.delay(150)
            except Exception:
                pass
            return cost, path

        if curr_coord in visitados and visitados[curr_coord] <= curr_dist_g:
            continue

        visitados[curr_coord] = curr_dist_g

        for coord_vizinho in get_neighborhood(mapa, curr_coord):
            novo_dist_g = curr_dist_g + get_value_from_map(mapa, coord_vizinho)
            if coord_vizinho not in visitados or novo_dist_g < visitados[coord_vizinho]:
                novo_h = manhattan_distance(coord_vizinho, destino)
                no_vizinho = TreeNode(coord_vizinho, novo_dist_g + novo_h, novo_dist_g)
                no_vizinho.set_parent(curr_node)
                fronteira.put(no_vizinho)

    print("Nenhuma solução encontrada")
    return None, None


def best_path_through_all(mapa, eventos):
    # tot_cost = 0
    # paths = []
    # nome_eventos = list(eventos.keys())
    # M = [[0] * (len(nome_eventos) + 2) for _ in range(len(nome_eventos) + 2)]
    # pontos = ['I'] +  nome_eventos + ['Z']
    # for i in range(0, len(pontos)):
    #     for j in range(i, len(pontos)):
    #         cost, path = busca_a_estrela(
    #             mapa,
    #             get_coord_from_map(mapa, pontos[i]),
    #             get_coord_from_map(mapa, pontos[j]),
    #         )
    #         M[i][j] = cost
    #         if i != j:
    #             M[j][i] = cost
    #         else:
    #             M[j][i] = None

    # print(M)

    tot_cost = 0
    paths = []
    nome_eventos = list(eventos.keys())
    for i in range(1, len(nome_eventos)):
        cost, path = busca_a_estrela(
            mapa,
            get_coord_from_map(mapa, nome_eventos[i - 1]),
            get_coord_from_map(mapa, nome_eventos[i]),
        )

        tot_cost += cost if cost else 0
        paths.append(path)

    return tot_cost, paths


# Read map first, then initialize pygame window
mapa, start, end = read_file("mapa_t1_instancia.txt")
WINDOW_WIDTH = len(mapa[0]) * CELL_SIZE
WINDOW_HEIGHT = len(mapa) * CELL_SIZE
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Mapa Elden Ring")

print("Encontrando o melhor caminho entre os eventos")
cost, paths = best_path_through_all(mapa, eventos)
print("Melhor custo sem as runas:", cost)
print('------------------------------')
print("Rodando o Simulated Annealing para encontrar o melhor uso de runas...")
solucao, custo_runas = best_simulated(eventos, runas)
print('-------------------------------')
print("Melhor solucao de runas encontrada:", solucao, "com custo:", custo_runas)
print('-------------------------------')
draw_map(mapa, None, None, [path for path in paths])
print(f"Solução encontrada com custo total: {cost + custo_runas} ")

# Keep window open until user closes it
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
pygame.quit()
