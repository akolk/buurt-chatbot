from dash.dependencies import Input, Output, State
from app import app

from components.textbox import render_textbox
import os
import uuid
import requests
import re
import pandas

#from pages.chatbot.chatbot_model import conversation

generated_uuid = uuid.uuid4()

# Initialize the Dash app with a Bootstrap theme
url_base_pathname=os.environ.get("BASE_URL", "/")
SPARQL_ENDPOINT = os.environ.get("SPARQL_ENDPOINT", "https://api.labs.kadaster.nl/datasets/dst/kkg/services/default/sparql")
GRAPHQL_ENDPOINT = os.environ.get("GRAPHQL_ENDPOINT", "https://labs.kadaster.nl/graphql")
# Endpoint where chat input is sent
QUESTION_ENDPOINT = os.environ.get("QUESTION_ENDPOINT", 'https://labs.kadaster.nl/predict?question=')

@app.callback(
    Output(component_id="display-conversation", component_property="children"), 
    Input(component_id="store-conversation", component_property="data")
)
def update_display(chat_history):
    return [
        render_textbox(x, box="human") if i % 2 == 0 else render_textbox(x, box="AI")
        for i, x in enumerate(chat_history.split("<split>")[:-1])
    ]

@app.callback(
    Output(component_id="user-input", component_property="value"),
    Input(component_id="submit", component_property="n_clicks"), 
    Input(component_id="user-input", component_property="n_submit"),
)
def clear_input(n_clicks, n_submit):
    return ""

@app.callback(
    Output(component_id="store-conversation", component_property="data"), 
    Output(component_id="loading-component", component_property="children"),
    Input(component_id="submit", component_property="n_clicks"), 
    Input(component_id="user-input", component_property="n_submit"),
    State(component_id="user-input", component_property="value"), 
    State(component_id="store-conversation", component_property="data"),
)
def run_chatbot(n_clicks, n_submit, user_input, chat_history):
    if n_clicks == 0 and n_submit is None:
        return "", None

    if user_input is None or user_input == "":
        return chat_history, None
    
    chat_history += f"Human: {user_input}<split>ChatBot: "
    #result_ai = conversation.predict(input=user_input)
    #model_output = result_ai.strip()
    response = send_to_endpoint(user_input)
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
        converted_text = convert_to_superscript(response['query'], response['sources'] )
        new_card = makecard("Antwoord", "Graphql", converted_text  )
        canvas_content.append(new_card)

    model_output = str(ret)
    chat_history += f"{model_output}<split>"
    return chat_history, None

def send_to_endpoint(user_input):
    generated_uuid = "bf20e1fa-d331-48da-ba32-64d29a948ded"
    QUESTION_ENDPOINT = os.environ.get("QUESTION_ENDPOINT", 'https://labs.kadaster.nl/predict?question=')
    conversation_id=f"&conversation_id={generated_uuid}"
    # Send the user input to the external question endpoint
    url = f"{QUESTION_ENDPOINT}{user_input}{conversation_id}"
    print(url)
    try:
        response = requests.get(QUESTION_ENDPOINT+user_input+conversation_id)
        return response.json()
    except Exception as e:
        print(e)
        return {'answer': str(e)}

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

def convert_to_superscript(text, sources):
    # Superscript digits in HTML
    superscript_map = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")

    # Regex pattern to find lists of numbers within square brackets
    pattern = re.compile(r'\[(\d+(?:,\s*\d+)*)\]')

    def replace_with_superscript(match):
        # Extract the matched number list
        numbers = match.group(1).translate(superscript_map)
        
        # Get the corresponding source URL for the current match
        if replace_with_superscript.counter - 1 < len(sources):
            url = sources[replace_with_superscript.counter - 1]
            replace_with_superscript.counter += 1
        else:
            url = '#'

        # Return the clickable superscript
        return f"<a href='{url}'><sup>{numbers}</sup></a>"

    # Initialize a counter to track the number of matches
    replace_with_superscript.counter = 1

    # Substitute all occurrences in the text
    return pattern.sub(replace_with_superscript, text)
