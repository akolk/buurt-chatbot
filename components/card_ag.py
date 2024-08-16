import 

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
