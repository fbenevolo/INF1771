import pygame
import time
from queue import PriorityQueue
from colorama import init, Fore, Style
from TreeNode2 import TreeNode

pygame.init()

# Your original global variables and setup
y = 0
x = 0
start = None
end = None

eventos = {
    '1': 55, '2': 60, '3': 65, '4': 70, '5': 75, '6': 90, '7': 95,
    '8': 120, '9': 125, '0': 130, 'B': 135, 'C': 150, 'E': 155,
    'G': 160, 'H': 170, 'J': 180
}

runas_powers = {
    1: 1.6, 2: 1.4, 3: 1.3, 4: 1.2, 5: 1.0
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

def read_file(filename):
    global x, y, WINDOW_WIDTH, WINDOW_HEIGHT, screen, start, end # start e end globalizados
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

def draw_map(mapa, current_node=None, visited=None, path=None):
    screen.fill((255, 255, 255))
    for j in range(y):
        for i in range(x):
            char = mapa[j][i]
            color = COLORS.get(char, COLORS['EVENT'] if char in eventos else (0, 0, 0))
            if path and (i, j) in path:
                color = COLORS['PATH']
            # MODIFICADO: 'visited' agora é um dicionário complexo, precisa extrair a coordenada
            elif visited and (i, j) in {k[0] for k in visited.keys()} and (i, j) != start and (i, j) != end:
                color = COLORS['VISITED']
            elif current_node and (i, j) == current_node.get_coord():
                color = COLORS['CURRENT']
            pygame.draw.rect(screen, color, (i * CELL_SIZE, j * CELL_SIZE, CELL_SIZE, CELL_SIZE))

    pygame.display.flip()


def otimiza_evento_runas(dificuldade_evento, runas_atuais_tuple):
    global runas_powers

    # runas_list: [(1.6, 5, 0), (1.4, 5, 1), ...] -> (poder, usos_restantes, indice_runa_0_4)
    runes_list = []
    for i, usos in enumerate(runas_atuais_tuple):
        # Associa o poder ao índice da runa
        runes_list.append((runas_powers[i+1], usos, i))

    # 1. Ordena por poder, decrescente (Estratégia Gulosa)
    runes_list.sort(key=lambda x: x[0], reverse=True)

    total_power = 0.0
    runas_usadas_indices = []

    # 2. Usa todas as runas disponíveis (usos_restantes > 0)
    for power, usos, index in runes_list:
        if usos > 0:
            total_power += power
            runas_usadas_indices.append(index)

    if total_power != 0:
        tempo_gasto = dificuldade_evento / total_power

    # 3. Cria o NOVO estado de uso das runas (novo estado imutável)
    novo_runes_usage = list(runas_atuais_tuple)
    for index in runas_usadas_indices:
        novo_runes_usage[index] -= 1

    return tempo_gasto, tuple(novo_runes_usage)

def heuristica_eventos_restantes(visited_events):
    global eventos, runas_powers

    max_total_power = sum(runas_powers.values())
    tempo_min_restante = 0

    for char, dificuldade in eventos.items():
        if char not in visited_events:
            # Tempo mínimo teórico para resolver o evento restante
            tempo_min_restante += dificuldade / max_total_power

    return tempo_min_restante

def calcula_h_completa(_from, to, visited_events):
    h_mapa = manhattan_distance(_from, to) * 1
    h_eventos = heuristica_eventos_restantes(visited_events)
    return h_mapa + h_eventos

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
    elif c == 'L':
        v = 15
    elif c == 'F':
        v = 10
    elif c == 'D':
        v = 8
    elif c == 'R':
        v = 5
    elif c == 'X':
        v = -1
    elif c in eventos:
        v = 1 # Custo de entrada no tile do evento é 1 (terreno livre)
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

# A* para gerencia estado complexo e custo total
def busca_a_estrela(mapa):
    cost = 0
    num_iter = 0
    fronteira = PriorityQueue()
    initial_runes_usage = (5, 5, 5, 5, 5)
    initial_visited_events = frozenset() 
    initial_h = calcula_h_completa(start, end, initial_visited_events)
    start_node = TreeNode(start, initial_h, 0, initial_runes_usage, initial_visited_events)
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
        curr_runes_usage = curr_node.get_runes_usage()
        curr_visited_events = curr_node.get_visited_events()
        state_key = curr_node.get_state_key()

        # Draw current state (visualization)
        draw_map(mapa, curr_node, visitados)

        if state_key in visitados and visitados[state_key] <= curr_dist_g:
            continue

        visitados[state_key] = curr_dist_g

        if curr_coord == end:
            # All 16 events visited
            all_events_visited = len(curr_visited_events) == len(eventos)
            # At least one rune with usage >= 1
            rune_preserved = any(usage >= 1 for usage in curr_runes_usage)

            if all_events_visited and rune_preserved:
                cost = curr_dist_g
                print(f" > Encontrei a solucao em {num_iter} iteracoes e custo {cost}")

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

            continue

        if curr_coord in visitados and visitados[curr_coord] <= curr_dist_g:
            continue

        for coord_vizinho in get_neighborhood(mapa, curr_coord):
            char_vizinho = get_char_from_map(mapa, coord_vizinho)
            custo_terreno = get_value(char_vizinho)

            novo_runes_usage = curr_runes_usage
            novo_visited_events = curr_visited_events
            tempo_evento = 0

            if char_vizinho in eventos and char_vizinho not in curr_visited_events:
                dificuldade = eventos[char_vizinho]
                tempo_evento, novo_runes_usage = otimiza_evento_runas(
                    dificuldade, curr_runes_usage
                )
                novo_visited_events = curr_visited_events.union({char_vizinho})

            # Custo g(x) total (Terreno + Evento)
            novo_dist_g = curr_dist_g + custo_terreno + tempo_evento
            novo_h = calcula_h_completa(coord_vizinho, end, novo_visited_events)

            no_vizinho = TreeNode(
                coord_vizinho,
                novo_dist_g + novo_h, # f(x)
                novo_dist_g,          # g(x)
                novo_runes_usage,
                novo_visited_events
            )
            no_vizinho.set_parent(curr_node)

            novo_state_key = no_vizinho.get_state_key()

            # Checagem de estado visitado complexo
            if novo_state_key not in visitados or novo_dist_g < visitados[novo_state_key]:
                fronteira.put(no_vizinho)

    print("Nenhuma solução encontrada")
    draw_map(mapa)  # Draw final map state
    return None, None

# Main execution
init()  #
try:
    mapa, start, end = read_file('mapa_t1_instancia.txt')
    cost, path = busca_a_estrela(mapa)
except FileNotFoundError:
    print("Erro: O arquivo 'mapa_t1_instancia.txt' não foi encontrado.")


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
pygame.quit()