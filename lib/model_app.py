import numpy as np
import pandas as pd
import geopandas as gpd

# from datetime import datetime
import datetime
import os

import plotly.express as px

import lib.data as data



#############
### Tests ###
#############


def tests():
    path = data.file_path('data/tests', date_ind = -1, file_name = 'sp-pos-quot-fra')
    vtaux = data.read_csv(path)
    
    vtaux=vtaux[:][vtaux['cl_age90']==0]
    
    vtaux['Total']=vtaux['T'].rolling(14).mean()
    vtaux['Positifs']=vtaux['P'].rolling(14).mean()
    
    fig=px.line(vtaux, x='jour', y = ['Total','Positifs'],
                title="<b>Dépistage COVID-19 :</b> Nombre et résultat des tests",
                labels = {
                    'jour':'Date', 
                    'value':'Nombre de tests', 
                    'variable':''}
                    )
    fig.update_layout(
        margin={"r":20,"t":60,"l":20,"b":20})

    return(fig)


################
### Hopitaux ###
################


def new_hosp_age(type):

    path = data.file_path('data/hospitalisations', date_ind = -1, file_name = 'covid-hosp-txad-age-fra')
    db1 = data.read_csv(path)

    df_db1 = db1.copy()
    df_db1.clage_90 = df_db1.clage_90.replace({0:"Moyenne", 9:"0-9 ans", 19:"10-19 ans", 29:"20-29 ans", 39:"30-39 ans", 49:"40-49 ans", 59:"50-59 ans", 69:"60-69 ans", 79:"70-79 ans", 89:"80-89 ans", 90:"90 ans et +"})
    df_db1.jour = pd.to_datetime(df_db1.jour, format = "%d/%m/%Y")
    df_db1.set_index('jour', inplace = True)
    df_db1.drop('fra', axis = 1, inplace = True)
    df_db1.reset_index(inplace = True)

    if type == "Soins critiques":
        fig = px.line(df_db1,   x = 'jour', y='tx_indic_7J_SC', color = 'clage_90',
                    title = "<b>Nouvelles hospitalisations en soin critique :</b> lors des 7 derniers jours (par classes d'âge)", 
                    labels = {
                        "jour" : "Date", 
                        "tx_indic_7J_SC" :"Nombre d'hospitalisations en soin critique" 
                    })

    else:
        fig = px.line(df_db1,   x = 'jour', y='tx_indic_7J_hosp', color = 'clage_90', 
                    title = "<b>Nouvelles hospitalisations :</b> lors des 7 derniers jours (par classes d'âge)</b>", 
                    labels = {
                        "jour" : "Date", 
                        "tx_indic_7J_hosp" :"Nombre d'hospitalisations", 
                        "clage_90":"Classes d'âge" 
                    })

    fig.update_layout(
        margin={"r":40,"t":60,"l":60,"b":20},
        height = 500)

    return(fig)


def hosp_sexe():

    path = data.file_path('data/hospitalisations', date_ind = -1, file_name = 'donnees-hospitalieres-covid19')
    db6 = data.read_csv(path)
    db6 = db6.groupby(['jour', 'sexe']).sum()
    db6.reset_index(inplace = True)
    db6.sexe = db6.sexe.replace({0:'Les deux', 1:'Homme', 2:"Femme"})

    fig1 = px.line(db6[list(db6.sexe != 'Les deux') or list(db6.sexe == 'Homme')], x="jour", y="hosp", color='sexe',
        title = "<b>Hospitalisations liées au COVID-19</b><br>(par sexe)",
        labels={
        "hosp": "Nombre de personnes hospitalisées", 
        "jour": "Date", 
        "sexe":"Sexe"
    })
    fig2 = px.line(db6[list(db6.sexe == 'Les deux') or list(db6.sexe == 'Homme')], x="jour", y="hosp",
        title = "<b>Hospitalisations liées au COVID-19</b><br>(total)",
    
        labels={
        "hosp": "Nombre de personnes hospitalisées", 
        "jour": "Date", 
        "sexe":"Sexe"
    })
    fig1.update_layout(
        margin={"r":40,"t":60,"l":60,"b":20},
        height = 500)
    fig2.update_layout(
        margin={"r":40,"t":60,"l":60,"b":20},
        height = 500)

    return(fig1, fig2)


############################
### Hosp par département ###
############################



