import time
import requests
from datetime import datetime, timedelta
from collections import Counter
import pandas as pd
import webbrowser

def main():
    print("Running intervalos3.py")
    total_pages = 11
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

    for page in reversed(range(1, total_pages)):
        result_json = (requests.get("https://blaze.com/api/roulette_games/history?page=" + str(page))).json()
        resultados = reversed(result_json['records'])
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

    # Crie o DataFrame original
    df1 = pd.DataFrame({
        "Números": rolls,
        "Horários": times,
        "Branco 1": zero_times + [None] * (len(rolls) - len(zero_times)),
        "Intervalo": intervals + [None] * (len(rolls) - len(intervals)),
        "Branco 2": zero_times[1:] + [None] * (len(rolls) - len(zero_times) + 1),
        "Intervalos": [interval[0] for interval in interval_freq] + [None] * (len(rolls) - len(interval_freq)),
        "Frequências": [interval[1] for interval in interval_freq] + [None] * (len(rolls) - len(interval_freq)),
    })

    # Crie um novo DataFrame para as colunas "Branco", "Pagador", "Ciclo" e "Falta Pagar"
    df2 = pd.DataFrame({
        "Branco": zero_times + [None] * (len(rolls) - len(zero_times)),
        "Pagador": payers + [None] * (len(rolls) - len(payers)),
        "Ciclo": cycles + [None] * (len(rolls) - len(cycles)),
        "Falta Pagar": missing_numbers + [None] * (len(rolls) - len(missing_numbers)),

    })



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
    for col in [8]:  # Colunas C, E, F
        df.iloc[:, col] = df.iloc[:, col].apply(lambda x: int(x) if isinstance(x, str) and x.isdigit() else x)
        # df.iloc[:, col] = df.iloc[:, col].apply(lambda x: int(x) if x != "" else x)


    # Substitua as URLs das imagens por tags de imagem HTML
    df["Números"] = df["Números"].apply(lambda url: f'<img src="{url}" width="50" height="50">')

    # Substitua "F" pela imagem desejada
    df["Pagador"] = df["Pagador"].apply(lambda x: f'<div style="position: relative; text-align: center;"><img src="./images/ciclo1.png" width="60" height="60"><span style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); color: white;">{x[:-1]}</span></div>' if isinstance(x, str) and x.endswith("F") else x)

    # Substitua os zeros na coluna "Brancos" pela URL da imagem correspondente
    #df["Branco"] = df["Branco"].replace({0: "D:\\pythonProject1\\images\\0.jpeg"})

    # Substitua as URLs das imagens por tags de imagem HTML
    #df["Branco"] = df["Branco"].apply(lambda url: f'<img src="{url}" width="50" height="50">' if pd.notnull(url) else "")

    # Crie uma nova coluna "Sequência" que combina "Números" e "Horários"
    df["Sequência"] = '<div style="text-align: center">' + df["Números"].astype(str) + "<br>" + df["Horários"].astype(str) + '</div>'

    # Crie uma nova coluna "Brancos" que combina "Brancos" e "Horário"
    #df["Brancos"] = '<div style="text-align: center">' + df["Branco"].astype(str) + "<br>" + df["Horário"].astype(str) + '</div>'

    # Remova as colunas "Números", "Horários", "Brancos" e "Horário"
    df = df.drop(columns=["Números", "Horários"])

    # Reordene as colunas para que "Sequência" e "Brancos" sejam as primeiras
    df = df[["Sequência", "Branco 1"] + [col for col in df.columns if col not in ["Sequência", "Branco 1"]]]

    # Adicione a imagem acima do horário nas colunas "Branco 1" e "Branco 2"
    df["Branco 1"] = df["Branco 1"].apply(lambda x: f'<img src="./images/0.jpeg" width="50" height="50"><br>{x}' if ":" in x else x)
    df["Branco 2"] = df["Branco 2"].apply(lambda x: f'<img src="./images/0.jpeg" width="50" height="50"><br>{x}' if ":" in x else x)

    # Adicione a imagem acima do horário na coluna "Branco" Df2
    df["Branco"] = df["Branco"].apply(lambda x: f'<img src="./images/0.jpeg" width="50" height="50"><br>{x}' if ":" in x else x)

    # Adicione a imagem à coluna "Intervalo"
    #df["Intervalo"] = df["Intervalo"].apply(lambda x: f'<div style="position: relative; text-align: center;"><img src="D:\\pythonProject1\\images\\intervalo2.png" width="50" height="50"><span style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); color: black;">{x}</span></div>' if pd.notnull(x) else "")

    # Adicione a imagem à coluna "Intervalo" apenas se a célula estiver preenchida
    df["Intervalo"] = df["Intervalo"].apply(lambda x: f'<div style="position: relative; text-align: center;"><img src="./images/intervalo1.png" width="50" height="55"><span style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); color: black;">{x}</span></div>' if x != "" else "")

    # Adicione a imagem à coluna "frequencias" apenas se a célula estiver preenchida
    df["Frequências"] = df["Frequências"].apply(lambda x: f'<div style="position: relative; text-align: center;"><img src="./images/freq.png" width="50" height="55"><span style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); color: white;">{x}</span></div>' if x != "" else "")

    # Converta a coluna "Intervalos" para números, ignorando os erros
    df["Intervalos"] = pd.to_numeric(df["Intervalos"], errors='coerce')

    # Calcule o valor máximo da coluna "Intervalos" antes de fazer a substituição
    max_interval = df["Intervalos"].max()

    # Crie uma função para gerar o HTML para uma barra
    def create_bar(value, max_value):
        # Calcule a largura da barra como uma porcentagem do valor máximo
        # Ajuste a largura para que o valor mínimo seja 50% da largura máxima
        width = 10 + ((value - 1) / (max_value - 1)) * 90

        # Retorne o HTML para a barra e o valor
        return f'{int(value)}<div style="background-color:blue; width:{width}%; height:10px;"></div>'

    # Aplique a função à coluna "Intervalos" para criar as barras
    df["Intervalos"] = df["Intervalos"].apply(lambda x: create_bar(x, max_interval) if pd.notnull(x) else "")

    def increase_font(value):
        if value is not None:
            return f'<span style="font-size: 1.2em;">{value}</span>'
        else:
            return value

    df["Intervalo"] = df["Intervalo"].apply(increase_font)
    df["Intervalos"] = df["Intervalos"].apply(increase_font)
    df["Frequências"] = df["Frequências"].apply(increase_font)

    # Adicione uma nova coluna "Espaço" entre "Brancos" e "Branco 1"
    #df.insert(df.columns.get_loc("Brancos") + 1, " * ", [""] * len(df))


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



    # Defina a largura da coluna vazia
    #html = html.replace('<th> </th>', '<th style="width: 50px;"></th>')
    # Remova o cabeçalho da coluna "Espaço" e defina a largura da coluna
    #html = html.replace('<th>Espaço</th>', '<th style="width: 50px;"></th>')

    # Adicione o CSS ao HTML
    html = html.replace('<table', '<table style="margin-left: auto; margin-right: auto; border: 10px solid #1a242d; border-collapse: collapse;" border="1" class="dataframe"')
    html = html.replace('<th', '<th style="text-align: center; background-color: #282d37; color: white; font-size: 1em; font-weight: bold; border: 2px solid #1a242d; padding: 0;"')
    html = html.replace('<td', '<td style="width: 100px;text-align: center; background-color: #0f1923; color: white; font-size: 0.8em; font-weight: bold; border: 2px solid #1a242d; padding: 0;"')
    html = html.replace('<thead>', '<thead style="background-color: #282d37;">')
    html = html.replace('<td>', '<td style="background-color: #282d37;">')


    # Escreva o HTML em um arquivo
    with open("../output.html", "w") as f:
        f.write(html)

    webbrowser.open('../output.html')

if __name__ == "__main__":
    main()