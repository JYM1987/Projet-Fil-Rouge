import dash
from dash.dependencies import Input, Output
from dash import dcc, html
import pandas as pd
import plotly.express as px
import json

with open('DfPE.json', 'r') as fichier_json:
    data = json.load(fichier_json)
df = pd.DataFrame(data)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
  html.H1('Job Market', style={'textAlign': 'center', 'color': 'mediumturquoise'}),
  html.Div(dcc.Dropdown(id = 'Dropdown',
                        options= [{'label': 'dureeTravailLibelleConverti', 'value': 'dureeTravailLibelleConverti'},
                                  {'label': 'lieuTravail_codepostal', 'value': 'lieuTravail_codepostal'},
{'label': 'typeContrat', 'value': 'typeContrat'},
{'label': 'natureContrat', 'value': 'natureContrat'}],
                        value= 'natureContrat'
  )),
  html.Div(dcc.Graph(id='graph_1')),

  html.Div(dcc.Slider(id = 'slider_1',
                      min = df['salaire_max'].min(),
                      max = df['salaire_max'].max(),
                      marks={nbr: nbr for nbr in df['salaire_max'].unique()},step = None))

], style = {'background' : 'beige'})

@app.callback(Output(component_id='graph_1', component_property='figure'),
            [Input(component_id='Dropdown', component_property='value')])
def update_graph(indicator):
    # Création de la figure plotly
    fig = px.scatter(df, x="intitule",
                        y=indicator,
                        color="qualificationCode",
                        hover_name="description")
    return fig

if __name__ == '__main__':
  app.run_server(debug=True,host = '0.0.0.0')