def map_dep(d):

    
    # geographic data
    EPSG = 4326
    departements = gpd.read_file("data/_france_geojson/departements.geojson").to_crs(EPSG)

    # population
    df_pop = pd.read_excel('data/_insee/pop_2021.xlsx')

    # covid data
    path = data.file_path('data/hospitalisations', date_ind = -1, file_name = 'donnees-hospitalieres-covid19')
    db6 = data.read_csv(path)

    df_map = db6.copy()
    df_map.jour = pd.to_datetime(df_map.jour)
    df_map = df_map.groupby(['jour', 'dep']).sum()
    df_map.drop(["sexe", "HospConv", "SSR_USLD", "autres", "rad", "dc"], axis = 1, inplace = True)
    df_map.reset_index(inplace = True)
    # df_map.head()

    gdf = df_map.merge(df_pop)
    gdf['hosp_prop'] = gdf['hosp'] / gdf['pop'] * 100
    gdf['rea_prop'] = gdf['rea'] / gdf['pop'] * 100
    gdf = departements.merge(gdf, left_on = 'code', right_on ='dep', how='left').drop('code', axis = 1)

    gdf['hosp_aff'] = gdf['hosp_prop'].round(2).astype(str) + ' %'
    gdf['rea_aff'] = gdf['rea_prop'].round(2).astype(str) + ' %'

    gdf.drop(['hosp', 'rea'], axis = 1, inplace = True)




    gdf_sub = gdf[gdf.jour == str(d)[:10] ].copy()
    gdf_sub.drop('jour', axis = 1, inplace = True)
    gdf_sub.set_index('dep', inplace = True)


    fig = px.choropleth(gdf_sub,
                    geojson=gdf_sub.geometry,
                    locations=gdf_sub.index,
                    color="hosp_prop",
                    color_continuous_scale="hot_r",
                    hover_data=["pop", "rea_aff"],
                    labels={'dep':'Département', "hosp_prop":"Hospitalisation", "rea_aff":"Réanimation", "pop":"Population"},
                    hover_name="nom",
                    projection="mercator", 

                    # width = 1000,
                    height = 700
                    )

    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(margin={"r":200,"t":50,"l":0,"b":0}, 
    title_text="<b>Pourcentage d'hospitalisations liées au COVID-19 <br>en fonction de la population du département</b><br>(" + str(d) + ")")

    return(fig)





############################
### Infectés par vaccins ###
############################

def inf_vacc():
    path = data.file_path('data/taux_incidence', date_ind = -1, file_name = 'sp-pe-tb-quot-fra')
    inc = data.read_csv(path)
    inc=pd.DataFrame(inc[:][inc['cl_age90']==0])

    path = data.file_path('data/vaccins', date_ind = -1, file_name = 'vacsi12-fra')
    vac = data.read_csv(path)

    indx=inc.index.tolist()
    pop=67114995
    bol=True
    Lb=[True]*6
    b=0
    k=0

    while (vac['n_cum_complet'][indx[k]]/pop<0.5):
        k=k+1

    D=vac["jour"][indx[k]]
    k=0
    
    while (inc['jour'][indx[k]]<D):
        k=k+1
    la=len(indx)
    L=[0]*k+[1]*(la-k)
    inc['indice']=L
    le=len(inc["jour"])
    L=[]
    Lt=[]
    T=[]
    Tt=[]
    for k in range(le):
        if inc['indice'][indx[k]]==0:
            Lt.append('NaN')
            Tt.append(inc['P'][indx[k]])
        else:
            if bol:
                Tt.append(inc['P'][indx[k]])
                Lt.append(inc['P'][indx[k]])
                bol=Lb[-b]
                Lb[-b]=False
                b=b+1
            else:
                Tt.append('NaN')
                Lt.append(inc['P'][indx[k]]) 
    y1 = '< 50%'
    y2 = '> 50%'

    inc[y1]=Tt
    inc[y2]=Lt
    inc[y1]=inc[y1].rolling(7).mean()
    inc[y2]=inc[y2].rolling(7).mean()

    # fig=(inc).iplot(x='jour',y = ['moins de 50% de la population est vacciné','plus de 50% de la population est vacciné'],title="Taux d'incidence de la covid-19")
    fig = px.line(inc, x='jour',y = [y1,y2], 
                title = "<b>Nombre de personnes infectées :</b> par jour avant et après vaccination", 
                labels = {
                    'jour':'Date', 
                    "value":"Personnes infectées",
                    'variable':'Taux de vaccination'
                })

    fig.update_layout(
        margin={"r":30,"t":60,"l":60,"b":20},
        height = 500, 
        legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01
    )
    )
    return(fig)



