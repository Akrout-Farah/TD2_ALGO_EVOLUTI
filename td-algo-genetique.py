#
# cedule.py — Cédule de maintenance de centrales électriques
# Algorithme génétique : sélection par loterie, croisement, 3 mutations comparées
#

import itertools
import random
import statistics

# ---------------------------------------------------------------------------
# 1. Données du problème
# ---------------------------------------------------------------------------
CAPACITES = [20, 15, 35, 40, 15, 15, 10]    # MW de chaque unité
DUREES = [2, 2, 1, 1, 1, 1, 1]              # intervalles de maintenance requis
DEMANDES = [80, 90, 65, 70]                 # MW demandés par intervalle
CAPACITE_TOTALE = sum(CAPACITES)            # 150 MW
NB_UNITES = len(CAPACITES)
NB_INTERVALLES = len(DEMANDES)


def genes_unite(duree):
    """Gènes de 4 bits valides pour une unité (intervalles consécutifs).
    durée 2 : 1100, 0110, 0011 ; durée 1 : 1000, 0100, 0010, 0001."""
    genes = []
    for debut in range(NB_INTERVALLES - duree + 1):
        bits = ["0"] * NB_INTERVALLES
        bits[debut:debut + duree] = ["1"] * duree
        genes.append("".join(bits))
    return genes


GENES_VALIDES = [genes_unite(d) for d in DUREES]

# Unités ayant la même durée (pour la mutation par échange)
GROUPES = [[u for u in range(NB_UNITES) if DUREES[u] == d]
           for d in sorted(set(DUREES))]


# ---------------------------------------------------------------------------
# 2. Évaluation d'un chromosome
# ---------------------------------------------------------------------------
def calculer_reserves(chromosome):
    """Réserve = capacité totale - puissance en maintenance - demande."""
    resultat = []
    for t in range(NB_INTERVALLES):
        en_maintenance = sum(CAPACITES[u] for u in range(NB_UNITES)
                             if chromosome[u][t] == "1")
        resultat.append(CAPACITE_TOTALE - en_maintenance - DEMANDES[t])
    return resultat


def fitness(chromosome):
    """Performance = plus petite réserve (0 si une réserve est négative)."""
    return max(0, min(calculer_reserves(chromosome)))


# ---------------------------------------------------------------------------
# 3. Population initiale
# ---------------------------------------------------------------------------
def creer_individu():
    return [random.choice(GENES_VALIDES[u]) for u in range(NB_UNITES)]


def creer_population(taille):
    return [creer_individu() for _ in range(taille)]


# ---------------------------------------------------------------------------
# 4. Sélection par loterie (roulette)
# ---------------------------------------------------------------------------
def selection_loterie(population, scores):
    """Chance d'être choisi proportionnelle à la fitness.
    Si toutes les fitness sont nulles, tirage uniforme."""
    total = sum(scores)
    if total == 0:
        return random.choice(population)
    tirage = random.uniform(0, total)
    cumul = 0
    for individu, score in zip(population, scores):
        cumul += score
        if cumul >= tirage:
            return individu
    return population[-1]


# ---------------------------------------------------------------------------
# 5. Croisement (un point, toujours entre deux blocs de 4 bits)
# ---------------------------------------------------------------------------
def croisement(parent1, parent2):
    coupure = random.randint(1, NB_UNITES - 1)
    return (parent1[:coupure] + parent2[coupure:],
            parent2[:coupure] + parent1[coupure:])


# ---------------------------------------------------------------------------
# 6. Mutations (toujours sur des blocs entiers -> cédule toujours valide)
# ---------------------------------------------------------------------------
def mutation_inversion(chromosome):
    """Inverse l'ordre des 4 bits d'un gène : 1100 -> 0011, 1000 -> 0001.
    Limite : 0110 reste 0110, et 0100 / 0010 ne font que s'échanger."""
    c = chromosome[:]
    u = random.randrange(NB_UNITES)
    c[u] = c[u][::-1]
    return c


def mutation_remplacement(chromosome):
    """Remplace un gène par une autre configuration valide de la même unité
    (comme sur la diapo : 0001 -> 0100)."""
    c = chromosome[:]
    u = random.randrange(NB_UNITES)
    c[u] = random.choice([g for g in GENES_VALIDES[u] if g != c[u]])
    return c


def mutation_echange(chromosome):
    """Échange les gènes de deux unités qui ont la même durée de maintenance
    (la cédule reste valide car les gènes sont compatibles)."""
    c = chromosome[:]
    groupe = random.choice([g for g in GROUPES if len(g) >= 2])
    i, j = random.sample(groupe, 2)
    c[i], c[j] = c[j], c[i]
    return c


