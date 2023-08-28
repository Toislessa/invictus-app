import sys
import requests
import subprocess
import threading
from waitress import serve
from interactivity import highlight, select, zoom_and_pan
import re
from datetime import datetime, date
import math
import dash
from dash import Dash, dcc, html, Input, Output
import plotly.graph_objects as go
import pandas as pd
subprocess.call([sys.executable, "grafico4.py"])
def run_monitor():

    subprocess.call([sys.executable, "monitor2.py"])

def run_soma():
    subprocess.call([sys.executable, "soma.py"])

# Criar e iniciar as threads para rodar os scripts em segundo plano
intervalos_thread = threading.Thread(target=run_monitor)
soma_thread = threading.Thread(target=run_soma)
intervalos_thread.start()
soma_thread.start()

# Variáveis globais para rastrear a última atualização e modificação do arquivo CSV
last_update_time = None
last_file_modification_time = None

# Estilos da tabela
table_style = {
    'backgroundColor': '#0f1923',
    'borderCollapse': 'collapse',
    'width': '100%',  # Ajuste a largura conforme necessário
    'height': '80%',
    'border': '0.5px solid #1a242d',
    "color": "white",

}

table_style_2 = {
    'backgroundColor': '#0f1923',
    'borderCollapse': 'collapse',

    'border': '1px solid #1a242d',
    "color": "white",

}

border_style = {'margin': '0.1px', }

# Definir o estilo da borda
#border_style = {'border': '0.1px solid #1a242d', 'padding': '1px', 'margin': '1px'}

cell_style = {
    'border': '1px solid #1a242d', # Mantenha a borda da célula, se quiser
    'padding': '0px',
    'textAlign': 'center', # Alinhar ao centro
    'width': '70px', # Ajuste a largura conforme necessário
    #'width': '100%',
    'height': '100%',
}


element_style = {
    'margin': '0px auto',   # Sem espaço externo
    'padding': '0px',  # Sem espaço interno
    'display': 'block', # Exibe como um bloco
    'border': 'none', # Tentando 'none' em vez de '0'
    'outline': 'none', # Adicionando outline 'none' para remover qualquer borda adicional

}

header_style = {
    'backgroundColor': '#282d37',
    'color': 'white',
    'border': '1px solid #1a242d',
    'padding': '7px',
    'textAlign': 'center',
}
# Estilo da imagem (definido fora da função)
image_style = {
    'width': '50%',
    'height': '50%',
    'border': 'none',
    'outline': 'none',
    'padding': '0px',
    'margin': '0px auto',
    'display': 'black'
}

# Estilo para o texto abaixo da imagem
text_style = {

    'margin': '0px',
    'padding': '0px',
    'textAlign': 'center',
    'outline': 'none',
    'border': 'none',
    'color': 'white',
    'fontSize': '10px'
}
casas_image_style = {
    'width': '100%',
    'height': '50px',  # Deixando mais alta
    'border': 'none',
    'outline': 'none',
    'padding': '0px',
    'margin': '0px auto',
    'display': 'block',
    'color': 'black'
}

table_container_style = {

    'overflow': 'auto',
    'scrollbar-width': 'none',  # Para Firefox
    '-ms-overflow-style': 'none',  # Para Internet Explorer e Edge
    #'width': '80%', # Certifique-se de definir a largura adequada
    #'height': '100%', # Certifique-se de definir a altura adequada
    'scrollbar-color': 'transparent transparent', # Para Firefox
    '-webkit-scrollbar': 'display: none', # Para Chrome, Safari
}

toggle_container_style = {
    'border': '1px solid #1a242d', # Borda fina
    'padding': '4px',
    'display': 'flex',
    'justifyContent': 'space-between', # Espaçamento entre os elementos
    'backgroundColor': '#1a242d',
    'color': 'white'
}

