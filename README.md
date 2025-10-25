# Trabalho de Inteligência Artificial

## Objetivo do Projeto

O projeto tem como objetivo aplicar técnicas de busca e otimização em IA para resolver um problema de navegação e decisão em um mapa com diferentes terrenos, eventos e recursos limitados (runas).
O agente deve:

1. Percorrer um mapa do ponto inicial (I) até o ponto final (Z);

2. Passar obrigatoriamente por 16 eventos com dificuldades distintas;

3. Utilizar runas mágicas, que alteram o tempo de execução e o custo do percurso;

4. Minimizar o custo total da rota, analisando combinações possíveis de runas e eventos.

## Execução do Algoritmo A*

### Funções principais

1. busca_a_estrela(mapa, origem, destino)

Implementa o algoritmo A* para encontrar o caminho mais curto entre dois pontos no mapa.

* Utiliza a distância de Manhattan como heurística;

* Considera os custos diferentes de cada tipo de terreno;

* Retorna o custo total e o caminho percorrido;

* Mantém uma lista de nós visitados para otimização e reconstrução da rota.

2. get_value(c)

Define o custo de movimento para cada tipo de célula do mapa

3. held_karp

4. best_path_through_all

## Otimização via Simulated Annealing

Cada um dos 16 eventos tem uma dificuldade, e há 5 tipos de runas, cada uma com um poder e uma quantidade limitada de uso (5x).
O objetivo do algoritmo é encontrar a melhor combinação de runas para todos os eventos, de modo que o custo total seja mínimo e nenhuma runa seja usada além do limite.

### Estrutura da solução

1. calc_custo

Quanto maior o poder combinado das runas, menor o custo relativo do evento.

2. gera_vizinho

Cria pequenas variações na solução atual:

* Adiciona, remove ou substitui uma runa aleatória;

* Garante que o limite de 5 usos por runa não seja excedido (via função repair).

3. valida_solucao

Corrige soluções inválidas, garantindo:

* Cada evento tenha pelo menos uma runa;

* Nenhuma runa seja usada mais que o limite.

4. sim_annealing

A temperatura decresce gradualmente, permitindo aceitar piores soluções no início (exploração), mas ficando mais restrito ao final (exploração local).