def SIR(n):
    path = data.file_path('data/taux_incidence', date_ind = -1, file_name = 'sp-pe-tb-quot-fra')
    inc = data.read_csv(path)
    inc=pd.DataFrame(inc[:][inc['cl_age90']==0])

    path = data.file_path('data/vaccins', date_ind = -1, file_name = 'vacsi12-fra')
    vac = data.read_csv(path)

    df=(inc[:][inc["cl_age90"]==0]).copy()
    ixv=(df[:][df["jour"]>="2020-12-27"]).copy()
    ixv["vaccination"]=list(vac["n_cum_complet"][:-1])
    ix={'jour': list(ixv["jour"][:]), 'P':list(ixv["P"][:]), 'vaccination':list(ixv["vaccination"][:])}
    ix=pd.DataFrame(ix)

    Ti=list(ix)
    auxR=0
    auxS=0
    I=[0]
    R=[0]
    #R2=[0]
    V=[0]
    pop=67114995
    #S=[pop]
    S2=[1]
    le=len(ix[Ti[0]])
    for k in range(le):
        z=k-n
        if z<0:
            z=0
            auxR=auxR+0
        else:
            auxR=auxR+ix[Ti[1]][z]
        auxS=auxS+ix[Ti[1]][k]
        V.append((ix[Ti[2]][k])/pop)
        I.append((sum(ix[Ti[1]][z:k+1]))/pop)
        #R2.append(auxR+ix[Ti[2]][k])
        S2.append((pop-auxS-ix[Ti[2]][k])/pop)
        R.append(auxR/pop)
        #S.append(S[-1]-ix[Ti[1]][k])


    y1 = "Infectée"
    y2 = "Ayant été infectée"
    y3 = "Vaine et non vaccinée"
    y4 = "Vaccinée"

    ix[y1]=I[1:]
    ix[y2]=R[1:]
    ix[y3]=S2[1:]
    ix[y4]=V[1:]
    X=[k for k in range(le+1)]

    fig = px.line(ix, x = 'jour', y = [y1,y2,y3, y4], 
                title = "<b>Visualisation SIR</b>", 
                labels = {
                    "value":"Pourcentage de la population", 
                    "variable": "% de population", 
                    "jour":"Date"
                })


    fig.update_layout(
        margin={"r":30,"t":60,"l":60,"b":20},
        height = 500, 
        legend=dict(
        yanchor="top",
        y=0.7,
        xanchor="left",
        x=0.01
    ))

    return(fig)








###################
### Vaccination ###
###################



def vac():
    path = data.file_path('data/vaccins', date_ind = -1, file_name = 'vacsi12-fra')
    vac = data.read_csv(path)

    vac['complet']=vac['n_complet'].rolling(14).mean()
    # pop=67114995
    # vac['n_cum_complet_pop']=vac['n_cum_complet']/pop

    fig1 = px.line(vac, x = 'jour', y = 'complet', 
    title = '<b>Nombre de vaccination pour la deuxième dose</b><br>Par jour (moyenne mobile)', 
    labels={
        'jour':'Date', 
        'complet':""
    })

    fig1.update_layout(
        margin={"r":30,"t":60,"l":30,"b":20})


    vac.rename(columns={"n_cum_dose1":"Dose 1", "n_cum_complet":"Dose 2", "n_cum_rappel":"Dose 3"}, inplace = True)

    fig2 = px.line(vac, x = 'jour', y = ['Dose 1', 'Dose 2', 'Dose 3'], 
    title = '<b>Nombre de personnes vaccinées en France</b>', 
    labels={
        "value":"Nombre de personnes vaccinés", 
        "jour":"Date", 
        "variable":""
    })


    fig2.update_layout(
        margin={"r":30,"t":60,"l":60,"b":20},
        # height = 500, 
        legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01
        ))

    d1= vac['Dose 1'].iloc[-1]
    d1_var = vac['Dose 1'].iloc[-1] - vac['Dose 1'].iloc[-2]
    d2= vac['Dose 2'].iloc[-1]
    d2_var = vac['Dose 2'].iloc[-1] - vac['Dose 2'].iloc[-2]
    d3= vac['Dose 3'].iloc[-1]
    d3_var = vac['Dose 3'].iloc[-1] - vac['Dose 3'].iloc[-2]

    return(fig1, fig2, d1, d1_var, d2, d2_var, d3, d3_var)


#####################
### TousAntiCovid ###
#####################

def tac():
    # tac=pd.read_csv("C:/Users/Utilisateur/Desktop/data-viz data/tac-metriques.csv")
    tac=pd.read_csv("https://www.data.gouv.fr/fr/datasets/r/0e2168ec-24c7-4b49-a900-c7dd12f8e88c")
    #lien :https://www.data.gouv.fr/fr/datasets/r/0e2168ec-24c7-4b49-a900-c7dd12f8e88c



    tac.rename(columns={"notified":"Notifiées", "qrCode":"Se déclarant infectées"}, inplace =True)

    fig1 = px.line(tac, x = 'date', y = 'register', 
                title = "<b>Nombre de personnes ayant TousAntiCovid</b><br>Installer actuellement sur leur smartphone", 
                labels={'register':"", "date":"Date"})

    fig2 = px.line(tac, x = 'date', y = ['Se déclarant infectées','Notifiées'], 
                title = "<b>Utilisation de l'application TousAntiCovid</b>", 
                labels = {
                    "variable":"", 
                    "date":"Date",
                    'value':"Nombre de personnes"
                }
                )

    fig1.update_layout(
        margin={"r":40,"t":60,"l":60,"b":20})
    fig2.update_layout(
            margin={"r":30,"t":60,"l":60,"b":20},
            # height = 500, 
            legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        ))

    return(fig1, fig2)


###########
### PGE ###
###########

