from dash.dependencies import Input, Output, State
from app import app

from components.textbox import render_textbox
from components.card_ag import makecard_ag
from components.card_text import makecard
from services.graphql import graphql_endpoint
from services.sparql import sparql_endpoint, sparql_results_to_dataframe
from services.endpoint import send_to_endpoint
from services.text import convert_to_superscript
import services.config

import os
import uuid
import requests
import re
import pandas

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
    response = send_to_endpoint(user_input)
    # Update the canvas content based on the response
    if response['language'] == 'graphql':
        # Generate graph based on GraphQL query (mock example)
        ret = graphql_endpoint(response['query'])
        gradf = graphql_to_dataframe(ret)
        new_card = makecard_ag("Antwoord", "Graphql", gradf)

    elif response['language'] == 'sparql':
        # Handle SPARQL query response (mock example)
        sparql_result = f"SPARQL Result: {response['query']}"
        ret = sparql_endpoint(response['query'])
        spardf = sparql_results_to_dataframe(ret)
        new_card = makecard_ag("SPARQL", "antwoord", spardf)

    elif response['language'] == 'url':
        # Handle URL response (mock example)
        new_card = makecard("URL", "link", response['query'])
        
    elif response['language'] == 'prompt':
        # Handle URL response (mock example)
        converted_text = convert_to_superscript(response['query'], response['sources'] )
        new_card = makecard("Antwoord", "Graphql", converted_text )

    model_output = str(ret)
    chat_history += f"{model_output}<split>"
    return chat_history, None
