import argparse
import pandas as pd
import joblib
from kahmpehr.widgets import create_table, create_parcoords_fig, create_filter_sidebar, create_summarizer
from pathlib import Path
import numpy as np

import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
from dash_table.Format import Format

def main():

    argparser = argparse.ArgumentParser(description='Compare ML experiments')
    argparser.add_argument('--logdir', type=str,
                           help='Path to experiments logs')
    argparser.add_argument('--port', type=int,
                           help='Port number', default=6969)
    args = vars(argparser.parse_args())

    df_data = pd.read_csv(Path(args['logdir'],'results.csv'))
    columns_metadata = joblib.load(Path(args['logdir'],'columns_metadata'))
    
    external_stylesheets = ['https://www.w3schools.com/w3css/4/w3.css','https://codepen.io/chriddyp/pen/bWLwgP.css']
    
    app = dash.Dash(__name__,external_stylesheets = external_stylesheets)
    table = create_table(id='interactive_datatable',data=df_data,columns=df_data.columns)
    parcoords_plot = create_parcoords_fig(data=df_data,columns=df_data.columns)

    refresh_interval = dcc.Interval(id='interval1', interval=30 * 1000, n_intervals=0)

    available_operations = {'mean':np.mean,'std':np.std}

    summarizer = create_summarizer(id='summarizer',groups=df_data.columns,operations=available_operations)
    tools_bar = html.Div(summarizer)

    visualization_div = html.Div([refresh_interval,tools_bar,table,html.Div(dcc.Graph(id='parcoords-fig',figure=parcoords_plot),style={'marginTop': '60px'})],
                                style={'overflow': 'scroll', 'marginLeft':'25%'})

    filter_sidebar, all_checklists = create_filter_sidebar(columns_metadata=columns_metadata)
    main_layout = html.Div([filter_sidebar,visualization_div])

    app.layout = main_layout

    summarizer_inputs = [Input(component_id='summarizer_group', component_property='value'),
                         Input(component_id='summarizer_operation', component_property='value')]
    col_filter_inputs = [Input(component_id=c.id, component_property='value') for c in all_checklists]
    refresh_input = [Input(component_id='interval1',component_property='n_intervals')]

    summarizer_events = ['summarizer_group.value','summarizer_operation.value']

    def group_apply(df,group,operation):
        grouped_data = df.groupby(group).aggregate(available_operations[operation]).reset_index()
        uniqued = df.groupby('run_id').aggregate(np.unique).reset_index()
        grouped_data = pd.concat([uniqued[uniqued.columns.difference(grouped_data.columns)],grouped_data],axis=1)
        return grouped_data

    @app.callback(Output(component_id='interactive_datatable', component_property='data'),
                  refresh_input + summarizer_inputs + col_filter_inputs)

    def update_table_data(interval,group,operation,*cols):
        ctx = dash.callback_context
        if ctx.triggered[0]['prop_id'] == 'interval1.n_intervals':
            local_data = pd.read_csv(Path(args['logdir'],'results.csv'))
        else:
            local_data = df_data

        if group and operation:
            local_data = group_apply(df_data,group,operation)
        else:
            local_data = df_data

        cols_ = []
        for col in cols:
            cols_ = cols_ + [col_i for col_i in col if col_i in local_data.columns]
        data_subset = local_data[cols_]
        
        return data_subset.to_dict('records')

    @app.callback(Output(component_id='interactive_datatable', component_property='columns'),
                  refresh_input + summarizer_inputs + col_filter_inputs)

    def update_table_cols(interval,group,operation,*cols):
        ctx = dash.callback_context
        
        if ctx.triggered[0]['prop_id'] == 'interval1.n_intervals':
            local_data = pd.read_csv(Path(args['logdir'],'results.csv'))
        else:
            local_data = df_data

        if group and operation:
            local_data = group_apply(df_data,group,operation)
        else:
            local_data = df_data

        cols_ = []
        for col in cols:
            cols_ = cols_ + [col_i for col_i in col if col_i in local_data.columns]
        out_cols = [{"name": i, "id": i, 'format': Format(precision=3), 'type':'numeric'} for i in cols_]
        
        return out_cols

    @app.callback(
        Output('parcoords-fig', 'figure'),
        [Input('interactive_datatable', 'columns'), Input('interactive_datatable', 'data')])

    def update_figure(cols, data):
        
        filtered_df = pd.DataFrame(data)
        col_names = filtered_df.columns
         
        return create_parcoords_fig(data=filtered_df,columns=col_names)

    app.run_server(port = args['port'], debug=True)

if __name__ == '__main__':
    main()
    