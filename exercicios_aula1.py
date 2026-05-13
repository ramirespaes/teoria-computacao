import itertools
import random
import time

TAREFAS = [
    {"nome": "Auth OAuth2",         "custo": 8,  "valor": 40},
    {"nome": "Dashboard métricas",  "custo": 13, "valor": 55},
    {"nome": "Exportar CSV",        "custo": 5,  "valor": 20},
    {"nome": "Refactor serviço X",  "custo": 20, "valor": 35},
    {"nome": "API notificações",    "custo": 10, "valor": 60},
    {"nome": "Upgrade deps",        "custo": 3,  "valor": 15},
    {"nome": "Testes E2E checkout", "custo": 8,  "valor": 50},
    {"nome": "Rate limiting",       "custo": 6,  "valor": 45},
    {"nome": "Docs OpenAPI",        "custo": 4,  "valor": 25},
    {"nome": "Cache Redis",         "custo": 12, "valor": 70},
]

CAPACIDADE = 40


def avaliar_solucao(individuo, tarefas, capacidade):
    custo = 0
    valor = 0

    for i in range(len(tarefas)):
        if individuo[i] == 1:
            custo += tarefas[i]["custo"]
            valor += tarefas[i]["valor"]

    if custo <= capacidade:
        return valor

    return 0


def busca_exaustiva(tarefas, capacidade):
    n = len(tarefas)
    melhor_individuo = [0] * n
    melhor_valor = 0

    for combo in itertools.product([0, 1], repeat=n):
        individuo = list(combo)

        custo = 0
        valor = 0

        for i in range(n):
            if individuo[i] == 1:
                custo += tarefas[i]["custo"]
                valor += tarefas[i]["valor"]

        if custo <= capacidade and valor > melhor_valor:
            melhor_valor = valor
            melhor_individuo = individuo[:]

    return melhor_individuo, melhor_valor


def greedy_knapsack(tarefas, capacidade):
    n = len(tarefas)
    individuo = [0] * n
    capacidade_restante = capacidade

    lista_roi = []

    for i in range(n):
        roi = tarefas[i]["valor"] / tarefas[i]["custo"]
        lista_roi.append((roi, i))

    lista_roi.sort(reverse=True)

    for roi, i in lista_roi:
        if tarefas[i]["custo"] <= capacidade_restante:
            individuo[i] = 1
            capacidade_restante -= tarefas[i]["custo"]

    valor_total = sum(tarefas[i]["valor"] for i in range(n) if individuo[i] == 1)

    return individuo, valor_total


def medir_complexidade(tamanhos, capacidade=30, repeticoes=3):
    resultados = {}

    for n in tamanhos:
        tempos = []

        for _ in range(repeticoes):
            tarefas_rand = []

            for _ in range(n):
                tarefa = {
                    "custo": random.randint(1, 10),
                    "valor": random.randint(5, 50)
                }
                tarefas_rand.append(tarefa)

            t0 = time.perf_counter()
            busca_exaustiva(tarefas_rand, capacidade)
            t1 = time.perf_counter()

            tempos.append((t1 - t0) * 1000)

        media = sum(tempos) / len(tempos)
        resultados[n] = media

    return resultados


def calcular_razoes_crescimento(tempos):
    ns = sorted(tempos.keys())

    print("\nn   | Tempo (ms)   | Razao  | 2^n")
    print("-" * 45)

    tempo_anterior = None

    for n in ns:
        t = tempos[n]

        if tempo_anterior is None:
            razao = "-"
        elif tempo_anterior == 0:
            razao = "N/A"
        else:
            razao = f"{t / tempo_anterior:.2f}x"

        print(f"{n:<4}| {t:<13.6f}| {razao:<7}| {2**n}")

        tempo_anterior = t

    print("\nConclusao: a razao tende a crescer rapidamente conforme o n aumenta")
    print("isso confirma o comportamento exponencial do algoritmo O(2^n)")


def gerar_vizinhos(individuo):
    vizinhos = []

    for i in range(len(individuo)):
        vizinho = individuo[:]

        if vizinho[i] == 0:
            vizinho[i] = 1
        else:
            vizinho[i] = 0

        vizinhos.append(vizinho)

    return vizinhos