# Dicionário mapeando números para caminhos de imagem
image_paths = {
    0: "./assets/0.svg",
    1: "./assets/1.png",
    2: "./assets/2.png",
    3: "./assets/3.png",
    4: "./assets/4.png",
    5: "./assets/5.png",
    6: "./assets/6.png",
    7: "./assets/7.png",
    8: "./assets/8.png",
    9: "./assets/9.png",
    10: "./assets/10.png",
    11: "./assets/11.png",
    12: "./assets/12.png",
    13: "./assets/13.png",
    14: "./assets/14.png",
}

# Caminhos de imagem para a segunda tabela

second_table_image_paths = {
    'Branco': "./assets/0.png",
    'Casas': "./assets/intervalo1.png",
    'Número de Vezes': "./assets/freq.png",
    'Payer': "./assets/ciclo2.png",
}

# Função para ler o CSV
def read_csv():
    try:
        df = pd.read_csv("df.csv")
        return df
    except Exception as e:
        return pd.DataFrame()

def read_csv_for_grid():
    try:
        df = pd.read_csv("df1.csv")
        return df
    except Exception as e:
        return pd.DataFrame()


def should_add_emoji(row_data, cell_value):
    current_time = datetime.now().time()
    cell_time_str = extract_time_from_cell(cell_value)

    if not cell_time_str:
        return False

    cell_time = datetime.strptime(cell_time_str, "%H:%M").time()
    time_difference_minutes = (datetime.combine(date.today(), cell_time) -
                               datetime.combine(date.today(), current_time)).total_seconds() / 60

    if time_difference_minutes < -2 and "P" not in cell_value and "X" not in cell_value:
        return True

    return False


def extract_time_from_cell(cell_value):
    #print(f"Extracting from cell: {cell_value}")

    time_pattern = re.compile(r"(\d{2}:\d{2})")

    # Verifique se o valor da célula é uma string ou semelhante a bytes
    if isinstance(cell_value, (str, bytes)):
        match = time_pattern.search(cell_value)
        if match:
            extracted_time = match.group(1)
            #print(f"Cell value: {cell_value}, Extracted time: {extracted_time}")
            return extracted_time
    return None

def highlight_time_cell(row_data, cell_value):
    #print(f"Checking cell: {cell_value}")

    # Obter o horário atual
    current_time = datetime.now().time()

    # Se qualquer célula na mesma linha tiver "X" ou "P", nenhuma análise será feita
    if any("P" in str(val) or "X" in str(val) for val in row_data):  # Converte val para string aqui
        return {}

    # Se a célula contiver uma representação de tempo
    cell_time_str = extract_time_from_cell(cell_value)
    if cell_time_str:
        cell_time = datetime.strptime(cell_time_str, "%H:%M").time()

        # Calcular a diferença de tempo em minutos
        time_difference_minutes = (datetime.combine(date.today(), cell_time) -
                                   datetime.combine(date.today(), current_time)).total_seconds() / 60
        #print(f"Time difference for cell {cell_value}: {time_difference_minutes} minutes")

        # Verificar as condições
        if 0 <= time_difference_minutes <= 5:
            return {"backgroundColor": "#2ECC40"}  # verde claro

    return {}

