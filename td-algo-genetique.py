# ===========================================================================
# Cédule de maintenance de centrales électriques par algorithme génétique
#
# Un individu (chromosome) = liste de 7 gènes de 4 bits (un gène par unité).
# Exemple : ['0110', '0011', '0001', '1000', '0100', '0010', '1000']
#   - un bit à '1' : l'unité est en maintenance pendant cet intervalle
#   - un bit à '0' : l'unité fonctionne
#
# Opérateurs :
#   - sélection  : loterie (roulette) + élitisme
#   - croisement : simple (1 point), double (2 points), uniforme (masque)
#   - mutation   : remplacement d'un gène par un gène valide de la même unité
#   - probabilités : Pc (croisement) et Pm (mutation)
# ===========================================================================

import random



# 1. DONNÉES ET PARAMÈTRES

# Capacité de chaque unité (MW)
CAPACITES = [20, 15, 35, 40, 15, 15, 10]
# Demande d'énergie (MW) dans chacun des 4 intervalles
DEMANDES = [80, 90, 65, 70]

NB_GENES = len(CAPACITES)             # 7 unités = 7 gènes
NB_INTERVALLES = len(DEMANDES)        # 4 intervalles
CAPACITE_TOTALE = sum(CAPACITES)      # 150 MW

# Gènes valides pour les unités 1 et 2 (2 intervalles de maintenance consécutifs)
GROUPE1 = ['1100', '0110', '0011']
# Gènes valides pour les unités 3 à 7 (1 seul intervalle de maintenance)
GROUPE2 = ['1000', '0100', '0010', '0001']

# Paramètres de l'algorithme 
NB_INDIVIDUS = 20        # nombre d'individus par génération
NB_GENERATIONS = 20      # nombre de générations
P_CROISEMENT = 0.8       # Pc : probabilité de croiser deux parents
P_MUTATION = 0.1         # Pm : probabilité de muter un enfant


def genes_valides(position):
    """Retourne la liste des gènes valides pour l'unité située à cette position."""
    if position < 2:
        return GROUPE1
    return GROUPE2



# 2. CRÉATION DE LA POPULATION INITIALE

def creer_individu():
    """Crée un individu : un gène valide choisi au hasard pour chaque unité."""
    return [random.choice(genes_valides(i)) for i in range(NB_GENES)]


def creer_generation():
    """Crée la génération initiale (sans individus identiques)."""
    generation = []
    while len(generation) < NB_INDIVIDUS:
        individu = creer_individu()
        if individu not in generation:
            generation.append(individu)
    return generation



# 3. ÉVALUATION

def puissance_en_maintenance(individu):
    """Puissance (MW) indisponible dans chacun des 4 intervalles."""
    resultat = []
    for t in range(NB_INTERVALLES):
        total = 0
        for u in range(NB_GENES):
            total += int(individu[u][t]) * CAPACITES[u]
        resultat.append(total)
    return resultat


def reserves(individu):
    """Réserve de chaque intervalle = capacité totale - maintenance - demande."""
    puissance = puissance_en_maintenance(individu)
    return [CAPACITE_TOTALE - puissance[t] - DEMANDES[t]
            for t in range(NB_INTERVALLES)]


def score(individu):
    """Score = la plus petite réserve (0 si une réserve est négative).
    Plus le score est grand, meilleur est l'individu."""
    return max(0, min(reserves(individu)))


# 4. SÉLECTION PAR ROULETTE

    """Choisit un parent au hasard : plus le score est grand, plus l'individu
    a de chances d'être choisi. Si tous les scores sont nuls, on tire au hasard."""
    total = sum(scores)
    if total == 0:
        return random.choice(population)

    tirage = random.uniform(0, total)
    cumul = 0
    for individu, s in zip(population, scores):
        cumul += s
        if cumul >= tirage:
            return individu
    return population[-1]



# 5. CROISEMENTS
#    On croise toujours des gènes entiers (blocs de 4 bits) : les enfants
#    sont donc toujours des cédules valides.
#    Chaque fonction reçoit 2 parents et retourne 2 enfants.

def croisement_simple(parent1, parent2, position):
    """Croisement à 1 point de coupure.
       
    """
    enfant1 = parent2[:position] + parent1[position:]
    enfant2 = parent1[:position] + parent2[position:]
    return enfant1, enfant2


def croisement_double(parent1, parent2, position1, position2):
    """Croisement à 2 points de coupure : on échange la partie du milieu.
      
    """
    enfant1 = parent1[:position1] + parent2[position1:position2] + parent1[position2:]
    enfant2 = parent2[:position1] + parent1[position1:position2] + parent2[position2:]
    return enfant1, enfant2


def croisement_uniforme(parent1, parent2, masque=None):
    """Croisement uniforme : un masque de 7 bits décide, gène par gène.
       masque = 1 -> enfant1 prend le gène du parent1, enfant2 celui du parent2
       masque = 0 -> enfant1 prend le gène du parent2, enfant2 celui du parent1
       
    """
    if masque is None:
        masque = [random.randint(0, 1) for _ in range(NB_GENES)]
    enfant1 = []
    enfant2 = []
    for i in range(NB_GENES):
        if masque[i] == 1:
            enfant1.append(parent1[i])
            enfant2.append(parent2[i])
        else:
            enfant1.append(parent2[i])
            enfant2.append(parent1[i])
    return enfant1, enfant2


