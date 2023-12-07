##################################################
###     Webscraping du site de pôle emploi     ###
##################################################
import os 
import requests
import json
import sys
import time

# Enregistrez le temps de début
debut = time.time()

#############################################################
# Appel de l'API de génération du Token
#############################################################

#récupération de la clé github ?
API_KEY = os.environ.get('api_key')
API_ID_CLIENT = os.environ.get('api_id_client')

#à supprimer : clé en dur pour test local
API_c1 = "PAR_dat"
API_c2 = "ascientest_7cc80d476c"
API_c3 = "bbaaa1b635864f02d8825a4e46eee4d87e45bc7e6642770741fa6f"
API_ID_CLIENT = API_c1+API_c2+API_c3
API_k1 = "e888aeb08dd9e4a022"
API_k2 = "d7895b851f305c6d343692"
API_k3 = "b0b52ef8135f1418a3661bc0"
API_KEY = API_k1+API_k2+API_k3

print("***********", API_KEY, "*****************")
print("***********", API_ID_CLIENT, "*****************")

# Paramètre du point d"accès (URL, entête et token)
url_token = "https://entreprise.pole-emploi.fr/connexion/oauth2/access_token?realm=%2Fpartenaire"
headers_token = { "Content-Type": "application/x-www-form-urlencoded"}
data_token = {
    "grant_type": "client_credentials"
   , "client_id": API_ID_CLIENT
   , "client_secret": API_KEY 
   , "scope": "api_offresdemploiv2 o2dsoffre api_stats-informations-territoirev1 infosterritoire"
}

def appel_API_token():
    """
    Appel et récupération du token d'habilitation pour l'utilisation de l'API offre d'emploi via l'API d'authentification
    :return: réponse de l'API d'authentification
    """
    r_token = requests.post(url_token, headers=headers_token, data=data_token)
    return r_token

def gestion_rc_token(reponse, params={}):
    """
    récupération et gestion de la réponse de l'API d'habilitation
    :reponse: la réponse de l'API d'authentification
    :params: le contenu de la partie data envoyé à l'API
    :return: le jeton d'autentification pour alimenter le header de l'API des offres d'emploi
    """
    if reponse.status_code == 200 :
        print("Récupération de la clé d'accès Pôle Emploi : OK")
        access_token_bearer = reponse.json()["access_token"]
        return access_token_bearer
    else:
        print(f"paramètres d'appel: {params} ") 
        sys.exit(f"Erreur lors de l'appel à l'API de génération du token de connection, code retour {reponse.status_code}, erreur : {reponse.json().get('error')}")

#############################################################
# Appel de l'API de récupération des jobs Pôle Emploi
#############################################################
seq_appel = 1

# Paramètre du point d"accès (URL et paramètres ; l'autorisation va être construite suite à un premier appel à l'API de génération du token)
url_offres = "https://api.pole-emploi.io/partenaire/offresdemploi/v2/offres/search?"
params = {
    "range" : "0-149",              #nombre d'offres renvoyés par appel (max 150)
    "qualification": 0,             # Niveau de qualification demandé (0 -> Non cadre ;  9 -> Cadre)
    "typeContrat":"CDI",            #ou CDD
    "tempsPlein" : "true",          #"true"/"false"
    "origineOffre":1,               #"1 : Pole emploi ; 2 : Partenaires
    "departement":67,
    "alternance":"false"
    #"motsCles": "informatique",    # Recherche par mot clé
    #"commune": "67482",            # Exemple de codes INSEE de communes
    #"distance" : 10                # rayon en km; 0 pour spécifier uniquement les offres de la ville
}

def appel_API_offres(access_token):
    """
    Appel et récupération de la réponse de l'API des offres d'emploi
    :access_token: jeton d'authentification de l'API d'authentification appelé précédemment
    :return: réponse brute de l'API des offres d'emploi
    """
    authorisation = {"Authorization": f"Bearer {access_token}"}
    r_req = requests.get(url_offres, params=params, headers=authorisation)
    return r_req

def maj_param_appel(variable, valeur):
    """
    Met à jours les paramètres d'appel à l'API d'offres d'emploi 
    :variable: nom de la variable à modifier
    :valeur: nouvelle valeur que doit avoir cette variable. Dans le cas du "range", la valeur contiendra le numéro de séquence d'appel afin pouvoir récupérer 
            toutes les réponses s'il existe plus de 150 offres
    :return: rien
    """
    #mise à jour spécique du range qui commence par un paramétrage "0-149" et qui augmente selon à pas de 150. 
    #le pas est paramétré selon le numéro de séquence d'appel qui commence à 1 et qui sera contenu dans la variable "valeur"
    if variable == "range":
        range_1 = "0-149"
        param_range = [int(i) + 150 * (valeur - 1) for i in range_1.split("-")]
        valeur = str(param_range[0])+"-"+ str(param_range[1])
    
    #Dans tous les cas, on va mettre à jour le paramétrage avec la valeur d'entrée ou calculée dans cette fonction
    params.update({variable: valeur})
    
