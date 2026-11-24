import random
from math import comb

N = 5
K = 10

TAILLE_POP = 100
NB_GENERATIONS = 500
PROBA_CROISEMENT = 0.9
PROBA_MUTATION = 0.2


def creer_individu():
    return random.sample(range(N * N), K)


def vers_grille(individu):
    grille = [[0] * N for _ in range(N)]

    for case in individu:
        ligne = case // N
        colonne = case % N
        grille[ligne][colonne] = 1

    return grille


def fitness(individu):
    grille = vers_grille(individu)
    erreurs = 0

    for i in range(N):
        if sum(grille[i]) % 2 != 0:
            erreurs += 1

        if sum(grille[j][i] for j in range(N)) % 2 != 0:
            erreurs += 1

    return erreurs


def selection(population):
    candidats = random.sample(population, 3)
    return min(candidats, key=fitness)


def croisement(p1, p2):
    if random.random() > PROBA_CROISEMENT:
        return p1[:]

    enfant = p1[:K // 2]

    for case in p2:
        if case not in enfant and len(enfant) < K:
            enfant.append(case)

    while len(enfant) < K:
        case = random.randint(0, N * N - 1)

        if case not in enfant:
            enfant.append(case)

    return enfant


def mutation(individu):
    if random.random() < PROBA_MUTATION:
        position = random.randint(0, K - 1)
        nouvelle_case = random.randint(0, N * N - 1)

        while nouvelle_case in individu:
            nouvelle_case = random.randint(0, N * N - 1)

        individu[position] = nouvelle_case

    return individu


def algorithme_genetique():
    population = [creer_individu() for _ in range(TAILLE_POP)]
    meilleur = min(population, key=fitness)

    for generation in range(NB_GENERATIONS):

        meilleur = min(population + [meilleur], key=fitness)

        if fitness(meilleur) == 0:
            print("Solution trouvée à la génération", generation)
            return meilleur

        nouvelle_population = [meilleur[:]]

        while len(nouvelle_population) < TAILLE_POP:
            p1 = selection(population)
            p2 = selection(population)

            enfant = croisement(p1, p2)
            enfant = mutation(enfant)

            nouvelle_population.append(enfant)

        population = nouvelle_population

        if generation % 50 == 0:
            print("Génération", generation,
                  "- Fitness :", fitness(meilleur))

    return meilleur


def afficher_grille(individu):
    grille = vers_grille(individu)

    for ligne in grille:
        print(" ".join("●" if case == 1 else "." for case in ligne))


if __name__ == "__main__":

    if K % 2 != 0:
        raise SystemExit("K doit être pair.")

    if K >= N * N:
        raise SystemExit("K doit être inférieur à N*N.")

    if N % 2 == 1 and K > N * (N - 1):
        raise SystemExit("Aucune solution possible.")

    print("Taille de l'espace de recherche :", comb(N * N, K))

    meilleur = algorithme_genetique()

    print("\nGrille obtenue :")
    afficher_grille(meilleur)

    print("\nFitness finale :", fitness(meilleur))

    if fitness(meilleur) == 0:
        print("Solution faisable : OUI")
    else:
        print("Solution faisable : NON")
