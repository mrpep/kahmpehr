import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash_table.Format import Format

import plotly.graph_objects as go
import numbers

def create_table(id=None, data=None, columns=None):
    table = dash_table.DataTable(
            id=id,
            columns=[
                {"name": i, "id": i, 'format': Format(precision=3), 'type':'numeric'} for i in columns
            ],
            data=data.to_dict('records'),
            editable=False,
            filter_action="native",
            sort_action="native",
            sort_mode="single",
            column_selectable="single",
            row_selectable="multi",
            row_deletable=False,
            selected_columns=[],
            selected_rows=[],
            page_action='native',
            page_current= 0,
            page_size= 8
        )

    return table

def create_parcoords_fig(data=None, columns=None):
    parcoords = go.Figure(data=
    go.Parcoords(
        line_color='red',
        dimensions = list([
            dict(range = [data[col].min(),data[col].max()],
                 label = col, values = data[col]) for col in columns if isinstance(data[col].iloc[0],numbers.Number)])
    )
)
    return parcoords

def create_filter_sidebar(columns_metadata=None):
    filter_divs = [html.Label('Filter Columns',id='title_filterbox',style={'fontWeight': 'bold','fontSize': 20})]
    all_checklists = []
    for category,cols in columns_metadata.items():
        detail_children = []
        detail_children.append(html.Summary(category,style={'fontWeight': 'bold'}))
        checklist = dcc.Checklist(id='available_{}'.format(category),
        options=[{'label': i, 'value': i } for i in cols],
        value=cols[:3])

        detail_children.append(checklist)
        all_checklists.append(checklist)
        filter_divs.append(html.Details(detail_children))

    filter_sidebar = html.Div(filter_divs,className='w3-sidebar w3-bar-block',style={'width':'25%'})

    return filter_sidebar, all_checklists