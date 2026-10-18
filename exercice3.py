"""TD2 - Exercice 3 : voyageur de commerce (8 villes) - tabou, recuit simulé, algorithme génétique."""
import itertools, math, random

INF = float("inf")
ARETES = {(1, 2): 14, (1, 3): 15, (1, 8): 17,
          (2, 3): 13, (2, 4): 14, (2, 5): 20, (2, 8): 21,
          (3, 4): 11, (3, 5): 21, (3, 6): 17, (3, 7): 9, (3, 8): 9,
          (4, 5): 11, (4, 6): 10, (4, 7): 8, (4, 8): 20,
          (5, 6): 15, (5, 7): 18,
          (6, 7): 9,
          (7, 8): 13}          


def d(a, b):
    return ARETES.get((min(a, b), max(a, b)), INF)


def cout(t):
    """t = [1, ..., ...] (sans le retour) ; le circuit revient en 1."""
    return sum(d(t[k], t[(k + 1) % len(t)]) for k in range(len(t)))


def voisin_swap(t, i, j):
    u = t[:]
    u[i], u[j] = u[j], u[i]
    return u


# question 1 :Recherche avec taboue
def tabou(initial, iterations=10, taille=3):
    cur = initial[:]
    best, best_c = cur[:], cout(cur)
    liste, journal = [], [(0, None, cur[:], cout(cur), best_c, [])]
    paires = list(itertools.combinations(range(1, 8), 2))       
    for it in range(1, iterations + 1):
        choix = None
        for i, j in paires:
            u = voisin_swap(cur, i, j)
            c = cout(u)
            m = frozenset({cur[i], cur[j]})
            if m in liste and c >= best_c:
                continue
            if choix is None or c < choix[1]:
                choix = (u, c, m)
        cur, c, m = choix
        liste.append(m)
        if len(liste) > taille:
            liste.pop(0)
        if c < best_c:
            best, best_c = cur[:], c
        journal.append((it, tuple(sorted(m)), cur[:], c, best_c, [tuple(sorted(x)) for x in liste]))
    return best, best_c, journal


# question2:Recuit simulé
def recuit(initial, T0=30.0, facteur=0.6, iterations=5, seed=1):
    rnd = random.Random(seed)
    cur, cur_c = initial[:], cout(initial)
    best, best_c = cur[:], cur_c
    T, journal = T0, []
    for it in range(1, iterations + 1):
        while True:                       
            i, j = rnd.sample(range(1, 8), 2)
            cand = voisin_swap(cur, i, j)
            cc = cout(cand)
            if cc < INF:
                break
        delta = cc - cur_c
        if delta <= 0:
            p, r, acc = None, None, True
        else:
            p = math.exp(-delta / T)
            r = rnd.random()
            acc = r < p
        journal.append((it, T, (cur[i], cur[j]), cand[:], cc, delta, p, r, acc))
        if acc:
            cur, cur_c = cand, cc
            if cur_c < best_c:
                best, best_c = cur[:], cur_c
        T *= facteur
    return best, best_c, journal


# question 3 :Algorithme génétique
def croisement_ox(p1, p2, rnd):
    a, b = sorted(rnd.sample(range(1, 8), 2))
    enfant = [None] * 8
    enfant[0] = 1
    enfant[a:b + 1] = p1[a:b + 1]
    reste = [v for v in p2 if v not in enfant]
    for k in range(1, 8):
        if enfant[k] is None:
            enfant[k] = reste.pop(0)
    return enfant


def mutation(t, rnd, pm=0.2):
    if rnd.random() < pm:
        i, j = rnd.sample(range(1, 8), 2)
        t = voisin_swap(t, i, j)
    return t


def genetique(taille_pop=8, generations=20, pm=0.2, seed=3):
    rnd = random.Random(seed)
    def aleatoire():
        v = list(range(2, 9)); rnd.shuffle(v); return [1] + v
    def faisable(t): return cout(t) < INF
    pop = []
    while len(pop) < taille_pop:
        t = aleatoire()
        if faisable(t):
            pop.append(t)
    best = min(pop, key=cout)
    historique = [(0, cout(best), best[:], sum(cout(t) for t in pop) / len(pop))]
    for g in range(1, generations + 1):
        def tournoi():
            a, b = rnd.sample(pop, 2)
            return a if cout(a) <= cout(b) else b
        nouvelle = [min(pop, key=cout)[:]]                      # élitisme
        while len(nouvelle) < taille_pop:
            e = mutation(croisement_ox(tournoi(), tournoi(), rnd), rnd, pm)
            if faisable(e):
                nouvelle.append(e)
        pop = nouvelle
        b = min(pop, key=cout)
        if cout(b) < cout(best):
            best = b[:]
        historique.append((g, cout(best), best[:], sum(cout(t) for t in pop) / len(pop)))
    return best, cout(best), historique


def optimum_exact():
    best = None
    for p in itertools.permutations(range(2, 9)):
        t = [1] + list(p)
        c = cout(t)
        if best is None or c < best[1]:
            best = (t, c)
    return best


if __name__ == "__main__":
    init = [1, 2, 3, 4, 5, 6, 7, 8]
    print("Initial", init, cout(init))
    print("TABOU"); b, c, j = tabou(init)
    for x in j: print(x)
    print(b, c)
    print("RECUIT"); b, c, j = recuit(init)
    for x in j: print(x)
    print(b, c)
    print("GA"); b, c, h = genetique()
    for x in h: print(x)
    print(b, c)
    print("EXACT", optimum_exact())