def create_grid(df):
    # Definir o número de linhas e colunas
    cols = 15


    # Pegar os 500 resultados mais recentes
    df_recent = df.tail(499).dropna(subset=['Números', 'Horários'])

    # Criar listas separadas para os números e os horários e invertê-las
    numbers = list(df_recent['Números'])[::-1]
    times = list(df_recent['Horários'])[::-1]

    # Calcular o número de linhas necessário
    rows = int(math.ceil(len(numbers) / float(cols)))

    # Criar contêineres para cada célula da grade
    containers = []
    for i in range(rows * cols):
        if i < len(numbers):
            number = numbers[i]
            time = times[i]
            image_path = image_paths.get(number, "./assets/Invictus.jpeg")
            container = html.Div(
                className='cell',  # Adicionando a classe 'cell' aqui
                children=[
                    html.Div(
                        children=[
                            html.Img(src=image_path, className='number-image', style={'width': '40px', 'height': '40px'}, **{'data-number': str(int(number))}),
                        ],
                        style={'width': '40px', 'height': '40px'}
                    ),
                    html.P(time, style={'color': 'white', 'fontSize': '11px', 'textAlign': 'center', 'marginTop': '0px', 'fontWeight': 'bold'}),
                ],
                style={'width': '40px', 'height': '50px', 'position': 'relative'}
            )
        else:
            container = html.Div(style={'width': '40px', 'height': '55px'})

        containers.append(container)

    # Reorganizar os contêineres na ordem desejada
    reordered_containers = []
    for row in range(rows):
        for col in range(cols):
            index = ((cols - 1) - col) + (row * cols)
            reordered_containers.append(containers[index])

    # Organizar os contêineres em uma grade
    grid = html.Div(
        children=reordered_containers,
        style={
            'display': 'grid',
            'gridTemplateColumns': 'repeat(15, 40px)',
            'gridTemplateRows': 'repeat(34, 55px)',
            'gridColumnGap': '2px',
            'gridRowGap': '2px',
            'backgroundColor': 'black',

        },
        id='grid-container'
    )

    return grid

def has_p_or_x_in_time_columns(row_data, columns, time_columns):
    return any("P" in str(row_data[columns.index(col)]) or "X" in str(row_data[columns.index(col)]) for col in time_columns)
# Função para criar a tabela personalizada
def create_custom_table(df):
    columns = ['Branco', 'L', '14', '28', '42', '56', '70', '84', '98', '112', '126', '140', '154', '168', '182', '196', '210', '224', '238', '252']
    df = df[columns]
    df = df.loc[~df['Branco'].isna()]
    time_columns = ['14', '28', '42', '56', '70', '84', '98', '112', '126', '140', '154', '168', '182', '196', '210', '224', '238', '252']

    def generate_cell(row_data, cell_value, column):
        content = cell_value
        highlighted_style = {}

        # Verificar se há "X" ou "P" nas colunas de horário
        if has_p_or_x_in_time_columns(row_data, columns, time_columns):
            #print(f"Ignorando linha: {row_data}")  # Mensagem de depuração
            pass
        else:
            if column in time_columns:
                current_time = datetime.now().time()
                cell_time_str = extract_time_from_cell(cell_value)
                #print(f"Analisando célula: {cell_value}, horário extraído: {cell_time_str}")  # Mensagem de depuração

                if cell_time_str:
                    cell_time = datetime.strptime(cell_time_str, "%H:%M").time()
                    time_difference_minutes = (datetime.combine(date.today(), cell_time) -
                                               datetime.combine(date.today(), current_time)).total_seconds() / 60
                    #print(f"Diferença de tempo: {time_difference_minutes}")  # Mensagem de depuração

                    # Verificar as condições
                    if -2 <= time_difference_minutes <= 5:
                        highlighted_style = {"backgroundColor": "#2ECC40","color": "black"}
                    elif time_difference_minutes < -2:
                        content = f"❌ {cell_value}"
                        # Adicionar Emoji ❌ nas células anteriores da mesma linha
                        for prev_col in time_columns:
                            if prev_col == column:
                                break
                            index = columns.index(prev_col)
                            row_data[index] = f"❌ {row_data[index]}"
                            #print(f"Adicionando Emoji ❌ na coluna {prev_col}")  # Mensagem de depuração

        # Se a coluna for "Branco"
        if column == "Branco":
            if "P" in cell_value:
                content = html.Div([html.Img(src="./assets/Pago_Verde.png", style=image_style),
                                    html.P(cell_value.replace("P", ""), style=text_style)], style=text_style)
            elif "X" in cell_value:
                content = html.Div([html.Img(src="./assets/Pago_Azul.png", style=image_style),
                                    html.P(cell_value.replace("X", ""), style=text_style)], style=text_style)
            else:
                content = html.Div(
                    style={'textAlign': 'center'},
                    children=[
                        html.Img(src="./assets/0.png", style=image_style),
                        html.P(cell_value, style=text_style)
                    ]
                )
        # Se a coluna for um dos horários especificados
        elif column in time_columns:
            if "P" in cell_value:
                content = html.Div([html.Img(src="./assets/pago.png", style=image_style),
                                    html.P(cell_value.replace("P", ""), style=text_style)], style=text_style)
            elif "X" in cell_value:
                content = html.Div([html.Img(src="./assets/pago5.png", style=image_style),
                                    html.P(cell_value.replace("X", ""), style=text_style)], style=text_style)


        return html.Td(content, style=highlighted_style if highlighted_style else cell_style)

    data = df.values.tolist()
    header = df.columns.tolist()

    table = html.Table(
        # Header
        [html.Tr([html.Th(col, style=header_style) for col in header])] +
        # Body
        [
            html.Tr([
                generate_cell(row_data, row_data[j], header[j]) for j in range(len(header))
            ]) for row_data in data
        ],
        style=table_style
    )
    return html.Div(children=[table], style=table_container_style, className="table-container", id="custom-table")


