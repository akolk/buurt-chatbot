import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import requests
import plotly.express as px
import os
import uuid

# Generate a random UUID
generated_uuid = uuid.uuid4()

# Initialize the Dash app with a Bootstrap theme
url_base_pathname=os.environ.get("BASE_URL", "")

app = dash.Dash(__name__,url_base_pathname=url_base_pathname, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Sample data for graphs
df = px.data.iris()

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
                dcc.Input(id='chat-input', type='text', placeholder='Type a message...', style={'width': '100%', 'margin-bottom': '10px'}),
                dbc.Button('Send', id='send-button', color='primary', style={'width': '100%'})
            ], style={'flex': '0'})  # Question entry at the bottom
        ], width=4, style={'display': 'flex', 'flex-direction': 'column', 'height': '100%'})  # Adjust width to 4 out of 12 columns
    ], style={'height': '100vh'})  # Full viewport height
])

# Endpoint where chat input is sent
QUESTION_ENDPOINT = 'https://labs.kadaster.nl/predict?question='

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
        fig = px.scatter(df, x='sepal_width', y='sepal_length', color='species')
        new_card = dbc.Card(
            dcc.Graph(figure=fig),
            style={'position': 'absolute', 'top': f'{10 + len(canvas_content) * 80}px', 'left': f'{10}px', 'width': '300px'}
        )
        canvas_content.append(new_card)

    elif response['language'] == 'sparql':
        # Handle SPARQL query response (mock example)
        sparql_result = f"SPARQL Result: {response['sparql']}"
        new_card = dbc.Card(
            html.Div(sparql_result),
            style={'position': 'absolute', 'top': f'{10 + len(canvas_content) * 80}px', 'left': f'{10}px', 'width': '300px'}
        )
        canvas_content.append(new_card)

    elif response['language'] == 'url':
        # Handle URL response (mock example)
        new_card = dbc.Card(
            html.A('Open Link', href=response['url'], target='_blank', className='btn btn-primary'),
            style={'position': 'absolute', 'top': f'{10 + len(canvas_content) * 80}px', 'left': f'{10}px', 'width': '300px'}
        )
        canvas_content.append(new_card)
    elif response['language'] == 'prompt':
        # Handle URL response (mock example)
        new_card = dbc.Card(
            html.Div(response['prompt']),
            style={'position': 'absolute', 'top': f'{10 + len(canvas_content) * 80}px', 'left': f'{10}px', 'width': '300px'}
        )
        canvas_content.append(new_card)

    return chat_history, canvas_content, chat_output, canvas_content

def send_to_endpoint(user_input):
    conversation_id=f"&conversion_id={generated_uuid}"
    # Send the user input to the external question endpoint
    try:
        response = requests.get(QUESTION_ENDPOINT+user_input+conversation_id)
        return response.json()
    except Exception as e:
        return {'answer': 'Sorry, there was an error contacting the server.'}

if __name__ == '__main__':
    HOST = os.environ.get('HOST', '0.0.0.0')
    PORT = int(os.environ.get('PORT', 8050))

    app.run_server(debug=True, host=HOST, port=PORT)
