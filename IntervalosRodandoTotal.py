import time
import requests
from datetime import datetime, timedelta
from collections import Counter
import pandas as pd
import webbrowser
import numpy as np
import copy
import base64

# Adicione as funções get_api_data e get_sequence do script INICIO.PY
total_pages = 11
last_sequence = None

def get_api_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Lança uma exceção se a resposta contiver um código de status de erro HTTP
        return response.json()
    except requests.HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except requests.RequestException as err:
        print(f'Other error occurred: {err}')
    except ValueError:  # Lançado quando .json() falha
        print('Invalid JSON')
    return None  # Retorna None se algo der errado

def get_sequence():
    global last_sequence
    sequence = []
    for page in (range(1, total_pages)):
        result_json = get_api_data("https://blaze.com/api/roulette_games/history?page=" + str(page))
        if result_json is None:
            continue
        records = (result_json['records'])
        for record in records:
            roll = record['roll']
            created_at = record['created_at']

            # Converte a string 'created_at' para um objeto datetime
            created_at_datetime = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%S.%fZ")
            # Diminui 3 horas
            created_at_datetime = created_at_datetime - timedelta(hours=3)
            # Converte o objeto datetime de volta para uma string no formato hh:mm
            created_at_str = created_at_datetime.strftime("%H:%M")
            sequence.append((roll, created_at_str))

    last_sequence = sequence
    return sequence