# Função para criar a segunda tabela personalizada
def create_second_table(df):
    # Selecionar apenas as colunas necessárias
    columns = ['Branco 1', 'Casas', 'Branco 2', 'Casas Ordem', 'Número de Vezes', 'Payer', 'Ciclo', 'Falta Pagar']
    df = df[columns]

    def generate_cell(value, column):
        content = value
        image_path = None
        style_to_use = image_style  # Estilo padrão
        text_style_to_use = {**text_style, 'fontWeight': 'bold'}  # Negrito por padrão

        if column == 'Falta Pagar':
            text_style_to_use['fontWeight'] = 'normal'  # Sem negrito
        if column == 'Casas':
            text_style_to_use['color'] = 'black'  # Cor preta

        # Verificar se o valor contém "F" na coluna 'Payer'
        if column == 'Payer' and "F" in str(value):
            image_path = second_table_image_paths['Payer']
            value = str(value).replace("F", "")  # Remover "F"

        if column in ['Branco 1', 'Branco 2']:
            image_path = second_table_image_paths['Branco']
            content = html.Div(
                children=[
                    html.Img(src=image_path, style=style_to_use),
                    html.P(value, style=text_style_to_use)  # Usar o estilo atualizado
                ],
                style={'position': 'relative', 'width': '100%', 'height': '100%'}
            )
        elif column == 'Casas':
            image_path = second_table_image_paths['Casas']
            style_to_use = casas_image_style  # Usando estilo separado
        elif column == 'Número de Vezes':
            image_path = second_table_image_paths['Número de Vezes']

        if image_path and column not in ['Branco 1', 'Branco 2']:
            content = html.Div(
                children=[
                    html.Img(src=image_path, style=style_to_use),
                    html.Div(value, style={**text_style_to_use, 'position': 'absolute', 'top': '50%', 'left': '50%',
                                           'transform': 'translate(-50%, -50%)', 'fontSize': '12px'})
                ],
                style={'position': 'relative', 'width': '100%', 'height': '100%'}
            )

        return html.Td(content, style=cell_style)  # Retorne a célula diretamente aqui

    # Transformar o DataFrame em uma lista de listas (cada lista é uma linha)
    data = df.values.tolist()
    header = df.columns.tolist()

    # Gerar a tabela
    table = html.Table(
        # Header
        [html.Tr([html.Th(col, style=header_style) for col in header])] +
        # Body
        [
            html.Tr([
                generate_cell(data[i][j], header[j]) for j in range(len(header))
            ]) for i in range(len(data))
        ],
        style=table_style_2
    )
    return html.Div(children=[table], style=table_container_style, className="table-container")  # Envolve a tabela na div