def pge_sec():
    db = pd.read_csv("data/pge/pge-departemental-naf-latest.csv", sep = ",")

    date_maj = db.date_maj.unique()[0]

    df_sec = db.copy()
    df_sec = df_sec.groupby(['libelle_section']).sum()
    df_sec.reset_index(inplace = True)
    df_sec = df_sec[['libelle_section', 'montant_total']]
    df_sec.sort_values('montant_total', inplace = True)

    df_sec.montant_total = np.round(df_sec.montant_total/1000000000, 3)

    fig = px.bar(df_sec, x='libelle_section', y = 'montant_total', orientation='v')
    fig.update_layout(
        height = 800
    )

    fig = px.bar(df_sec, x='libelle_section', y = 'montant_total', 
                title = "<b>Montants des PGE accordés par secteurs d'activité</b><br>En millards d'Euros (" + date_maj + ")", 
                labels = {
                    "libelle_section":"",
                    "montant_total":"Montant"
                }, 
                hover_data={"libelle_section":False},
                hover_name="libelle_section")
    fig.update_layout(
        margin={"r":40,"t":60,"l":60,"b":20},
        height = 800)
    
    return(fig)

def pge_dep():
    db = pd.read_csv("data/pge/pge-departemental-naf-latest.csv", sep = ",")

    date_maj = db.date_maj.unique()[0]

    df_sec = db.copy()
    df_sec = df_sec.groupby(['libelle_departement', 'dep']).sum()
    df_sec.reset_index(inplace = True)
    df_sec = df_sec[['libelle_departement', 'dep', 'montant_total']]
    df_sec.sort_values('montant_total', inplace = True)

    df_sec.montant_total = np.round(df_sec.montant_total/1000000000, 3)

    df_sec.head()


    EPSG = 4326
    departements = gpd.read_file("data/_france_geojson/departements.geojson").to_crs(EPSG)
    df_map = departements.merge(df_sec, left_on='code', right_on='dep')
    df_map.drop(['code', 'nom'], axis = 1, inplace = True)
    df_map.set_index('dep', inplace = True)

    fig = px.choropleth(df_map,
                    geojson=df_map.geometry,
                    locations=df_map.index,
                    color="montant_total",
                    labels={
                            'montant_total':"Montant"},
                    # hover_data={'index':False},
                    hover_name="libelle_departement",
                    projection="mercator", 

                    # width = 1000,
                    height = 400
                    )

    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(margin={"r":200,"t":50,"l":0,"b":0}, 
    title_text="<b>Montants des PGE accordés par département</b><br>En milliards d'Euros (" + date_maj + ")")
    return(fig)

def pge_dep_nb():
    db = pd.read_csv("data/pge/pge-departemental-naf-latest.csv", sep = ",")

    date_maj = db.date_maj.unique()[0]

    df_sec = db.copy()
    df_sec = df_sec.groupby(['libelle_departement', 'dep']).sum()
    df_sec.reset_index(inplace = True)
    df_sec.montant_total = np.round(df_sec.montant_total/1000000000, 3)
    df_sec = df_sec[['libelle_departement', 'dep', 'nombre_pge', 'montant_total']]

    df_sec.head()


    EPSG = 4326
    departements = gpd.read_file("data/_france_geojson/departements.geojson").to_crs(EPSG)
    df_map = departements.merge(df_sec, left_on='code', right_on='dep')
    df_map.drop(['code', 'nom'], axis = 1, inplace = True)
    df_map.set_index('dep', inplace = True)

    fig = px.choropleth(df_map,
                    geojson=df_map.geometry,
                    locations=df_map.index,
                    color="nombre_pge",
                    hover_data={'montant_total':True},
                    labels={
                            'nombre_pge':"Nombre", 
                            "montant_total":"Montant (Mds)"},
                    hover_name="libelle_departement",
                    projection="mercator", 

                    # width = 1000,
                    height = 400
                    )

    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(margin={"r":200,"t":50,"l":0,"b":0}, 
    title_text="<b>Nombre de PGE accordés par département</b><br>En milliards d'Euros (" + date_maj + ")")
    return(fig)

###########################
### Fonds de solidarité ###
###########################

import lib.data_axel as data_axel

