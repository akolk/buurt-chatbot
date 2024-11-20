import dash_bootstrap_components as dbc
import dash_ag_grid as dag
from dash import dcc, html 
import services.config

def makecard_ag(id, text, obj, style):
    style['textAlign'] = "left"
    return dbc.Card(

                [
                html.Div(
                    f"{text}",
                    id={"type": "card-content", "index": id},
                    style=style,
                )
                ],
                id={"type": "dynamic-card", "index": id},
                style=style
                #style={"width": "max-content", "height": "100%", "transition": "all 0.5s"}
                #dag.AgGrid(
                #       services.config.buttonidx     rowData=df.to_dict(orient="records"),
                #            columnDefs=[{"field": i} for i in df.columns],
                #            #style=style
                #            style={"height": "80%", "width": "100%"}
                #        ),
                #        style=style, body=True, color="light", inverse=False,
                #        className="shadow-lg p-3 mb-5 bg-white rounded"
        ,className="sticky-note-card"
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
