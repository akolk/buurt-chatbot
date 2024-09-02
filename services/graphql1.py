class ProcessGraphQL:
    def __init__(self, data):
        self.apollo = apollo
        self.dashboard = dashboard
        self.chart = chart
        self.request$ = Subject()
        self.features$ = Subject()
        self.graph$ = Subject()
        self.viewPort$ = Subject()
        self.showgraph$ = Subject()
        self.featurecount = Subject()
        self.answer$ = Subject()
        self.grid$ = Subject()
        self.errors = None
        self.schema = GraphQLSchema
        self.dashboard$ = Subject()

    async def request_query(self, message: BotMessage) -> CustomInformation:
        query_result = await self.apollo.query({
            "query": parse(message.query),
            "errorPolicy": "all",
            "fetchPolicy": "no-cache"
        }).toPromise()

        data = query_result.data
        self.errors = query_result.errors

        graph_type = ""
        graph_data = []
        charts = []
        grid = []
        dash = []
        custom = CustomInformation(info=None, features=None)

        answer_chatbot = [{'chatbotanswer': item} for item in find_all_by_key(data, 'chatbotanswer')]

        if self.errors:
            if self.errors[0]['message'] == "Adres niet gevonden":
                custom['adreserror'] = True
                return custom

        features = []
        keys = list(data.keys())

        for key in keys:
            graph_data = []

            if any(key.startswith(t) for t in environment.graphTypes):
                graph_type = key
                self.process_data(data[graph_type], features, graph_data)

                if graph_data:
                    titel = data[graph_type].get('_grafiektitel', graph_type.split('_')[1] if '_' in graph_type else "")
                    legends = self.combine_legends(data)
                    charts.append({"graphType": graph_type, "data": graph_data, "legend": legends, "titel": titel})
                else:
                    custom.info = "Geen data op dit niveau beschikbaar. Probeer een andere vraag."
                    answer_chatbot.append({'chatbotanswer': 'Geen data op dit niveau beschikbaar. Probeer een andere vraag.'})

            elif key.startswith("dashboard"):
                dash = data[key]
                legends = self.combine_legends(data)
                custom.dashBoard = self.dashboard.generate({"dashboard": data[key], "legend": legends})

            elif key.startswith("grid"):
                grid_data = data[key]
                grid_keys = list(grid_data.keys())
                self.grid$.on_next(grid_data[grid_keys[0]])

            else:
                self.process_data(data[key], features, graph_data)

        if charts:
            custom.graphData = self.chart.generate(charts)
        elif features:
            custom.features = features
            custom.info = ""

        lokalebekendmakingen = None
        if find_key(data, 'lokalebekendmakingen'):
            lokalebekendmakingen = find_all_by_key(data, 'lokalebekendmakingen')

        if lokalebekendmakingen:
            if not lokalebekendmakingen[0]:
                answer_chatbot.append({'chatbotanswer': 'Er zijn geen lokale bekendmakingen gevonden.'})
            else:
                answer_chatbot.append({'chatbotanswer': f'{len(lokalebekendmakingen)} lokale bekendmakingen gevonden.'})

        if not answer_chatbot and not charts and not dash and not features:
            custom.answer = ['Niks gevonden! Probeer een andere vraag of een ander adres.']
        else:
            custom.answer = [item['chatbotanswer'] for item in answer_chatbot]

        return custom

    def find_aantal_groep(self, data: Any) -> Any:
        if isinstance(data, list) and data:
            for item in data:
                ret = self.check_item_aantal_groep(item)
                if ret:
                    return item
        else:
            return self.check_item_aantal_groep(data)

    def check_item_aantal_groep(self, data: Any) -> Any:
        if not data:
            return None
        datakeys = list(data.keys())
        if any(key.startswith('aantal_') or key == 'aantal' for key in datakeys) and any(key.startswith('groep_') or key == 'groep' for key in datakeys):
            return data
        else:
            koppelobj = [k for k in datakeys if isinstance(data[k], dict) or (isinstance(data[k], list) and data[k] and isinstance(data[k][0], dict))]
            for koppel in koppelobj:
                ret = self.find_aantal_groep(data[koppel])
                if ret:
                    return ret
            return {}

    def process_data(self, data: Any, features: List[Any], graph_data: List[Any]):
        if isinstance(data, list) and data:
            for query_data in data:
                datakeys = list(query_data.keys())

                if any(key.startswith('aantal_') or key == 'aantal' for key in datakeys) and any(key.startswith('groep_') or key == 'groep' for key in datakeys):
                    graph_data.append(query_data)

                geometrie = [veld for veld in datakeys if environment.geometrie in veld]
                for geom in geometrie:
                    feature = self.transform_polygon(query_data[geom], query_data)
                    features.append(feature)

                koppelobj = [koppel for koppel in datakeys if isinstance(query_data[koppel], dict) or (isinstance(query_data[koppel], list) and query_data[koppel] and isinstance(query_data[koppel][0], dict))]
                for koppel in koppelobj:
                    self.process_data(query_data[koppel], features, graph_data)
        else:
            self.process_item(data, features, graph_data)

    def process_item(self, query_data: Any, features: List[Any], graph_data: List[Any]):
        if not query_data:
            return
        datakeys = list(query_data.keys())
        geometrie = [veld for veld in datakeys if environment.geometrie in veld]
        for geom in geometrie:
            if query_data[geom]:
                feature = self.transform_polygon(query_data[geom], query_data)
                features.append(feature)

        koppelobj = [koppel for koppel in datakeys if isinstance(query_data[koppel], dict) or (isinstance(query_data[koppel], list) and query_data[koppel] and isinstance(query_data[koppel][0], dict))]
        for koppel in koppelobj:
            self.process_data(query_data[koppel], features, graph_data)

        if any(key.startswith('aantal_') or key == 'aantal' for key in datakeys) and any(key.startswith('groep_') or key == 'groep' for key in datakeys):
            graph_data.append(query_data)

    def transform_polygon(self, geometric_data: str, query_data: Any) -> Any:
        wkt_format = WKT()  # Replace with your WKT parser
        feature = wkt_format.read_feature(geometric_data, {
            'dataProjection': environment.backend_epsg,
            'featureProjection': environment.frontend_epsg,
        })

        if 'lokaalID' in query_data:
            feature.set_id(query_data['lokaalID'])

        for key, value in query_data.items():
            if key.lower().endswith(('_uri', '_iri', '_url')):
                feature.set(key, value)

        for attr in environment.feature_attributes:
            if attr in query_data:
                feature.set(attr, query_data[attr])

        return feature

    def combine_legends(self, data: Any) -> List[str]:
        keys = find_all_by_key(data, 'legend')
        return keys
