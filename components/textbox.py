from dash import html
import dash_bootstrap_components as dbc
from app import app


def render_textbox(obj, box:str = "AI"):
    style = {
        "max-width": "60%",
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
        textbox_human = dbc.Card(obj['question'], style=style, body=True, color="primary", inverse=True)
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
                "float": "left",
            },
        )
        if obj['language'] == 'prompt':
            textbox = dbc.Card(obj['query'], style=style, body=True, color="light", inverse=False)
        else:
            textbox = html.P("nog niet geimplementeerd")
            
        return html.Div([thumbnail, textbox])

    else:
        raise ValueError("Incorrect option for `box`.")
