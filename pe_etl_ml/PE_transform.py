###########################################################################################
###   Transformation des données du site de pôle emploi + insert dans une base No SQL   ###
###########################################################################################
import pandas as pd
import numpy as np
import json
import re
from PE_extraction import dataPE
import time


# on supprime la limite de l'affichage de l'ouput car on a beaucoup de colonne !
pd.set_option('display.max_rows', None)
# Enregistrez le temps de début
debut = time.time()

#---------------------------------------------------
# récupération des données de l'API
#---------------------------------------------------

# Charger le contenu du JSON en tant que liste d'objets
"""with open("dataPE.json", "r") as file:
    dataPE = json.loads(file.read())"""

#---------------------------------------------------
# Fonctions du programme
#---------------------------------------------------

def calcul_multiplicateur(index:int, periodicite:str, nb_mois=12):
    """
    Permet de Calculer le multiplicateur à appliquer afin de pouvoir transformer la valeur du salaire brute horaire ou mensuelle en un salaire annuel
    :index: index de la ligne, permettant d'aller récupérer la durée horaire de travail par semaine dans la zone "dureeTravail" du DF
    :periodicite: contient la périodicité du salaire (annuelle, mensuelle ou horaire)
    :nb_mois: contient le nombre de mois sur lequel est calculé le salaire (12,13,14...)
    :return: le multiplicateur de salaire
    """
    if periodicite == "Horaire":
        # on est payé sur 52 semaines par an que l'on multiplie au nb d'heure travaillé par semaine 
        multiplicateur = float(df.loc[index,"dureeTravail"]) * 52/12 * float(nb_mois)
    elif periodicite == "Mensuel":
        multiplicateur = float(nb_mois)
    else :
        multiplicateur = 1
    return multiplicateur
     

#---------------------------------------------------
# Création du Dataframe de données
#---------------------------------------------------
comp = []

