############################################################################
###  ML sur le calcul du salaire en fonction des critères de l'emploi   ###
###########################################################################
#from PE_transform import df
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
df = pd.read_csv("df2.csv", header = 0, low_memory=False)

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

#suppression des données non utilisables
df_ml = df_ml.dropna()

#on ne garde que les codes ROME ayant plus de 20 offres recensées
df_ml = df_ml[df_ml["romeCode"].map(df_ml["romeCode"].value_counts()) >= 100]

#constitution du jeu de test et d'entrainement
features = df_ml.drop("salaire_moyen", axis = 1)
target = df_ml["salaire_moyen"]
X_train, X_test, y_train, y_test = train_test_split(features, target, test_size = 0.2, random_state=42)

#séparation des variables catégorielles et numériques
X_train_cat = X_train[["romeCode"]]
X_train_num = X_train.drop(["romeCode"], axis =1)

X_test_cat = X_test[["romeCode"]]
X_test_num = X_test.drop(["romeCode"], axis =1)

#encodage des variables catégorielles
ohe = OneHotEncoder(drop="first", sparse=False)
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
model = RandomForestRegressor(max_depth = 75, n_estimators=50, max_features=31, random_state=42, criterion='squared_error', min_samples_split=2, min_samples_leaf=1)
#DecisionTreeRegressor  - score train : 0.915
#DecisionTreeRegressor - score test : 0.612

#ML avec un arbre de classification 
#model = DecisionTreeClassifier(max_depth = 5000,  min_samples_leaf = 1, random_state=42, class_weight={"romeCode": 2})
model1 = DecisionTreeClassifier(max_depth = 100,  min_samples_leaf = 1, random_state=42)
#DecisionTreeRegressor  - score train : 0.9538157061431286
#DecisionTreeRegressor - score test : 0.19126029132362254

#ML avec un arbre de regression
model2 = DecisionTreeRegressor(max_depth=50, min_samples_split=5, min_samples_leaf=1, random_state=42, max_features=700) 
#DecisionTreeRegressor  - score train : 0.8884622383773013
#DecisionTreeRegressor - score test : 0.3707654596141745

# arbre aléatoire
model3 = RandomForestClassifier(n_estimators=5, random_state=42)
#DecisionTreeRegressor  - score train : 0.8881728942368587
#DecisionTreeRegressor - score test : 0.1889803673210893

#Clustering
#////model4 = KMeans(n_clusters=50, random_state=42, n_init="auto")

#KNN
model5 = KNeighborsClassifier(n_neighbors=5)
# score train : 0.9529290690310322
# score test : 0.1865104496516783

#entrainement du model choisi (RandomForestRegressor)

model.fit(X_train_robust, y_train)
y_pred = model.predict(X_test_robust)
print(f"\nDecisionTreeRegressor  - score train : {round(model.score(X_train_robust,y_train),3)}")
print(f"DecisionTreeRegressor - score test : {round(model.score(X_test_robust, y_test),3)}")
print(f"Temps d'exécution {round((time.time()-debut)/60 ,3)} minutes")


print('\nMean Absolute Error (MAE):', metrics.mean_absolute_error(y_test, y_pred))
print('Mean Squared Error (MSE):', metrics.mean_squared_error(y_test, y_pred))
print('Root Mean Squared Error (RMSE):', metrics.mean_squared_error(y_test, y_pred, squared=False))
print('Mean Absolute Percentage Error (MAPE):', metrics.mean_absolute_percentage_error(y_test, y_pred))
print('Explained Variance Score:', metrics.explained_variance_score(y_test, y_pred))
print('Max Error:', metrics.max_error(y_test, y_pred))
print('Mean Squared Log Error:', metrics.mean_squared_log_error(y_test, y_pred))
print('Median Absolute Error:', metrics.median_absolute_error(y_test, y_pred))
print('R^2:', metrics.r2_score(y_test, y_pred))
