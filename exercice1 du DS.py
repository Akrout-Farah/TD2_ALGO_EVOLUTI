import random

LABYRINTHE = [
    [0, 1, 0, 0, 1, 0, 0, 0, 0, 0],
    [0, 1, 0, 0, 1, 0, 1, 1, 1, 1],
    [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
    [1, 1, 1, 0, 1, 0, 1, 0, 1, 0],
    [0, 0, 0, 0, 0, 0, 1, 0, 1, 0],
    [0, 0, 1, 1, 1, 0, 1, 0, 1, 0],
    [0, 1, 0, 0, 0, 0, 0, 0, 1, 0],
    [0, 1, 0, 1, 0, 1, 0, 0, 0, 0],
    [0, 1, 0, 1, 0, 1, 0, 1, 1, 1],
    [0, 1, 0, 1, 0, 1, 0, 0, 0, 0]
]

TAILLE = 10
DEPART = (0, 0)
SORTIE = (9, 9)

LONGUEUR = 60
TAILLE_POP = 100
NB_GENERATIONS = 1000
PROBA_CROISEMENT = 0.9
PROBA_MUTATION = 0.05

DEPLACEMENTS = {
    0: (-1, 0),
    1: (1, 0),
    2: (0, -1),
    3: (0, 1)
}

NOMS = {
    0: "Haut",
    1: "Bas",
    2: "Gauche",
    3: "Droite"
}


def creer_individu():
    return [random.randint(0, 3) for _ in range(LONGUEUR)]


def parcourir(individu):
    position = DEPART
    chemin = [position]

    for gene in individu:
        dl, dc = DEPLACEMENTS[gene]

        nouvelle = (position[0] + dl, position[1] + dc)

        if not (0 <= nouvelle[0] < TAILLE and 0 <= nouvelle[1] < TAILLE):
            break

        if LABYRINTHE[nouvelle[0]][nouvelle[1]] == 1:
            break

        if nouvelle in chemin:
            break

        position = nouvelle
        chemin.append(position)

        if position == SORTIE:
            return position, chemin, True

    return position, chemin, False


def fitness(individu):
    position, _, _ = parcourir(individu)

    return abs(position[0] - SORTIE[0]) + abs(position[1] - SORTIE[1])



def selection(population):
    scores = [1 / (1 + fitness(individu)) for individu in population]

    total = sum(scores)
    probabilites = [score / total for score in scores]

    return random.choices(population, weights=probabilites, k=1)[0]


def croisement(p1, p2):
    if random.random() < PROBA_CROISEMENT:
        point = random.randint(1, LONGUEUR - 1)

        e1 = p1[:point] + p2[point:]
        e2 = p2[:point] + p1[point:]

        return e1, e2

    return p1[:], p2[:]


def mutation(individu):
    for i in range(LONGUEUR):
        if random.random() < PROBA_MUTATION:
            individu[i] = random.randint(0, 3)

    return individu


def algorithme_genetique():
    population = [creer_individu() for _ in range(TAILLE_POP)]
    meilleur = min(population, key=fitness)

    for generation in range(NB_GENERATIONS):

        meilleur = min(population + [meilleur], key=fitness)

        if fitness(meilleur) == 0:
            print("Sortie trouvée à la génération", generation)
            return meilleur

        nouvelle_population = [meilleur[:]]

        while len(nouvelle_population) < TAILLE_POP:
            p1 = selection(population)
            p2 = selection(population)

            e1, e2 = croisement(p1, p2)

            nouvelle_population.append(mutation(e1))
            nouvelle_population.append(mutation(e2))

        population = nouvelle_population[:TAILLE_POP]

        if generation % 20 == 0:
            print("Génération", generation,
                  "- Fitness :", fitness(meilleur))

    return meilleur


def afficher_labyrinthe(chemin):
    for i in range(TAILLE):
        ligne = ""

        for j in range(TAILLE):
            if LABYRINTHE[i][j] == 1:
                ligne += "# "
            elif (i, j) in chemin:
                ligne += "* "
            else:
                ligne += ". "

        print(ligne)


if __name__ == "__main__":

    meilleur = algorithme_genetique()

    position, chemin, reussi = parcourir(meilleur)

    print("\nPosition finale :", (position[0] + 1, position[1] + 1))
    print("Sortie atteinte :", "OUI" if reussi else "NON")
    print("Fitness finale :", fitness(meilleur))
    print("Nombre de cases parcourues :", len(chemin))

    print("\nLabyrinthe et chemin du robot :")
    afficher_labyrinthe(chemin)

    print("\nDéplacements utilisés :")
    print(" -> ".join(NOMS[g] for g in meilleur[:len(chemin) - 1]))
