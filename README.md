# Challenge Data Visualisation en Actuariat 2021


## Membres du groupe Data visfalisation

- BÉRU Théodore
- CLAVIER Mathieu
- DESCAMPS Arthur
- GINOVART Axel
- GUICHARD Victor


## Structure du répertoire

Le répertoire GitHub est composé de trois dossiers principaux :
- data
- lib
- requirements
- app.py
- README.md


## Se repérer dans le code

Pour accéder à notre code, il y a deux principaux fichiers.

- app.py (configurant aggrégeant les graphes plotly)
- lib/model_app.py (comportant les scripts de créations des graphiques)

Les fichiers data.py et data_axel.py sont des fichiers annexes pour importer les données de manière générique.

Le répertoire data permet de facilement actualiser les données.
Par exemple, pour actualiser les données d'hospitalisations, il suffit de rajouter un répertoire yyyy-mm-dd dans le dossier hospitalisations. Puis le dashboard choisit automatiquement les données les plus récentes.


## Configuration nécessaire pour lancer le dashboard


Language utilisé : Python 3.7 ou 3.8

Un fichier requirements.txt est mis à disposition. (attention, 3 liens sont à modifier avec votre chemin d'accès)


La librairie geopandas nécessaire dans le code n'est pas installable directement dans le cloud des bibliothèques officielles. La commande pip install geopandas ne fonctionne donc pas.
Ainsi, il est nécessaire d'installer manuellement les librairies GDAL, fiona et Castopy. 

Les fichiers .whl pour la version 3.8.10 de Python sont disponibles dans le dossier requirements.
Sinon, pour les autres versions de Python télécharger les .whl [ici](https://www.lfd.uci.edu/~gohlke/pythonlibs/).


Nous recommendons d'utiliser un environnement virtuel pour réaliser les installations.




## Autres supports

- Un impression pdf du dashboard (l'export du dashboard en pdf n'est pas très bien adapté)




## Limites du Dashboard

Voici quelques limites et améliorations qui auraient été possibles avec plus de temps.

- L'accessibilité aurait pu être améliorée en hébergeant le dashboard sur GitHub et donnant simplement un lien pour consulter le dashboard.

- Le dashboard n'a pas pu être optimisé en terme de complexité temporelle. Idéalement, il faudrait gérer les caches plus intelligement et ne pas refaire des traitements identiques sur certaines dataframes lorsqu'un même dataframe est utilisé pour plusieurs graphiques.

