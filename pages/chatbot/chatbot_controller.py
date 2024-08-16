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
import json

@app.callback(
    Output(component_id="display-conversation", component_property="children"), 
    Input(component_id="store-conversation", component_property="data")
)
def update_display(chat_history):
    # the chat_history is a string representation of list of json objects. So we need to convert it back to json
    if isinstance(chat_history, str):
        json_data = json.loads(chat_history)
    else:
        json_data = None
        
    return [
        render_textbox(item, box="human") if 'question' in item else render_textbox(item, box="AI")
        for item in json_data
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

    if isinstance(chat_history, str):
        json_data = json.loads(chat_history)

    json_data.append({ 'question': user_input })
    response = send_to_endpoint(user_input)
    json_data.append(response)
    
    chat_history = json.dumps(json_data)
    return chat_history, None
