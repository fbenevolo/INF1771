from queue import PriorityQueue
from TreeNode import TreeNode

import time
import heapq

print("\033[2J")   #apaga tela
print("\033[?25l") #apaga cursor


y = 0
x = 0


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
            if lines[j][i] in ('F', 'f'):
                end = (i, j)

    if not start or not end:
        raise ValueError("Start ('I'/'i') or end ('F'/'f') not found in map")

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
                print(lines[j][i], end='')

        print()



def get_value(c):
    v = -1

    if c == '.' or c == 'I' or c == 'F':
        v = 1
    elif c == 'X':
        v = -1

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

mapa, start, end = read_file('draft/mapa30.txt')

def manhattan_distance(_from, to):
    # |x2 - x1| + |y2 - y1|
    return abs(to[0] - _from[0]) + abs(to[1] - _from[1])

def busca_a_estrela(mapa):
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
        time.sleep(0.05)

        if curr_coord == end: # se chegou no final, retorna
            print(" > Encontrei a solucao em", num_iter)
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