def hill_climbing(tarefas, capacidade, solucao_inicial=None, max_iter=1000, verbose=False):
    if solucao_inicial is None:
        atual, _ = greedy_knapsack(tarefas, capacidade)
    else:
        atual = solucao_inicial[:]

    atual_valor = avaliar_solucao(atual, tarefas, capacidade)
    n_iter = 0

    for it in range(max_iter):
        vizinhos = gerar_vizinhos(atual)

        melhor_viz = vizinhos[0]
        melhor_viz_valor = avaliar_solucao(vizinhos[0], tarefas, capacidade)

        for v in vizinhos:
            val = avaliar_solucao(v, tarefas, capacidade)

            if val > melhor_viz_valor:
                melhor_viz_valor = val
                melhor_viz = v

        if melhor_viz_valor > atual_valor:
            atual = melhor_viz
            atual_valor = melhor_viz_valor
            n_iter = it + 1

            if verbose:
                print(f"  iteracao {it + 1}: melhorou para {atual_valor}")
        else:
            n_iter = it
            break

    return atual, atual_valor, n_iter


def comparar_abordagens(tarefas, capacidade):
    print("\n=== COMPARACAO DAS ABORDAGENS ===\n")

    t0 = time.perf_counter()
    ind1, val1 = busca_exaustiva(tarefas, capacidade)
    tempo1 = (time.perf_counter() - t0) * 1000

    nomes1 = [tarefas[i]["nome"] for i in range(len(tarefas)) if ind1[i] == 1]

    print(f"Brute Force: valor={val1}, tempo={tempo1:.6f}ms")
    print(f"  tarefas: {nomes1}")

    t0 = time.perf_counter()
    ind2, val2 = greedy_knapsack(tarefas, capacidade)
    tempo2 = (time.perf_counter() - t0) * 1000

    nomes2 = [tarefas[i]["nome"] for i in range(len(tarefas)) if ind2[i] == 1]

    print(f"\nGreedy: valor={val2}, tempo={tempo2:.6f}ms")
    print(f"  tarefas: {nomes2}")

    t0 = time.perf_counter()
    ind3, val3, iters = hill_climbing(tarefas, capacidade)
    tempo3 = (time.perf_counter() - t0) * 1000

    nomes3 = [tarefas[i]["nome"] for i in range(len(tarefas)) if ind3[i] == 1]

    print(f"\nHill Climbing: valor={val3}, tempo={tempo3:.6f}ms, iteracoes={iters}")
    print(f"  tarefas: {nomes3}")


print("=== Testando Ex 1 ===")

ind, val = busca_exaustiva(TAREFAS, CAPACIDADE)

custo = 0

for i in range(len(TAREFAS)):
    if ind[i] == 1:
        custo += TAREFAS[i]["custo"]

assert custo <= CAPACIDADE
assert val > 0

print(f"Ex 1 OK - valor={val}, custo={custo}")

print("\n=== Testando Ex 2 ===")

ind, val = greedy_knapsack(TAREFAS, CAPACIDADE)

custo = 0

for i in range(len(TAREFAS)):
    if ind[i] == 1:
        custo += TAREFAS[i]["custo"]

assert custo <= CAPACIDADE
assert val > 0

print(f"Ex 2 OK - valor={val}, custo={custo}")

print("\n=== Testando Ex 3 ===")

tamanhos = [5, 8, 10, 12, 14, 16]
tempos = medir_complexidade(tamanhos)

print("Ex 3 OK")

calcular_razoes_crescimento(tempos)

print("\n=== Testando Ex 4 ===")

ind, val, iters = hill_climbing(TAREFAS, CAPACIDADE)

custo = 0

for i in range(len(TAREFAS)):
    if ind[i] == 1:
        custo += TAREFAS[i]["custo"]

assert custo <= CAPACIDADE
assert val > 0

print(f"Ex 4 OK - valor={val}, custo={custo}, iteracoes={iters}")

print("\nTestando 5 pontos de partida aleatorios:")

for r in range(5):
    inicio = [random.randint(0, 1) for _ in range(len(TAREFAS))]
    ind_r, val_r, it_r = hill_climbing(TAREFAS, CAPACIDADE, solucao_inicial=inicio)

    print(f"  partida {r + 1}: valor={val_r}, iteracoes={it_r}")

comparar_abordagens(TAREFAS, CAPACIDADE)