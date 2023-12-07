############################################################################
###  ML sur le calcul du salaire en fonction des critères de l'emploi   ###
###########################################################################
from PE_transform import df, df_dash
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, MinMaxScaler, RobustScaler
from sklearn.tree import DecisionTreeRegressor, DecisionTreeClassifier
from sklearn import metrics
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.neighbors import KNeighborsClassifier
import time


debut = time.time()
# on supprime la limite de l'affichage de l'ouput car on a beaucoup de colonne !
pd.set_option('display.max_rows', None)

#####################################
###   Création du DF de données   ###
#####################################

# Chargez le DataFrame en spécifiant les types de données
#df = pd.read_csv("df2.csv",sep='|', header = 0, low_memory=False)

#construction du DF de données
df_ml = df[["competences_nb",       "deplacementCode",      "dureeTravail", 
            "experience_nb_annees", "lieuTravail_num_dep",  "qualificationCode", 
            "romeCode",             "salaire_moyen",        "codeNAF_division"]]

#dans le doute, on va retyper toutes les colonnes. (=> DtypeWarning)
df_ml.loc[:, "competences_nb"] = df_ml["competences_nb"].astype("int64")
df_ml.loc[:, "deplacementCode"] = df_ml["deplacementCode"].astype("int64")
df_ml.loc[:, "dureeTravail"] = df_ml["dureeTravail"].astype("float64")
df_ml.loc[:, "experience_nb_annees"] = df_ml["experience_nb_annees"].astype("float64")
df_ml.loc[:, "lieuTravail_num_dep"] = df_ml["lieuTravail_num_dep"].astype("int64")
df_ml.loc[:, "qualificationCode"] = df_ml["qualificationCode"].astype("int64")
df_ml.loc[:, "romeCode"] = df_ml["romeCode"].astype("object")
df_ml.loc[:, "salaire_moyen"] = df_ml["salaire_moyen"].astype("float64")
df_ml.loc[:, "codeNAF_division"] = df_ml["codeNAF_division"].astype("object")

###############################
### Nettoyage des données   ###
###############################
df_ml_mod = df_ml
#Suppression des lignes qui ont un salaire moyen non renseigné ( valorisés à 0 ~30% du dataset)
df_ml_mod = df_ml_mod.loc[df_ml_mod["salaire_moyen"] != 0]
#suppression des données non utilisables (essentiellement les codeNAF non renseignés ~ 2,5% du dataset)
df_ml_mod = df_ml_mod.dropna()
#on ne garde que les codes ROME ayant plus de 20 offres recensées
df_ml_mod = df_ml_mod[df_ml_mod["romeCode"].map(df_ml_mod["romeCode"].value_counts()) >= 20]

#constitution du jeu de test et d'entrainement
features = df_ml_mod.drop("salaire_moyen", axis = 1)
target = df_ml_mod["salaire_moyen"]
X_train, X_test, y_train, y_test = train_test_split(features, target, test_size = 0.1, random_state=42)

#séparation des variables catégorielles et numériques
X_train_cat = X_train[["romeCode"]]
X_train_num = X_train.drop(["romeCode"], axis =1)

X_test_cat = X_test[["romeCode"]]
X_test_num = X_test.drop(["romeCode"], axis =1)

#encodage des variables catégorielles
ohe = OneHotEncoder(drop="first", sparse_output=False)
X_train_cat = ohe.fit_transform(X_train_cat)
X_test_cat  = ohe.transform(X_test_cat)

#réassemblage des données
X_train_ohe = np.concatenate((X_train_cat, X_train_num), axis=1)
X_test_ohe = np.concatenate((X_test_cat,X_test_num), axis=1)

#Normalisation
scaler = MinMaxScaler()
X_train_scaler = scaler.fit_transform(X_train_ohe)
X_test_scaler = scaler.transform(X_test_ohe)

#gestion des outliers
robustscaler = RobustScaler()
X_train_robust = robustscaler.fit_transform(X_train_scaler)
X_test_robust = robustscaler.transform(X_test_scaler)


# arbre aléatoire regression => !!!! Meilleur ML !!!!
model1 = RandomForestRegressor(max_depth = 70, n_estimators=100, max_features=25, random_state=42, criterion='squared_error', min_samples_split=2, min_samples_leaf=1)
#DecisionTreeRegressor  - score train : 0.915
#DecisionTreeRegressor - score test : 0.612
"""
#ML avec un arbre de classification 
model2 = DecisionTreeClassifier(max_depth = 50,  min_samples_leaf = 1, random_state=42, min_samples_split=2)
#DecisionTreeRegressor  - score train : 0.9538157061431286
#DecisionTreeRegressor - score test : 0.19126029132362254

#KNN
model3 = KNeighborsClassifier(n_neighbors=5)
# score train : 0.9529290690310322
# score test : 0.1865104496516783

#ML avec un arbre de regression
model4 = DecisionTreeRegressor(max_depth=100, min_samples_split=5, min_samples_leaf=1, random_state=42, max_features=300) 
#DecisionTreeRegressor  - score train : 0.8884622383773013
#DecisionTreeRegressor - score test : 0.3707654596141745

# arbre aléatoire
model5 = RandomForestClassifier(n_estimators=5, random_state=42)
#DecisionTreeRegressor  - score train : 0.8881728942368587
#DecisionTreeRegressor - score test : 0.1889803673210893

#Clustering
#////model6 = KMeans(n_clusters=50, random_state=42, n_init="auto") => plantage...
"""

