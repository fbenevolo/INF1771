from queue import PriorityQueue
from TreeNode import TreeNode

import time
import heapq

from colorama import init, Fore, Style

print("\033[2J")   #apaga tela
print("\033[?25l") #apaga cursor

init()

y = 0
x = 0

eventos = {
    '1': 55,
    '2': 60,
    '3': 65,
    '4': 70,
    '5': 75,
    '6': 90,
    '7': 95,
    '8': 120,
    '9': 125,
    '0': 130,
    'B': 135,
    'C': 150,
    'E': 155,
    'G': 160,
    'H': 170,
    'J': 180
}

runas = {
    
    '1': {'poder': 1.6, 'usos': 5},
    '2': {'poder': 1.4, 'usos': 5},
    '3': {'poder': 1.3, 'usos': 5},
    '4': {'poder': 1.2, 'usos': 5},
    '5': {'poder': 1.0, 'usos': 5}
}

def read_file(filename):
    global x, y
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

    return lines, start, end


def printMap(lines, actual):

    print()
    print()
    print()

    print("\033[%d;%dH" % (0, 0)) # y, x

    for j in range(y):
        for i in range(x):
            if actual[0] == i and actual[1] == j:
                print('█', end='')
            else:
                char = lines[j][i]
                if char == 'A':
                    print(Fore.BLUE + char + Style.RESET_ALL, end='')
                elif char == 'M':
                    print(Fore.YELLOW + char + Style.RESET_ALL, end='')  # Brown approximated with yellow
                elif char == 'N':
                    print(Fore.WHITE + char + Style.RESET_ALL, end='')
                elif char == 'F':
                    print(Fore.GREEN + char + Style.RESET_ALL, end='')
                elif char == 'D':
                    print(Fore.RED + char + Style.RESET_ALL, end='')
                elif char == 'R':
                    print(Fore.LIGHTBLACK_EX + char + Style.RESET_ALL, end='')  # Grey approximated with light black
                elif char == '.':
                    print(Fore.LIGHTWHITE_EX + char + Style.RESET_ALL, end='')  # Different tone of white
                else:
                    print(char, end='')

        print()

#Não está completo. Só para ter uma base 
def calculaTempoEvento(dificuldade_evento):

    if runas['1']['usos'] == 0:

        return dificuldade_evento

    tempo_do_evento = dificuldade_evento / runas['1']['poder']    

    return tempo_do_evento

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

mapa, start, end = read_file('mapa_t1_instancia.txt')

def manhattan_distance(_from, to):
    # |x2 - x1| + |y2 - y1|
    return abs(to[0] - _from[0]) + abs(to[1] - _from[1])

def busca_a_estrela(mapa):
    cost = 0
    num_iter = 0
    fronteira = PriorityQueue()
    fronteira.put(TreeNode(start, manhattan_distance(start, end), 0))
    visitados = {}

    while not fronteira.empty():
        num_iter += 1
        curr_node = fronteira.get()
        curr_coord = curr_node.get_coord() # pega a coordenada atual
        curr_dist_g = curr_node.get_value_gx() # pega a distancia percorrida até o nó atual

        printMap(mapa, curr_coord)
        #time.sleep(0.05)

        if curr_coord == end: # se chegou no final, retorna
            cost = curr_dist_g
            print(" > Encontrei a solucao em", num_iter, "iterações e custo", cost)
            return

        # se a coordenada atual tiver sido visitada e a distancia percorrida até ele for menor ou igual a percorrida até o atual, prossiga
        if curr_coord in visitados and visitados[curr_coord] <= curr_dist_g:
            continue

        visitados[curr_coord] = curr_dist_g # distancia atual vai ser a distancia percorrida até o nó atual

        for coord_vizinho in get_neighborhood(mapa, curr_coord): # para cada vizinho da posição atual
            novo_dist_g = curr_dist_g + get_value_from_map(mapa, coord_vizinho)
            if coord_vizinho not in visitados or novo_dist_g < visitados[coord_vizinho]: #
                novo_h = manhattan_distance(coord_vizinho, end) # nova distancia do nó até o fim é a distancia manhattan do nó até o fim
                no_vizinho = TreeNode(coord_vizinho, novo_dist_g + novo_h, novo_dist_g) # coloca o vizinho na fronteira com a sua heuristica calculada
                fronteira.put(no_vizinho)

    print("Nenhuma solução encontrada")
    return



busca_a_estrela(mapa)
