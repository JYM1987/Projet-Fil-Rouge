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

#________________________________________________________________________________
################################# Data prep #############################
#________________________________________________________________________________

#data prep
with open('DfPE.json', 'r') as fichier_json:
    data = json.load(fichier_json)
df = pd.DataFrame(data)

#### columns
columns_to_display = ['id','intitule','entreprise_nom','secteurActiviteLibelle','codeNAF_division_libelle','typeContrat','salaire_moyen','lieuTravail_nom_ville','dateCreation','description']  
columns_display_names = { 
    'id': 'ID de l\'offres',
    'intitule': 'Rôle',
    'entreprise_nom':'Entreprise',
    'secteurActiviteLibelle':'Secteur d\'activite',
    'codeNAF_division_libelle':'Domaine d\'activité',
    'typeContrat':'Type de contrat',
    'salaire_moyen':'Salaire',
    'lieuTravail_nom_ville':'Ville',
    'dateCreation' :'Date annonce',
    'description':'description de l\'offres'
    }
df_sample_filtered = df[df['salaire_moyen'] != 0]

sample_size = 10000
if sample_size <= len(df):
    df_sample = df_sample_filtered.sample(sample_size)
else:    df_sample = df_sample_filtered.copy()


df_sample['lieuTravail_latitude'] = pd.to_numeric(df_sample['lieuTravail_latitude'], errors='coerce')
df_sample['lieuTravail_longitude'] = pd.to_numeric(df_sample['lieuTravail_longitude'], errors='coerce')
df_sample = df_sample.dropna(subset=['lieuTravail_latitude', 'lieuTravail_longitude'])
df_sample = df_sample.dropna(subset=['codeNAF_division_libelle'])


df['experience_nb_annees'] = pd.to_numeric(df['experience_nb_annees'], errors='coerce')
df = df.dropna(subset=['experience_nb_annees'])
df_sample_2_filtered = df[df['experience_nb_annees'] < 8]
sample_size_2 = 100
if sample_size_2 <= len(df):
    df_sample_2 = df_sample_2_filtered.sample(sample_size_2)
else:    df_sample_2 = df_sample_2_filtered.copy()


secteur_options = [{'label': secteur, 'value': secteur} for secteur in df['secteurActiviteLibelle'].unique()]

#________________________________________________________________________________
################################# App creation#############################
#________________________________________________________________________________
external_stylesheets = [dbc.themes.CERULEAN]
app = Dash(__name__, external_stylesheets=external_stylesheets)
colors = { 'background': '#e3eef6'}
#________________________________________________________________________________
################################# Layout def #############################
#________________________________________________________________________________  


#________________________________________________________________________________  
# App layout
app.layout = dbc.Container([

        html.Div(style={
            'background-image': 'url("/assets/background.jpg")',
            'background-repeat': 'no-repeat',
            'background-position': 'right top',
            'background-size': '150px 100px'
            }),

    #________________________________________________________________________________  
    dbc.Row([
        html.Div('Mon Job Market Explorer', className="text-primary text-center fs-3", style={'font-weight': 'bold', 'font-size': '24px'})
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
            value=df_sample['codeNAF_division_libelle'].unique(),
            placeholder="Sélectionnez votre domaine d'activité",
            style={'width': '50%', 'margin-bottom': '10px'}
        )
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
                    df_sample,
                    lat='lieuTravail_latitude',
                    lon='lieuTravail_longitude',
                    color='salaire_moyen',
                    size='salaire_moyen',
                    #hover_data=['intitule', 'lieuTravail_nom_ville'],
                    custom_data=['intitule', 'lieuTravail_nom_ville'],
                    #title='Je choisis la localisation',
                    labels={
                        'salaire_moyen': 'Salaire',
                        'lieuTravail_nom_ville' : 'Ville'
                        },
                    mapbox_style= "open-street-map",#'carto-positron',
                    height=600
                ).update_traces(
                    hovertemplate='Salaire: %{text}<br>Intitule: %{customdata[0]}<br>Ville: %{customdata[1]}',
                    text=df_sample['salaire_moyen'].astype(str)  # Convert 'salaire_moyen' to string for hover template
                     )
            )
        ], className="six columns"),
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
                    ], #, 'lieuTravail_codepostal'],
                    value='salaire_moyen',
                    inline=True,
                    id='my-dbc-radio-items-final')
     ]),
     #________________________________________________________________________________                   
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dash_table.DataTable(
                    columns=[{'name': columns_display_names.get(col, col), 'id': col} for col in columns_to_display ], 
                    data=df[columns_to_display].to_dict('records'), 
                    page_size=15, 
                    style_table={'overflowX': 'auto'})
            ]),
        ], width=6), 
        dbc.Col([  
            dbc.Card([
                dcc.Graph(figure={}, id='graph-placeholder-dbc-final')
            ]),
        ], width=6),
    ]),
#________________________________________________________________________________  
 
#________________________________________________________________________________ 


#________________________________________________________________________________          
], fluid=True)
#________________________________________________________________________________
################################# Callbacks #############################
#________________________________________________________________________________

#________________________________________________________________________________

#________________________________________________________________________________
@app.callback(
    Output(component_id='graph-placeholder-dbc-final', component_property='figure'),
    Input(component_id='my-dbc-radio-items-final', component_property='value')
)
#________________________________________________________________________________

def update_graph(col_chosen):
    x_axis_label = 'Secteur Activité' 

    y_axis_labels = {
        'salaire_moyen': 'salaire moyen',
        'experience_nb_annees': 'nombre d\'année d\'expérience'
    }

    y_axis_label = y_axis_labels.get(col_chosen, 'Choisir la variable à afficher')

 #replace df with df_sample_2
    fig = px.histogram(df_sample_2, x='secteurActiviteLibelle', y=col_chosen, height=500
                       ,color="typeContrat",
                        hover_data=['salaire_moyen', 'experience_nb_annees','intitule'],
                        labels={
                        'salaire_moyen': 'Salaire Moyen',
                        'experience_nb_annees': 'Années d\'Expérience',
                        'intitule':'Poste d\'emploi'
                         }
                        )
    fig.update_layout(xaxis_title=x_axis_label, yaxis_title=y_axis_label)
    return fig

#________________________________________________________________________________
################################# Run App #############################
#________________________________________________________________________________
if __name__ == '__main__':
    app.run_server(debug=True)
