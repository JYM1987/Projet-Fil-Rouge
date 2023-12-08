#________________________________________________________________________________
################################# Imports #############################
#________________________________________________________________________________
from dash import Dash, dcc, html, Input, Output
from dash.dependencies import Input, Output
from dash import dash_table
import plotly.express as px
import pandas as pd
import json
import requests

#________________________________________________________________________________
################################# Data prep #############################
#________________________________________________________________________________

#data prep
with open('splitted_1.json', 'r') as fichier_json:
    data = json.load(fichier_json)
df = pd.DataFrame(data)

#### columns
columns_to_display = ['id','intitule','entreprise_nom','secteurActiviteLibelle','codeNAF_libelle_division','typeContrat','salaire_min','lieuTravail_nom_ville','description']  # Choose the columns to display
columns_display_names = { 
    'id': 'ID de l\'offres',
    'intitule': 'Rôle',
    'entreprise_nom':'Entreprise',
    'secteurActiviteLibelle':'Secteur d\'activite',
    'codeNAF_libelle_division':'Code NAF',
    'typeContrat':'Type de contrat',
    'salaire_min':'Salaire',
    'lieuTravail_nom_ville':'Ville',
    'description':'description de l\'offres'
    }

#________________________________________________________________________________
################################# App creation#############################
#________________________________________________________________________________

app = Dash(__name__)

#________________________________________________________________________________
################################# Layout def #############################
#________________________________________________________________________________  


app.layout = html.Div([
    html.H1("Mon Job Market Explorer"),   
#________________________________________________________________________________  
#map + bar
    # First Row
    html.Div([
        # colonne 1.1
        html.Div([
            # Content for the first column in the first row
            html.H3("Localisation des offres"),
            # Map
            dcc.Graph(
                id='map',
                figure=px.scatter_mapbox(
                    df,
                    lat='lieuTravail_latitude',
                    lon='lieuTravail_longitude',
                    color='salaire_min',
                    size='salaire_min',
                    hover_name='intitule',
                    title='Je choisis la localisation',
                    labels={'salaire_min': 'Salaire'},
                    mapbox_style='carto-positron',
                    height=600
                )
            )
        ], className="six columns"),  # This sets the width to 6 columns out of 12
        # colonne 1.2
        html.Div([
            # Content for the second column in the first row
            html.H3("Top salaire"),
            # Bar Chart
            dcc.Graph(
                id='bar-chart',
                figure=px.bar(
                    df,
                    x='secteurActiviteLibelle',
                    y='salaire_min',
                    title='Je choisis le domaine',
                    labels={'secteurActiviteLibelle': 'Industrie', 'salaire_min': 'Salaire moyen'},
                    height=500
                )
            ),
        ], className="six columns"),  # This sets the width to 6 columns out of 12
    ], className="row"),  # This sets the layout to a row

#________________________________________________________________________________  
#nuage de points         
    # Second Row
    html.Div([
        html.H3("Expérience professionnelle"),
        # colonne 2.1
        html.Div([
            dcc.Graph(
                id='scatter-plot',
                figure=px.scatter(
                df,
                x='experienceLibelle',
                y='salaire_min',
                color='secteurActiviteLibelle',
                title='Combien je gagne selon mon expérience ?',
                labels={'experienceLibelle': 'Experience', 'salaire_min': 'Salary'},
                height=400
                )
            ),
    ], style = {'background' : 'beige'}),
], className="row"),

#________________________________________________________________________________  
#Dropdown + Table          
    # third Row
    html.Div([
        html.H3("Mes offres d'emplois"),
        # colonne 3.1
        html.Div([
            dcc.Dropdown(
            id='filter-options',
            options=[
                {'label': 'dureeTravailLibelleConverti', 'value': 'duree de travail'},
                {'label': 'lieuTravail_codepostal', 'value': 'lieu de travail - codepostal'},
                {'label': 'typeContrat', 'value': 'type de contrat'},
                {'label': 'natureContrat', 'value': 'nature de contrat'}
            ],
            multi=True,  # Allow multiple selections
            value='nature de contrat',  # Initial value, none selected
            style={'width': "40%"}
            ),
        ], style = {'background' : 'beige'}),
        # colonne 3.2
        html.Div([
            dash_table.DataTable(
            id='my_dashtable',
            columns=[
                {'name': columns_display_names.get(col, col), 'id': col} for col in columns_to_display
            ],         
            data=df[columns_to_display].to_dict('records'),
            page_size=2 #10
            ),
        ], className="row", style = {'background' : 'beige'}),
    ]),
])
# Callback to update DataTable based on checklist selection
@app.callback(
    Output('my-dashtable', 'data'),
    [Input('filter-options', 'value')]
)
# selected function
def update_table(selected_options):
    # Filter DataFrame based on selected options
    filtered_df = data.copy()
    if 'dureeTravailLibelleConverti' in selected_options:
        # Apply filtering logic for Option 1
        filtered_df = filtered_df[filtered_df['lieuTravail_codepostal'].notnull()]
    if 'typeContrat' in selected_options:
        # Apply filtering logic for Option 2
        filtered_df = filtered_df[filtered_df['typeContrat'].notnull()]
    if 'natureContrat' in selected_options:
        # Apply filtering logic for Option 3
        filtered_df = filtered_df[filtered_df['natureContrat'].notnull()]

    return filtered_df.to_dict('records')
#________________________________________________________________________________  



"""
df = px.data.gapminder() 
df_france = df[df['country'] == 'France']
fig = px.choropleth(df_france, locations="iso_alpha",
                    color="lifeExp", 
                    hover_name="country", 
                    color_continuous_scale=px.colors.sequential.Plasma)
fig.show()


#__________________
app.layout = html.Div([
    html.H4('Job Market'),
    html.P("Select a contract:"),
    dcc.RadioItems(
        id='candidate', 
        options=["CDI", "CDD"],
        value="CDI",
        inline=True
    ),
    dcc.Graph(id="graph"),
])


@app.callback(
    Output("graph", "figure"), 
    Input("candidate", "value"))
def display_choropleth(candidate):
    df = px.df
    geojson = px.df_geojson()
    fig = px.choropleth(
        df, geojson=geojson, color=candidate,
        locations="lieuTravail_commune", featureidkey="properties.lieuTravail_commune",
        projection="mercator", range_color=[0, 6500])
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    return fig

"""





#________________________________________________________________________________
################################# Run App #############################
#________________________________________________________________________________
if __name__ == '__main__':
    app.run_server(debug=True)