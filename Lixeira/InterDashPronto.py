
from dash import Dash, html, Input, Output
from intervalos import main as get_dataframe
from bs4 import BeautifulSoup
import json
from dash_dangerously_set_inner_html import DangerouslySetInnerHTML

app = Dash(__name__)

app.layout = html.Div(children=[
    html.H1(children='Análise de Roleta'),

    html.Div(children='''
        Tabela de dados será exibida aqui.
    '''),

    # Adiciona um botão para atualizar os dados
    html.Button('Atualizar dados', id='update-button'),

    # Adiciona um espaço reservado para a tabela de dados
    html.Div(id='table-container')
])

def generate_html(cell_content, col):
    if isinstance(cell_content, str) and '<div' in cell_content:
        # Se a célula contiver uma tag <div>, retorne o conteúdo da célula como está
        return DangerouslySetInnerHTML(cell_content)
    elif isinstance(cell_content, str) and 'img' in cell_content and 'text' in cell_content:
        try:
            # Tenta converter a string para um dicionário
            cell_content = json.loads(cell_content.replace("'", "\""))
        except json.JSONDecodeError:
            pass

    if isinstance(cell_content, dict) and 'img' in cell_content:
        return DangerouslySetInnerHTML(f"""
            <div style="text-align: center">
                <img src="{cell_content['img']}" style="max-width: 50px; max-height: 50px">
                <br>
                <span>{cell_content['text']}</span>
            </div>
        """)
    elif isinstance(cell_content, str) and '<img' in cell_content:
        return DangerouslySetInnerHTML(cell_content)
    else:
        return cell_content



@app.callback(
    Output('table-container', 'children'),
    [Input('update-button', 'n_clicks')]
)
def update_table(n_clicks):
    if n_clicks is None:
        # Se o botão ainda não foi clicado, não faça nada
        return

    # Obtenha o DataFrame
    df = get_dataframe()

    # Crie uma tabela HTML a partir do DataFrame
    table = html.Table(
        # Header
        [html.Tr([html.Th(col, style={'border': '1px solid #1a242d', 'color': 'white', 'text-align': 'center'}) for col in df.columns])] +

        # Body
        [html.Tr([
            html.Td(
                generate_html(df.iloc[i][col], col),
                style={'border': '1px solid #1a242d', 'color': 'white', 'text-align': 'center'}
            ) for col in df.columns
        ]) for i in range(len(df))],
        style={'border': '1px solid #1a242d', 'background-color': '#0f1923', 'border-collapse': 'collapse'}
    )

    return table

if __name__ == '__main__':
    app.run_server(debug=True)