def montants_non_normes_graph():    
    PATH_R = "data/fonds-solidarite"
    files = data_axel.files_available(path_r=PATH_R,folder_ind = 0)
    dossiers=data_axel.folders_available(path_r=PATH_R)
    liste_eco_regionaux=[]
    nom_fichier1=data_axel.files_available(path_r=PATH_R,folder_ind = 0)[2][len(PATH_R+'/'+dossiers[0]+'\\'):] # renvoie le nom de fichier normal, fonds-solidarite-volet-1-regional-naf-latest
    nom_fichier2='fonds-solidarite-volet-2-regional-naf-latest.csv'   #des fois le premier fichier est vide, il faut donc prendre le fichier 2
    for i in range(len(dossiers)):
        try: #on commence par le fichier2, car il manque un fichier 1 dans le dossier du 1er septembre 2021, ce qui fausse les données de ce jour
            fichier2=pd.read_csv(data_axel.files_available(path_r=PATH_R,folder_ind = i)[data_axel.files_available(path_r=PATH_R,folder_ind = i).index(PATH_R+'/'+dossiers[i]+'\\'+nom_fichier2)])
        except ValueError: #dans le cas où le fichier 2 n'existe pas, fichier2 est un DataFrame vide
            fichier2=pd.DataFrame()
        try:
            fichier1=pd.read_csv(data_axel.files_available(path_r=PATH_R,folder_ind = i)[data_axel.files_available(path_r=PATH_R,folder_ind = i).index(PATH_R+'/'+dossiers[i]+'\\'+nom_fichier1)])
            fichier_glob=pd.concat([fichier1,fichier2]) #notre fichier global est une concaténation des deux fichiers
            liste_eco_regionaux.append(fichier_glob) #on ajoute le fichier global à notre liste, on aura donc une liste représentant l'évolution des différentes colonnes dans le temps
        except ValueError: #dans le cas où le fichier 1 est vide comme pour le 1er septembre 2021, on ne prend pas en compte les données
            pass
    evol_montant= [file.groupby(['libelle_region'])['montant_total'].sum()/10**3 for file in liste_eco_regionaux] #on prend la somme totale par région à chaque date
    abscisse=pd.DataFrame([[nom_fichier[4:] for i in range(len(evol_montant[0]))] for nom_fichier in dossiers]) #on crée un dataframe avec 1 colonne pour chaque région et une ligne pour chaque date
    #cela correspondra à l'abscisse de notre plot
    abscisse.drop(np.where(abscisse[0]=='2021-09-01')[0][0],inplace=True) #on enlève la date du 01/09/2021
    abscisse.reset_index(drop=True,inplace=True) #on reset l'index
    evol_montant=[evol_montant[date].reset_index().set_index(abscisse.loc[date,]) for date in range(len(evol_montant))] #on met les régions en colonnes et les dates en index pour pouvoir plot le dataframe
    df= pd.DataFrame()
    for i in range(len(evol_montant)):
        df=pd.concat([df,evol_montant[i]]) #on regroupe toutes les sommes totales par région par date dans un même dataframe
    
    fig=px.line(df,y="montant_total",color="libelle_region",
            labels={'index':'Date','montant_total':"Montant (en milliers d'Euros)"}, 
            title = "<b>Montant des aides par région</b><br>En milliers d'Euros")
    fig.update_layout(showlegend=False)
    return(fig)


def montants_non_normes_pie():
    PATH_R = "data/fonds-solidarite"
    files = data_axel.files_available(path_r=PATH_R,folder_ind = 0)
    dossiers=data_axel.folders_available(path_r=PATH_R)
    liste_eco_regionaux=[]
    nom_fichier1=data_axel.files_available(path_r=PATH_R,folder_ind = 0)[2][len(PATH_R+'/'+dossiers[0]+'\\'):] # renvoie le nom de fichier normal, fonds-solidarite-volet-1-regional-naf-latest
    nom_fichier2='fonds-solidarite-volet-2-regional-naf-latest.csv'   #des fois le premier fichier est vide, il faut donc prendre le fichier 2
    for i in range(len(dossiers)):
        try: #on commence par le fichier2, car il manque un fichier 1 dans le dossier du 1er septembre 2021, ce qui fausse les données de ce jour
            fichier2=pd.read_csv(data_axel.files_available(path_r=PATH_R,folder_ind = i)[data_axel.files_available(path_r=PATH_R,folder_ind = i).index(PATH_R+'/'+dossiers[i]+'\\'+nom_fichier2)])
        except ValueError: #dans le cas où le fichier 2 n'existe pas, fichier2 est un DataFrame vide
            fichier2=pd.DataFrame()
        try:
            fichier1=pd.read_csv(data_axel.files_available(path_r=PATH_R,folder_ind = i)[data_axel.files_available(path_r=PATH_R,folder_ind = i).index(PATH_R+'/'+dossiers[i]+'\\'+nom_fichier1)])
            fichier_glob=pd.concat([fichier1,fichier2]) #notre fichier global est une concaténation des deux fichiers
            liste_eco_regionaux.append(fichier_glob) #on ajoute le fichier global à notre liste, on aura donc une liste représentant l'évolution des différentes colonnes dans le temps
        except ValueError: #dans le cas où le fichier 1 est vide comme pour le 1er septembre 2021, on ne prend pas en compte les données
            pass
    evol_montant= [file.groupby(['libelle_region'])['montant_total'].sum()/10**3 for file in liste_eco_regionaux] #on prend la somme totale par région à chaque date
    abscisse=pd.DataFrame([[nom_fichier[4:] for i in range(len(evol_montant[0]))] for nom_fichier in dossiers]) #on crée un dataframe avec 1 colonne pour chaque région et une ligne pour chaque date
    #cela correspondra à l'abscisse de notre plot
    abscisse.drop(np.where(abscisse[0]=='2021-09-01')[0][0],inplace=True) #on enlève la date du 01/09/2021
    abscisse.reset_index(drop=True,inplace=True) #on reset l'index
    evol_montant=[evol_montant[date].reset_index().set_index(abscisse.loc[date,]) for date in range(len(evol_montant))] #on met les régions en colonnes et les dates en index pour pouvoir plot le dataframe
    df= pd.DataFrame()
    for i in range(len(evol_montant)):
        df=pd.concat([df,evol_montant[i]]) #on regroupe toutes les sommes totales par région par date dans un même dataframe
    df_pie=df.groupby(['libelle_region'])['montant_total'].sum().reset_index()
    df_pie=pd.concat([df_pie,pd.DataFrame([['Autres',0]],columns=['libelle_region','montant_total'])])
    df_pie.reset_index(drop=True,inplace=True)
    df_pie_inter=df_pie #on crée un df intermédiaire pour que le drop ne gêne pas l'itération
    montant_total_somme=df_pie['montant_total'].sum()
    for i in range(len(df_pie)-1):
        if df_pie_inter.loc[i,].montant_total<0.03*montant_total_somme: #on regroupe les montants d'aide inférieurs à 2% de l'aide totale
            df_pie.iat[len(df_pie)-1,1]+=df_pie_inter.loc[i][1]
            df_pie.drop(i,inplace=True)
    fig_pie=px.pie(df_pie,values='montant_total',names='libelle_region',title='<b>Montant brut cumulé des fonds de solidarité par région</b>')
    return(fig_pie)

