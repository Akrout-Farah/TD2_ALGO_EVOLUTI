correction Du DS _ Farah Akrout _ LSI3 1.1
```


## Exercice 1 : Robot dans le labyrinthe

Le robot part de la case (1,1) en haut à gauche et doit atteindre la case (10,10) en bas à droite. Il s'arrête s'il se cogne contre un mur, s'il revient sur une case déjà visitée, ou s'il atteint la sortie.

**1) Codage des individus**
Un individu est une liste de 60 déplacements. Chaque gène vaut : `0` = haut, `1` = bas, `2` = gauche, `3` = droite.
Exemple : `[3, 3, 1, 1, 3, ...]` = droite, droite, bas, bas, droite...

**2) Fonction fitness**
`fitness = distance  entre la position finale du robot et la sortie`
(= |ligne - 10| + |colonne - 10|). Plus elle est petite, mieux c'est. Une fitness de **0** signifie que le robot a atteint la sortie.

**3) Opérateur de mutation**
Chaque gène a 5 % de chance d'être remplacé par une direction tirée au hasard (0 à 3).

**4) Code complet**
 `exercice1 du DS.py` : création de la population, (probabilité proportionnelle à 1 / (1 + fitness)) , croisement en un point, mutation.



---

## Exercice 2 : Grille n×n avec k jetons

Placer k jetons (k < n²) pour que chaque ligne et chaque colonne contienne un nombre **pair** de jetons. Exemple : n = 5, k = 10.

**1) Taille de l'espace de recherche**
On choisit k cases parmi n² cases : **C(n², k)**.
Pour n = 5 et k = 10 : C(25, 10) = **3 268 760** solutions possibles.

**2.a) Codage des solutions**
Un individu est une liste de k numéros de cases différents (de 0 à n²-1), avec `numéro = ligne × n + colonne`.
Exemple (n = 5) : la case ligne 2, colonne 3 a le numéro 13. Ce codage garantit qu'il y a toujours exactement k jetons.

**2.b) Fonction fitness**
`fitness = nombre de lignes impaires + nombre de colonnes impaires`
- fitness = 0 : **solution faisable**
- fitness > 0 : **solution non faisable** (plus la valeur est grande, plus la solution est mauvaise)

**2.c) Code complet**
`exercice 2 du DS.py` :
- **Sélection** : tournoi de 3 individus
- **Croisement** : l'enfant garde la 1ère moitié du parent 1, puis est complété avec les cases du parent 2 (sans doublon)
- **Mutation** : un jeton est déplacé vers une case libre au hasard

**Remarque :** il n'y a de solution que si k est pair (et k ≤ n(n-1)

