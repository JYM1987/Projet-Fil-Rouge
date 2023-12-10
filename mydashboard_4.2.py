#________________________________________________________________________________
################################# Imports #############################
#________________________________________________________________________________
import dash
from dash import Dash, html, dash_table, dcc
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import json
import dash_bootstrap_components as dbc
from pymongo import MongoClient

print("------ Début de Dash ------")
#________________________________________________________________________________
################################# liaison mongodb #############################
#________________________________________________________________________________

#---------------------------------------------------
# Lecture de la base NoSQL
#---------------------------------------------------
# Connexion à MongoDB
client = MongoClient(host="127.0.0.1", port = 27017)
#définition de la DB
DB = client["DB_job"]
#définition de la collection Dash
c_dash = DB["Dash"]
data_from_mongo = c_dash.find({})
df = pd.DataFrame(list(data_from_mongo))

#________________________________________________________________________________
################################# Data prep #############################
#________________________________________________________________________________

# with open('DfPE.json', 'r') as fichier_json:
#     data = json.load(fichier_json)
# df = pd.DataFrame(data)

#### df filters

#________________________________________________________________________________
# table columns display
columns_to_display = ['id','intitule','entreprise_nom','secteurActiviteLibelle','codeNAF_division_libelle','typeContrat','salaire_moyen','salaire_moyen_ML','lieuTravail_nom_ville','dateCreation','description']  
columns_display_names = { 
    'id': 'ID de l\'offres',
    'intitule': 'Rôle',
    'entreprise_nom':'Entreprise',
    'secteurActiviteLibelle':'Secteur d\'activite',
    'codeNAF_division_libelle':'Domaine d\'activité',
    'typeContrat':'Type de contrat',
    'salaire_moyen':'Salaire',
    'salaire_moyen_ML' : 'Salaire simulé',
    'lieuTravail_nom_ville':'Ville',
    'dateCreation' :'Date annonce',
    'description':'description de l\'offres'
    }
#________________________________________________________________________________
# 10% du dataset complet
#for the map

df_copy1 = df.copy()

df_copy1['salaire_moyen'] = pd.to_numeric(df_copy1['salaire_moyen'], errors='coerce')
df_filtered1 = (df_copy1['salaire_moyen'] > 10000) & (df_copy1['salaire_moyen'] < 80000)
df_filtered1 = df_copy1[df_filtered1].dropna()

df_filtered1['lieuTravail_latitude'] = pd.to_numeric(df_filtered1['lieuTravail_latitude'], errors='coerce')
df_filtered1 ['lieuTravail_longitude'] = pd.to_numeric(df_filtered1['lieuTravail_longitude'], errors='coerce')
df_filtered1 = df_filtered1.dropna(subset=['lieuTravail_latitude', 'lieuTravail_longitude'])
df_filtered1 = df_filtered1.dropna(subset=['codeNAF_division_libelle'])
# condition2 = df_copy1['experience_nb_annees'] < 8
# df_filtered1 = df_copy1[condition2].dropna()


sample_size1 = 13000
if sample_size1 <= len(df_filtered1):
    df_sample1 = df_filtered1.sample(n=sample_size1, random_state=42)
else:    df_sample1 = df_filtered1.copy()

#________________________________________________________________________________
# 5% du dataset complet
# sample_size2 =  6000
# histograme

sample_size2 = 1000
if sample_size2 <= len(df_filtered1):
    df_sample2 = df_sample1.sample(n=sample_size2, random_state=52)
else:    df_sample2 = df_sample1.copy()


codeNAF_counts = df_sample2['codeNAF_division_libelle'].value_counts()

# Sélectionner les 10 codes NAF les plus fréquents
top_10_codeNAF = codeNAF_counts.head(15).index

# Filtrer le DataFrame pour inclure uniquement les lignes correspondant aux 10 codes NAF sélectionnés
df_top_10 = df_sample2[df_sample2['codeNAF_division_libelle'].isin(top_10_codeNAF)]

