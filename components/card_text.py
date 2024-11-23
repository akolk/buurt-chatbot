import dash_bootstrap_components as dbc
from dash import dcc, html 

def makecard(cardtitle,title,body, style, className):
    return dbc.Card(
       [
        #dbc.CardHeader(cardtitle),
        dbc.CardBody(
            [
                html.H5(cardtitle, className="card-title"),
                html.P(body, className="card-text"),
            ]
        ),
       ],
       className=className,
        
       # ,
       style=style
    )