#Extraction des données du Json
data_aplat = []
for job in dataPE:
    data_doc = {
    "accessibleTH": job.get("accessibleTH", ""),
    "appellationlibelle": job.get("appellationlibelle", ""),
    "codeNAF": job.get("codeNAF", ""),
    "competences_nb" : len(job.get("competences", "")),
    #competences : mise à plat Cf ci-dessous
    "dateActualisation": job.get("dateActualisation", ""),
    "dateCreation": job.get("dateCreation", ""),
    "deplacementCode": job.get("deplacementCode", 1),           #intialisation à 1 = jamais de déplacement
    "deplacementLibelle": job.get("deplacementLibelle", ""),
    "description": job.get("description", ""), 
    "dureeTravailLibelle": job.get("dureeTravailLibelle", ""),
    "dureeTravailLibelleConverti": job.get("dureeTravailLibelleConverti", ""),
    "entreprise_nom": job.get("entreprise").get("nom", ""),
    "entreprise_description": job.get("entreprise").get("description", ""),
    "entreprise_logo": job.get("entreprise").get("logo", ""),
    "entreprise_url": job.get("entreprise").get("url", ""),
    "entreprise_adaptee": job.get("entreprise").get("entrepriseAdaptee", ""),
    "experienceExige": job.get("experienceExige", ""),
    "experienceLibelle": job.get("experienceLibelle", ""),
    #"formations": job.get("formations", ""),                   #faible taux de complétion !
    "id": job.get("id", ""),
    "intitule": job.get("intitule", ""),
    "langues_nb" : len(job.get("langues", "")),
    #langues : mise à plat cf ci-dessous
    "lieuTravail_libelle": job.get("lieuTravail").get("libelle", ""),
    "lieuTravail_latitude": job.get("lieuTravail").get("latitude", ""),
    "lieuTravail_longitude": job.get("lieuTravail").get("longitude", ""),
    "lieuTravail_codepostal": str(job.get("lieuTravail").get("codePostal", "")).zfill(5),
    "lieuTravail_commune": str(job.get("lieuTravail").get("commune", "")).zfill(5),
    "natureContrat": job.get("natureContrat", ""),
    "origineOffre": job.get("origineOffre").get("origine", ""),
    "outilsBureautiques": job.get("outilsBureautiques", ""),    
    "permis_nb" : len(job.get("permis", "")),
    #permis : mise à plat Cf ci-dessous
    "qualificationCode": job.get("qualificationCode", ""),
    "qualificationLibelle": job.get("qualificationLibelle", ""),
    "romeCode": job.get("romeCode", ""),
    "romeLibelle": job.get("romeLibelle", ""),
    "salaire_libelle": job.get("salaire").get("libelle", ""),
    "salaire_commentaire": job.get("salaire").get("commentaire", ""),
    "salaire_complement1": job.get("salaire").get("complement1", ""),
    "salaire_complement2": job.get("salaire").get("complement2", ""),
    "codeNAF_division": job.get("secteurActivite", 0),
    "secteurActiviteLibelle": job.get("secteurActiviteLibelle", ""),
    "typeContrat": job.get("typeContrat", ""),
    "typeContratLibelle": job.get("typeContratLibelle", "")
    }
    
    if job.get("langues") != None :
        for i, langue in enumerate(job.get("langues")):
                if langue != None:
                    dict1= {f"langues{i+1}_libelle" : f"{langue.get('libelle','-')}"}
                    dict2 = {f"langues{i+1}_exigence" : f"{langue.get('exigence', '-')}"}
                    data_doc.update(dict1)
                    data_doc.update(dict2)

    if job.get("permis") != None :
        for i, type_permis in enumerate(job.get("permis")):
                dict1= {f"permis{i+1}_libelle" : f"{type_permis.get('libelle', '')}"}
                dict2 = {f"permis{i+1}_exigence" : f"{type_permis.get('exigence', '')}"}
                data_doc.update(dict1)
                data_doc.update(dict2)
    else:
        for i in range(1,3):
            data_doc.update({f"permis{i}_libelle" : ""})
            data_doc.update({f"permis{i}_exigence" : ""})

    if job.get("competences") != None:
        for i, comp in enumerate(job.get("competences")):
                dict1= {f"competences{i+1:02d}_code" : f'{comp.get("code", "")}'}
                dict2 = {f"competences{i+1:02d}_libelle" : f'{comp.get("libelle", "")}'}
                dict3 = {f"competences{i+1:02d}_exigence" : f'{comp.get("exigence", "")}'}
                data_doc.update(dict1)
                data_doc.update(dict2)
                data_doc.update(dict3)


    if job.get("qualitesProfessionnelles") != None:
        for i, qualite in enumerate(job.get("qualitesProfessionnelles")):
                dict1= {f"qualitesProfessionnelles{i+1}_libelle" : f"{qualite.get('libelle', '')}"}
                dict2 = {f"qualitesProfessionnelles{i+1}_description" : f"{qualite.get('description', '')}"}
                data_doc.update(dict1)
                data_doc.update(dict2)

    data_aplat.append(data_doc)

df = pd.DataFrame(data_aplat)
df= df[sorted(df.columns)]

#recopie des données dans un CSV pour vérification
"""df.to_csv("df.csv",sep='|', index=False)
"""
#---------------------------------------------------
# Transformation des données
#---------------------------------------------------

#transformation des Nan en "" (issu de la mise à plat des données)
df = df.fillna("")

# Suppression des doublons
df = df.drop_duplicates()

#remplissage "accessibleTH" par son mode (false)
df["accessibleTH"] = df["accessibleTH"].replace("", df["accessibleTH"].mode()[0])

