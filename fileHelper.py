def read_file(filename):
    global x, y, WINDOW_WIDTH, WINDOW_HEIGHT, screen
    with open(filename) as file:
        lines = [line.strip("\n") for line in file.readlines()]
    y = len(lines)
    x = len(lines[0]) if y > 0 else 0
    start = None
    end = None
    for j in range(y):
        for i in range(x):
            if lines[j][i] in ("I", "i"):
                start = (i, j)
            if lines[j][i] in ("Z", "z"):
                end = (i, j)
    if not start or not end:
        raise ValueError("Start ('I'/'i') or end ('Z'/'z') not found in map")

    ## Initialize Pygame window
    # WINDOW_WIDTH = x * CELL_SIZE
    # WINDOW_HEIGHT = y * CELL_SIZE
    # screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    # pygame.display.set_caption("A* Pathfinding Visualization")

    return lines, start, end
