#############################################################
###   Création de la base NoSQL + insert des données PE   ###
#############################################################
from pprint import pprint
from pymongo import MongoClient
from PE_ml import df, df_dash
import time

# Enregistrez le temps de début
debut = time.time()

#---------------------------------------------------
# création de la base NoSQL
#---------------------------------------------------

# Connexion à MongoDB
client = MongoClient(host="127.0.0.1", port = 27017)

#création de la DB
DB = client["DB_job"]
#Création et initialisation de la collection "PE_all" qui regroupe toutes les données de Pôle Emploi 
# et "Dash" qui regroupe toutes les données utiles pour faire un Dashboard
c_PE = DB["PE"]
c_dash = DB["Dash"]
# RAZ des collections
c_PE.drop()
c_dash.drop()

#---------------------------------------------------
# insertion des données 
#---------------------------------------------------
c_PE.insert_many(df.to_dict(orient="records"))

df_dash["salaire_moyen_ML"] = df["salaire_moyen_ML"]
c_dash.insert_many(df_dash.to_dict(orient="records"))

print(f"\nLoad - nombre d'enregistrements : {c_PE.count_documents({})}")
print(f"Temps d'exécution {round((time.time()-debut)/60 ,2)} minutes")