#extraction de la durée horaire du libellé et transformation au format numérique 38H30 ==> 38.5
df["dureeTravail"] = df["dureeTravailLibelle"].apply(lambda x : x[:2]+"."+ (str(round(int(x.replace(" ", "")[3:5])/60*100 )) if x.replace(" ", "")[3:4].isnumeric() else "00"))
df["dureeTravail"] = df["dureeTravail"].astype("float")

#Reset des index car les transfo suivantes produisent des bizarreries...
df.reset_index(drop=True, inplace=True)

#extraction de la durée d'expérience souhaitée en années en fonction du formatage présent
for x, ligne in enumerate(df["experienceLibelle"]):
    #si la ligne contient "an" et qu'il existe un nombre dans le libellé
    if  (" an" in ligne or " An" in ligne or " ans" in ligne  or " Ans" in ligne or " an(s)" in ligne or " An(s)" in ligne) and re.search(r"\d+", ligne):
        df.at[x, "experience_nb_annees"] = re.search(r"\d+", ligne).group()
    #si la ligne contient "mois" et qu'il existe un nombre dans le libellé
    elif " mois" in ligne and re.search(r"\d+", ligne):
        df.at[x, "experience_nb_annees"] = round(int(re.search(r"\d+", ligne).group())/12, 2)
    #Sinon, si le libellé est simplement formaté avec les 2 mots suivants, on fixera arbitrairement l'expérience requise à 3ans.
    elif "Expérience souhaitée" in ligne or "Expérience exigée" in ligne :
        df.at[x, "experience_nb_annees"] = 3
    #Sinon, on sera dans le cas "Débutant accepté"
    else:
        df.at[x, "experience_nb_annees"] = 0

#extraction du numéro de département et de la ville de la zone lieuTravail_libellé 
#-- extraction et formatage du département sur 2c
df["lieuTravail_num_dep"] = df["lieuTravail_libelle"].str.split(" - ", expand=True)[0]
df["lieuTravail_num_dep"] = df["lieuTravail_num_dep"].str.zfill(2)
#-- extraction du nom de la ville
df["lieuTravail_nom_ville"] = df["lieuTravail_libelle"].str.split(" - ", expand=True)[1]
df.fillna("", inplace=True)

#extraction du salaire minimum et maximum : on 
df["salaire_libelle"] = df["salaire_libelle"].str.replace("," , ".")
for x, ligne in enumerate(df["salaire_libelle"]):
    #recherche des chiffres et des mots-clé ["Horaire", "Mensuel", "Annuel"] pour la périodicité du salaire et du mot "sur" qui nous indiquera le nb de mois [=> sur x mois]
    #la fonction recherche ci dessous renverra une liste en fonction des éléments qu'elle va trouver.
    #soit elle sera vide soit elle aura cette structure : [périodicité, salaire_min, salaire_max*, "sur"*, nb_de_mois*]         
    # --> les éléments * sont facultatifs ; "sur et "nb_de_mois" vont toujours de paire
        l_resultats = re.findall(r"Horaire\b|Mensuel\b|Annuel\b|\d+\.?\d*|\bsur\b", ligne)
        nb_resultats = len(l_resultats)

        if nb_resultats == 2:
            #il n'y a qu'un salaire que l'on va calculer en annuel en fonction de la périodicité affichée et du temps de travail
            multiplicateur = calcul_multiplicateur(x, l_resultats[0])
            df.loc[x,"salaire_min"] = np.trunc(float(l_resultats[1]) * multiplicateur)
            df.loc[x,"salaire_max"] = df.loc[x,"salaire_min"] 
        elif nb_resultats == 3:
            #il n'y a que le salaire minimum et maximum que l'on va calculer en annuel en fonction de la périodicité affichée et du temps de travail
            multiplicateur = calcul_multiplicateur(x, l_resultats[0])
            df.loc[x,"salaire_min"] = np.trunc(float(l_resultats[1]) * multiplicateur)
            df.loc[x,"salaire_max"] = np.trunc(float(l_resultats[2]) * multiplicateur)
        elif nb_resultats == 4:
            #il n'y a que le salaire minimum et le nombre de mois
            multiplicateur = calcul_multiplicateur(x, l_resultats[0], l_resultats[3])
            df.loc[x,"salaire_min"] = np.trunc(float(l_resultats[1]) * multiplicateur)
            df.loc[x,"salaire_max"] = df.loc[x,"salaire_min"] 
        elif nb_resultats == 5:
            #il y a le salaire minimum, maximum et le nombre de mois
            multiplicateur = calcul_multiplicateur(x, l_resultats[0], l_resultats[4])
            df.loc[x,"salaire_min"] = np.trunc(float(l_resultats[1]) * multiplicateur)
            df.loc[x,"salaire_max"] = np.trunc(float(l_resultats[2]) * multiplicateur)
        else:
            df.loc[x,"salaire_min"] = 0
            df.loc[x,"salaire_max"] = 0