def gestion_rc_offres(reponse, seq_appel, params):
    """
    Gestion des codes retour de l'API des offres d'emploi
    :reponse: réponse brute de l'API des offres d'emploi
    :seq_appel: Séquence d'appel dans le cas d'appel successif si le nombre d'offres > 150
    :params: paramètre d'appel de l'API des offres d'emploi
    :return: True si l'appel s'est bien passé, false dans le cas contraire
    """
    if reponse.status_code == 200 :
        print("Récupération de la liste des jobs : OK")
    elif reponse.status_code == 206:
        if seq_appel == 20:
            print("Récupération partielle de la liste des jobs : plus de 3000 jobs !")
        else:
            return True
    elif reponse.status_code == 204 :
        if seq_appel == 1:
            print("Aucune offre trouvée pour les critères de sélection ! : OK")
            print(f"Paramètre en d'appel : {params}")
            return False
        else:
            print("Récupération de la liste des jobs : OK")
            return False
    elif reponse.status_code == 400 :
        print(f"Problème d'appel avec les paramètres suivants : \n {params} - {reponse.json()['message']}")
        return False
    else:
        print(f"Paramètre en d'appel : {params}")
        print(f"Séquence d'appel n°{seq_appel}") 
        print(f"Reponse {reponse}")    
        sys.exit(f"Erreur lors de l'appel à l'API de récupération des jobs, code retour {reponse.status_code} - {reponse.json()['message']}")
    
######################################
#traitement principal
######################################

#----------------------------------
#Extraction des données emplois
#----------------------------------
#cinématique : étant donné que l'API nous limite à 3000 emplois par appel, nous allons démultiplier les appels en jouant sur les paramètres d'appel
#afin de récolte un panel de job le plus large possible et l'agréger dans la liste datePE :
dataPE = []
#récupération des annonces pour chacun des départements français de métropole
for departement in [f"{i:02d}" for i in range(1,96)]:
    maj_param_appel("departement", departement)

    #(ré)initialisation du token d'accès tous les 10 départements afin de ne pas se faire jeter par l'API.
    if departement in [f"{i:02d}" for i in range(1,96,1)]:
        rep_token = appel_API_token()
        access_token = gestion_rc_token(rep_token, data_token)

    #récupération des annonces pour en fonction de la qualification du poste : non cadre (0) ou cadre (9)
    for qualification in [0,9]:
        maj_param_appel("qualification", qualification)

        #récupération des annonces pour en fonction du type de contrat
        for type_contrat in ["CDI", "CDD"]:
            maj_param_appel("typeContrat", type_contrat)

            #récupération des annonces Pôle emploi (1) ainsi que des fournisseurs autres (2) et on réinitialise le range à "0-149"
            for origine_offre in [1,2]:
                seq_appel = 1
                maj_param_appel("origineOffre", origine_offre)
                maj_param_appel("range", seq_appel)
                #récupération des offres 
                r_req = appel_API_offres(access_token)
                if gestion_rc_offres(r_req, seq_appel, params):
                    for offre in r_req.json()["resultats"]:
                        dataPE.append(offre)

                # -- on boucle si on n'a pas récupéré toutes les réponses lors du 1er appel  -- limitation technique fixée 3000 enregs soit à 19 séquences d'appel par l'API
                while r_req.status_code == 206 and seq_appel < 20:
                    seq_appel += 1 
                    maj_param_appel("range", seq_appel)
                    r_req = appel_API_offres(access_token)
                    if gestion_rc_offres(r_req, seq_appel, params):
                        for offre in r_req.json()["resultats"]:
                            dataPE.append(offre)
                    
#écriture d'un fichier externe pour visualisation du json de réponse
with open("dataPE.json", "w") as fichier:
    json.dump(dataPE, fichier, indent=4)
#with open("r_req.json", "w") as fichier:
#   fichier.write(r_req.text)

print(f"\nExtraction - Nombre de données extraites : {len(dataPE)}")
print(f"Temps d'exécution {round((time.time()-debut)/60 ,2)} minutes")

