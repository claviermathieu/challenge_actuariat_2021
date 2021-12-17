import streamlit as st
# To make things easier later, we're also importing numpy and pandas for
# working with sample data.
import numpy as np
import pandas as pd
import plotly.express as px
from datetime import datetime

# Personnal lib
import lib.model_app as model



########################################
### Titre
########################################

st.set_page_config(layout='wide')
st.title('Challenge Data Visualisation en Actuariat 2021')





########################################
### NAV
########################################


st.sidebar.markdown("""


- [Accueil](#challenge-data-visualisation-en-actuariat-2021)

# État des lieux sanitaire

1. [Dépistages (tests)](#1-1-d-pistage-tests)
2. [Hopitaux](#1-2-hopitaux)
3. [Hospitalisations par département](#1-3-hopistalisations-par-d-partement)
4. [Synthèse](#1-4-synth-se)

# Impact des actions de l'État

5. [Vaccination](#2-1-vaccination)
6. [TousAntiCovid](#2-2-tousanticovid)
7. [Fonds de solidarité](#2-3-fonds-de-solidarit)
8. [PGE](#2-4-pr-t-garanti-par-l-tat-pge)
9. [Échéances fiscales](#2-5-reports-des-ch-ances-fiscales)

""")



########################################
st.markdown("## I. État des lieux sanitaire")
########################################


########################################
st.markdown("### 1.1. Dépistage (tests)")
########################################

st.markdown("""
Les données proviennent de [cette page](https://www.data.gouv.fr/fr/datasets/donnees-relatives-aux-resultats-des-tests-virologiques-covid-19/). 
Il s'agit du fichier nommé **sp-pos-quot-fra**.

De ces données, il est possible d'extraire le nombre de tests effectués chaque jour ainsi que le taux de positivité.
""")


st.plotly_chart(model.tests(), use_container_width=True)



########################################
st.markdown("### 1.2. Hopitaux")
########################################

st.markdown("""

#### 1.2.1. Hospitalisation par sexe

Les données proviennent de [cette page](https://www.data.gouv.fr/fr/datasets/donnees-hospitalieres-relatives-a-lepidemie-de-covid-19/). 
Il s'agit du fichier nommé **donnees-hospitalieres-covid19**.

De ces données, il est possible d'extraire le nombre de d'hospitalisations. Ces données sont très importantes car la saturation des hôpitaux est le principal indicateur pour durcir les 
contraintes sanitaires.
""")

col1, col2 = st.columns(2)

fig1, fig2 = model.hosp_sexe()

col1.plotly_chart(fig2, use_container_width=True)

col2.plotly_chart(fig1, use_container_width=True)

########################################

st.markdown("""

#### 1.2.2. Hospitalisations par classes d'âge

Les données proviennent de [cette page](https://www.data.gouv.fr/fr/datasets/donnees-hospitalieres-relatives-a-lepidemie-de-covid-19/). 
Il s'agit du fichier nommé **covid-hosp-txad-age-fra**.

De ces données, il est possible d'extraire le nombre de nouvelles hospitalisations lors des 7 
derniers jours ainsi que le nombre total de personnes hospitalisées.
""")


col1, col2 = st.columns([1, 5])

type = col1.radio("Service :",
('Classique', 'Soins critiques'))



col2.plotly_chart(model.new_hosp_age(type), use_container_width=True)




########################################
st.markdown("### 1.3. Hopistalisations par département et par date")
########################################

st.markdown("""
Les données proviennent de [cette page](https://www.data.gouv.fr/fr/datasets/donnees-hospitalieres-relatives-a-lepidemie-de-covid-19/). 
Il s'agit du fichier nommé **donnees-hospitalieres-covid19**.

Ici, il est possible d'observer le nombre de personnes hospitalisées par département et par date.
""")


col1, col2 = st.columns([1, 4])

d = col1.date_input(
    "Date d'observation",
     datetime(2021, 7, 6), 
     min_value=datetime(2020, 3, 18),
     max_value=datetime(2021,12,2))


my_fig = model.map_dep(d)
col2.plotly_chart(my_fig)






########################################
st.markdown("### 1.4. Synthèse")
########################################

st.markdown("""

#### 1.4.1. Avant et après vaccination

Les données proviennent de deux pages.
- [Concernant la vaccination](https://www.data.gouv.fr/fr/datasets/donnees-relatives-aux-personnes-vaccinees-contre-la-covid-19-1/) (Il s'agit du fichier nommé **vacsi12-fra**.)
- [Concernant le taux d'incidence](https://www.data.gouv.fr/fr/datasets/taux-dincidence-de-lepidemie-de-covid-19/) (Il s'agit du fichier nommé **sp-pe-tb-quot-fra**.)

""")



st.plotly_chart(model.inf_vacc(), use_container_width = True)



