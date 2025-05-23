from dash import html
import dash_bootstrap_components as dbc
from app import app
from components.card_ag import makecard_ag
from components.card_text import makecard
from services.graphql import graphql_endpoint, graphql_to_dataframe
from services.sparql import sparql_endpoint, sparql_to_dataframe
import services.config 

def render_textbox(obj, box:str = "AI"):
    style = {
        "max-width": "100%",
        "width": "max-content",
        "padding": "5px 10px",
        "border-radius": 25,
        "margin-bottom": 20,
        'border': '0px solid'
    }

    if box == "human":
        style["margin-left"] = "auto"
        style["margin-right"] = 0

        thumbnail_human = html.Img(
            src=app.get_asset_url("human.png"),
            style={
                "border-radius": 50,
                "height": 36,
                "margin-left": 5,
                "float": "right",
            },
        )

        textbox_human = makecard("Vraag", "Vraag", obj['question'], style, "sticky-note-card")
                       #color="primary", 
                       #style=style,
                       #id={"type": "dynamic-button", "index": obj['buttonidx']},
                       #className="",
                       #style=style
        #textbox_human = dbc.Card(obj['question'], style=style, body=True, color="primary", inverse=True
        #,                 className="shadow-lg p-3 mb-5 bg-black rounded"
        #textbox_human = dbc.Card(obj['question'], style=style, body=True, inverse=True, className="sticky-note-card")
        return html.Div([thumbnail_human, textbox_human])

    elif box == "AI":
        style["margin-left"] = 0
        style["margin-right"] = "auto"
        
        thumbnail = html.Img(
            src=app.get_asset_url("chatbot.png"),
            style={
                "border-radius": 50,
                "height": 36,
                "margin-right": 5,
                "float": "left"
            },
        )
        #textbox_ai = dbc.Card(obj['chatbotresponse'], style=style, body=True, color="primary", inverse=True
        #,                 className="shadow-lg p-3 mb-5 bg-white rounded"
        #)           
        b = dbc.Button(
                       makecard_ag(obj['buttonidx'], obj['chatbotresponse'], obj, style, "sticky-note-card-ai"), 
                       #color="primary", 
                       #style=style,
                       id={"type": "dynamic-button", "index": obj['buttonidx']},
                       className="btn btn-outline-primary",
                       style=style
                      )

        return html.Div([thumbnail, b])
    else:
        raise ValueError("Incorrect option for `box`.")
