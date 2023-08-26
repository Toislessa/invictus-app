import os
import time
import sys
import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import pandas as pd
import requests
from datetime import datetime, timedelta
import subprocess
import threading
from waitress import serve

# Variáveis globais para rastrear a última atualização e modificação do arquivo CSV
last_update_time = None
last_file_modification_time = None

# Função para ler o CSV
def read_csv():
    try:
        df = pd.read_csv("df.csv")
        return df
    except Exception as e:
        return pd.DataFrame()
# Função para obter dados da API

def write_current_result(result):
    with open('current_result.txt', 'w') as file:
        file.write(str(result[0]) + ',' + result[1])


def get_api_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except (requests.HTTPError, requests.RequestException, ValueError):
        return None
# Função para monitorar os resultados
def monitor_results():
    global last_update_time
    last_update_time = datetime.now()  # Atualização no início do monitoramento
    before_result = ()
    while True:
        resultado = get_api_data("https://api-v2.blaze.com/api/roulette_games/current")
        if resultado is None or resultado['status'] != 'rolling':
            time.sleep(1)
            continue
        created_at_datetime = datetime.strptime(resultado['created_at'], "%Y-%m-%dT%H:%M:%S.%fZ")
        created_at_datetime = created_at_datetime - timedelta(hours=3)
        created_at_str = created_at_datetime.strftime("%H:%M")
        current_result = (
            int(resultado['roll']),
            created_at_str,
        )

        if before_result != current_result:
            before_result = current_result
            last_update_time = datetime.now()  # Atualização no início do processo
            print(f'Novo resultado: {current_result}')
            write_current_result(current_result)  # Escreve o resultado atual em um arquivo
            print(f'Gerando novos dados em {datetime.now()}')
            subprocess.call([sys.executable, "intervalos13.py"])
            last_update_time = datetime.now()  # Atualização durante o processamento
            print(f'Atualizando a tabela em {last_update_time}')
        time.sleep(1)


# Iniciar a thread de monitoramento
monitor_thread = threading.Thread(target=monitor_results)
monitor_thread.daemon = True
monitor_thread.start()

# Definir o layout do aplicativo Dash
app = dash.Dash(__name__)

app.layout = html.Div(
    children=[
        html.H1(children="Roulette Dashboard"),
        dash_table.DataTable(
            id='table',
            columns=[{"name": i, "id": i} for i in read_csv().columns],
            data=read_csv().to_dict('records'),
            style_cell={'textAlign': 'left'},
            style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': 'rgb(248, 248, 248)'
                }
            ],
            style_header={
                'backgroundColor': 'rgb(230, 230, 230)',
                'fontWeight': 'bold'
            }
        ),
        dcc.Interval(
            id='interval-component',
            interval=2*1000, # em milissegundos
            n_intervals=0
        )
    ]
)

@app.callback(
    Output('table', 'data'),
    Input('interval-component', 'n_intervals'))
def update_table(n):
    global last_file_modification_time
    try:
        current_modification_time = os.path.getmtime("df.csv")
        if current_modification_time != last_file_modification_time:
            last_file_modification_time = current_modification_time
            df = pd.read_csv("df.csv")
            print(f'Tabela atualizada em {datetime.now()}')
            return df.to_dict('records')
    except:
        pass
    raise dash.exceptions.PreventUpdate

if __name__ == '__main__':
    serve(app.server, host='0.0.0.0', port=8050)
