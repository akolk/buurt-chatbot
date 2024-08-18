import dash_bootstrap_components as dbc
import dash_ag_grid as dag
from dash import dcc, html 
import services.config

def makecard_ag(cardtitle, title, df, style):
    return dbc.Card(
                html.Div(
                                    f"Card {i+1} - Click to view data",
                                    id={"type": "card-content", "index": services.config.buttonidx},
                                    style={"textAlign": "center"},
                ),
                id={"type": "dynamic-card", "index": i},
                style={"width": "80px", "height": "100px", "transition": "all 0.5s"}
                #dag.AgGrid(
                #            rowData=df.to_dict(orient="records"),
                #            columnDefs=[{"field": i} for i in df.columns],
                #            #style=style
                #            style={"height": "80%", "width": "100%"}
                #        ),
                #        style=style, body=True, color="light", inverse=False,
                #        className="shadow-lg p-3 mb-5 bg-white rounded"
    )

    #return dbc.Card(
    #   [
    #    dbc.CardHeader(cardtitle),
    #    dbc.CardBody(
    #        [
    #            html.H5(title, className="card-title"),
    #            dag.AgGrid(
    #                rowData=df.to_dict("records"),
    #                columnDefs=[{"field": i} for i in df.columns],
    #                style={"height": "100%", "width": "100%"}
    #            )
    #        ]
    #    ),
    #   ],
    #   className="shadow-lg p-3 mb-5 bg-white rounded",
    #   style=style
    #)