def croiser(parent1, parent2, type_croisement):
    """Croise deux parents avec le type choisi : "simple", "double" ou "uniforme".
    Les positions de coupure sont tirées au hasard."""
    if type_croisement == "simple":
        position = random.randint(1, NB_GENES - 1)
        return croisement_simple(parent1, parent2, position)
    if type_croisement == "double":
        pos1, pos2 = sorted(random.sample(range(1, NB_GENES), 2))
        return croisement_double(parent1, parent2, pos1, pos2)
    return croisement_uniforme(parent1, parent2)


# 6. MUTATION
#    On remplace le gène situé à la position donnée par un gène valide
#    pour cette unité (groupe 1 pour les unités 1 et 2, groupe 2 pour les autres).

def mutation(individu, position):
    if position < 2:
        individu[position] = random.choice(GROUPE1)
    else:
        individu[position] = random.choice(GROUPE2)
    return individu


# 7. AFFICHAGE

def afficher_detail(individu):
    """Affiche la cédule d'un individu : maintenance de chaque unité et réserves."""
    print("  Chromosome :", individu)
    for u in range(NB_GENES):
        intervalles = [str(t + 1) for t in range(NB_INTERVALLES)
                       if individu[u][t] == "1"]
        print(f"  Unité {u + 1} ({CAPACITES[u]} MW) : "
              f"maintenance aux intervalles {', '.join(intervalles)}")
    print("  Réserves :", reserves(individu))
    print("  Score (plus petite réserve) :", score(individu), "MW")



# 8. ALGORITHME GÉNÉTIQUE (boucle principale)

def executer(type_croisement):
    """Lance l'algorithme génétique avec le type de croisement choisi.
    Retourne le meilleur individu trouvé."""
    population = creer_generation()
    meilleur = max(population, key=score)

    for numero in range(1, NB_GENERATIONS + 1):
        # 1) Évaluation de la génération
        scores = [score(individu) for individu in population]
        courant = population[scores.index(max(scores))]
        if score(courant) > score(meilleur):
            meilleur = courant
        print(f"Génération {numero:2d} : meilleur score = {score(meilleur)}")

        # 2) Nouvelle génération : on garde d'abord le meilleur (élitisme)
        nouvelle = [meilleur]
        while len(nouvelle) < NB_INDIVIDUS:
            # Sélection de 2 parents par loterie
            parent1 = selection_loterie(population, scores)
            parent2 = selection_loterie(population, scores)

            # Croisement avec la probabilité Pc, sinon les enfants copient les parents
            if random.random() < P_CROISEMENT:
                enfant1, enfant2 = croiser(parent1, parent2, type_croisement)
            else:
                enfant1, enfant2 = parent1[:], parent2[:]

            # Mutation avec la probabilité Pm (sur une position tirée au hasard)
            if random.random() < P_MUTATION:
                enfant1 = mutation(enfant1, random.randint(0, NB_GENES - 1))
            if random.random() < P_MUTATION:
                enfant2 = mutation(enfant2, random.randint(0, NB_GENES - 1))

            nouvelle.append(enfant1)
            nouvelle.append(enfant2)

        population = nouvelle[:NB_INDIVIDUS]

    # La dernière génération doit aussi être évaluée
    for individu in population:
        if score(individu) > score(meilleur):
            meilleur = individu

    print("\nMeilleur individu trouvé :")
    afficher_detail(meilleur)
    return meilleur


if __name__ == "__main__":
    # --- Démonstration des 3 croisements sur deux parents donnés ----------
    parent1 = ['0110', '0011', '0001', '1000', '0100', '0010', '1000']
    parent2 = ['1100', '0110', '0100', '0001', '0010', '1000', '0100']
    print("Parent 1 :", parent1)
    print("Parent 2 :", parent2)

    enfant1, enfant2 = croisement_simple(parent1, parent2, 4)
    print("\nCroisement simple (coupure après le gène 4) :")
    print("  enfant 1 :", enfant1)
    print("  enfant 2 :", enfant2)

    enfant1, enfant2 = croisement_double(parent1, parent2, 2, 5)
    print("\nCroisement double (coupures après les gènes 2 et 5) :")
    print("  enfant 1 :", enfant1)
    print("  enfant 2 :", enfant2)

    masque = [1, 0, 0, 1, 1, 0, 1]
    enfant1, enfant2 = croisement_uniforme(parent1, parent2, masque)
    print("\nCroisement uniforme (masque", masque, ") :")
    print("  enfant 1 :", enfant1)
    print("  enfant 2 :", enfant2)

    # --- Algorithme génétique avec chacun des 3 croisements ---------------
    for type_croisement in ["simple", "double", "uniforme"]:
        print("\n==================== Croisement", type_croisement,
              "====================\n")
        executer(type_croisement)