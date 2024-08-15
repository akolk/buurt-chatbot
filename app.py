import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import dash_ag_grid as dag
import requests
import plotly.express as px
import os
import uuid
import pandas as pd
idx=0

# Generate a random UUID
generated_uuid = uuid.uuid4()

# Initialize the Dash app with a Bootstrap theme
url_base_pathname=os.environ.get("BASE_URL", "/")
SPARQL_ENDPOINT = os.environ.get("SPARQL_ENDPOINT", "https://api.labs.kadaster.nl/datasets/dst/kkg/services/default/sparql")
GRAPHQL_ENDPOINT = os.environ.get("GRAPHQL_ENDPOINT", "https://labs.kadaster.nl/graphql")
# Endpoint where chat input is sent
QUESTION_ENDPOINT = os.environ.get("QUESTION_ENDPOINT", 'https://labs.kadaster.nl/predict?question=')

app = dash.Dash(__name__,url_base_pathname=url_base_pathname, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Layout of the app
app.layout = dbc.Container([
    dcc.Store(id='store-chat-history', data=[]),
    dcc.Store(id='store-canvas-content', data=[]),
    dbc.Row([
        # Canvas area (left side, full width)
        dbc.Col([
            html.Div(id='canvas-output', style={'position': 'relative', 'height': '100%', 'border': '1px solid #ccc'})
        ], width=8),  # Adjust width to 8 out of 12 columns
        # Chatbot area (right side)
        dbc.Col([
            dbc.Row([
                html.Div(id='chat-output', style={'border': '1px solid #ccc', 'padding': '10px', 'height': '300px', 'overflowY': 'scroll', 'margin-bottom': '10px'})
            ], style={'flex': '1'}),  # Chat history on top
            dbc.Row([
                dcc.Input(id='chat-input', type='text', placeholder='Stel een vraag of geef een opdracht ....', style={'width': '100%', 'margin-bottom': '10px'}),
                dbc.Button('Send', id='send-button', color='primary', style={'width': '100%'})
            ], style={'flex': '0'})  # Question entry at the bottom
        ], width=4, style={'display': 'flex', 'flex-direction': 'column', 'height': '100%'})  # Adjust width to 4 out of 12 columns
    ], style={'height': '100vh'})  # Full viewport height
])

@app.callback(
    Output('store-chat-history', 'data'),
    Output('store-canvas-content', 'data'),
    Output('chat-output', 'children'),
    Output('canvas-output', 'children'),
    Input('send-button', 'n_clicks'),
    State('chat-input', 'value'),
    State('store-chat-history', 'data'),
    State('store-canvas-content', 'data')
)
def update_chat(n_clicks, user_input, chat_history, canvas_content):

    if n_clicks is None or not user_input:
        return chat_history, canvas_content, [], []

    # Send user input to the external question endpoint
    response = send_to_endpoint(user_input)
    
    # Update chat history with user input and bot response
    new_message = {'user': user_input, 'bot': response.get('query', 'Er ging iets fout en ik heb geen antwoord gekregen. Probeer opnieuw.')}
    chat_history.append(new_message)

    # Update chat output in the UI
    chat_output = [html.Div([html.P(f'User: {msg["user"]}'), html.P(f'Bot: {msg["bot"]}')]) for msg in chat_history]

    # Update the canvas content based on the response
    if response['language'] == 'graphql':
        # Generate graph based on GraphQL query (mock example)
        ret = graphql_endpoint(response['query'])
        gradf = graphql_to_dataframe(ret)
        new_card = makecard_ag("Antwoord", "Graphql", gradf)
        canvas_content.append(new_card)

    elif response['language'] == 'sparql':
        # Handle SPARQL query response (mock example)
        sparql_result = f"SPARQL Result: {response['query']}"
        ret = sparql_endpoint(response['query'])
        spardf = sparql_results_to_dataframe(ret)
        new_card = makecard_ag("SPARQL", "antwoord", spardf)
        canvas_content.append(new_card)

    elif response['language'] == 'url':
        # Handle URL response (mock example)
        new_card = makecard("URL", "link", response['query'])
        canvas_content.append(new_card)
        
    elif response['language'] == 'prompt':
        # Handle URL response (mock example)
        new_card = makecard("Antwoord", "Graphql", response['query']  )
        canvas_content.append(new_card)

    return chat_history, canvas_content, chat_output, canvas_content

def send_to_endpoint(user_input):
    conversation_id=f"&conversation_id={generated_uuid}"
    # Send the user input to the external question endpoint
    try:
        response = requests.get(QUESTION_ENDPOINT+user_input+conversation_id)
        return response.json()
    except Exception as e:
        return {'answer': 'Sorry, there was an error contacting the server.'}

def makecard(cardtitle,title,body):
    return dbc.Card(
       [
        dbc.CardHeader(cardtitle),
        dbc.CardBody(
            [
                html.H5(title, className="card-title"),
                html.P(body, className="card-text"),
            ]
        ),
       ],
       className="shadow-lg p-3 mb-5 bg-white rounded"
    )
    
def makecard_ag(cardtitle, title, df):
    
    return dbc.Card(
       [
        dbc.CardHeader(cardtitle),
        dbc.CardBody(
            [
                html.H5(title, className="card-title"),
                dag.AgGrid(
                    rowData=df.to_dict("records"),
                    columnDefs=[{"field": i} for i in df.columns],
                    style={"height": "100%", "width": "100%"}
                )
            ]
        ),
       ],
       className="shadow-lg p-3 mb-5 bg-white rounded"
    )


def graphql_endpoint(query):
    try:
        response = requests.post(GRAPHQL_ENDPOINT, json={"query": query})
        return response.json()
    except Exception as e:
        return {'query': 'Sorry, there was an error contacting the graphql server.'}

def sparql_endpoint(query):
    headers ={
                'Content-Type': 'application/sparql-query',
                'accept': 'application/sparql-results+json'
            }
    
    try:
        response = requests.post(SPARQL_ENDPOINT, data=query, headers=headers)
        return response.json()
    except Exception as e:
        return {'query': 'Sorry, there was an error contacting the sparql server.'}

def sparql_results_to_dataframe(json_data):
    if json_data is None:
        return pd.DataFrame()

    # Extract the variables from the head of the JSON response
    variables = json_data['head']['vars']

    # Extract the results from the JSON response
    results = json_data['results']['bindings']

    # Prepare a list to hold the rows of the DataFrame
    data = []

    # Iterate through the results and extract each variable's value
    for result in results:
        row = {}
        for var in variables:
            row[var] = result[var]['value'] if var in result else None
        data.append(row)

    # Convert the list of rows into a DataFrame
    df = pd.DataFrame(data, columns=variables)
    return df

def find_key(data, target_key):
    if isinstance(data, dict):
        for key, value in data.items():
            if key == target_key:
                return value
            elif isinstance(value, (dict, list)):
                result = find_key(value, target_key)
                if result is not None:
                    return result
    elif isinstance(data, list):
        for item in data:
            result = find_key(item, target_key)
            if result is not None:
                return result
    return None

def flatten_json(json_data, parent_key='', sep='_'):
    """
    A helper function to flatten a nested JSON object into a single level.
    """
    items = []
    for k, v in json_data.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_json(v, new_key, sep=sep).items())
        elif isinstance(v, list):
            for i, item in enumerate(v):
                items.extend(flatten_json(item, f"{new_key}{sep}{i}", sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

def graphql_to_dataframe(json_data):
    """
    Convert the JSON data to a DataFrame. 
    This function flattens the JSON and converts it to a DataFrame.
    """
    if 'data' not in json_data:
        print("No 'data' key in the JSON response.")
        return pd.DataFrame()

    data = json_data['data']

    # Assuming data is a dictionary of lists or nested dictionaries
    if isinstance(data, dict):
        flat_data = []
        for key, value in data.items():
            if isinstance(value, list):
                for item in value:
                    flat_data.append(flatten_json(item))
            else:
                flat_data.append(flatten_json(value))

        # Convert the list of flat dictionaries to a DataFrame
        df = pd.DataFrame(flat_data)
    else:
        df = pd.DataFrame([flatten_json(data)])

    return df
        
if __name__ == '__main__':
    HOST = os.environ.get('HOST', '0.0.0.0')
    PORT = int(os.environ.get('PORT', 8050))

    app.run_server(debug=True, host=HOST, port=PORT)
