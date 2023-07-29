import time
import requests
import json
from datetime import datetime, timedelta
from collections import Counter
import pandas as pd
import webbrowser
import numpy as np
import copy
import base64
import logging

# Função para ler dados de um arquivo JSON
def read_from_file(filename):
    with open(filename, 'r') as f:
        return json.load(f)

# Função para escrever dados em um arquivo JSON
def write_to_file(filename, data):
    with open(filename, 'w') as f:
        f.write(json.dumps(data))

# Configuração do logging
logging.basicConfig(filename='intervalos.log', level=logging.INFO, format='%(asctime)s %(message)s')
logging.info('Iniciando script...')

def main():
    logging.info('Iniciando def main')
    print("Running def main")
    logging.info('Running def main')
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
    multiplos_14 = [[] for _ in range(400)]  # Lista para armazenar os múltiplos de 14
    pagou = [[] for _ in range(400)]  # Lista para armazenar as mensagens de pagamento
    multiplos_14_before = [[] for _ in
                           range(400)]  # Lista para armazenar os horários um minuto antes dos múltiplos de 14
    multiplos_14_after = [[] for _ in
                          range(400)]  # Lista para armazenar os horários um minuto depois dos múltiplos de 14
    p_placed_indices = []  # Lista para armazenar os índices das linhas que já tiveram um "P" colocado nelas

    logging.info('Recuperando dados do arquivo...')
    # Recuperar os dados do arquivo
    try:
        sequence = read_from_file('sequence.json')
        logging.info('Dados recuperados do arquivo com sucesso.')
    except Exception as e:
        logging.error(f'Erro ao recuperar dados do arquivo: {e}')
        sequence = []  # Adicione esta linha para definir sequence como uma lista vazia em caso de erro

    logging.info('Processando dados...')
    # Processar os dados para gerar um DataFrame
    # Aqui, estou assumindo que os dados estão no formato que você precisa
    # Se não estiverem, você precisará processá-los para colocá-los no formato correto
    try:
        logging.info(f'sequence: {sequence}')

        logging.info('for roll, created_at_str in sequence:')
        for roll, created_at_str in sequence:
            rolls.append(roll)
            times.append(created_at_str)
            print(f"sequence:{sequence}")
            if roll == 0:
                zeros.append(roll)
                zero_times.append(created_at_str)
                cycles.append(f"Ciclo{cycle_count}")
                print(f"cycle_numbers:{cycle_numbers}")
                logging.info(f"cycle_numbers:{cycle_numbers}")
                missing_numbers.append(list(cycle_numbers - current_cycle_numbers))
                print(f"current_cycle_numbers:{current_cycle_numbers}")
                logging.info(f"current_cycle_numbers:{current_cycle_numbers}")
                print(f"missing_numbers:{missing_numbers}")
                logging.info(f"missing_numbers:{missing_numbers}")
                if first_zero_found:
                    intervals.append(interval_count)
                interval_count = 0
                first_zero_found = True
                p_placed = False  # Redefina a variável de controle para False quando um novo zero for sorteado
                logging.info('Iniciando Adicione os múltiplos de 14')
                # Adicione os múltiplos de 14
                for i in range(14, 400, 14):
                    next_time = (datetime.strptime(created_at_str, "%H:%M") + timedelta(minutes=i)).strftime("%H:%M")
                    time_before = (datetime.strptime(created_at_str, "%H:%M") + timedelta(minutes=i - 1)).strftime("%H:%M")
                    time_after = (datetime.strptime(created_at_str, "%H:%M") + timedelta(minutes=i + 1)).strftime("%H:%M")
                    multiplos_14[i - 1].append(next_time)
                    multiplos_14_before[i - 1].append(time_before)
                    multiplos_14_after[i - 1].append(time_after)
                    pagou[i - 1].append(None)  # Adicione None à lista "pagou"
                logging.info('final Adicione os múltiplos de 14')
                for i in range(14, 400, 14):
                    if not p_placed:
                        if created_at_str in multiplos_14[i - 1]:
                            index = multiplos_14[i - 1].index(created_at_str)
                            if index not in p_placed_indices:
                                multiplos_14[i - 1][index] = f"P {created_at_str} Lata"
                                p_placed = True
                                p_placed_indices.append(index)
                        elif created_at_str in multiplos_14_before[i - 1]:
                            index = multiplos_14_before[i - 1].index(created_at_str)
                            if index not in p_placed_indices:
                                multiplos_14[i - 1][index] = f"P {created_at_str} Antes"
                                p_placed = True
                                p_placed_indices.append(index)
                        elif created_at_str in multiplos_14_after[i - 1]:
                            index = multiplos_14_after[i - 1].index(created_at_str)
                            if index not in p_placed_indices:
                                multiplos_14[i - 1][index] = f"P {created_at_str} Depois"
                                p_placed = True
                                p_placed_indices.append(index)

                logging.info('Final P dos multiplos')
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
                    logging.info('Final Pagador')
                    if cycle_numbers.issubset(current_cycle_numbers):
                        print("Cycle completed!")
                        logging.info('Cycle completed!')
                        last_payer = str(last_payer) + "F"
                        payers[-1] = last_payer
                        current_cycle_numbers = set()  # Reinicie current_cycle_numbers aqui
                        cycle_count += 1  # Incrementa o contador de ciclos

            elif first_zero_found:
                interval_count += 1
                print(f"Roll:{roll}, Created at: {created_at_str}, Interval count: {interval_count}")
                logging.info(f"Roll:{roll}, Created at: {created_at_str}, Interval count: {interval_count}")
        time.sleep(1)

    except Exception as e:
        logging.error(f'Erro ao processar os dados: {e}')

    # Adicione o último intervalo à lista de intervalos
    if interval_count > 0:
        intervals.append(interval_count)
        print(f"Zero found at {created_at_str}, interval: {interval_count}")

    interval_counts = Counter(intervals)
    interval_freq = [(interval, freq) for interval, freq in interval_counts.items()]
    interval_freq.sort(key=lambda x: x[0], reverse=True)
    intervalos = [interval[0] for interval in interval_freq]
    frequencias = [interval[1] for interval in interval_freq]
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
    logging.info('Criando DF')
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
    for i in range(14, 400, 14):
        # Garanta que a lista multiplos_14[i - 1] tenha o mesmo comprimento que o número de linhas no DataFrame df2
        multiplos_14[i - 1] += [None] * (max_len - len(multiplos_14[i - 1]))

        df2[f"{i}"] = multiplos_14[i - 1]

    # Concatene os dois DataFrames horizontalmente
    df = pd.concat([df1, df2], axis=1)

    # Crie um dicionário para mapear os números às imagens
    image_dict = {
        0: "./assets/0.jpeg",
        1: "./assets/1.jpeg",
        2: "./assets/2.jpeg",
        3: "./assets/3.jpeg",
        4: "./assets/4.jpeg",
        5: "./assets/5.jpeg",
        6: "./assets/6.jpeg",
        7: "./assets/7.jpeg",
        8: "./assets/8.jpeg",
        9: "./assets/9.jpeg",
        10: "./assets/10.jpeg",
        11: "./assets/11.jpeg",
        12: "./assets/12.jpeg",
        13: "./assets/13.jpeg",
        14: "./assets/14.jpeg",
    }
    logging.info('Inicia configuração do DF')
    # Substitua os números na coluna "Números" pelas imagens correspondentes
    df["Números"] = df["Números"].map(image_dict)

    # Substitua NaN por uma string vazia
    df.fillna("", inplace=True)

    # Tente converter as colunas para inteiros apenas para a visualização
    for col in [3, 5, 6]:  # Colunas C, E, F
        # df.iloc[:, col] = df.iloc[:, col].apply(lambda x: int(x) if isinstance(x, str) and x.isdigit() else x)
        df.iloc[:, col] = df.iloc[:, col].apply(lambda x: int(x) if x != "" else x)

    # Tente converter as colunas para inteiros apenas para a visualização
    # Encontre a primeira entrada não nula na coluna 8
    # first_non_null_entry = df.iloc[:, 8].dropna().iloc[0]

    # Verifique se a primeira entrada não nula é uma string que contém um dígito
    # if isinstance(first_non_null_entry, str) and first_non_null_entry.isdigit():
    # df.iloc[:, 8] = df.iloc[:, 8].apply(lambda x: int(x) if isinstance(x, str) and x.isdigit() else x)
    # else:
    # df.iloc[:, 8] = df.iloc[:, 8].apply(lambda x: int(x) if x != "" else x)
    # Tente converter as colunas para inteiros apenas para a visualização

    for col in [8]:  # Colunas C, E, F
        df.iloc[:, col] = df.iloc[:, col].apply(lambda x: int(x) if isinstance(x, str) and x.isdigit() else x)
        # df.iloc[:, col] = df.iloc[:, col].apply(lambda x: int(x) if x != "" else x)

    # Substitua as URLs das imagens por tags de imagem HTML
    df["Números"] = df["Números"].apply(lambda url: f'<img src="{url}" width="50" height="50">')

    # Substitua "F" pela imagem desejada
    df["Pagou"] = df["Pagou"].apply(lambda x: f'<div style="position: relative; text-align: center;"><img src="./assets/ciclo1.png" width=45" height="45"><span style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); color: white;">{x[:-1]}</span></div>' if isinstance(x, str) and x.endswith("F") else x)

    # Crie uma nova coluna "Sequência" que combina "Números" e "Horários"
    df["Sequência"] = '<div style="text-align: center">' + df["Números"].astype(str) + "<br>" + df["Horários"].astype(str) + '</div>'

    # Remova as colunas "Números", "Horários", "Brancos" e "Horário"
    df = df.drop(columns=["Números", "Horários"])

    # Reordene as colunas para que "Sequência" e "Brancos" sejam as primeiras
    df = df[["Sequência", "Branco 1"] + [col for col in df.columns if col not in ["Sequência", "Branco 1"]]]

    # Adicione a imagem acima do horário nas colunas "Branco 1" e "Branco 2"
    df["Branco 1"] = df["Branco 1"].apply(lambda x: f'<img src="./assets/0.jpeg" width="50" height="50"><br>{x}' if ":" in x else x)
    df["Branco 2"] = df["Branco 2"].apply(lambda x: f'<img src="./assets/0.jpeg" width="50" height="50"><br>{x}' if ":" in x else x)

    # Adicione a imagem acima do horário na coluna "Branco" Df2
    df["Branco"] = df["Branco"].apply(lambda x: f'<img src="./assets/0.jpeg" width="50" height="50"><br>{x}' if ":" in x else x)

    # Adicione a imagem à coluna "Intervalo" apenas se a célula estiver preenchida
    df["Casas"] = df["Casas"].apply(lambda x: f'<div style="position: relative; text-align: center;"><img src="./assets/intervalo1.png" width="50" height="55"><span style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); color: black;">{x}</span></div>' if x != "" else "")

    # Adicione a imagem à coluna "frequencias" apenas se a célula estiver preenchida
    df["Nº de Vezes"] = df["Nº de Vezes"].apply(lambda x: f'<div style="position: relative; text-align: center;"><img src="./assets/freq.png" width="35" height="35"><span style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); color: white;">{x}</span></div>' if x != "" else "")

    # Cria uma lista com os nomes das colunas
    columns = [str(i) for i in range(14, 400, 14)]  # Cria uma lista com os nomes das colunas
    for column in columns:
        df[column] = df[column].apply(lambda x: f'<div style="text-align: center;"><img src="./assets/pago.png" width="30" height="30"><br><div>{x[2:]}</div></div>' if isinstance(x, str) and x.startswith('P ') else x)

    # Converta a coluna "Casas Ordem" para números, ignorando os erros
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

    df['Falta Pagar'] = df['Falta Pagar'].apply(lambda x: ', '.join(map(str, x)) if isinstance(x, list) else x)

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

    # Tente converter as colunas para inteiros apenas para a visualização
    for col in range(9, len(df.columns)):  # Colunas I em diante
        df.iloc[:, col] = df.iloc[:, col].apply(lambda x: int(x) if isinstance(x, str) and x.isdigit() else x)

    # Salve o DataFrame como um arquivo HTML
    with open('../output.html', 'w') as f:
        f.write(df.to_html(index=False))

    logging.info('Final do script')


# Chama a função main
if __name__ == "__main__":
    main()