#entrainement du model choisi (RandomForestRegressor)
model1.fit(X_train_robust, y_train)
y_pred_test = np.trunc(model1.predict(X_test_robust))

print("\nMachine Learning - statistiques finales")
print('------------------------------------------------------------')
print(f"RandomForestRegressor  - score train : {round(model1.score(X_train_robust,y_train),3)}")
print(f"RandomForestRegressor - score test : {round(model1.score(X_test_robust, y_test),3)}")
print('------------------------------------------------------------')
print('\nMean Absolute Error (MAE):', np.trunc(metrics.mean_absolute_error(y_test, y_pred_test)))
print('Mean Squared Error (MSE):', np.trunc(metrics.mean_squared_error(y_test, y_pred_test)))
print('Root Mean Squared Error (RMSE):', np.trunc(metrics.mean_squared_error(y_test, y_pred_test, squared=False)))
print('Mean Absolute Percentage Error (MAPE):', round(metrics.mean_absolute_percentage_error(y_test, y_pred_test)),3)
print('Explained Variance Score:', round(metrics.explained_variance_score(y_test, y_pred_test)),3)
print('Max Error:', np.trunc(metrics.max_error(y_test, y_pred_test)))
print('Mean Squared Log Error:', round(metrics.mean_squared_log_error(y_test, y_pred_test)),3)
print('Median Absolute Error:', np.trunc(metrics.median_absolute_error(y_test, y_pred_test)))


############################################################################################################################
#alimentation du DF Pôle emploi avec les données simulées dans une nouvelle colonne : concaténation des simuls train et test
############################################################################################################################

#suppression des données non utilisables (essentiellement les codeNAF non renseignés ~ 2,5% du dataset)

df_ml_all = df_ml.fillna("")

features_all = df_ml_all.drop("salaire_moyen", axis = 1)
target_all = df_ml_all["salaire_moyen"]

#séparation des variables catégorielles et numériques
X_cat = features_all[["romeCode"]]
X_num = features_all.drop(["romeCode"], axis =1)

#encodage des variables catégorielles
ohe = OneHotEncoder(drop="first", sparse_output=False)

#X_cat_encoded  = ohe.fit_transform(X_cat)
X_cat_encoded = ohe.fit_transform(X_cat)
X_cat_encoded = ohe.transform(X_cat)

#réassemblage des données
X_ohe = np.concatenate((X_cat_encoded, X_num), axis=1)

#Normalisation
scaler = MinMaxScaler()
X_scaler  = scaler.fit_transform(X_ohe)
X_scaler = scaler.transform(X_ohe)

#gestion des outliers
robustscaler = RobustScaler()
X_robust = robustscaler.fit_transform(X_scaler)
X_robust = robustscaler.transform(X_scaler)

#on va reprédire les données avec le meilleur modèle
model1.fit(X_robust, target_all)
df["salaire_moyen_ML"] = np.trunc(model1.predict(X_robust))
df_dash["salaire_moyen_ML"] = df["salaire_moyen_ML"]

print("\nMachine Learning - statistiques finales")
print('------------------------------------------------------------')
print(f"RandomForestRegressor  - score réel : {round(model1.score(X_robust, target_all),3)}")
print('------------------------------------------------------------')
print('\nMean Absolute Error (MAE):', np.trunc(metrics.mean_absolute_error(target_all, df["salaire_moyen_ML"])))
print('Mean Squared Error (MSE):', np.trunc(metrics.mean_squared_error(target_all, df["salaire_moyen_ML"])))
print('Root Mean Squared Error (RMSE):', np.trunc(metrics.mean_squared_error(target_all, df["salaire_moyen_ML"], squared=False)))
print('Mean Absolute Percentage Error (MAPE):', round(metrics.mean_absolute_percentage_error(target_all, df["salaire_moyen_ML"])),3)
print('Explained Variance Score:', round(metrics.explained_variance_score(target_all, df["salaire_moyen_ML"])),3)
print('Max Error:', np.trunc(metrics.max_error(target_all, df["salaire_moyen_ML"])))
print('Mean Squared Log Error:', round(metrics.mean_squared_log_error(target_all, df["salaire_moyen_ML"])),3)
print('Median Absolute Error:', np.trunc(metrics.median_absolute_error(target_all, df["salaire_moyen_ML"])))

print(f"Temps d'exécution {round((time.time()-debut)/60 ,2)} minutes")