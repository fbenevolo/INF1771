import pygame
import math
from queue import PriorityQueue
from colorama import init, Fore, Style
from TreeNode import TreeNode
import random
import math
import pandas as pd
from copy import deepcopy

#pygame.init()

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
    #screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    #pygame.display.set_caption("A* Pathfinding Visualization")

    return lines, start, end

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
            #pygame.draw.rect(screen, color, (i * CELL_SIZE, j * CELL_SIZE, CELL_SIZE, CELL_SIZE))
            # Draw grid lines
            pygame.draw.rect(screen, (50, 50, 50), (i * CELL_SIZE, j * CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)
    pygame.display.flip()

def get_coord_from_map(mapa, char):
    for j in range(y):
        for i in range(x):
            if mapa[j][i] == char:
                return (i, j)
    return None

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
        v = 1
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
        '''
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None, None
        '''

        num_iter += 1
        curr_node = fronteira.get()
        curr_coord = curr_node.get_coord()
        curr_dist_g = curr_node.get_value_gx()

        #draw_map(mapa, curr_node, visitados)

        if curr_coord == destino:
            cost = curr_dist_g
            #print(f" > Encontrei a distância em {num_iter} iteracoes até o fim e custo {cost}")
            # Reconstruct path for visualization
            path = []
            node = curr_node
            while node:
                path.append(node.get_coord())
                node = node.get_parent()
            path.reverse()
            # Draw final path
            #draw_map(mapa, None, visitados, path)
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

    #print("Nenhuma solução encontrada")
    #draw_map(mapa)
    return None, None

def simulated_annealing_runes(
    eventos_dificuldade,
    runas,
    movement_cost=0.0,
    max_runas_por_evento=2,
    temperatura_inicial=500.0,
    taxa_resfriamento=0.98,
    iteracoes_por_temp=150,
    temperatura_minima=1e-3,
    seed=None
):
    """
    Otimiza a distribuição de runas nos eventos usando Simulated Annealing.
    """
    if seed is not None:
        random.seed(seed)

    qtd_eventos = len(eventos_dificuldade)
    runa_ids = list(runas.keys())
    max_usos = {r: runas[r]['usos'] for r in runa_ids}
    poderes = {r: runas[r]['poder'] for r in runa_ids}

    # --- funções auxiliares ---
    def random_event_runes():
        k = random.randint(1, min(max_runas_por_evento, len(runa_ids)))
        return random.sample(runa_ids, k)

    def random_solution():

        usos = {r: 0 for r in runas.keys()}
        solucao = []

        for _ in range(qtd_eventos):
            evento_runas = []
            for _ in range(random.randint(1, 2)):  # até 2 runas por evento
                # sorteia apenas runas com menos de 5 usos
                runas_disponiveis = [r for r, u in usos.items() if u < 5]
                if not runas_disponiveis:
                    break
                escolhida = random.choice(runas_disponiveis)
                evento_runas.append(escolhida)
                usos[escolhida] += 1
            solucao.append(evento_runas)

        return solucao

    def count_uses(sol):
        counts = {r: 0 for r in runa_ids}
        for ev in sol:
            for r in ev:
                counts[r] += 1
        return counts

    from copy import deepcopy


    def repair(sol):

        sol = deepcopy(sol)

        # --- contar usos atuais ---
        usos = {r: 0 for r in runas.keys()}
        for evento in sol:
            for r in evento:
                usos[r] += 1

        # --- remover excessos ---
        for r in list(runas.keys()):
            while usos[r] > max_usos[r]:
                # escolhe evento onde a runa aparece
                candidatos = [i for i, ev in enumerate(sol) if r in ev]
                if not candidatos:
                    break
                i = random.choice(candidatos)
                if len(sol[i]) > 1:
                    sol[i].remove(r)
                    usos[r] -= 1
                else:
                    # substitui por outra runa livre
                    livres = [rr for rr, u in usos.items() if u < max_usos[rr] and rr != r]
                    if livres:
                        nova = random.choice(livres)
                        sol[i] = [nova]
                        usos[nova] += 1
                        usos[r] -= 1
                    else:
                        break

        # --- garantir que todos eventos tenham pelo menos 1 runa ---
        for evento in sol:
            if len(evento) == 0:
                livres = [r for r, u in usos.items() if u < max_usos[r]]
                if livres:
                    nova = random.choice(livres)
                    evento.append(nova)
                    usos[nova] += 1

        # --- garantir que sobre pelo menos uma runa com uso < limite ---
        if all(usos[r] >= max_usos[r] for r in runas.keys()):
            r = random.choice(list(runas.keys()))
            candidatos = [i for i, ev in enumerate(sol) if r in ev and len(ev) > 1]
            if candidatos:
                i = random.choice(candidatos)
                sol[i].remove(r)
                usos[r] -= 1
            else:
                # troca por outra runa
                alt = random.choice([x for x in runas.keys() if x != r])
                i = random.randrange(len(sol))
                sol[i] = [alt]
                usos[alt] += 1
                usos[r] = max(0, usos[r] - 1)

        return sol


    def custo_total(sol):
        total = movement_cost
        chaves_eventos = list(eventos_dificuldade.keys())

        # Garante que o número de eventos corresponde ao tamanho da solução
        if len(sol) != len(chaves_eventos):
            raise ValueError(f"O número de eventos ({len(chaves_eventos)}) não corresponde ao tamanho da solução ({len(sol)}).")

        for idx, ev in enumerate(sol):
            chave_evento = chaves_eventos[idx]     # '1', '2', '3', ..., 'J'
            dificuldade = eventos_dificuldade[chave_evento]
            soma_poder = sum(poderes[r] for r in ev)
            total += dificuldade / soma_poder
        return total    

    def vizinho(sol):
        """Gera um vizinho aleatório válido da solução atual."""
        novo = deepcopy(sol)
        i = random.randrange(qtd_eventos)  # escolhe evento aleatório

        if random.random() < 0.5:
            # Adicionar uma runa se ainda há espaço e runas disponíveis
            livres = [r for r in runa_ids if r not in novo[i]]
            if livres and len(novo[i]) < max_runas_por_evento:
                novo[i].append(random.choice(livres))
        else:
            # Remover ou substituir runa
            if len(novo[i]) > 1:
                novo[i].remove(random.choice(novo[i]))
            else:
                # Substitui completamente o evento por nova combinação
                novo[i] = random_event_runes()

        # Garante que o vizinho respeite as restrições
    
        return repair(novo)


    # --- inicialização ---
    sol_atual = repair(random_solution())
    custo_atual = custo_total(sol_atual)
    melhor_sol = deepcopy(sol_atual)
    melhor_custo = custo_atual

    T = temperatura_inicial
    historico = []

    while T > temperatura_minima:
        for _ in range(iteracoes_por_temp):
            sol_nova = vizinho(sol_atual)
            custo_novo = custo_total(sol_nova)
            delta = custo_novo - custo_atual

            # critério de aceitação
            if delta < 0 or random.random() < math.exp(-delta / T):
                sol_atual = sol_nova
                custo_atual = custo_novo
                if custo_atual < melhor_custo:
                    melhor_sol = deepcopy(sol_atual)
                    melhor_custo = custo_atual

        historico.append({'T': T, 'melhor_custo': melhor_custo})
        T *= taxa_resfriamento

    # --- resultado ---
    usos = count_uses(melhor_sol)

    return {
        'melhor_solucao': melhor_sol,
        'melhor_custo': round(melhor_custo, 2),
        'usos_runa': usos,
    }

def criaMatrizRotas(eventos):

    qtd_eventos = len(eventos) #+2 para incluir inicio e fim
    total_nos = qtd_eventos + 2

    matriz = [[math.inf for _ in range(total_nos)] for _ in range(total_nos)]

    eventos_chaves = list(eventos.keys())
    nomes = ['I'] + eventos_chaves + ['Z']
    
    

    #Ligacao entre eventos
    for i, origem in enumerate(eventos_chaves):
        for j, destino in enumerate(eventos_chaves):

            if i == j:

                matriz[i + 1][j + 1] = math.inf
            
            else:

                custo, _ = busca_a_estrela(mapa, get_coord_from_map(mapa, origem), get_coord_from_map(mapa, destino))
                if custo is not None:
                        
                    matriz[i + 1][j + 1] = custo
                    matriz[j + 1][i + 1] = custo

    #Ligacoes do inicio (I) para todos os eventos
    for j, destino in enumerate(eventos_chaves):

        custo, _ = busca_a_estrela(mapa, get_coord_from_map(mapa, 'I'), get_coord_from_map(mapa, destino))
        if custo is not None:

            matriz[0][j + 1] = custo
            matriz[j + 1][0] = custo

    #Ligacoes de todos os eventos para o fim (Z)
    for i, origem in enumerate(eventos_chaves):

        custo, _ = busca_a_estrela(mapa, get_coord_from_map(mapa, origem), get_coord_from_map(mapa, 'Z'))
        if custo is not None:
            matriz[i + 1][-1] = custo
            matriz[-1][i + 1] = custo


    matriz = pd.DataFrame(matriz, index=nomes, columns=nomes)

    return matriz

res = simulated_annealing_runes(
    eventos,
    runas,
    movement_cost=1000,
    temperatura_inicial=400,
    taxa_resfriamento=0.97,
    iteracoes_por_temp=100,
    seed=42
)


# Main execution
init()  # Initialize colorama (though not used in visualization)
mapa, start, end = read_file('mapa_t1_instancia.txt')
#cost, path = busca_a_estrela(mapa, get_coord_from_map(mapa, '1'), get_char_from_map(mapa, 'Z'))
grafo = criaMatrizRotas(eventos)

print(grafo)

#print(grafo)

'''
print("\n Melhor custo total:", res['melhor_custo'])
print(" Usos de cada runa:", res['usos_runa'])
print(" Melhor combinação encontrada:\n")
for i, ev in enumerate(res['melhor_solucao'], 1):
    print(f"  Evento {i}: {ev}")
'''
'''
# Keep window open until closed by user
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
pygame.quit()
'''
