import streamlit as st

# Define a class to handle the dashboard data
class DashboardService:
    def __init__(self):
        self.overviews = []
        self.bottom = []
        self.charts = []

    def generate(self, data):
        """
        Process and generate the dashboard data.
        """
        self.overviews = []
        self.bottom = []
        self.charts = []

        dashboard = data.get("dashboard", {})
        legend = data.get("legend", {})

        for item in dashboard.keys():
            if item.startswith("overview"):
                adjustitem = self.extract_adjustitem(dashboard[item])
                self.overviews.append({
                    "titel": self.add_spaces(item.split('_')[1]),
                    "label": adjustitem.get("groep"),
                    "aantal": adjustitem.get("aantal"),
                    "tooltip": self.find_tooltip(legend, adjustitem.get("groep"))
                })

            elif item.startswith("bottom"):
                adjustitem = self.extract_adjustitem(dashboard[item])
                self.bottom.append({
                    "titel": self.add_spaces(item.split('_')[1]),
                    "label": adjustitem.get("groep"),
                    "aantal": adjustitem.get("aantal"),
                    "tooltip": self.find_tooltip(legend, adjustitem.get("groep"))
                })

            elif any(item.startswith(graph_type) for graph_type in ["graphType1", "graphType2"]):  # Define your graph types
                self.charts.append({
                    "graphType": item,
                    "data": dashboard[item],
                    "legend": legend,
                    "titel": ""
                })

        return {
            "overviews": self.overviews,
            "bottom": self.bottom,
            "charts": self.charts,
            "titel": dashboard.get("_dashboardtitel", "Dashboard")
        }

    def extract_adjustitem(self, dashboard_item):
        """
        Extract the relevant item from the dashboard data based on structure.
        """
        if isinstance(dashboard_item, list) and 'unpivot' in dashboard_item[0]:
            return dashboard_item[0].get('unpivot', [{}])[0]
        return dashboard_item

    def find_tooltip(self, legend, label):
        """
        Find and return tooltip based on legend and label.
        """
        if not legend:
            return label
        found = next((item for item in legend if item.get("label") == label), None)
        return found.get("tooltip") if found else label

    def add_spaces(self, val):
        """
        Add spaces before uppercase letters in a string.
        """
        import re
        return re.sub(r'([A-Z])', r' \1', val).strip()

    def add_percentage_tooltip(self, range_values):
        """
        Add percentage tooltips to range values based on their total.
        """
        total = sum(r['value'] for r in range_values)
        for r in range_values:
            percentage = (r['value'] / total) * 100
            r['tooltipText'] += f": {percentage:.1f}%"
        return range_values

# Streamlit UI
#st.title("Dashboard Service in Streamlit")

# Input simulation (In a real app, this could be replaced with data upload or API call)
#data = {
#    "dashboard": {
#        "overview_sales": {"groep": "Sales", "aantal": 150},
#        "bottom_orders": {"groep": "Orders", "aantal": 100},
#        "graphType1_chart": {"value": 20},
#    },
#    "legend": [
#        {"label": "Sales", "tooltip": "Total sales overview"},
#        {"label": "Orders", "tooltip": "Total orders overview"},
#    ]
#}

#Initialize and generate dashboard
#dashboard_service = DashboardService()
#dashboard_result = dashboard_service.generate(data)

# Display results in Streamlit
#st.subheader("Overviews")
#for overview in dashboard_result["overviews"]:
#    st.write(f"{overview['titel']}: {overview['label']} - {overview['aantal']}")
#    st.write(f"Tooltip: {overview['tooltip']}")

#st.subheader("Bottom")
#for bottom_item in dashboard_result["bottom"]:
#    st.write(f"{bottom_item['titel']}: {bottom_item['label']} - {bottom_item['aantal']}")
#    st.write(f"Tooltip: {bottom_item['tooltip']}")

#st.subheader("Charts")
#for chart in dashboard_result["charts"]:
#    st.write(f"Chart Type: {chart['graphType']}")
#    st.write(f"Data: {chart['data']}")
#    st.write(f"Legend: {chart['legend']}")

#st.subheader("Dashboard Title")
#st.write(dashboard_result["titel"])
