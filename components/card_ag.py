import dash_bootstrap_components as dbc
import dash_ag_grid as dag
from dash import dcc, html 

def makecard_ag(cardtitle, title, df, style):
    return dbc.Card(
        dag.AgGrid(
                    rowData=df.to_dict("records"),
                    columnDefs=[{"field": i} for i in df.columns],
                    style={"height": "100%", "width": "100%"}
                ),
                style=style, body=True, color="light", inverse=False,
                className="shadow-lg p-3 mb-5 bg-white rounded"
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
