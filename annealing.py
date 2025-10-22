import random
import math

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

runas_powers = {1: 1.6, 2: 1.4, 3: 1.3, 4: 1.2, 5: 1.0}

num_uso_runas = [5] * len(runas_powers)


def calc_custo(solucao, dificuldades, runas):
    total = 0
    for i, usadas in enumerate(solucao):
        tot_poder = sum(runas[r] for r in usadas)
        total += dificuldades[i] / tot_poder
    return total


def valida_solucao(solucao):
    usos = {r: 0 for r in runas_powers.keys()}
    for usadas in solucao:
        for runa in usadas:
            usos[r] += 1
    return all(usos[r] <= 5 for r in runas_powers if r != 5 and usos[5] <= 4)


def gera_vizinho(solucao, runas):
    nova_sol = [list(run) for run in solucao]
    cidade = random.randint(0, len(solucao) - 1)
    ato = random.choice(["adicionar", "remover", "trocar"])
    runa = random.choice(list(runas.keys()))

    if ato == "adicionar":
        runas_pos = [r for r in list(runas.keys()) if r not in nova_sol[cidade]]
        if runas_pos:
            nova_sol[cidade].append(random.choice(runas_pos))
    elif ato == "remove":
        nova_sol[cidade].remove(random.choice(nova_sol[cidade]))
    elif ato == "trocar":
        if nova_sol[cidade]:
            removida = random.choice(nova_sol[cidade])
            nova = random.choice([r for r in list(runas.keys()) if r != removida])
            nova[cidade].remove(removida)
            if nova in nova_sol[cidade]:
                nova_sol[cidade].append(nova)

    return nova_sol


def sim_annealing(eventos, runas, Tini=100, Tmin=1e-3, alpha=0.95, iter=1000):
    solucao = [[random.choice(list(runas.keys()))] for _ in eventos]
    print(solucao)
    custo = calc_custo(solucao, eventos, runas)

    melhor_sol = solucao
    melhor_custo = custo

    t = Tini

    while t > Tmin:
        for _ in range(iter):
            vizinho = gera_vizinho(solucao, runas)
            if not valida_solucao(solucao):
                continue

            custo_vizinho = calc_custo(vizinho, eventos, runas)
            deltaE = custo_vizinho - custo

            if deltaE < 0 or random.random() < math.exp(-delta / t):
                solucao = vizinho
                custo = custo_vizinho
                if custo < melhor_custo:
                    melhor_sol = solucao
                    melhor_custo = custo

        t *= alpha

    return melhor_sol, melhor_custo


melhor_solucao, melhor_custo = sim_annealing(eventos, runas_powers)
print("Melhor solução encontrada:")
for i, r in enumerate(melhor_solucao):
    print(f"Cidade {i + 1}: {r}")
print("Custo total:", melhor_custo)