def montants_normes_graph():
    PATH_R = "data/fonds-solidarite"
    files = data_axel.files_available(path_r=PATH_R,folder_ind = 0)
    dossiers=data_axel.folders_available(path_r=PATH_R)
    liste_eco_regionaux_2021=[]
    nom_fichier1=data_axel.files_available(path_r=PATH_R,folder_ind = 0)[2][len(PATH_R+'/'+dossiers[0]+'\\'):] # renvoie le nom de fichier normal, fonds-solidarite-volet-1-regional-naf-latest
    nom_fichier2='fonds-solidarite-volet-2-regional-naf-latest.csv'   #des fois le premier fichier est vide, il faut donc prendre le fichier 2
    for i in range(len(dossiers[dossiers.index('fds-2021-01-18')+1:])): #le fichier du 18/01/2021 est le dernier où la variable nombre_entreprises n'apparaît pas

        try: #on commence par le fichier2, car il manque un fichier 1 dans le dossier du 1er septembre 2021, ce qui fausse les données de ce jour
            fichier2=pd.read_csv(data_axel.files_available(path_r=PATH_R,folder_ind = i+dossiers.index('fds-2021-01-18')+1)[data_axel.files_available(path_r=PATH_R,folder_ind = i+dossiers.index('fds-2021-01-18')+1).index(
                PATH_R+'/'+dossiers[i+dossiers.index('fds-2021-01-18')+1]+'\\'+nom_fichier2)])
        except ValueError: #dans le cas où le fichier 2 n'existe pas, fichier2 est un DataFrame vide
            fichier2=pd.DataFrame()
        try:
            fichier1=pd.read_csv(data_axel.files_available(path_r=PATH_R,folder_ind = i+dossiers.index('fds-2021-01-18')+1)[data_axel.files_available(path_r=PATH_R,folder_ind = i+dossiers.index('fds-2021-01-18')+1).index(
                PATH_R+'/'+dossiers[i+dossiers.index('fds-2021-01-18')+1]+'\\'+nom_fichier1)])
            fichier_glob=pd.concat([fichier1,fichier2]) #notre fichier global est une concaténation des deux fichiers
            liste_eco_regionaux_2021.append(fichier_glob) #on ajoute le fichier global à notre liste, on aura donc une liste représentant l'évolution des différentes colonnes dans le temps
        except ValueError: #dans le cas où le fichier 1 est vide comme pour le 1er septembre 2021, on ne prend pas en compte les données
            pass
    evol_montant_2021= [file.groupby(['libelle_region'])['montant_total'].sum()/10**3 for file in liste_eco_regionaux_2021] #on prend la somme totale par région à chaque date
    evol_nb_entreprises_2021= [file.groupby(['libelle_region'])['nombre_entreprises'].sum() for file in liste_eco_regionaux_2021] #on prend le nombre d'entreprises total par région à chaque date
    evol_montant_norme=[evol_montant_2021[i]/evol_nb_entreprises_2021[i] for i in range(len(evol_montant_2021))]
    abscisse_norme=pd.DataFrame([[nom_fichier[4:] for i in range(len(evol_montant_norme[0]))] for nom_fichier in dossiers[dossiers.index('fds-2021-01-18')+1:]]) #on crée un dataframe avec 1 colonne pour chaque région et une ligne pour chaque date
    #cela correspondra à l'abscisse de notre plot
    abscisse_norme.drop(np.where(abscisse_norme[0]=='2021-09-01')[0][0],inplace=True) #on enlève la date du 01/09/2021
    abscisse_norme.reset_index(drop=True,inplace=True) #on reset l'index
    evol_montant_norme=[evol_montant_norme[date].reset_index().set_index(abscisse_norme.loc[date,]) for date in range(len(evol_montant_norme))] #on met les régions en colonnes et les dates en index pour pouvoir plot le dataframe
    df_norme= pd.DataFrame()
    for i in range(len(evol_montant_norme)):
        df_norme=pd.concat([df_norme,evol_montant_norme[i]]) #on regroupe toutes les sommes totales par région par date dans un même dataframe
    df_norme.columns=['libelle_region','montants_normes'] #on renomme la colonne des montants normés

    fig_norme=px.line(df_norme,y="montants_normes",color="libelle_region",
    labels={'index':'Date','montants_normes':"Montant normalisés (en milliers d'Euros)"}, 
    title="<b>Montant des aides normalisés par le nombre d'entreprises</b><br>En milliers d'Euros")
    fig_norme.update_layout(showlegend=False)
    return(fig_norme)