def create_graph(num_bars, range_values):
    df = pd.read_csv('output.csv')
    df = df.iloc[::-1].reset_index(drop=True)
    df['Resultado'] = df['Resultado'].apply(
        lambda x: float(x.replace(' ', '').replace('.', '').replace(',', '.').strip()))
    df['Hora'] = df['Hora'].apply(lambda x: x.strip())  # Removendo o excesso de espaços na hora
    df['Close'] = df['Resultado'].cumsum()
    df['Open'] = [0] + list(df['Close'][:-1])
    df['High'] = df['Close']
    df['Low'] = df['Close']

    # Mantém apenas os num_bars resultados solicitados e aplica o range
    df = df.tail(num_bars).iloc[range_values[0]: range_values[1]]
    hover_text = [f"Pedra: {val['Pedra']}<br>Hora: {val['Hora']}<br>Resultado: R${val['Resultado']:.2f}" if val['Resultado'] >= 0
                  else f"Pedra: {val['Pedra']}<br>Hora: {val['Hora']}<br>Prejuízo: R${-val['Resultado']:.2f}" for _, val in df.iterrows()]

    scale_factor = 20  # Fator de escala que você quer aplicar

    df['Close'] *= scale_factor
    df['Open'] *= scale_factor
    df['High'] *= scale_factor
    df['Low'] *= scale_factor

    fig = go.Figure(data=[go.Candlestick(x=df.index,
                                         open=df['Open'],
                                         high=df['High'],
                                         low=df['Low'],
                                         close=df['Close'],
                                         increasing_line_color='green',
                                         decreasing_line_color='red',
                                         hovertext=hover_text,
                                         hoverinfo="text")])

    # Calcular o alcance do eixo x para adicionar espaço adicional à direita
    x_range = [df.index.min(), df.index.max() + num_bars * 0.2]
    # Calcular o alcance do eixo y para adicionar espaço adicional à direita

    y_min = df['Low'].min()
    y_max = df['High'].max()
    y_margin = (y_max - y_min) * 0.2  # 5% de margem
    y_range = [y_min - y_margin, y_max + y_margin]

    fig.update_layout(xaxis_rangeslider_visible=False,
                      height=292, template="plotly_dark",
                      xaxis_title='Rodada',
                      yaxis_title='Valor',
                      xaxis=dict(showgrid=False, zeroline=True, showticklabels=False, range=x_range),
                      # Adicionar o alcance do eixo x aqui
                      yaxis=dict(gridcolor='darkgrey', range=y_range),  # Adicionar o alcance do eixo y aqui
                      margin=dict(l=0, r=0, b=0, t=0),
                      dragmode='pan')  # Habilita o pan

    return fig

# Definir o layout do aplicativo Dash
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__)

# Definir o layout do aplicativo Dash
df = read_csv()


# Definir o layout do aplicativo Dash
# Definir o layout do aplicativo Dash
app.layout = html.Div(
    children=[
        # Div para a grade e as tabelas (lado a lado)
        html.Div(
            children=[
                # Div para a grade
                html.Div(
                    children=create_grid(df),
                    style={
                        **border_style,
                        'overflow': 'auto',
                        'height': '1050px',
                        'width': '635px',
                    }
                ),
                # Div para as tabelas e o gráfico (empilhados verticalmente)
                html.Div(
                    children=[
                        # Div para a tabela personalizada, segunda tabela e RadioItems (empilhados)
                        html.Div(
                            children=[
                                # Div para os RadioItems (acima das tabelas)
                                html.Div(
                                    children=dcc.RadioItems(
                                        id='display-and-table-selection',
                                        options=[
                                            {'label': 'Exibir Tudo', 'value': 'all'},
                                            {'label': 'Falta Pagar', 'value': 'no_images'},
                                            {'label': 'Tabela Custom', 'value': 'custom'},
                                            {'label': 'Tabela 2', 'value': 'second'},
                                        ],
                                        value='all',
                                        labelStyle={'display': 'inline-block', 'margin-right': '15px', 'color': 'white'},
                                    ),
                                    style={'border': '1px solid #1a242d', 'padding': '1px', 'margin': '1px'}
                                ),
                                # Div para a tabela personalizada
                                html.Div(
                                    id='custom-table-container',
                                    children=create_custom_table(df),
                                    style={
                                        **border_style,
                                        'overflow': 'auto',
                                        'height': '300px',
                                        'width': '705px'
                                    }
                                ),
                                # Div para a segunda tabela
                                html.Div(
                                    id='second-table-container',
                                    children=create_second_table(df),
                                    style={
                                        **border_style,
                                        'overflow': 'auto',
                                        'height': '300px',
                                        'width': '430px',
                                        'display': 'none',
                                    }
                                ),
                            ],
                            style={'float': 'right'}
                        ),
                        # Div para o gráfico e o Slider (com borda)
                        html.Div(
                            children=[
                                # Div para o Slider
                                html.Div([
                                    dcc.Slider(
                                        min=100,
                                        max=2500,
                                        step=100,
                                        marks={i: str(i) for i in range(100, 2600, 100)},
                                        value=100,
                                        id='num-bars-select',
                                    )
                                ], style={"width": "100%", "margin": "0px", "padding": "10px 0px"}),  # Ajustando o estilo do Slider
                                # Div para o gráfico
                                dcc.Graph(id="candles"),
                                dcc.Interval(id="interval", interval=1000),
                            ],
                            style={'border': '2px solid #1a242d', 'padding': '0px'}  # Aplicando a borda
                        ),
                    ],
                    style={'display': 'flex', 'flexDirection': 'column'}  # Alinhar verticalmente
                ),
            ],
            style={'display': 'flex', 'flexDirection': 'row'}  # Alinhar horizontalmente
        ),
        # Interval
        dcc.Interval(
            id='interval-component',
            interval=1 * 1000,
            n_intervals=0
        )
    ]
)

