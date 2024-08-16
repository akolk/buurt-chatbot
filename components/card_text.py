import dash_bootstrap_components as dbc

def makecard(cardtitle,title,body):
    return dbc.Card(
       [
        dbc.CardHeader(cardtitle),
        dbc.CardBody(
            [
                html.H5(title, className="card-title"),
                html.P(body, className="card-text"),
            ]
        ),
       ],
       className="shadow-lg p-3 mb-5 bg-white rounded"
    )