#________________________________________________________________________________
# 1% du dataset complet
# histograme

# df_copy2 = df.copy()
# df_copy2['experience_nb_annees'] = pd.to_numeric(df_copy2['experience_nb_annees'], errors='coerce')
# df_copy2 = df_copy2.dropna(subset=['experience_nb_annees'])
# condition2 = (df_copy2['experience_nb_annees'] < 8) & (df_copy2['salaire_moyen'] > 10000 ) & (df_copy2['salaire_moyen'] < 80000)
# df_filtered2 = df_copy2[condition2].dropna()

# sample_size2 = 130
# if sample_size2 <= len(df_filtered2):
#     df_sample2 = df_filtered2.sample(n=sample_size2, random_state=52)
# else:    df_sample2 = df_filtered2.copy()

#________________________________________________________________________________

secteur_options = [{'label': secteur, 'value': secteur} for secteur in df['secteurActiviteLibelle'].unique()]

#________________________________________________________________________________
################################# App creation#############################
#________________________________________________________________________________
external_stylesheets = [dbc.themes.CERULEAN]
app = Dash(__name__, external_stylesheets=external_stylesheets)

#________________________________________________________________________________
################################# Layout def #############################
#________________________________________________________________________________  


#________________________________________________________________________________  
# App layout
app.layout = dbc.Container([
    #________________________________________________________________________________  
    dbc.Row([
        html.Div('Mon Job Market Explorer', className="text-primary text-center fs-3", style={'font-weight': 'bold', 'font-size': '24px'})
    ]),
    #________________________________________________________________________________  

    dbc.Row([
        html.Div([
            html.H3('Je choisis ma localisation', className="text-primary text-center fs-3", style={'font-size': '24px'}),
            # Map
            dcc.Graph(
                id='map',
                figure=px.scatter_mapbox(
                    #df,
                    df_sample1,
                    lat='lieuTravail_latitude',
                    lon='lieuTravail_longitude',
                    color='salaire_moyen',
                    size='salaire_moyen',
                    custom_data=['intitule', 'salaire_moyen', 'salaire_moyen_ML','lieuTravail_nom_ville'],
                    labels={
                        'intitule': 'Intitule',           
                        'salaire_moyen': 'Salaire',
                        'salaire_moyen_ML' : 'Salaire simulé',
                        'lieuTravail_nom_ville' : 'Ville'
                        },
                    mapbox_style= "open-street-map",#'carto-positron',
                    height=600
                ).update_traces(
                    hovertemplate='Intitulé: %{customdata[0]}<br>Salaire: %{customdata[1]}<br>Salaire_simulé: %{customdata[2]}<br>Ville: %{customdata[3]}',
                   )
            )
        ], className="six columns"),
    ]),
    #________________________________________________________________________________  
    dbc.Row([
        html.Div('Je choisis mon domaine d\'activité', className="text-primary text-center fs-3")
    ]),
    dbc.Row([
        dcc.Dropdown(
            id='secteur-dropdown',
            options=secteur_options,
            multi=False,
            value=df['codeNAF_division_libelle'].unique(),
            placeholder="Sélectionnez votre domaine d'activité",
            style={'width': '50%', 'margin-bottom': '10px'}
        )
    ]),

     #________________________________________________________________________________  
    dbc.Row([
        dbc.Card([
            dash_table.DataTable(
            columns=[{'name': columns_display_names.get(col, col), 'id': col} for col in columns_to_display ], 
             data=df[columns_to_display].to_dict('records'), 
             page_size=15, 
             style_table={'overflowX': 'auto'},
             id='mytable'
             )
            ]),
     ]), 
     #________________________________________________________________________________  
    dbc.Row([
        html.Div('Je parcours mes offres d\'emploi', className="text-primary text-center fs-3")
    ]),
    #________________________________________________________________________________  
    dbc.Row([
    dcc.RadioItems(options=[
                    {'label': 'salaire moyen', 'value': 'salaire_moyen'},
                    {'label': 'années d\'expérience', 'value': 'experience_nb_annees'},                 
                    ], 
                    value='salaire_moyen',
                    inline=True,
                    id='my-dbc-radio-items-final')
     ]),
     #________________________________________________________________________________                   
    dbc.Row([ 
        dbc.Card([
             dcc.Graph(figure={}, id='graph-placeholder-dbc-final')
            ]),
     ]),
#________________________________________________________________________________  
 
#________________________________________________________________________________ 


#________________________________________________________________________________          
], fluid=True)
#________________________________________________________________________________
################################# Callbacks #############################
#________________________________________________________________________________
# @app.callback(
#     Output('mytable', 'data'),
#     Input('secteur-dropdown', 'value')
# )
#________________________________________________________________________________
#def update_table(selected_secteur):
    # # Filter the data based on the selected domain
    # print(f"Selected Secteur: {selected_secteur}")
    # filtered_df = df[df['codeNAF_division_libelle'].astype(str) == str(selected_secteur)]
    # print(f"Filtered DataFrame: {filtered_df}")
    # updated_data = filtered_df[columns_to_display].to_dict('records')
    # print(f"Updated Data: {updated_data}")
    # return updated_data

    # # Create the updated map
    # updated_map = px.scatter_mapbox(
    #     filtered_df,
    #     lat='lieuTravail_latitude',
    #     lon='lieuTravail_longitude',
    #     color='salaire_moyen',
    #     size='salaire_moyen',
    #     custom_data=['intitule', 'lieuTravail_nom_ville'],
    #     labels={'salaire_moyen': 'Salaire', 'lieuTravail_nom_ville': 'Ville'},
    #     mapbox_style="open-street-map",
    #     height=600
    # ).update_traces(
    #     hovertemplate='Salaire: %{text}<br>Intitule: %{customdata[0]}<br>Ville: %{customdata[1]}',
    #     text=filtered_df['salaire_moyen'].astype(str)  # Convert 'salaire_moyen' to string for hover template
    # )
    #return updated_table