# Adicionar interatividade
highlight()
select()
zoom_and_pan()

@app.callback(
    Output('grid-container', 'children'),
    Input('interval-component', 'n_intervals'))
def update_grid(n):

    df = read_csv_for_grid()  # Utilizando a nova função para ler o df1.csv
    return create_grid(df)

# Callback para atualizar a tabela dinamicamente

@app.callback(
    Output('custom-table-container', 'children'),
    [Input('interval-component', 'n_intervals'),
     Input('display-and-table-selection', 'value')]
)
def update_table(n_intervals, selection_value):
    df = read_csv()

    if selection_value == 'no_images':
        columns_with_images = ['14', '28', '42', '56', '70', '84', '98', '112', '126', '140', '154', '168', '182', '196', '210', '224', '238', '252']
        # Filtrando as linhas que não contêm "P" ou "X" em nenhuma das colunas especificadas
        df = df[~df[columns_with_images].apply(lambda row: any("P" in str(cell) or "X" in str(cell) for cell in row), axis=1)]

    return create_custom_table(df)

@app.callback(
    [Output('custom-table-container', 'style'),
     Output('second-table-container', 'style')],
    [Input('display-and-table-selection', 'value')]
)
def toggle_tables(selected_table):
    if selected_table == 'custom':
        return (
            {**border_style, 'overflow': 'auto', 'height': '375px', 'width': '705px'},
            {**border_style, 'overflow': 'auto', 'height': '375px', 'width': '430px', 'display': 'none'}
        )
    elif selected_table == 'second':
        return (
            {**border_style, 'overflow': 'auto', 'height': '375px', 'width': '705px', 'display': 'none'},
            {**border_style, 'overflow': 'auto', 'height': '375px', 'width': '430px'}
        )
    else:
        return (
            {**border_style, 'overflow': 'auto', 'height': '375px', 'width': '705px'},
            {**border_style, 'overflow': 'auto', 'height': '375px', 'width': '430px', 'display': 'none'}
        )

@app.callback(
    Output("range-slider", "max"),
    Output("range-slider", "value"),
    Input("num-bars-select", "value")
)
def update_rangeslider(num_bars):
    return num_bars, [0, num_bars]

@app.callback(
    Output("candles", "figure"),
    Input("interval", "n_intervals"),
    Input("num-bars-select", "value"),)

def update_figure(n_intervals, num_bars):
    return create_graph(num_bars, [0, num_bars])

if __name__ == '__main__':
    serve(app.server, host='0.0.0.0', port=8050, threads=100)