def main():
    print("Running intervalos.py")
    sequence = get_sequence()  # Obtenha a sequência em tempo real

    rolls = []  # Lista para armazenar os números
    times = []  # Lista para armazenar os horários
    zeros = []  # Lista para armazenar os zeros
    zero_times = []  # Lista para armazenar os horários dos zeros
    intervals = []  # Lista para armazenar os intervalos entre os zeros
    interval_count = 0  # Contador para o intervalo atual entre os zeros
    first_zero_found = False  # Flag para indicar se o primeiro zero foi encontrado
    payers = []  # Lista para armazenar os números pagadores
    cycle_numbers = set(range(1, 15))  # Conjunto de números para um ciclo completo
    current_cycle_numbers = set()  # Conjunto de números para o ciclo atual
    cycle_count = 1  # Contador para o ciclo atual
    cycles = []  # Lista para armazenar o ciclo atual
    missing_numbers = []  # Lista para armazenar os números que faltam
    multiplos_14 = [[] for _ in range(790)]  # Lista para armazenar os múltiplos de 14
    pagou = [[] for _ in range(790)]  # Lista para armazenar as mensagens de pagamento
    multiplos_14_dict = {}  # Dicionário para mapear os horários dos múltiplos de 14 aos seus índices

    for page in reversed(range(1, total_pages)):
        result_json = (requests.get("https://blaze.com/api/roulette_games/history?page=" + str(page))).json()
        resultados = reversed(result_json['records'])
        p_placed = False  # Variável de controle para verificar se um "P" já foi colocado
        for resultado in resultados:
            roll = resultado['roll']
            created_at = resultado['created_at']

            created_at_datetime = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%S.%fZ")
            created_at_datetime = created_at_datetime - timedelta(hours=3)

            if created_at_datetime.date() != datetime.now().date():
                continue

            created_at_str = created_at_datetime.strftime("%H:%M")

            rolls.append(roll)
            times.append(created_at_str)


            if roll == 0:
                zeros.append(roll)
                zero_times.append(created_at_str)
                cycles.append(f"Ciclo{cycle_count}")
                missing_numbers.append(list(cycle_numbers - current_cycle_numbers))
                if first_zero_found:
                    intervals.append(interval_count)
                interval_count = 0
                first_zero_found = True
                p_placed = False  # Redefina a variável de controle para False quando um novo zero for sorteado

                # Adicione os múltiplos de 14
                for i in range(14, 790, 14):
                    next_time = (created_at_datetime + timedelta(minutes=i)).strftime("%H:%M")
                    multiplos_14[i - 1].append(next_time)
                    pagou[i - 1].append(None)  # Adicione None à lista "pagou"
                    multiplos_14_dict[next_time] = i - 1  # Adicione o horário e o índice ao dicionário

                # Verifique se o horário atual está no dicionário de múltiplos de 14
                for i in range(14, 790, 14):
                    if created_at_str in multiplos_14[i - 1] and not p_placed:
                        index = multiplos_14[i - 1].index(created_at_str)
                        multiplos_14[i - 1][index] = f"P {created_at_str}"
                        p_placed = True  # Mude o estado da variável de controle para True quando um "P" for colocado

                if rolls:
                    last_payer_index = -2
                    while abs(last_payer_index) <= len(rolls) and rolls[
                        last_payer_index] == 0:  # Continue procurando até encontrar um número não-zero
                        last_payer_index -= 1
                    if abs(last_payer_index) > len(rolls):
                        last_payer = " "
                    else:
                        last_payer = rolls[last_payer_index]
                    payers.append(last_payer)
                    if last_payer != " ":
                        current_cycle_numbers.add(last_payer)  # Adicione o número pagador a current_cycle_numbers aqui

                    if cycle_numbers.issubset(current_cycle_numbers):
                        print("Cycle completed!")
                        last_payer = str(last_payer) + "F"
                        payers[-1] = last_payer
                        current_cycle_numbers = set()  # Reinicie current_cycle_numbers aqui
                        cycle_count += 1  # Incrementa o contador de ciclos

            elif first_zero_found:
                interval_count += 1
                print(f"Roll:{roll}, Created at: {created_at_str}, Interval count: {interval_count}")

        time.sleep(1)

        # Adicione o último intervalo à lista de intervalos
    if interval_count > 0:
        intervals.append(interval_count)
        print(f"Zero found at {created_at_str}, interval: {interval_count}")

        # Conte a frequência de cada intervalo
    interval_counts = Counter(intervals)

    # Crie uma lista de tuplas (intervalo, frequência)
    interval_freq = [(interval, freq) for interval, freq in interval_counts.items()]

    # Ordene a lista de tuplas em ordem decrescente pelo intervalo
    interval_freq.sort(key=lambda x: x[0], reverse=True)

    # Crie listas separadas para "Intervalos" e "Frequências"
    intervalos = [interval[0] for interval in interval_freq]
    frequencias = [interval[1] for interval in interval_freq]

    # Crie uma lista separada para "Branco 2"
    branco_2 = zero_times[1:]

    max_len = max(len(rolls), len(times), len(zero_times), len(intervals), len(branco_2), len(intervalos),
                  len(frequencias))

    rolls += [None] * (max_len - len(rolls))
    times += [None] * (max_len - len(times))
    zero_times += [None] * (max_len - len(zero_times))
    intervals += [None] * (max_len - len(intervals))
    branco_2 += [None] * (max_len - len(branco_2))
    intervalos += [None] * (max_len - len(intervalos))
    frequencias += [None] * (max_len - len(frequencias))

    df1 = pd.DataFrame({
        "Números": rolls,
        "Horários": times,
        "Branco 1": zero_times,
        "Casas": intervals,
        "Branco 2": branco_2,
        "Casas Ordem": intervalos,
        "Nº de Vezes": frequencias,
    })

    # Preencha as listas mais curtas com None até que todas as listas tenham o mesmo comprimento
    max_len = max(len(zero_times), len(payers), len(cycles), len(missing_numbers))
    zero_times += [None] * (max_len - len(zero_times))
    payers += [None] * (max_len - len(payers))
    cycles += [None] * (max_len - len(cycles))
    missing_numbers += [None] * (max_len - len(missing_numbers))

    df2 = pd.DataFrame({
        "Branco": zero_times,
        "Pagou": payers,
        "Ciclo": cycles,
        "Falta Pagar": missing_numbers,
    })

    # Adicione as colunas "14" a "196" ao DataFrame df2
    for i in range(14, 790, 14):
        # Garanta que a lista multiplos_14[i - 1] tenha o mesmo comprimento que o número de linhas no DataFrame df2
        multiplos_14[i - 1] += [None] * (max_len - len(multiplos_14[i - 1]))

        df2[f"{i}"] = multiplos_14[i - 1]


    # Concatene os dois DataFrames horizontalmente
    df = pd.concat([df1, df2], axis=1)

    # Crie um dicionário para mapear os números às imagens
    image_dict = {
        0: "./images/0.jpeg",
        1: "./images/1.jpeg",
        2: "./images/2.jpeg",
        3: "./images/3.jpeg",
        4: "./images/4.jpeg",
        5: "./images/5.jpeg",
        6: "./images/6.jpeg",
        7: "./images/7.jpeg",
        8: "./images/8.jpeg",
        9: "./images/9.jpeg",
        10: "./images/10.jpeg",
        11: "./images/11.jpeg",
        12: "./images/12.jpeg",
        13: "./images/13.jpeg",
        14: "./images/14.jpeg",
    }

    # Substitua os números na coluna "Números" pelas imagens correspondentes
    df["Números"] = df["Números"].map(image_dict)

    # Substitua NaN por uma string vazia
    df.fillna("", inplace=True)

    # Tente converter as colunas para inteiros apenas para a visualização
    for col in [3, 5, 6]:  # Colunas C, E, F
        #df.iloc[:, col] = df.iloc[:, col].apply(lambda x: int(x) if isinstance(x, str) and x.isdigit() else x)
        df.iloc[:, col] = df.iloc[:, col].apply(lambda x: int(x) if x != "" else x)

    # Tente converter as colunas para inteiros apenas para a visualização
    # Encontre a primeira entrada não nula na coluna 8
    #first_non_null_entry = df.iloc[:, 8].dropna().iloc[0]

    # Verifique se a primeira entrada não nula é uma string que contém um dígito
    #if isinstance(first_non_null_entry, str) and first_non_null_entry.isdigit():
        #df.iloc[:, 8] = df.iloc[:, 8].apply(lambda x: int(x) if isinstance(x, str) and x.isdigit() else x)
    #else:
        #df.iloc[:, 8] = df.iloc[:, 8].apply(lambda x: int(x) if x != "" else x)
    # Tente converter as colunas para inteiros apenas para a visualização

    for col in [8]:  # Colunas C, E, F
        df.iloc[:, col] = df.iloc[:, col].apply(lambda x: int(x) if isinstance(x, str) and x.isdigit() else x)
        # df.iloc[:, col] = df.iloc[:, col].apply(lambda x: int(x) if x != "" else x)

    # Substitua as URLs das imagens por tags de imagem HTML
    df["Números"] = df["Números"].apply(lambda url: f'<img src="{url}" width="50" height="50">')

    # Substitua "F" pela imagem desejada
    df["Pagou"] = df["Pagou"].apply(lambda x: f'<div style="position: relative; text-align: center;"><img src="./images/ciclo1.png" width=45" height="45"><span style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); color: white;">{x[:-1]}</span></div>' if isinstance(x, str) and x.endswith("F") else x)

    # Crie uma nova coluna "Sequência" que combina "Números" e "Horários"
    df["Sequência"] = '<div style="text-align: center">' + df["Números"].astype(str) + "<br>" + df["Horários"].astype(str) + '</div>'

    # Remova as colunas "Números", "Horários", "Brancos" e "Horário"
    df = df.drop(columns=["Números", "Horários"])

    # Reordene as colunas para que "Sequência" e "Brancos" sejam as primeiras
    df = df[["Sequência", "Branco 1"] + [col for col in df.columns if col not in ["Sequência", "Branco 1"]]]

    # Adicione a imagem acima do horário nas colunas "Branco 1" e "Branco 2"
    df["Branco 1"] = df["Branco 1"].apply(lambda x: f'<img src="./images/0.jpeg" width="50" height="50"><br>{x}' if ":" in x else x)
    df["Branco 2"] = df["Branco 2"].apply(lambda x: f'<img src="./images/0.jpeg" width="50" height="50"><br>{x}' if ":" in x else x)

    # Adicione a imagem acima do horário na coluna "Branco" Df2
    df["Branco"] = df["Branco"].apply(lambda x: f'<img src="./images/0.jpeg" width="50" height="50"><br>{x}' if ":" in x else x)

    # Adicione a imagem à coluna "Intervalo" apenas se a célula estiver preenchida
    df["Casas"] = df["Casas"].apply(lambda x: f'<div style="position: relative; text-align: center;"><img src="./images/intervalo1.png" width="50" height="55"><span style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); color: black;">{x}</span></div>' if x != "" else "")

    # Adicione a imagem à coluna "frequencias" apenas se a célula estiver preenchida
    df["Nº de Vezes"] = df["Nº de Vezes"].apply(lambda x: f'<div style="position: relative; text-align: center;"><img src="./images/freq.png" width="35" height="35"><span style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); color: white;">{x}</span></div>' if x != "" else "")

    # Cria uma lista com os nomes das colunas
    columns = [str(i) for i in range(14, 790, 14)]  # Cria uma lista com os nomes das colunas
    for column in columns:
        df[column] = df[column].apply(lambda x: f'<div style="text-align: center;"><img src="./images/pago.png" width="30" height="30"><br><div>{x[2:]}</div></div>' if isinstance(x, str) and x.startswith('P ') else x)

    # Converta a coluna "Intervalos" para números, ignorando os erros
    df["Casas Ordem"] = pd.to_numeric(df["Casas Ordem"], errors='coerce')

    # Calcule o valor máximo da coluna "Intervalos" antes de fazer a substituição
    max_interval = df["Casas Ordem"].max()

    # Crie uma função para gerar o HTML para uma barra
    def create_bar(value, max_value):
        # Calcule a largura da barra como uma porcentagem do valor máximo
        # Ajuste a largura para que o valor mínimo seja 50% da largura máxima
        width = 10 + ((value - 1) / (max_value - 1)) * 90

        # Retorne o HTML para a barra e o valor
        return f'{int(value)}<div style="background-color:blue; width:{width}%; height:10px;"></div>'

    # Aplique a função à coluna "Intervalos" para criar as barras
    df["Casas Ordem"] = df["Casas Ordem"].apply(lambda x: create_bar(x, max_interval) if pd.notnull(x) else "")

    def increase_font(value):
        if value is not None:
            return f'<span style="font-size: 1.2em;">{value}</span>'
        else:
            return value

    df["Casas"] = df["Casas"].apply(increase_font)
    df["Casas Ordem"] = df["Casas Ordem"].apply(increase_font)
    df["Nº de Vezes"] = df["Nº de Vezes"].apply(increase_font)

    # Defina uma função para adicionar o estilo CSS
    def add_style(cell):
        if cell == "&nbsp;":
            return 'background-color: #808080;'  # Use qualquer cor em hexadecimal que você quiser
        else:
            return ''

    # Aplique a função de estilo à coluna vazia
    df_styled = df.style.applymap(add_style, subset=pd.IndexSlice[:, [' ']])

    # Gere o HTML do DataFrame sem o índice
    html = df.to_html(index=False, escape=False)

    # Adicione o CSS ao HTML
    html = html.replace('<table', '<table style="margin-left: auto; margin-right: auto; border: 10px solid #1a242d; border-collapse: collapse;" border="1" class="dataframe"')
    html = html.replace('<th', '<th style="text-align: center; background-color: #282d37; color: white; font-size: 1em; font-weight: bold; border: 2px solid #1a242d; padding: 0;"')
    html = html.replace('<td', '<td style="width: 80px;text-align: center; background-color: #0f1923; color: white; font-size: 0.8em; font-weight: bold; border: 2px solid #1a242d; padding: 0;"')
    html = html.replace('<thead>', '<thead style="background-color: #282d37;">')
    html = html.replace('<td>', '<td style="background-color: #282d37;">')


    # Escreva o HTML em um arquivo
    with open("output1.html", "w") as f:
        f.write(html)

    webbrowser.open('output1.html')

if __name__ == "__main__":
    main()