y = 0
x = 0

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


def get_value(c):
    v = -1
    if c == "." or c == "I" or c == "Z":
        v = 1
    elif c == "M":
        v = 50
    elif c == "A":
        v = 20
    elif c == "N":
        v = 15
    elif c == "D":
        v = 8
    elif c == "R":
        v = 5
    elif c == "X":
        v = -1
    elif c in eventos:
        v = 0
    return v


def get_char_from_map(mapa, coord):
    return mapa[coord[1]][coord[0]]


def get_value_from_map(mapa, coord):
    return get_value(get_char_from_map(mapa, coord))


def get_coord_from_map(mapa, char):
    # iterate rows directly and return coordinates as (x, y)
    for j, row in enumerate(mapa):
        for i, c in enumerate(row):
            if c == char:
                return (i, j)
    return None


def add_valid_pos(nb, mapa, coord):
    if get_value_from_map(mapa, coord) > -1:
        nb.append(coord)


def get_neighborhood(mapa, coord):
    nb = []
    # compute map bounds from provided mapa (avoid module-level x,y)
    h = len(mapa)
    w = len(mapa[0]) if h > 0 else 0

    x0, y0 = coord
    # left/right
    if x0 - 1 >= 0:
        add_valid_pos(nb, mapa, (x0 - 1, y0))
    if x0 + 1 < w:
        add_valid_pos(nb, mapa, (x0 + 1, y0))
    # up/down
    if y0 - 1 >= 0:
        add_valid_pos(nb, mapa, (x0, y0 - 1))
    if y0 + 1 < h:
        add_valid_pos(nb, mapa, (x0, y0 + 1))
    return nb


def manhattan_distance(_from, to):
    return abs(to[0] - _from[0]) + abs(to[1] - _from[1])
