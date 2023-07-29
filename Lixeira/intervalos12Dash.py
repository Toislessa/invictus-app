import dash
import dash_table

# Inicialize o aplicativo Dash
app = dash.Dash(__name__)

# Defina a layout do aplicativo
app.layout = dash.html.Div([
    dash_table.DataTable(
        id='table1',
        columns=[{"name": i, "id": i} for i in df3.columns],
        data=df3.to_dict('records'),
    ),
    dash_table.DataTable(
        id='table2',
        columns=[{"name": i, "id": i} for i in df1.columns],
        data=df1.to_dict('records'),
    )
])

# Execute o aplicativo
if __name__ == '__main__':
    app.run_server(debug=True)
