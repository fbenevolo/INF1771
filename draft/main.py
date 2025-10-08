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
    lines = None
    start = (0,0)
    end = (0,0)

    with open(filename) as file:
        lines = file.readlines()

        j = 0
        for line in lines:
            lines[j] = line.strip('\n')

            # accept upper/lower case for start/end markers
            if line.find('Z') > -1 or line.find('z') > -1:
                pos = line.find('Z') if line.find('Z') > -1 else line.find('z')
                end = (pos, j)
            if line.find('i') > -1 or line.find('I') > -1:
                pos = line.find('i') if line.find('i') > -1 else line.find('I')
                start = (pos, j)
            j += 1

    x = len(lines[0])
    y = len(lines)

    return lines, start, end


def printMap(lines, actual):

    print()
    print()
    print()

    #print("\033[%d;%dH" % (0, 0)) # y, x

    for j in range(y):
        for i in range(x):
            if actual[0] == i and actual[1] == j:
                print('█', end='')
            else:
                print(lines[j][i], end='')

        print()



def get_value(c):

    v = -1

    if c == '.' or c == 'I' or c == 'Z':
        v = 1
    else:
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

mapa, start, end = read_file('../mapa_t1_instancia.txt')

def busca_largura(mapa):

    global start

    num_iter = 0
    fronteira = []
    fronteira.append(start)
    visitados = []

    while fronteira:

        num_iter += 1
        posicao_atual = fronteira.pop(0)
        visitados.append(posicao_atual)

        printMap(mapa, posicao_atual)
        time.sleep(0.1)

        if posicao_atual == end:
            print(" > Encontrei a solucao em", num_iter)
            return

        for vizinho in get_neighborhood(mapa, posicao_atual):

            if vizinho not in visitados:
                fronteira.append(vizinho)


def busca_profundidade(mapa):

    global start

    num_iter = 0
    fronteira = []
    fronteira.append(start)
    visitados = []

    while fronteira:

        num_iter += 1


        posicao_atual = fronteira.pop(0)
        visitados.append(posicao_atual)


        printMap(mapa, posicao_atual)
        time.sleep(0.1)

        if posicao_atual == end:
            print(" > Encontrei a solucao em", num_iter)
            return

        for vizinho in get_neighborhood(mapa, posicao_atual):

            if vizinho not in visitados:
                fronteira.append(vizinho)


def manhattan_distance(_from, to):
    # |x2 - x1| + |y2 - y1|
    return abs(to[0] - _from[0]) + abs(to[1] - _from[1])

def busca_a_estrela(mapa):

    global start

    num_iter = 0
    fronteira = PriorityQueue()
    fronteira.put(TreeNode(start, manhattan_distance(start, end), 0))
    visitados = []

    while fronteira:

        num_iter += 1
        no_arv = fronteira.get()
        distancia_atual = no_arv.get_value_gx() + manhattan_distance(no_arv.get_coord(), end)
        posicao_atual = no_arv.get_coord()
        visitados.append(posicao_atual)

        printMap(mapa, posicao_atual)
        time.sleep(0.1)

        if posicao_atual == end:
            print(" > Encontrei a solucao em", num_iter)
            return

        for vizinho in get_neighborhood(mapa, posicao_atual):

            if vizinho not in visitados:
                fronteira.put(vizinho)


busca_a_estrela(mapa)
