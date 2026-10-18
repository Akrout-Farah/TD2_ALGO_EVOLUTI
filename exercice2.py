"""TD2 - Exercice 2 : problème de transport (containers) par recherche tabou."""
import itertools

COUT = [[5, 3, 4],
        [6, 7, 2]]
OFFRE = [8, 9]
DEMANDE = [4, 5, 8]


def cout_total(x):
    return sum(COUT[i][j] * x[i][j] for i in range(2) for j in range(3))


def solution_initiale():
    """Méthode du coin nord-ouest : toujours réalisable, mais sans tenir compte des coûts."""
    o, d = OFFRE[:], DEMANDE[:]
    x = [[0] * 3 for _ in range(2)]
    i = j = 0
    while i < 2 and j < 3:
        q = min(o[i], d[j])
        x[i][j] = q
        o[i] -= q
        d[j] -= q
        if o[i] == 0:
            i += 1
        else:
            j += 1
    return x


def voisins(x):
    """Mouvement : transférer 1 container le long du cycle (i1,j1)-(i1,j2)-(i2,j2)-(i2,j1).
    On retire 1 en (i1,j1) et (i2,j2), on ajoute 1 en (i1,j2) et (i2,j1)."""
    for i1, i2 in [(0, 1), (1, 0)]:
        for j1 in range(3):
            for j2 in range(3):
                if j1 != j2 and x[i1][j1] > 0 and x[i2][j2] > 0:
                    y = [r[:] for r in x]
                    y[i1][j1] -= 1; y[i2][j2] -= 1
                    y[i1][j2] += 1; y[i2][j1] += 1
                    yield y, (frozenset({(i1, j1), (i2, j2)}), frozenset({(i1, j2), (i2, j1)}))


def inverse(m):
    retire, ajoute = m
    return (ajoute, retire)


def tabou(iterations=10, taille_liste=3):
    x = solution_initiale()
    best, best_c = [r[:] for r in x], cout_total(x)
    liste = []
    journal = [(0, None, [r[:] for r in x], cout_total(x), best_c, [])]
    for it in range(1, iterations + 1):
        choix = None
        for y, m in voisins(x):
            c = cout_total(y)
            if m in liste and c >= best_c:      
                continue
            if choix is None or c < choix[1]:
                choix = (y, c, m)
        if choix is None:
            break
        x, c, m = choix
        liste.append(inverse(m))
        if len(liste) > taille_liste:
            liste.pop(0)
        if c < best_c:
            best, best_c = [r[:] for r in x], c
        journal.append((it, m, [r[:] for r in x], c, best_c, liste[:]))
    return best, best_c, journal


def force_brute():
    """Vérification : toutes les solutions entières réalisables."""
    meilleur = None
    for x11 in range(0, 5):
        for x12 in range(0, 6):
            x13 = 8 - x11 - x12
            x21, x22, x23 = 4 - x11, 5 - x12, 8 - x13
            if min(x13, x21, x22, x23) < 0:
                continue
            x = [[x11, x12, x13], [x21, x22, x23]]
            c = cout_total(x)
            if meilleur is None or c < meilleur[1]:
                meilleur = (x, c)
    return meilleur


if __name__ == "__main__":
    print("Initiale :", solution_initiale(), cout_total(solution_initiale()))
    best, bc, j = tabou()
    for it, m, x, c, b, l in j:
        print(it, m, x, c, b, l)
    print("Meilleure :", best, bc)
    print("Optimum exact :", force_brute())