def montants_normes_pie():
    PATH_R = "data/fonds-solidarite"
    files = data_axel.files_available(path_r=PATH_R,folder_ind = 0)
    dossiers=data_axel.folders_available(path_r=PATH_R)
    liste_eco_regionaux_2021=[]
    nom_fichier1=data_axel.files_available(path_r=PATH_R,folder_ind = 0)[2][len(PATH_R+'/'+dossiers[0]+'\\'):] # renvoie le nom de fichier normal, fonds-solidarite-volet-1-regional-naf-latest
    nom_fichier2='fonds-solidarite-volet-2-regional-naf-latest.csv'   #des fois le premier fichier est vide, il faut donc prendre le fichier 2
    for i in range(len(dossiers[dossiers.index('fds-2021-01-18')+1:])): #le fichier du 18/01/2021 est le dernier où la variable nombre_entreprises n'apparaît pas

        try: #on commence par le fichier2, car il manque un fichier 1 dans le dossier du 1er septembre 2021, ce qui fausse les données de ce jour
            fichier2=pd.read_csv(data_axel.files_available(path_r=PATH_R,folder_ind = i+dossiers.index('fds-2021-01-18')+1)[data_axel.files_available(path_r=PATH_R,folder_ind = i+dossiers.index('fds-2021-01-18')+1).index(
                PATH_R+'/'+dossiers[i+dossiers.index('fds-2021-01-18')+1]+'\\'+nom_fichier2)])
        except ValueError: #dans le cas où le fichier 2 n'existe pas, fichier2 est un DataFrame vide
            fichier2=pd.DataFrame()
        try:
            fichier1=pd.read_csv(data_axel.files_available(path_r=PATH_R,folder_ind = i+dossiers.index('fds-2021-01-18')+1)[data_axel.files_available(path_r=PATH_R,folder_ind = i+dossiers.index('fds-2021-01-18')+1).index(
                PATH_R+'/'+dossiers[i+dossiers.index('fds-2021-01-18')+1]+'\\'+nom_fichier1)])
            fichier_glob=pd.concat([fichier1,fichier2]) #notre fichier global est une concaténation des deux fichiers
            liste_eco_regionaux_2021.append(fichier_glob) #on ajoute le fichier global à notre liste, on aura donc une liste représentant l'évolution des différentes colonnes dans le temps
        except ValueError: #dans le cas où le fichier 1 est vide comme pour le 1er septembre 2021, on ne prend pas en compte les données
            pass
    evol_montant_2021= [file.groupby(['libelle_region'])['montant_total'].sum()/10**3 for file in liste_eco_regionaux_2021] #on prend la somme totale par région à chaque date
    evol_nb_entreprises_2021= [file.groupby(['libelle_region'])['nombre_entreprises'].sum() for file in liste_eco_regionaux_2021] #on prend le nombre d'entreprises total par région à chaque date
    evol_montant_norme=[evol_montant_2021[i]/evol_nb_entreprises_2021[i] for i in range(len(evol_montant_2021))]
    abscisse_norme=pd.DataFrame([[nom_fichier[4:] for i in range(len(evol_montant_norme[0]))] for nom_fichier in dossiers[dossiers.index('fds-2021-01-18')+1:]]) #on crée un dataframe avec 1 colonne pour chaque région et une ligne pour chaque date
    #cela correspondra à l'abscisse de notre plot
    abscisse_norme.drop(np.where(abscisse_norme[0]=='2021-09-01')[0][0],inplace=True) #on enlève la date du 01/09/2021
    abscisse_norme.reset_index(drop=True,inplace=True) #on reset l'index
    evol_montant_norme=[evol_montant_norme[date].reset_index().set_index(abscisse_norme.loc[date,]) for date in range(len(evol_montant_norme))] #on met les régions en colonnes et les dates en index pour pouvoir plot le dataframe
    df_norme= pd.DataFrame()
    for i in range(len(evol_montant_norme)):
        df_norme=pd.concat([df_norme,evol_montant_norme[i]]) #on regroupe toutes les sommes totales par région par date dans un même dataframe
    df_norme.columns=['libelle_region','montants_normes'] #on renomme la colonne des montants normés
    df_pie_norme=df_norme.groupby(['libelle_region'])['montants_normes'].sum().reset_index()
    fig_pie_norme=px.pie(df_pie_norme,values='montants_normes',names='libelle_region',
    title='<b>Montants normés cumulés des fonds de solidarité par région</b>')
    return(fig_pie_norme)





