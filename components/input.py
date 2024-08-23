import dash_bootstrap_components as dbc
from dash import dcc, html

def render_chat_input():
    chat_input = dbc.InputGroup(
        children=[
            dbc.Input(id="user-input", placeholder="Stel een vraag ....", type="text"),
            dcc.Upload(
                id='upload-data',
                children=html.Div([
                  'Sleep en plaats of ',
                   html.A('selecteer bestand(en)')
                ]),
                multiple=True  # Allow multiple files to be uploaded
            ),
            dbc.Button(id="submit", children=">", color="success"),
            
        ],
    )
    return chat_input