MUTATIONS = {
    "inversion": mutation_inversion,
    "remplacement": mutation_remplacement,
    "échange": mutation_echange,
}


# ---------------------------------------------------------------------------
# 7. Boucle principale de l'algorithme génétique
# ---------------------------------------------------------------------------
def algorithme_genetique(mutation=mutation_inversion, taille_pop=50,
                         generations=100, p_croisement=0.8, p_mutation=0.1,
                         graine=None):
    """Retourne (meilleur chromosome, sa fitness, historique par génération)."""
    if graine is not None:
        random.seed(graine)

    population = creer_population(taille_pop)
    meilleur = max(population, key=fitness)
    historique = []

    for _ in range(generations):
        scores = [fitness(ind) for ind in population]

        courant = population[scores.index(max(scores))]
        if fitness(courant) > fitness(meilleur):
            meilleur = courant
        historique.append(fitness(meilleur))

        nouvelle = [meilleur]                      # élitisme
        while len(nouvelle) < taille_pop:
            p1 = selection_loterie(population, scores)
            p2 = selection_loterie(population, scores)

            if random.random() < p_croisement:
                e1, e2 = croisement(p1, p2)
            else:
                e1, e2 = p1[:], p2[:]

            if random.random() < p_mutation:
                e1 = mutation(e1)
            if random.random() < p_mutation:
                e2 = mutation(e2)

            nouvelle.extend([e1, e2])
        population = nouvelle[:taille_pop]

    # la dernière génération doit aussi être évaluée
    for ind in population:
        if fitness(ind) > fitness(meilleur):
            meilleur = ind

    return meilleur, fitness(meilleur), historique


# ---------------------------------------------------------------------------
# 8. Vérification : optimum exact par force brute (3 x 3 x 4^5 = 9216 cédules)
# ---------------------------------------------------------------------------
def optimum_force_brute():
    meilleur, f_max = None, -1
    for combinaison in itertools.product(*GENES_VALIDES):
        chromosome = list(combinaison)
        f = fitness(chromosome)
        if f > f_max:
            meilleur, f_max = chromosome, f
    return meilleur, f_max


# ---------------------------------------------------------------------------
# 9. Affichage et expériences
# ---------------------------------------------------------------------------
def afficher(chromosome):
    print("  Chromosome :", " ".join(chromosome))
    for u, gene in enumerate(chromosome, start=1):
        intervalles = [str(t + 1) for t in range(NB_INTERVALLES) if gene[t] == "1"]
        print(f"    Unité {u} ({CAPACITES[u - 1]} MW) : "
              f"maintenance aux intervalles {', '.join(intervalles)}")
    print("  Réserves :", calculer_reserves(chromosome))
    print("  Fitness (plus petite réserve) :", fitness(chromosome), "MW")


def fitness_moyenne(nb_essais, **params):
    return statistics.mean(
        algorithme_genetique(graine=s, **params)[1] for s in range(nb_essais))


if __name__ == "__main__":
    # Exemple du cours : fitness attendue = 20
    print("=== Exemple du cours ===")
    afficher(["0110", "0011", "0001", "1000", "0100", "0010", "1000"])

    opt, f_opt = optimum_force_brute()
    print("\n=== Optimum exact (force brute) ===")
    afficher(opt)

    print("\n=== Comparaison des mutations (30 exécutions chacune) ===")
    for nom, mut in MUTATIONS.items():
        resultats = [algorithme_genetique(mutation=mut, graine=s)[1]
                     for s in range(30)]
        trouve = sum(1 for r in resultats if r == f_opt)
        print(f"  {nom:<13} moyenne = {statistics.mean(resultats):5.2f} | "
              f"min = {min(resultats)} | optimum trouvé {trouve}/30")

    print("\n=== Influence de Pc et Pm (mutation par remplacement, 10 essais) ===")
    pms = [0.05, 0.1, 0.2]
    print("  Pc \\ Pm | " + " | ".join(f"{pm:>5}" for pm in pms))
    for pc in [0.6, 0.8, 0.9]:
        ligne = [f"{fitness_moyenne(10, mutation=mutation_remplacement, p_croisement=pc, p_mutation=pm):>5.1f}"
                 for pm in pms]
        print(f"  {pc:>7} | " + " | ".join(ligne))

    print("\n=== Une exécution détaillée (mutation par inversion) ===")
    best, f, hist = algorithme_genetique(mutation=mutation_inversion, graine=42)
    afficher(best)
    print("  Meilleure fitness aux générations 1, 10, 20, 50, 100 :",
          [hist[i] for i in (0, 9, 19, 49, 99)])