#########################
### Reports échéances ###
#########################

path = "data/reports_echeances"
reports = os.listdir(path)
reports = [x for x in reports if '202' in x]
os.listdir(path + '/reports-2020-10-08')

def dict_to_pandas(dictionary, df = None):
    if df is not None:
        data = df.append(dictionary, ignore_index = True)
    else:
        data = pd.DataFrame(dictionary)
    return data



def reports_bruts(mainf = 'data/reports_echeances'):
    series = pd.DataFrame()
    index = []
    for x in reports:
        filedate = x[-10:]
        filedate = datetime.date.fromisoformat(filedate)
        index.append(filedate)
        path = os.path.join(mainf, x)
        file = pd.read_csv(os.path.join(path,'reports-echeances-regional-naf-latest.csv'))
        d = {x : sum(file[file.libelle_region == x].montant_total)/1_000_000_000 for x in file.libelle_region.unique()}
        series = dict_to_pandas(d, series)
    series['Index'] = index
    series.set_index('Index', inplace = True)
    ill_col = [x for x in  series.columns if not isinstance(x, str)]
    series.drop(columns = ill_col, inplace = True)
    series['France'] = series.sum('columns')
    fig = px.line(series, x = series.index, y = 'France', 
                title = "<b>Évolution du montant total de reports d'échéances fiscales</b> <br>En milliards d'Euros", 
                labels = {
                    "France":"Montant total de reports d'échéances",
                    "Index":"Date"
                })
    fig.update_layout(
        margin={"r":40,"t":60,"l":60,"b":20},
        height = 500)
            
    return(fig)

def repartition(mainf = 'data/reports_echeances'): #pas forcément utile
    series = pd.DataFrame()
    index = []
    for x in reports:
        filedate = x[-10:]
        filedate = datetime.date.fromisoformat(filedate)
        index.append(filedate)
        path = os.path.join(mainf, x)
        file = pd.read_csv(os.path.join(path,'reports-echeances-regional-naf-latest.csv'))
        d = {x : sum(file[file.libelle_section == x].montant_total)/1_000_000_000 for x in file.libelle_section.unique()}
        series = dict_to_pandas(d, series)
    series['Index'] = index
    series.set_index('Index', inplace = True)
    ill_col = [x for x in  series.columns if not isinstance(x, str)]
    series.drop(columns = ill_col, inplace = True)
    pie_data = pd.DataFrame()
    names = list(series.columns)
    values = [series[x][-1] for x in names]
    pie_data['names'] = names
    pie_data['values'] = values
    
    fig = px.pie(pie_data, values = 'values', names = 'names', 
            title = "<b>Répartition des montants des reports par secteurs d'activité</b>")
    fig.update_layout(
        margin={"r":40,"t":60,"l":60,"b":20},
        height = 500)
    
    return(fig)


def nouveaux_reports():
    mainf = 'data/reports_echeances'
    series = pd.DataFrame()
    index = []
    for i, x in enumerate(reports):
        filedate = x[-10:]
        filedate = datetime.date.fromisoformat(filedate)
        index.append(filedate)
        path = os.path.join(mainf, x)
        file = pd.read_csv(os.path.join(path,'reports-echeances-regional-naf-latest.csv'))
        good_col = [x for x in file.libelle_section.unique() if isinstance(x, str)]
        d = {x : sum(file[file.libelle_section == x].nombre_reports) for x in good_col}
        if i > 0:
            diff = {x : d[x] - mem[x] for x in d}
        else:
            diff = d
        mem = d 
        series = dict_to_pandas(diff, series)
    series['Index'] = index
    series.set_index('Index', inplace = True)
    ill_col = [x for x in  series.columns if not isinstance(x, str)]
    series.drop(columns = ill_col, inplace = True)
    series = series.sum(axis = 1)
    series = series[-10:]
    fig = px.bar(series, x = series.index, y = series, 
    title = "<b>Nouveaux reports d'échéances fiscales</b>", 
    labels = {
        "y":"", 
        "Index":"Date"
    })
    fig.update_layout(
    margin={"r":30,"t":60,"l":30,"b":20},
    height = 500)
        
    return(fig)