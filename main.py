import pygame
import math
import time
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

CELL_SIZE = 5
WINDOW_WIDTH = 0
WINDOW_HEIGHT = 0
screen = None

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
    "PATH": (0, 0, 0),  # Red for final path (changed for visibility)
}

def manhattan_distance(_from, to):
    return abs(to[0] - _from[0]) + abs(to[1] - _from[1])

def draw_map(mapa, current_node=None, visited=None, path=None):
    if not mapa:
        return
    h = len(mapa)
    w = len(mapa[0])
    screen.fill((255, 255, 255))
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
    start_node = TreeNode(origem, manhattan_distance(origem, destino), 0)
    fronteira.put(start_node)
    visitados = {}

    while not fronteira.empty():
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
                f" > Encontrei a distância em {num_iter} iterações até o fim e custo {cost}"
            )
            path = []
            node = curr_node
            while node:
                path.append(node.get_coord())
                node = node.get_parent()
            path.reverse()
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

def held_karp(M):
    n = len(M)
    dp = {}
    parent_node = {}

    Z_idx = n - 1

    for j in range(1, n):
        mask = 1 << j
        dp[mask] = {}
        parent_node[mask] = {}
        dp[mask][j] = M[0][j] if M[0][j] != float('inf') else float('inf')
        parent_node[mask][j] = 0

    for m in range(2, n):
        for mask in range(1, 1 << n):
            if bin(mask).count('1') == m:
                dp[mask] = {}
                parent_node[mask] = {}

                for j in range(1, n):
                    if mask & (1 << j):
                        prev_mask = mask ^ (1 << j)
                        min_prev_cost = float('inf')
                        best_k = -1

                        if prev_mask in dp:

                            for k in range(1, n):
                                if (prev_mask & (1 << k)) and k in dp[prev_mask] and dp[prev_mask][k] != float('inf'):
                                    cost = dp[prev_mask][k] + M[k][j]
                                    if cost < min_prev_cost:
                                        min_prev_cost = cost
                                        best_k = k

                        dp[mask][j] = min_prev_cost
                        parent_node[mask][j] = best_k


    intermediate_events_mask = ((1 << (n - 1)) - 1) ^ (1 << 0)

    min_path_cost = float('inf')
    last_event_before_Z = -1

    for k in range(1, Z_idx):
        final_state_mask = intermediate_events_mask

        if final_state_mask in dp and k in dp[final_state_mask] and dp[final_state_mask][k] != float('inf'):
            cost = dp[final_state_mask][k] + M[k][Z_idx]

            if cost < min_path_cost:
                min_path_cost = cost
                last_event_before_Z = k

    path_indices = []

    if min_path_cost == float('inf') or last_event_before_Z == -1:
        return float('inf'), []

    path_indices.append(Z_idx)


    curr_j = last_event_before_Z
    curr_mask = intermediate_events_mask

    while curr_j != 0 and curr_j != -1:
        path_indices.append(curr_j)

        if curr_mask not in parent_node or curr_j not in parent_node[curr_mask]:
            return float('inf'), []

        prev_k = parent_node[curr_mask][curr_j]
        curr_mask = curr_mask ^ (1 << curr_j)
        curr_j = prev_k

    path_indices.append(0)
    path_indices.reverse()

    return min_path_cost, path_indices

def best_path_through_all(mapa, eventos):
    all_coords_path = []
    nome_eventos = list(eventos.keys())
    M = [[0] * (len(nome_eventos) + 2) for _ in range(len(nome_eventos) + 2)]
    pontos = ['I'] + nome_eventos + ['Z']
    print("--------------")
    print("Executando o A* para encontrar os custos de todos os menores caminhos entre eventos...")
    print("--------------")
    for i in range(len(pontos)):
        for j in range(i, len(pontos)):
            cost, path = busca_a_estrela(
                mapa,
                get_coord_from_map(mapa, pontos[i]),
                get_coord_from_map(mapa, pontos[j]),
            )
            M[i][j] = cost if cost is not None else float('inf')
            M[j][i] = M[i][j] if i != j else float('inf')

    print("--------------")
    print("Matriz montada, executando Held-Karp para encontrar o menor caminho entre os eventos...")
    print("--------------")
    min_path_cost, path_indices = held_karp(M)
    path_names = [pontos[i] for i in path_indices]

    draw_map(mapa, None, None, [])


    for i in range(len(path_indices) - 1):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return min_path_cost, path_names

        start_event = pontos[path_indices[i]]
        end_event = pontos[path_indices[i + 1]]
        start_coord = get_coord_from_map(mapa, start_event)
        end_coord = get_coord_from_map(mapa, end_event)
        cost, segment_path = busca_a_estrela(mapa, start_coord, end_coord)
        if segment_path:
            if all_coords_path and segment_path:
                all_coords_path.extend(segment_path[1:])
            else:
                all_coords_path.extend(segment_path)
            draw_map(mapa, None, None, all_coords_path)
            print(f"Drawing path from {start_event} to {end_event}")
            time.sleep(0.5)

    return min_path_cost, path_names

# Read map first, then initialize pygame window
mapa, start, end = read_file("mapa_t1_instancia.txt")
WINDOW_WIDTH = len(mapa[0]) * CELL_SIZE
WINDOW_HEIGHT = len(mapa) * CELL_SIZE
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Mapa Elden Ring")

print("Encontrando o melhor caminho entre os eventos")
cost, path_names = best_path_through_all(mapa, eventos)
print("Melhor custo sem as runas:", cost)
print("Caminho encontrado (eventos):", path_names)
print('------------------------------')
print("Rodando o Simulated Annealing para encontrar o melhor uso de runas...")
solucao, custo_runas = best_simulated(eventos, runas)
print('-------------------------------')
print("Melhor solução de runas encontrada:", solucao, "com custo:", custo_runas)
print('-------------------------------')
print(f"Solução encontrada com custo total: {cost + custo_runas}")

time.sleep(60)
pygame.quit()