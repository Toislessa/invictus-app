from waitress import serve
import dash
from dash import dcc, html, Input, Output
from flask import Flask
from flask_socketio import SocketIO
import soma2
import monitor3

# Inicialização
server = Flask(__name__)
socketio = SocketIO(server)
app = dash.Dash(__name__, server=server)

# Layout do Dash
app.layout = html.Div([
    html.H1("Correspondências em Tempo Real"),
    html.Div(id='live-update-text'),
    dcc.Interval(
        id='interval-component',
        interval=1*1000,  # em milissegundos
        n_intervals=0
    )
])

# Callback para atualização em tempo real
@app.callback(
    Output('live-update-text', 'children'),
    Input('interval-component', 'n_intervals')
)
def update_layout(n):
    return "Aguardando atualizações..."

# Manipulador SocketIO
@socketio.on('new number')
def handle_message(message):
    print('Received new number:', message)
    # Atualize seu Dash aqui com os novos números


@socketio.on('new_csv_data')
def handle_new_csv_data(message):
    print('CSV atualizado:', message)
    # Aqui, você pode ler o novo arquivo CSV e atualizar o Dash
    df = pd.read_csv("df1.csv")
    # Atualize seu Dash aqui com os novos dados do CSV

if __name__ == '__main__':
    soma2.init(socketio)
    monitor3.init(socketio)  # Inicializando o monitor2
    serve(app.server, host='0.0.0.0', port=8080)