st.markdown("""

#### 1.4.2. Évolution du nombre d'infectés et de la vaccination

Les données proviennent de [cette page](https://www.data.gouv.fr/fr/datasets/taux-dincidence-de-lepidemie-de-covid-19/). 
Il s'agit du fichier nommé **sp-pe-tb-quot-fra**.

L'objectif est d'avoir une visualisation classique SIR de la pandémie.
""")

st.plotly_chart(model.SIR(21), use_container_width = True)




########################################
st.markdown("## II. Impact des actions de l'État")
########################################




########################################
st.markdown("### 2.1. Vaccination")
########################################

st.markdown("""
Les données proviennent de [cette page](https://www.data.gouv.fr/fr/datasets/donnees-relatives-aux-personnes-vaccinees-contre-la-covid-19-1/). 

Il s'agit du fichier **vacsi12-fra** permettant d'accéder aux informations concernant la vaccination.
""")

fig1, fig2, d1, d1_var, d2, d2_var, d3, d3_var= model.vac()

col1, col2, col3 = st.columns(3)
col1.metric("Dose 1", str(d1), str(d1_var) + " dernier jour")
col2.metric("Dose 2", str(d2), str(d2_var) + " dernier jour")
col3.metric("Dose 3", str(d3), str(d3_var) + " dernier jour")


col1, col2 = st.columns(2)


col1.plotly_chart(fig1, use_container_width = True)
col2.plotly_chart(fig2, use_container_width = True)





########################################
st.markdown("### 2.2. TousAntiCovid")
########################################

st.markdown("""
Les données proviennent de [cette page](https://www.data.gouv.fr/fr/datasets/metriques-dutilisation-de-lapplication-tousanticovid/). 


Le présent jeu de données informe pour chaque jour depuis le lancement de l'application le 2 juin 2020 :
- Total cumulé du nombre d'applications enregistrées moins le nombre de désenregistrements.
- Total cumulé d'utilisateurs notifiés par l'application : le nombre d'utilisateurs notifiés par l'application comme contacts à risque suite à une exposition à la COVID-19, depuis le 2 juin 2020.
- Total cumulé d'utilisateurs se déclarant comme des cas de COVID-19 par jour : le nombre d'utilisateurs qui se sont déclarés comme des cas de COVID-19 dans l'application, depuis le 2 juin 2020.
""")

col1, col2 = st.columns(2)

fig1, fig2 = model.tac()

col1.plotly_chart(fig1, use_container_width = True)
col2.plotly_chart(fig2, use_container_width = True)






########################################
st.markdown("### 2.3. Fonds de solidarité")
########################################


st.markdown("""
Les données proviennent de [cette page](https://github.com/etalab/dashboard-aides-entreprises/tree/master/published-data/fonds-solidarite). 

Une multitude de fichiers sont aggrégés pour permettre une visualisation temporelle.
""")


col1, col2 = st.columns(2)

col1.plotly_chart(model.montants_non_normes_graph(), use_container_width = True)
col2.plotly_chart(model.montants_non_normes_pie(), use_container_width = True)

col1.plotly_chart(model.montants_normes_graph(), use_container_width = True)
col2.plotly_chart(model.montants_normes_pie(), use_container_width = True)

########################################
st.markdown("### 2.4. Prêt garanti par l'État (PGE)")
########################################


st.markdown("""
Les données proviennent de [cette page](https://www.data.gouv.fr/fr/datasets/donnees-relatives-aux-prets-garantis-par-letat-dans-le-cadre-de-lepidemie-de-covid-19/). 
Il s'agit du fichier nommé **pge-departemental-naf-covid19-csv**.

L'État a fortement soutenu l'économie en accordant des garantis pour faciliter l'emprunt des entreprises.
""")

st.plotly_chart(model.pge_sec(), use_container_width = True)


col1, col2 = st.columns(2)

col1.plotly_chart(model.pge_dep(), use_container_width = True)
col2.plotly_chart(model.pge_dep_nb(), use_container_width = True)



# st.plotly_chart(model.repartition(), use_container_width = True)





########################################
st.markdown("### 2.5. Reports des échéances fiscales")
########################################

st.markdown("""
Les données proviennent de [cette page](https://github.com/etalab/dashboard-aides-entreprises/tree/master/published-data/reports-echeances). 

L'État à consenti à décaler la collecte des impôts. De la même manière que pour les fonds de solidarité, une multitude de fichiers ont été aggrégés pour permettre
une visualisation temporelle.
""")

col1, col2 = st.columns(2)

col1.plotly_chart(model.reports_bruts(), use_container_width = True)
col2.plotly_chart(model.nouveaux_reports(), use_container_width = True)



st.plotly_chart(model.repartition(), use_container_width = True)





