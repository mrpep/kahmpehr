import argparse
import pandas as pd
import joblib
from widgets import create_table, create_parcoords_fig, create_filter_sidebar
from pathlib import Path

import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
from dash_table.Format import Format

def main(args):
    df_data = pd.read_csv(Path(args['logdir'],'results.csv'))
    columns_metadata = joblib.load(Path(args['logdir'],'columns_metadata'))
    
    external_stylesheets = ['https://www.w3schools.com/w3css/4/w3.css','https://codepen.io/chriddyp/pen/bWLwgP.css']
    app = dash.Dash(__name__,external_stylesheets = external_stylesheets)
    table = create_table(id='interactive_datatable',data=df_data,columns=df_data.columns)
    parcoords_plot = create_parcoords_fig(data=df_data,columns=df_data.columns)

    refresh_interval = dcc.Interval(id='interval1', interval=30 * 1000, n_intervals=0)

    visualization_div = html.Div([refresh_interval,table,html.Div(dcc.Graph(id='parcoords-fig',figure=parcoords_plot),style={'marginTop': '60px'})],
                                style={'overflow': 'scroll', 'marginLeft':'25%'})

    filter_sidebar, all_checklists = create_filter_sidebar(columns_metadata=columns_metadata)
    main_layout = html.Div([filter_sidebar,visualization_div])

    app.layout = main_layout

    @app.callback(
    Output(component_id='interactive_datatable', component_property='data'),
    [Input(component_id='interval1',component_property='n_intervals')] + [Input(component_id=c.id, component_property='value') for c in all_checklists]
)

    def update_table_cols(interval,*cols):
        ctx = dash.callback_context
        if ctx.triggered[0]['prop_id'] == 'interval1.n_intervals':
            local_data = pd.read_csv(Path(args['logdir'],'results.csv'))
        else:
            local_data = df_data

        cols_ = []
        for col in cols:
            cols_ = cols_ + col
        data_subset = local_data[cols_]
        
        return data_subset.to_dict('records')

    @app.callback(
        Output(component_id='interactive_datatable', component_property='columns'),
        [Input(component_id='interval1',component_property='n_intervals')] + [Input(component_id=c.id, component_property='value') for c in all_checklists]
    )
    def update_table_cols(interval,*cols):
        ctx = dash.callback_context
        if ctx.triggered[0]['prop_id'] == 'interval1.n_intervals':
            local_data = pd.read_csv(Path(args['logdir'],'results.csv'))
        else:
            local_data = df_data

        cols_ = []
        for col in cols:
            cols_ = cols_ + col
        out_cols = [{"name": i, "id": i, 'format': Format(precision=3), 'type':'numeric'} for i in cols_]
        
        return out_cols

    @app.callback(
        Output('parcoords-fig', 'figure'),
        [Input('interactive_datatable', 'columns')])

    def update_figure(cols):
        
        col_names = [col['name']for col in cols]
        filtered_df = df_data[col_names]
        
        return create_parcoords_fig(data=filtered_df,columns=col_names)

    return app

if __name__ == '__main__':
    argparser = argparse.ArgumentParser(description='Compare ML experiments')

    argparser.add_argument('--logdir', type=str,
                           help='Path to experiments logs')
    argparser.add_argument('--port', type=int,
                           help='Port number')

    args = vars(argparser.parse_args())

    app = main(args)
    app.run_server(port = args['port'], debug=True)