#________________________________________________________________________________
@app.callback(
    Output(component_id='graph-placeholder-dbc-final', component_property='figure'),
    Input(component_id='my-dbc-radio-items-final', component_property='value')
)
#________________________________________________________________________________

def update_graph(col_chosen):
    x_axis_label = 'Secteur Activité' 

    y_axis_labels = {
        'salaire_moyen': 'Salaire moyen',
        'experience_nb_annees': 'Nombre d\'année d\'expérience',
    }

    y_axis_label = y_axis_labels.get(col_chosen, 'Choisir la variable à afficher')

 #replace df with df_sample_2
    fig = px.scatter(df_top_10, x='codeNAF_division_libelle', 
                       y=col_chosen, 
                       height=900,
                       color= 'codeNAF_division_libelle',
                       #color = 'typeContrat',
                       hover_data=['codeNAF_division_libelle','intitule','typeContrat','salaire_moyen', 'experience_nb_annees'],
                       labels={
                        'codeNAF_division_libelle': 'Domaine d\'activité',
                        'intitule':'Poste',
                        'typeContrat': 'Contrat',
                        'salaire_moyen': 'Salaire Moyen',
                        'experience_nb_annees': 'Années d\'Expérience'
                         }
                        )
    fig.update_xaxes(categoryorder='category ascending', tickangle=45) #, showticklabels=False)
    #fig.update_layout(xaxis_title='', yaxis_title=y_axis_label)
    #fig.update_layout(yaxis_title=y_axis_label)
    fig.update_layout(xaxis_title=x_axis_label, yaxis_title=y_axis_label)
    # Supprimer les labels des couleurs
    fig.update_traces(marker=dict(size=12, line=dict(color='white', width=2)), selector=dict(mode='markers'), showlegend=False)

    return fig

#________________________________________________________________________________
################################# Run App #############################
#________________________________________________________________________________
if __name__ == '__main__':
    app.run_server(debug=True)