# Ajoutez ensuite la colonne "salaire_moyen"
df["salaire_moyen"] = np.trunc((df["salaire_min"] + df["salaire_max"]) / 2)
#exclusion des salaires moyens supérieurs à 150K€ à l'année : dus à des erreurs de saisie.
df["salaire_moyen"] = df["salaire_moyen"].apply(lambda x : 0 if x > 150000 else x)

#Rajout de la division du code 
#-- on récupère la base de données NAF du réseau
df_naf = pd.read_csv("NAF.csv", header=0 , sep=';')
#on index la première colonne
df_naf = df_naf.set_index("Division_NAF")

#-- pour chaque code NAF du type xx.yy.*, nous allons rajouter une colonne avec le libellé correspondant à la division xx
df["codeNAF_division_libelle"] = ""
for x,ligne in enumerate(df["codeNAF"]):
    if ligne != "" and ligne != "":
        df.loc[x,["codeNAF_division_libelle"]] = str(df_naf.loc[int(ligne[:2]), "Libelle_division_NAF"])

#homogénéisation des types de données
df[["experience_nb_annees", "dureeTravail"]] = df[["experience_nb_annees", "dureeTravail"]].astype('float')
df[["deplacementCode", "origineOffre", "qualificationCode"]] = df[["deplacementCode", "origineOffre", "qualificationCode"]].astype('int')
df[["salaire_min", "salaire_max", "salaire_moyen"]] = df[["salaire_min", "salaire_max", "salaire_moyen"]].astype("int")

#df contient toutes les données de Pôle Emploi, on va aussi créer un DF spécialement pour faire un Dashboard sous Dash
#les Dataframes finaux :
df= df[sorted(df.columns)]     

df_dash = df[[  "codeNAF_division_libelle",   	"entreprise_nom",			"lieuTravail_commune",			"romeLibelle",
                "dateCreation",                 "experienceExige",          "lieuTravail_longitude",		"salaire_min",
                "description",                  "experienceLibelle",        "lieuTravail_nom_ville",    	"salaire_max",					  
                "dureeTravailLibelle",          "id",                       "lieuTravail_codepostal",		"salaire_moyen",		 				   
                "dureeTravailLibelleConverti",  "intitule",                 "natureContrat",    			"secteurActiviteLibelle",
                "entreprise_adaptee",           "lieuTravail_latitude",     "qualificationLibelle",			"typeContrat",				                
                "experience_nb_annees",			"lieuTravail_libelle",		"qualificationCode"]]        
df_dash= df_dash[sorted(df_dash.columns)]  


#extraction en CSV et Json pour vérification / travail en local
"""df.to_csv("df2.csv",sep='|', index=False)
#extraction en json
with open("DfPE.json", "w") as fichier:
    json.dump(df_dash.to_dict(orient='records'), fichier, indent=4)"""

print(f"\nTransformation - nombre d'enregistrements : {len(df)}")
print(f"Temps d'exécution {round((time.time()-debut)/60 ,2)} minutes")

