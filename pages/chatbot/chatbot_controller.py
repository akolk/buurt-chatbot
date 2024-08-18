import dash
from dash.dependencies import Input, Output, State, ALL
from app import app

from components.textbox import render_textbox
from components.card_ag import makecard_ag
from components.card_text import makecard
from services.graphql import graphql_endpoint, graphql_to_dataframe
from services.sparql import sparql_endpoint, sparql_to_dataframe
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

# Callback to handle card expansion and content update
@app.callback(
    Output({"type": "dynamic-card", "index": ALL}, "style"),
    Output({"type": "card-content", "index": ALL}, "children"),
    Input({"type": "dynamic-button", "index": ALL}, "n_clicks"),
    State({"type": "dynamic-card", "index": ALL}, "style")
    #,
    #State("graphql-store", "data")  # Access session data from the store
)
def resize_card_and_update_content(n_clicks, styles):
    ctx = dash.callback_context

    #if not ctx.triggered:
    #    return styles, [f"Card {i+1} - Click to view data" for i in range(services.config.buttonidx)]
    
    clicked_button = n_clicks.index(max(n_clicks)) + 1
    
    new_styles = []
    new_contents = []

    session_data = {
        0: pd.DataFrame({"x": range(10), "y": [i ** 2 for i in range(10)]}),
        1: pd.DataFrame({"x": range(10), "y": [i ** 1.5 for i in range(10)]}),
        2: pd.DataFrame({"x": range(10), "y": [i ** 1.5 for i in range(10)]}),
        3: pd.DataFrame({"x": range(10), "y": [i ** 1.5 for i in range(10)]}),
        # Add more datasets as needed
    }

    for i, (n, style) in enumerate(zip(n_clicks, styles)):
        if i == clicked_button and n and n % 2 != 0:
            # Resize and show the graph or table based on session data
            new_styles.append({"width": "500px", "height": "500px", "transition": "all 0.5s"})
            data = session_data[i]
            df = pd.DataFrame(data)

            # Example: Show a graph for even index cards and a table for odd index cards
            if triggered_index % 2 == 0:
                fig = px.line(df, x="x", y="y", title=f"Graph for Card {triggered_index + 1}")
                new_contents.append(dcc.Graph(figure=fig, style={"height": "100%"}))
            else:
                new_contents.append(
                    dash_table.DataTable(
                        columns=[{"name": i, "id": i} for i in df.columns],
                        data=df.to_dict('records'),
                        style_table={"height": "100%", "overflowY": "auto"},
                        style_cell={"textAlign": "center"},
                    )
                )
        #else:
        #    # Reset to original size and content
        #    new_styles.append({"width": "100px", "height": "100px", "transition": "all 0.5s"})
        #    new_contents.append(f"Card {i+1} - Click to view data")

    return new_styles, new_contents
