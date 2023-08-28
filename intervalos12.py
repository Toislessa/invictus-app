from collections import Counter
import pandas as pd
import os
import asyncio
import aiohttp
from datetime import datetime, timedelta
from datetime import time as dt_time
import webbrowser
import time
from collections import OrderedDict
from datetime import datetime

from joblib import Parallel, delayed
start_time = time.time()  # Início da medição do tempo

async def fetch(session, url):
    async with session.get(url) as response:
        return await response.json()

async def main():
    print("Running intervalos.py")
    # Delete the output.html file if it exists
    if os.path.exists("output.html"):
        os.remove("output.html")
    total_pages = 12
    rolls = []  # Lista para armazenar os números
    times = []  # Lista para armazenar os horários
    zeros = []  # Lista para armazenar os zeros
    zeros_2 = []  # Lista para armazenar os zeros
    zero_times = []  # Lista para armazenar os horários dos zeros
    rolls_2 = []  # Lista para armazenar os números a partir das 22h do dia anterior
    times_2 = []  # Lista para armazenar os horários a partir das 22h do dia anterior
    zero_times_2 = []  # Lista para armazenar os horários dos zeros a partir das 22h do dia anterior
    intervals = []  # Lista para armazenar os intervalos entre os zeros
    interval_count = 0  # Contador para o intervalo atual entre os zeros
    first_zero_found = False  # Flag para indicar se o primeiro zero foi encontrado
    payers = []  # Lista para armazenar os números pagadores
    cycle_numbers = set(range(1, 15))  # Conjunto de números para um ciclo completo
    current_cycle_numbers = set()  # Conjunto de números para o ciclo atual
    cycle_count = 1  # Contador para o ciclo atual
    cycles = []  # Lista para armazenar o ciclo atual
    missing_numbers = []  # Lista para armazenar os números que faltam
    todas_as_listas_de_multiplos = []

    urls = ["https://blaze.com/api/roulette_games/history?page=" + str(page) for page in reversed(range(1, total_pages + 1))]

    semaphore = asyncio.Semaphore(12)  # limita o número de solicitações simultâneas a 5
    async with aiohttp.ClientSession() as session:
        tasks = []
        for url in urls:
            tasks.append(fetch(session, url))
        pages = await asyncio.gather(*tasks)

    for page in pages:
        resultados = reversed(page['records'])
        for resultado in resultados:
            roll = resultado['roll']
            roll_2 = resultado['roll']
            created_at = resultado['created_at']
            created_at_2 = resultado['created_at']

            created_at_datetime = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%S.%fZ")
            created_at_datetime_2 = datetime.strptime(created_at_2, "%Y-%m-%dT%H:%M:%S.%fZ")
            created_at_datetime = created_at_datetime - timedelta(hours=3)
            created_at_datetime_2 = created_at_datetime_2 - timedelta(hours=3)

            created_at_str = created_at_datetime.strftime("%H:%M")
            created_at_str_2 = created_at_datetime_2.strftime("%H:%M")

            # Verifique se o horário é após as 22h do dia anterior ou antes da hora atual do dia atual
            if (created_at_datetime_2.time() >= dt_time(22, 0) and created_at_datetime_2.date() == (
                    datetime.now() - timedelta(days=1)).date()) or (
                    created_at_datetime_2.time() <= datetime.now().time() and created_at_datetime_2.date() == datetime.now().date()):
                rolls_2.append(roll_2)
                created_at_str_2 = created_at_datetime_2.strftime("%H:%M")
                times_2.append(created_at_str_2)

            # Verifique se a data é a data atual
            if created_at_datetime.date() == datetime.now().date():
                rolls.append(roll)
                times.append(created_at_str)

            if roll == 0:
                if ((created_at_datetime_2.time() >= dt_time(22, 0) and created_at_datetime_2.date() == (
                        datetime.now() - timedelta(days=1)).date()) or (
                        created_at_datetime_2.time() < datetime.now().time() and created_at_datetime_2.date() == datetime.now().date())):
                    zeros_2.append(roll)
                    zero_times_2.append(created_at_str_2)
                    print(f"Zero encontrado em {created_at_str_2}")
                    multiplos_14 = []

                    # Adicione os múltiplos de 14 a esta lista
                    for i in range(14, 262, 14):
                        if created_at_str_2 is not None:  # Verifique se created_at_str_2 não é None
                            next_time = (datetime.strptime(created_at_str_2, "%H:%M") + timedelta(minutes=i)).strftime(
                                "%H:%M")
                            multiplos_14.append(next_time)

                    print(f"Lista de múltiplos criada para este zero: {multiplos_14}")

                    # Adicione esta lista de múltiplos à lista de todas as listas de múltiplos
                    todas_as_listas_de_multiplos.append(multiplos_14)



            if roll == 0 and created_at_datetime.date() == datetime.now().date():

                zeros.append(roll)
                zero_times.append(created_at_str)
                print(f"Zero encontrado em {created_at_str}")
                multiplos_14 = []

                cycles.append(f"Ciclo{cycle_count}")
                print(f"cycle_numbers:{cycle_numbers}")
                missing_numbers.append(list(cycle_numbers - current_cycle_numbers))
                print(f"current_cycle_numbers:{current_cycle_numbers}")
                print(f"missing_numbers:{missing_numbers}")

                if first_zero_found:
                    intervals.append(interval_count)
                interval_count = 0
                first_zero_found = True

                # Crie a "lista do zero"
                zero_list = [created_at_str,
                               (created_at_datetime - timedelta(minutes=1)).strftime("%H:%M"),
                               (created_at_datetime + timedelta(minutes=1)).strftime("%H:%M")]
                print(f"Lista do zero criada: {zero_list}")

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

    # ####################Nova análise de probabilidades
    zeros_indices = [i for i, roll_2 in enumerate(rolls_2) if roll_2 == 0]
    zeros_horarios = [times_2[i] for i in zeros_indices]

    zeros_numeros_antecessores = []
    zeros_numeros_sucessores = []

    for zero_index in zeros_indices:
        antecessores = []
        sucessores = []
        count = 0

        # Capturar os três números anteriores ao zero
        i = zero_index - 1
        while count < 3 and i >= 0:
            if rolls_2[i] != 0:  # note que aqui estamos comparando com o número 0, não a string '0'
                antecessores.append(rolls_2[i])
                count += 1
            i -= 1

        # Resetar o contador
        count = 0

        # Capturar os três números posteriores ao zero
        i = zero_index + 1
        while count < 3 and i < len(rolls_2):
            if rolls_2[i] != 0:  # note que aqui estamos comparando com o número 0, não a string '0'
                sucessores.append(rolls_2[i])
                count += 1
            i += 1

        zeros_numeros_antecessores.append(antecessores)
        zeros_numeros_sucessores.append(sucessores)
        #  Imprimir os antecessores e sucessores dos últimos 3 zeros
        print("Sucessores dos últimos 3 zeros: ", zeros_numeros_sucessores[-3:])

    # Garantir que nenhum zero esteja presente nos conjuntos de números antecessores e posteriores
    for i, numeros_antecessores in enumerate(zeros_numeros_antecessores):
        zeros_numeros_antecessores[i] = [num for num in numeros_antecessores if num != '0']
    for i, numeros_sucessores in enumerate(zeros_numeros_sucessores):
        zeros_numeros_sucessores[i] = [num for num in numeros_sucessores if num != '0']

    # Em caso de falta de três números anteriores ou posteriores, registrar os números disponíveis
    for i, numeros_antecessores in enumerate(zeros_numeros_antecessores):
        if len(numeros_antecessores) < 3:
            zeros_numeros_antecessores[i] = rolls_2[zero_index - len(numeros_antecessores):zero_index][
                                            ::-1] + numeros_antecessores[::-1]
    for i, numeros_sucessores in enumerate(zeros_numeros_sucessores):
        if len(numeros_sucessores) < 3:
            zeros_numeros_sucessores[i] = numeros_sucessores + rolls_2[zero_index + 1:zero_index + 1 + (
                    3 - len(numeros_sucessores))]

    # Não registrar o mesmo zero várias vezes se ocorrerem zeros com o mesmo horário
    zeros_indices_uniq = []
    zeros_horarios_uniq = []
    zeros_numeros_antecessores_uniq = []
    zeros_numeros_sucessores_uniq = []
    for i, horario in enumerate(zeros_horarios):
        if horario not in zeros_horarios_uniq:
            zeros_indices_uniq.append(zeros_indices[i])
            zeros_horarios_uniq.append(horario)
            zeros_numeros_antecessores_uniq.append(zeros_numeros_antecessores[i])
            zeros_numeros_sucessores_uniq.append(zeros_numeros_sucessores[i])

    # Inicializar a lista para armazenar os horários prováveis dos próximos zeros
    zeros_horarios_provaveis = []

    # Calcular as probabilidades e obter os horários prováveis dos próximos zeros
    for i in range(len(zeros_indices_uniq)):
        zero_horario = zeros_horarios_uniq[i]
        numeros_antecessores = zeros_numeros_antecessores_uniq[i]
        numeros_sucessores = zeros_numeros_sucessores_uniq[i]

        # Verificar se a sequência de números antes tem menos de 3 números
        if len(numeros_antecessores) < 3:
            numeros_antecessores = ['0'] * (3 - len(numeros_antecessores)) + numeros_antecessores

        # Verificar se a sequência de números depois tem menos de 3 números
        if len(numeros_sucessores) < 3:
            numeros_sucessores = numeros_sucessores + ['0'] * (3 - len(numeros_sucessores))

        # Calcular as probabilidades
        probabilidades = []

        # Calcular as probabilidades
        probabilidades = []

        # Calcular as probabilidades
        probabilidades = []

        # Função para ajustar as horas e minutos
        def ajustar_horario(horas, minutos):
            horas += minutos // 60
            minutos = minutos % 60
            return horas % 24, minutos

        probabilidades.append(
                f"{ajustar_horario(int(zero_horario.split(':')[0]), int(zero_horario.split(':')[1]) + int(numeros_antecessores[0]))[0]:02d}:{ajustar_horario(int(zero_horario.split(':')[0]), int(zero_horario.split(':')[1]) + int(numeros_antecessores[0]))[1]:02d}")
        probabilidades.append(
                f"{ajustar_horario(int(zero_horario.split(':')[0]), int(zero_horario.split(':')[1]) + int(numeros_antecessores[1]))[0]:02d}:{ajustar_horario(int(zero_horario.split(':')[0]), int(zero_horario.split(':')[1]) + int(numeros_antecessores[1]))[1]:02d}")
        probabilidades.append(
                f"{ajustar_horario(int(zero_horario.split(':')[0]), int(zero_horario.split(':')[1]) + int(numeros_sucessores[0]))[0]:02d}:{ajustar_horario(int(zero_horario.split(':')[0]), int(zero_horario.split(':')[1]) + int(numeros_sucessores[0]))[1]:02d}")
        probabilidades.append(
                f"{ajustar_horario(int(zero_horario.split(':')[0]), int(zero_horario.split(':')[1]) + int(numeros_sucessores[1]))[0]:02d}:{ajustar_horario(int(zero_horario.split(':')[0]), int(zero_horario.split(':')[1]) + int(numeros_sucessores[1]))[1]:02d}")
        probabilidades.append(
                f"{ajustar_horario(int(zero_horario.split(':')[0]), int(zero_horario.split(':')[1]) + int(numeros_antecessores[0]) + int(numeros_antecessores[1]))[0]:02d}:{ajustar_horario(int(zero_horario.split(':')[0]), int(zero_horario.split(':')[1]) + int(numeros_antecessores[0]) + int(numeros_antecessores[1]))[1]:02d}")
        probabilidades.append(
                f"{ajustar_horario(int(zero_horario.split(':')[0]), int(zero_horario.split(':')[1]) + int(numeros_antecessores[0]) + int(numeros_sucessores[0]))[0]:02d}:{ajustar_horario(int(zero_horario.split(':')[0]), int(zero_horario.split(':')[1]) + int(numeros_antecessores[0]) + int(numeros_sucessores[0]))[1]:02d}")
        probabilidades.append(
                f"{ajustar_horario(int(zero_horario.split(':')[0]), int(zero_horario.split(':')[1]) + int(numeros_antecessores[0]) + int(numeros_sucessores[1]))[0]:02d}:{ajustar_horario(int(zero_horario.split(':')[0]), int(zero_horario.split(':')[1]) + int(numeros_antecessores[0]) + int(numeros_sucessores[1]))[1]:02d}")
        probabilidades.append(
                f"{ajustar_horario(int(zero_horario.split(':')[0]), int(zero_horario.split(':')[1]) + int(numeros_antecessores[1]) + int(numeros_sucessores[0]))[0]:02d}:{ajustar_horario(int(zero_horario.split(':')[0]), int(zero_horario.split(':')[1]) + int(numeros_antecessores[1]) + int(numeros_sucessores[0]))[1]:02d}")
        probabilidades.append(
                f"{ajustar_horario(int(zero_horario.split(':')[0]), int(zero_horario.split(':')[1]) + int(numeros_antecessores[1]) + int(numeros_sucessores[1]))[0]:02d}:{ajustar_horario(int(zero_horario.split(':')[0]), int(zero_horario.split(':')[1]) + int(numeros_antecessores[1]) + int(numeros_sucessores[1]))[1]:02d}")
        probabilidades.append(
                f"{ajustar_horario(int(zero_horario.split(':')[0]), int(zero_horario.split(':')[1]) + int(numeros_sucessores[0]) + int(numeros_sucessores[1]))[0]:02d}:{ajustar_horario(int(zero_horario.split(':')[0]), int(zero_horario.split(':')[1]) + int(numeros_sucessores[0]) + int(numeros_sucessores[1]))[1]:02d}")
        probabilidades.append(
                f"{ajustar_horario(int(zero_horario.split(':')[0]), int(zero_horario.split(':')[1]) + int(numeros_antecessores[0]) + int(numeros_antecessores[1]) + int(numeros_sucessores[0]))[0]:02d}:{ajustar_horario(int(zero_horario.split(':')[0]), int(zero_horario.split(':')[1]) + int(numeros_antecessores[0]) + int(numeros_antecessores[1]) + int(numeros_sucessores[0]))[1]:02d}")
        probabilidades.append(
                f"{ajustar_horario(int(zero_horario.split(':')[0]), int(zero_horario.split(':')[1]) + int(numeros_antecessores[0]) + int(numeros_antecessores[1]) + int(numeros_sucessores[1]))[0]:02d}:{ajustar_horario(int(zero_horario.split(':')[0]), int(zero_horario.split(':')[1]) + int(numeros_antecessores[0]) + int(numeros_antecessores[1]) + int(numeros_sucessores[1]))[1]:02d}")
        probabilidades.append(
                f"{ajustar_horario(int(zero_horario.split(':')[0]), int(zero_horario.split(':')[1]) + int(numeros_antecessores[1]) + int(numeros_sucessores[0]) + int(numeros_sucessores[1]))[0]:02d}:{ajustar_horario(int(zero_horario.split(':')[0]), int(zero_horario.split(':')[1]) + int(numeros_antecessores[1]) + int(numeros_sucessores[0]) + int(numeros_sucessores[1]))[1]:02d}")
        probabilidades.append(
                f"{ajustar_horario(int(zero_horario.split(':')[0]), int(zero_horario.split(':')[1]) + int(numeros_antecessores[0]) + int(numeros_sucessores[0]) + int(numeros_sucessores[1]))[0]:02d}:{ajustar_horario(int(zero_horario.split(':')[0]), int(zero_horario.split(':')[1]) + int(numeros_antecessores[0]) + int(numeros_sucessores[0]) + int(numeros_sucessores[1]))[1]:02d}")
        probabilidades.append(
                f"{ajustar_horario(int(zero_horario.split(':')[0]), int(zero_horario.split(':')[1]) + int(numeros_antecessores[0]) + int(numeros_antecessores[1]) + int(numeros_sucessores[0]) + int(numeros_sucessores[1]))[0]:02d}:{ajustar_horario(int(zero_horario.split(':')[0]), int(zero_horario.split(':')[1]) + int(numeros_antecessores[0]) + int(numeros_antecessores[1]) + int(numeros_sucessores[0]) + int(numeros_sucessores[1]))[1]:02d}")
        probabilidades.append(
                f"{ajustar_horario(int(zero_horario.split(':')[0]), int(zero_horario.split(':')[1]) + int(numeros_antecessores[0]) + int(numeros_antecessores[1]) + int(numeros_sucessores[0]) + int(numeros_sucessores[1]) + int(numeros_antecessores[2]))[0]:02d}:{ajustar_horario(int(zero_horario.split(':')[0]), int(zero_horario.split(':')[1]) + int(numeros_antecessores[0]) + int(numeros_antecessores[1]) + int(numeros_sucessores[0]) + int(numeros_sucessores[1]) + int(numeros_antecessores[2]))[1]:02d}")
        probabilidades.append(
                f"{ajustar_horario(int(zero_horario.split(':')[0]), int(zero_horario.split(':')[1]) + int(numeros_antecessores[0]) + int(numeros_antecessores[1]) + int(numeros_sucessores[0]) + int(numeros_sucessores[1]) + int(numeros_sucessores[2]))[0]:02d}:{ajustar_horario(int(zero_horario.split(':')[0]), int(zero_horario.split(':')[1]) + int(numeros_antecessores[0]) + int(numeros_antecessores[1]) + int(numeros_sucessores[0]) + int(numeros_sucessores[1]) + int(numeros_sucessores[2]))[1]:02d}")
        probabilidades.append(
                f"{ajustar_horario(int(zero_horario.split(':')[0]), int(zero_horario.split(':')[1]) + int(numeros_antecessores[0]) + int(numeros_antecessores[1]) + int(numeros_sucessores[0]) + int(numeros_sucessores[1]) + int(numeros_sucessores[2]) + int(numeros_antecessores[2]))[0]:02d}:{ajustar_horario(int(zero_horario.split(':')[0]), int(zero_horario.split(':')[1]) + int(numeros_antecessores[0]) + int(numeros_antecessores[1]) + int(numeros_sucessores[0]) + int(numeros_sucessores[1]) + int(numeros_sucessores[2]) + int(numeros_antecessores[2]))[1]:02d}")

        # Armazenar os horários prováveis na lista geral
        zeros_horarios_provaveis.append(probabilidades)

        # Exibir as informações na saída
    for i, indice in enumerate(zeros_indices_uniq):
        print(f"Branco: {zeros_horarios_uniq[i]}")
        print(f"Números antes: {', '.join(map(str, zeros_numeros_antecessores_uniq[i]))}")
        print(f"Números depois: {', '.join(map(str, zeros_numeros_sucessores_uniq[i]))}")
        print("Horários prováveis:")
        for j, horario_provavel in enumerate(zeros_horarios_provaveis[i]):
            print(f"E{j + 1} - {horario_provavel}")
        print()
    # INICIO DE CRIA O DF 3 COM AS PERNAS DOS BRANCOS

    # Inicialize uma lista vazia para armazenar os dados do DataFrame
    df3_data = []
    df4_data = []
    # Itere sobre os índices únicos dos zeros
    for i, indice in enumerate(zeros_indices_uniq[-5:]):  # Pegue apenas os últimos 10 zeros
        # Inicialize um dicionário vazio para armazenar os dados da linha atual
        row_data = {}
        # Adicione o horário do zero à coluna 'Branco'
        row_data['Branco'] = zeros_horarios_uniq[-5:][i]  # Pegue apenas os últimos 10 horários de zeros
        # Adicione os horários prováveis às colunas 'E1' a 'E18'
        for j, horario_provavel in enumerate(
                zeros_horarios_provaveis[-5:][i]):  # Pegue apenas os últimos 10 horários prováveis
            row_data[f'E{j + 1}'] = horario_provavel
        # Adicione os dados da linha à lista de dados do DataFrame
        df3_data.append(row_data)
        df4_data.append(row_data)
    # Crie o DataFrame 'df3' a partir da lista de dados
    df3 = pd.DataFrame(df3_data)
    df4 = pd.DataFrame(df4_data)

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

    max_len = max(len(rolls), len(times), len(zero_times), len(zero_times_2), len(intervals), len(branco_2),
                  len(intervalos), len(frequencias), len(rolls_2), len(times_2))

    rolls += [None] * (max_len - len(rolls))
    times += [None] * (max_len - len(times))
    zero_times += [None] * (max_len - len(zero_times))
    zero_times_2 += [None] * (max_len - len(zero_times_2))  # Adicione esta linha
    intervals += [None] * (max_len - len(intervals))
    branco_2 += [None] * (max_len - len(branco_2))
    intervalos += [None] * (max_len - len(intervalos))
    frequencias += [None] * (max_len - len(frequencias))
    rolls_2 += [None] * (max_len - len(rolls_2))  # Adicione esta linha
    times_2 += [None] * (max_len - len(times_2))  # Adicione esta linha

    df1 = pd.DataFrame({
        "Números": rolls,
        "Horários": times,
        "Branco 1": zero_times,
        "Casas": intervals,
        "Branco 2": branco_2,
        "Casas Ordem": intervalos,
        "Número de Vezes": frequencias,
    })

    # Preencha as listas mais curtas com None até que todas as listas tenham o mesmo comprimento
    max_len = max(len(zero_times),len(zero_times_2),len(payers), len(cycles), len(missing_numbers))
    zero_times += [None] * (max_len - len(zero_times))
    zero_times_2 += [None] * (max_len - len(zero_times_2))
    payers += [None] * (max_len - len(payers))
    cycles += [None] * (max_len - len(cycles))
    missing_numbers += [None] * (max_len - len(missing_numbers))

    df2 = pd.DataFrame({

        "Pagador": payers,
        "Ciclo": cycles,
        "Falta Pagar": missing_numbers,
        "Branco": zero_times_2,
    })

    df2['Linha'] = range(1, len(df2) + 1)

    def get_ith_multiple(multiplos, i):
        try:
            return multiplos[i]
        except IndexError:
            return None

    # Adicione as colunas "224" a "14" ao DataFrame df2
    for i in range(14, 262, 14):  # Altere 197 para 226
        # Crie uma lista para armazenar os valores da coluna atual
        col_values = [get_ith_multiple(multiplos, i // 14 - 1) for multiplos in todas_as_listas_de_multiplos]

        # Garanta que a lista col_values tenha o mesmo comprimento que o número de linhas no DataFrame df2
        if len(col_values) > max_len:
            col_values = col_values[:max_len]
        else:
            col_values += [None] * (max_len - len(col_values))

        # Adicione a lista col_values como uma nova coluna no DataFrame df2
        df2[str(i)] = col_values
        print(f"Coluna {i} adicionada ao DataFrame com valores: {col_values}")

    # Concatene os dois DataFrames horizontalmente
    df = pd.concat([df1, df2], axis=1)

    print(f"zero_times: {zero_times}")
    print(f"zero_times_2: {zero_times_2}")

    def color_column(val):
        color = '#1a242d'
        return 'background-color: %s' % color

    styled = df.style.applymap(color_column, subset=['Linha'])

    def adjust_time(hour, minute):
        hour += minute // 60
        minute = minute % 60
        return hour % 24, minute

    def get_time_shifted(time_str, shift):
        if time_str is None:
            return None
        time_format = "%H:%M"
        dt = datetime.strptime(time_str, time_format)
        shifted_time = dt + timedelta(minutes=shift)
        return shifted_time.strftime(time_format)

    df['multiplos'] = df[df.columns[12:30]].apply(lambda x: ','.join(x.dropna().astype(str)), axis=1)
    df['multiplos'] = df['multiplos'].apply(lambda x: x.split(','))

# (Filtro) Compara os horários provaveis de df3 com os horários das colunas de multiplos
    horarios_provaveis = [horario for sublist in zeros_horarios_provaveis[-5:] for horario in sublist][-80:]
    multiples_of_14_cols = list(range(14, 262, 14))

    def process_row(row):
        total_correspondentes = 0  # Contador para horários correspondentes
        for horario in horarios_provaveis:
            hora, minuto = map(int, horario.split(':'))
            for ajuste in [-1, 0, 1]:
                hora_ajustada, minuto_ajustado = adjust_time(hora, minuto + ajuste)
                horario_ajustado = f"{hora_ajustada:02d}:{minuto_ajustado:02d}"
                if row == horario_ajustado:
                    total_correspondentes += 1  # Incrementa o contador
        if total_correspondentes:  # Se o contador não for zero
            return f"{row} Total: {total_correspondentes}"  # Adiciona o total de horários correspondentes à célula
        else:
            return row

    for col in multiples_of_14_cols:
        df[str(col)] = Parallel(n_jobs=-1)(delayed(process_row)(row) for row in df[str(col)])
# FIM (Filtro) Compara os horários provaveis de df3 com os horários das colunas de multiplos

# Inicio Colocar "P" nos multiplos de 14
    index_to_column = {i: str(14 * (i + 1)) for i in range(252 // 14)}
    previous_time = None

    previous_zero_time = None  # Inicialize a variável fora do loop

    for i, row in df.iterrows():
        print(f"Processando linha {i}...")
        if row['Branco'] is not None and "P" not in row['multiplos']:
            print(f"  multiplos: {row['multiplos']}")
            if previous_zero_time == row['Branco']:
                df.at[i, 'multiplos'] = ["DUPLO" for _ in row['multiplos']]  # Substitua todos os horários por "DUPLO"
                for column in index_to_column.values():  # Substitua os valores correspondentes nas colunas de múltiplos de 14 por "DUPLO"
                    df.at[i, column] = "DUPLO"
                continue  # Se o horário do zero correspondente for igual ao horário do zero anterior, pule para a próxima iteração
            previous_zero_time = row['Branco']  # Atualize o horário do zero anterior
            previous_time = row['Branco']
            for j, multiplos in df['multiplos'].items():
                print(f"  Processando célula {j}...")
                if any("P" in multiplo for multiplo in multiplos) or j > i:
                    continue
                found = False
                for shift, label in [(0, 'Lata'), (-1, 'Depois'), (1, 'Antes')]:
                    zero_time_2 = get_time_shifted(row['Branco'], shift)
                    print(f"  Verificando zero_time: {zero_time_2}")
                    if zero_time_2 in multiplos:
                        print(f"  Encontrado {zero_time_2} em multiplos!")
                        df.at[i, 'Branco'] = f"P {row['Branco']} {label} Linha {j + 1}"
                        zero_time_index = multiplos.index(zero_time_2)
                        column = index_to_column[zero_time_index]
                        df.at[j, column] = f"P {df.at[j, column]} {label}"
                        df.at[j, 'multiplos'] = [f"P {multiplo} {label}" if multiplo == zero_time_2 else multiplo for
                                                 multiplo in multiplos]
                        found = True
                        break
                if found:
                    break

    # Fim coloca "P" nos multiplos

# inicio gerar df4
    # Crie um OrderedDict para armazenar os horários
    horarios_sem_p = OrderedDict()

    hora_atual = datetime.now().time()  # obtenha a hora atual
    uma_hora_depois = (datetime.now() + timedelta(hours=1)).time()  # obtenha a hora que será uma hora a partir de agora

    for i, row in df.iterrows():
        print(f"Processando linha {i}...")
        # Verifique se "P" está em algum lugar da lista de horários
        if any("P" in multiplo for multiplo in row['multiplos']):
            continue  # Se "P" estiver presente, ignore esta linha
        print(f"  multiplos: {row['multiplos']}")
        # Adicione os horários sem "P" ao OrderedDict se eles forem a partir da hora atual e dentro de uma hora
        for multiplo in row['multiplos']:
            hora_multiplo = datetime.strptime(multiplo, "%H:%M").time() if multiplo else None
            if hora_multiplo and hora_atual <= hora_multiplo <= uma_hora_depois:
                horarios_sem_p[multiplo] = None

    # Converta o OrderedDict em uma lista e ordene-a
    horarios_sem_p = sorted(list(horarios_sem_p.keys()), key=lambda x: datetime.strptime(x, '%H:%M'))

    # Crie um DataFrame vazio com os horários como cabeçalhos
    # df4 = pd.DataFrame(columns=horarios_sem_p)
    # Adicione 'Horarios' no início da lista de colunas
    horarios_sem_p.insert(0, 'Horarios')
    # Reindexe o DataFrame para ter as novas colunas
    df4 = df4.reindex(columns=horarios_sem_p)
    # Substitua NaN por uma string vazia
    df4.fillna('', inplace=True)
    # Adicione valores à coluna "Horarios"
    df4.at[0, 'Horarios'] = 'Lin/Col'
    df4.at[1, 'Horarios'] = 'Branco1'
    df4.at[2, 'Horarios'] = 'Branco2'
    df4.at[3, 'Horarios'] = 'Falso'
    df4.at[4, 'Horarios'] = 'Total'
# fim gerar df4

    df = df.drop(columns=['multiplos'])

    # Crie um dicionário para mapear os números às imagens
    image_dict = {
        0: "./static/0.jpeg",
        1: "./static/1.jpeg",
        2: "./static/2.jpeg",
        3: "./static/3.jpeg",
        4: "./static/4.jpeg",
        5: "./static/5.jpeg",
        6: "./static/6.jpeg",
        7: "./static/7.jpeg",
        8: "./static/8.jpeg",
        9: "./static/9.jpeg",
        10: "./static/10.jpeg",
        11: "./static/11.jpeg",
        12: "./static/12.jpeg",
        13: "./static/13.jpeg",
        14: "./static/14.jpeg",
    }
    # Substitua os números na coluna "Números" pelas imagens correspondentes
    df["Números"] = df["Números"].map(image_dict)
    # Substitua NaN por uma string vazia
    df.fillna("", inplace=True)
    # Tente converter as colunas para inteiros apenas para a visualização
    for col in [3, 5, 6]:  # Colunas C, E, F
        # df.iloc[:, col] = df.iloc[:, col].apply(lambda x: int(x) if isinstance(x, str) and x.isdigit() else x)
        df.iloc[:, col] = df.iloc[:, col].apply(lambda x: int(x) if x != "" else x)

    for col in [8]:  # Colunas C, E, F
        df.iloc[:, col] = df.iloc[:, col].apply(lambda x: int(x) if isinstance(x, str) and x.isdigit() else x)
        # df.iloc[:, col] = df.iloc[:, col].apply(lambda x: int(x) if x != "" else x)
    # Substitua as URLs das imagens por tags de imagem HTML
    df["Números"] = df["Números"].apply(lambda url: f'<img src="{url}" width="50" height="50">')
    # Substitua "F" pela imagem desejada
    df["Pagador"] = df["Pagador"].apply(lambda x: f'<div style="position: relative; text-align: center;"><img src="./static/ciclo2.png" width="45" height=45"><span style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); color: white;">{x[:-1]}</span></div>' if isinstance(x, str) and x.endswith("F") else x)

    # Crie uma nova coluna "Sequência" que combina "Números" e "Horários"
    df["Sequência"] = '<div style="text-align: center">' + df["Números"].astype(str) + "<br>" + df["Horários"].astype(
        str) + '</div>'

    # Remova as colunas "Números", "Horários", "Brancos" e "Horário"
    df = df.drop(columns=["Números", "Horários"])

    # Reordene as colunas para que "Sequência" e "Brancos" sejam as primeiras
    df = df[["Sequência", "Branco 1"] + [col for col in df.columns if col not in ["Sequência", "Branco 1"]]]

    # Adicione a imagem acima do horário nas colunas "Branco 1" e "Branco 2"
    df["Branco 1"] = df["Branco 1"].apply(
        lambda x: f'<img src="./static/0.jpeg" width="50" height="50"><br>{x}' if ":" in x else x)
    df["Branco 2"] = df["Branco 2"].apply(
        lambda x: f'<img src="./static/0.jpeg" width="50" height="50"><br>{x}' if ":" in x else x)

    # Adicione a imagem acima do horário na coluna "Branco" Df2
    df["Branco"] = df["Branco"].apply(
        lambda x: f'<img src="./static/pago3.jpeg" width="50" height="50"><br>{x.replace("P ", "")}' if "P" in x else (
            f'<img src="./static/0.jpeg" width="50" height="50"><br>{x}' if ":" in x else x))

    # Adicione a imagem à coluna "Intervalo" apenas se a célula estiver preenchida
    df["Casas"] = df["Casas"].apply(lambda
                                        x: f'<div style="position: relative; text-align: center;"><img src="./static/intervalo1.png" width="50" height="55"><span style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); color: black;">{x}</span></div>' if x != "" else "")

    # Adicione a imagem à coluna "frequencias" apenas se a célula estiver preenchida
    df["Número de Vezes"] = df["Número de Vezes"].apply(lambda
                                                            x: f'<div style="position: relative; text-align: center;"><img src="./static/freq.png" width="50" height="55"><span style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); color: white;">{x}</span></div>' if x != "" else "")

    # Cria uma lista com os nomes das colunas
    columns = [str(i) for i in range(14, 262, 14)]  # Cria uma lista com os nomes das colunas
    for column in columns:
        df[column] = df[column].apply(lambda
                                          x: f'<div style="text-align: center;"><img src="./static/pago.png" width="20" height="20"><br><div>{x[2:]}</div></div>' if isinstance(
            x, str) and x.startswith('P ') else x)


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
    df["Número de Vezes"] = df["Número de Vezes"].apply(increase_font)

    # Defina uma função para adicionar o estilo CSS
    def add_style(cell):
        if cell == "&nbsp;":
            return 'background-color: #808080;'  # Use qualquer cor em hexadecimal que você quiser
        else:
            return ''

    # Aplique a função de estilo à coluna vazia
    df_styled = df.style.applymap(add_style, subset=pd.IndexSlice[:, [' ']])

    # Gere o HTML do DataFrame df sem o índice
    html_df = df.to_html(index=False, escape=False)

    # Gere o HTML do DataFrame df3 sem o índice e adicione um ID
    html_df3 = df3.to_html(index=False, escape=False)
    html_df3 = f'<div id="df3" style="display: block;">{html_df3}</div>'

    # Gere o HTML do DataFrame df4 sem o índice e adicione um ID
    html_df4 = df4.to_html(index=False, escape=False)
    html_df4 = f'<div id="df4" style="display: none;">{html_df4}</div>'

    # Adicione o botão de alternância ao HTML
    toggle_button = """
    <div class="switch-container">
      <span class="switch-label">Exibir Horarios que faltam pagar</span>
      <div class="switch">
        <input type="checkbox" onclick="toggleDf()" id="toggle">
        <label for="toggle" class="slider round"></label>
      </div>
    </div>
    """

    # Em seguida, substitua o nome da coluna "E1" por uma tag de imagem HTML
    html_df3 = html_df3.replace('>E1<', '><img src="./static/E1.png" width="100%" height="100%" /><')
    html_df3 = html_df3.replace('>E2<', '><img src="./static/E2.png" width="100%" height="100%" /><')
    html_df3 = html_df3.replace('>E3<', '><img src="./static/E3.png" width="100%" height="100%" /><')
    html_df3 = html_df3.replace('>E4<', '><img src="./static/E4.png" width="100%" height="100%" /><')
    html_df3 = html_df3.replace('>E5<', '><img src="./static/E5.png" width="100%" height="100%" /><')
    html_df3 = html_df3.replace('>E6<', '><img src="./static/E6.png" width="100%" height="100%" /><')
    html_df3 = html_df3.replace('>E7<', '><img src="./static/E7.png" width="100%" height="100%" /><')
    html_df3 = html_df3.replace('>E8<', '><img src="./static/E8.png" width="100%" height="100%" /><')
    html_df3 = html_df3.replace('>E9<', '><img src="./static/E9.png" width="100%" height="100%" /><')
    html_df3 = html_df3.replace('>E10<', '><img src="./static/E10.png" width="100%" height="100%" /><')
    html_df3 = html_df3.replace('>E11<', '><img src="./static/E11.png" width="100%" height="100%" /><')
    html_df3 = html_df3.replace('>E12<', '><img src="./static/E12.png" width="100%" height="100%" /><')
    html_df3 = html_df3.replace('>E13<', '><img src="./static/E13.png" width="100%" height="100%" /><')
    html_df3 = html_df3.replace('>E14<', '><img src="./static/E14.png" width="100%" height="100%" /><')
    html_df3 = html_df3.replace('>E15<', '><img src="./static/E15.png" width="100%" height="100%" /><')
    html_df3 = html_df3.replace('>E16<', '><img src="./static/E16.png" width="100%" height="100%" /><')
    html_df3 = html_df3.replace('>E17<', '><img src="./static/E17.png" width="100%" height="100%" /><')
    html_df3 = html_df3.replace('>E18<', '><img src="./static/E18.png" width="100%" height="100%" /><')

    # Concatene o HTML de df3, df4, o botão de alternância e df
    # Concatene o HTML de df3, df4, o botão de alternância e df
    html = f'<div style="overflow:auto; height:auto;">{toggle_button}{html_df3}{html_df4}</div><div style="overflow:auto; height:74vh;">{html_df}</div>'

    # Adicione o CSS ao HTML
    html = html.replace('<table',
                        '<table style="margin-left: auto; margin-right: auto; border: 10px solid #1a242d; border-collapse: collapse;" border="1" class="dataframe"')
    html = html.replace('<th',
                        '<th style="text-align: center; background-color: #282d37; color: white; font-size: 1em; font-weight: bold; border: 2px solid #1a242d; padding: 0;"')
    html = html.replace('<td',
                        '<td style="width: 80px;text-align: center; background-color: #0f1923; color: white; font-size: 1em; font-weight: bold; border: 2px solid #1a242d; padding: 0;"')
    html = html.replace('<thead>', '<thead style="background-color: #282d37;">')
    html = html.replace('<td>', '<td style="background-color: #282d37;">')

    # Adicione a declaração do charset UTF-8
    html = '<!DOCTYPE html>\n<html>\n<head>\n<meta charset="UTF-8">\n</head>\n<body>\n' + html

    # Adicione o código JavaScript ao HTML
    html += """
    
    
    <script>
    // Quando a página é carregada, restaure a posição de rolagem
    window.onload = function() {
        var scrollPosition = sessionStorage.getItem('scrollPosition');
        if (scrollPosition) {
            window.scrollTo(0, scrollPosition);
        }
        fetch('http://127.0.0.1:5000/delete_output', {
            method: 'POST',
        })
        .then(response => response.text())
        .then(data => console.log(data))
        .catch((error) => {
            console.error('Error:', error);
        });
    };

    // Antes da página ser descarregada, armazene a posição de rolagem
    window.onbeforeunload = function() {
        var scrollPosition = window.pageYOffset || document.documentElement.scrollTop;
        sessionStorage.setItem('scrollPosition', scrollPosition);
    };
    
    var df3Visible = true;

function toggleDf() {
    if (df3Visible) {
        document.getElementById('df3').style.display = 'none';
        document.getElementById('df4').style.display = 'block';
    } else {
        document.getElementById('df3').style.display = 'block';
        document.getElementById('df4').style.display = 'none';
    }
    df3Visible = !df3Visible;
}    
    </script>
    """

    # Adicione o CSS do botão de alternância ao HTML
    html += """
    <style>
    .switch-container {
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 10px;
      background-color: #282d37;  /* Adicione esta linha */
      color: white;  /* Adicione esta linha */
    }

    .switch-label {
      margin-right: 10px;
    }

    .switch {
      position: relative;
      display: inline-block;
      width: 30px;  /* Reduzido pela metade */
      height: 17px;  /* Reduzido pela metade */
    }

    .switch input {
      opacity: 0;
      width: 0;
      height: 0;
    }

    .slider {
      position: absolute;
      cursor: pointer;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background-color: #ccc;
      -webkit-transition: .4s;
      transition: .4s;
    }

    .slider:before {
      position: absolute;
      content: "";
      height: 13px;  /* Reduzido pela metade */
      width: 13px;  /* Reduzido pela metade */
      left: 2px;  /* Reduzido pela metade */
      bottom: 2px;  /* Reduzido pela metade */
      background-color: white;
      -webkit-transition: .4s;
      transition: .4s;
    }

    input:checked + .slider {
      background-color: #2196F3;
    }

    input:focus + .slider {
      box-shadow: 0 0 1px #2196F3;
    }

    input:checked + .slider:before {
      -webkit-transform: translateX(13px);  /* Reduzido pela metade */
      -ms-transform: translateX(13px);  /* Reduzido pela metade */
      transform: translateX(13px);  /* Reduzido pela metade */
    }

    .slider.round {
      border-radius: 17px;  /* Reduzido pela metade */
    }

    .slider.round:before {
      border-radius: 50%;
    }
    </style>
    """

    # Escreva o HTML em um arquivo
    with open("output.html", "w") as f:
        f.write(html)
    webbrowser.open('output.html')

if __name__ == "__main__":
    asyncio.run(main())

end_time = time.time()  # Fim da medição do tempo
print(f"Tempo total de execução: {end_time - start_time} segundos")
