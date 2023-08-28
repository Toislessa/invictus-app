from collections import Counter
import pandas as pd
import os
import asyncio
import aiohttp
from datetime import time as dt_time
import time
from collections import OrderedDict
from datetime import datetime, timedelta, date
from joblib import Parallel, delayed

start_time = time.time()  # Início da medição do tempo

async def fetch(session, url):
    async with session.get(url) as response:
        return await response.json()

def read_current_result():
    try:
        with open('current_result.txt', 'r') as file:
            result = file.readline().strip().split(',')
            return int(result[0]), result[1]
    except:
        return None

async def main():
    print("Running intervalos13. Aguarde.....")
    # Delete the output.html file if it exists
    if os.path.exists("output1.html"):
        os.remove("output1.html")
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
    sequence = []
    sequence_2 = []
    sequence_3 = []
    urls = ["https://blaze.com/api/roulette_games/history?page=" + str(page) for page in
            reversed(range(1, total_pages + 1))]

    semaphore = asyncio.Semaphore(12)  # limita o número de solicitações simultâneas a 5
    async with aiohttp.ClientSession() as session:
        tasks = []
        for url in urls:
            tasks.append(fetch(session, url))
        pages = await asyncio.gather(*tasks)
    current_result_added = False  # Variável para controlar se o current_result já foi adicionado
    current_result_added2 = False
    for page_index, page in enumerate(pages):
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
                sequence_2.append((roll_2, created_at_str_2, created_at_datetime_2))

            # Verifique se a data é a data atual
            if created_at_datetime.date() == datetime.now().date():
                rolls.append(roll)
                times.append(created_at_str)
                sequence.append((roll, created_at_str, created_at_datetime))

    current_result = read_current_result()
    if current_result:
        rolls.reverse()
        rolls_2.reverse()
        times.reverse()
        times_2.reverse()
        rolls_2.insert(0,current_result[0])
        times_2.insert(0,current_result[1])
        rolls.insert(0,current_result[0])
        times.insert(0,current_result[1])
        rolls.reverse()
        rolls_2.reverse()
        times.reverse()
        times_2.reverse()

    for roll_2, created_at_str_2, created_at_datetime_2 in sequence_2:

        if roll_2 == 0:
            if ((created_at_datetime_2.time() >= dt_time(22, 0) and created_at_datetime_2.date() == (
                    datetime.now() - timedelta(days=1)).date()) or (
                    created_at_datetime_2.time() < datetime.now().time() and created_at_datetime_2.date() == datetime.now().date())):
                zeros_2.append(roll_2)
                zero_times_2.append(created_at_str_2)
                multiplos_14 = []

                # Adicione os múltiplos de 14 a esta lista
                for i in range(14, 262, 14):
                    if created_at_str_2 is not None:  # Verifique se created_at_str_2 não é None
                        next_time = (datetime.strptime(created_at_str_2, "%H:%M") + timedelta(minutes=i)).strftime(
                            "%H:%M")
                        multiplos_14.append(next_time)

                # Adicione esta lista de múltiplos à lista de todas as listas de múltiplos
                todas_as_listas_de_multiplos.append(multiplos_14)
    for index, (roll, created_at_str, created_at_datetime) in enumerate(sequence):
        if roll == 0 and created_at_datetime.date() == datetime.now().date():
            zeros.append(roll)
            zero_times.append(created_at_str)
            multiplos_14 = []
            cycles.append(f"Ciclo{cycle_count}")
            missing_numbers.append(list(cycle_numbers - current_cycle_numbers))

            if first_zero_found:
                intervals.append(interval_count)
            interval_count = 0
            first_zero_found = True

            # Crie a "lista do zero"
            zero_list = [created_at_str,
                         (created_at_datetime - timedelta(minutes=1)).strftime("%H:%M"),
                         (created_at_datetime + timedelta(minutes=1)).strftime("%H:%M")]
            # print(f"Lista do zero criada: {zero_list}")

            if index > 0 :  # Obtenha o pagador imediatamente antes do zero atual
                last_payer = rolls[index - 1]
            else:
                last_payer = " "
            payers.append(last_payer)
            if last_payer != " ":
                current_cycle_numbers.add(last_payer)  # Adicione o número pagador a current_cycle_numbers aqui

            if cycle_numbers.issubset(current_cycle_numbers):
                last_payer = str(last_payer) + "F"
                payers[-1] = last_payer
                current_cycle_numbers = set()  # Reinicie current_cycle_numbers aqui
                cycle_count += 1  # Incrementa o contador de ciclos

        elif first_zero_found:
            interval_count += 1

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
        # print("Sucessores dos últimos 3 zeros: ", zeros_numeros_sucessores[-3:])

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
    #for i, indice in enumerate(zeros_indices_uniq):
        # print(f"Branco: {zeros_horarios_uniq[i]}")
        # print(f"Números antes: {', '.join(map(str, zeros_numeros_antecessores_uniq[i]))}")
        # print(f"Números depois: {', '.join(map(str, zeros_numeros_sucessores_uniq[i]))}")
        # print("Horários prováveis:")
        #for j, horario_provavel in enumerate(zeros_horarios_provaveis[i]):
            #print(f"E{j + 1} - {horario_provavel}")
        # print()
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
        # print(f"Zero found at {created_at_str}, interval: {interval_count}")

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
    max_len = max(len(zero_times), len(zero_times_2), len(payers), len(cycles), len(missing_numbers))
    zero_times += [None] * (max_len - len(zero_times))
    zero_times_2 += [None] * (max_len - len(zero_times_2))
    payers += [None] * (max_len - len(payers))
    cycles += [None] * (max_len - len(cycles))
    missing_numbers += [None] * (max_len - len(missing_numbers))

    df2 = pd.DataFrame({

        "Payer": payers,
        "Ciclo": cycles,
        "Falta Pagar": missing_numbers,
        "Branco": zero_times_2,
    })

    df2['L'] = range(1, len(df2) + 1)

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
        # print(f"Coluna {i} adicionada ao DataFrame com valores: {col_values}")

    # Concatene os dois DataFrames horizontalmente
    df = pd.concat([df1, df2], axis=1)

    # print(f"zero_times: {zero_times}")
    # print(f"zero_times_2: {zero_times_2}")

    def color_column(val):
        color = '#1a242d'
        return 'background-color: %s' % color

    styled = df.style.applymap(color_column, subset=['L'])

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
            return f"{row} {total_correspondentes}"  # Adiciona o total de horários correspondentes à célula
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
        # print(f"Processando linha {i}...")
        if row['Branco'] is not None:
            # print(f"  multiplos: {row['multiplos']}")
            if previous_zero_time == row['Branco']:
                df.at[i, 'multiplos'] = ["DUPLO" for _ in row['multiplos']]  # Substitua todos os horários por "DUPLO"
                for column in index_to_column.values():  # Substitua os valores correspondentes nas colunas de múltiplos de 14 por "DUPLO"
                    df.at[i, column] = "DUPLO"
                continue  # Se o horário do zero correspondente for igual ao horário do zero anterior, pule para a próxima iteração
            previous_zero_time = row['Branco']  # Atualize o horário do zero anterior

            # 2 - Procura por "X" não presente em row['multiplos'], mesmo se "P" estiver presente
            if not any("X" in multiplo for multiplo in row['multiplos']):
                previous_time = row['Branco']
                for j, multiplos in df['multiplos'].items():
                    # print(f"  Processando célula {j}...")
                    if j > i or any("X" in multiplo for multiplo in multiplos) or any(
                            "P" in multiplo for multiplo in multiplos):
                        continue
                    zero_time_2 = get_time_shifted(row['Branco'], 0)  # Busca pelo minuto exato
                    # print(f"  Verificando zero_time: {zero_time_2}")
                    if zero_time_2 in multiplos:
                        # print(f"  Encontrado {zero_time_2} em multiplos!")
                        df.at[i, 'Branco'] = f"X {row['Branco']} Linha {j + 1}"
                        zero_time_index = multiplos.index(zero_time_2)
                        column = index_to_column[zero_time_index]
                        df.at[j, column] = f"X {df.at[j, column]} Lata"
                        df.at[j, 'multiplos'] = [f"X {multiplo} Lata" if multiplo == zero_time_2 else multiplo for
                                                 multiplo in multiplos]
                        break  # Interrompe a busca do horário quando encontra uma correspondência

            # 1 - Procura por "P" não presente em row['multiplos']
            if not any("P" in multiplo for multiplo in row['multiplos']) and not any(
                    "X" in multiplo for multiplo in row['multiplos']):
                previous_time = row['Branco']
                for j, multiplos in df['multiplos'].items():
                    # print(f"  Processando célula {j}...")
                    if j > i or any("X" in multiplo for multiplo in multiplos) or any(
                            "P" in multiplo for multiplo in multiplos):
                        continue
                    for shift, label in [(-1, '+1Min'),
                                         (1, '-1Min')]:  # Busca pelos horários com minuto antes e depois
                        zero_time_2 = get_time_shifted(row['Branco'], shift)
                        # print(f"  Verificando zero_time: {zero_time_2}")
                        if zero_time_2 in multiplos:
                            # print(f"  Encontrado {zero_time_2} em multiplos!")
                            df.at[i, 'Branco'] = f"P {row['Branco']} Linha {j + 1}"
                            zero_time_index = multiplos.index(zero_time_2)
                            column = index_to_column[zero_time_index]
                            df.at[j, column] = f"P {df.at[j, column]} {label}"
                            df.at[j, 'multiplos'] = [f"P {multiplo} {label}" if multiplo == zero_time_2 else multiplo
                                                     for multiplo in multiplos]
                            break  # Interrompe a busca do horário quando encontra uma correspondência
                        else:
                            continue
                        break

    # Fim coloca "P" nos multiplos

    # Fim coloca "P" nos multiplos

    # INICIO gerar df4
    # Crie um OrderedDict para armazenar os horários
    horarios_sem_p = OrderedDict()

    hora_atual = datetime.now().time()  # obtenha a hora atual
    uma_hora_depois = (datetime.now() + timedelta(hours=0.5)).time()  # obtenha a hora que será uma hora a partir de agora

    for i, row in df.iterrows():
        # print(f"Processando linha {i}...")
        # Verifique se "P" está em algum lugar da lista de horários
        if any("P" in multiplo for multiplo in row['multiplos']):
            continue  # Se "P" estiver presente, ignore esta linha
        # print(f"  multiplos: {row['multiplos']}")
        # Adicione os horários sem "P" ao OrderedDict se eles forem a partir da hora atual e dentro de uma hora
        # Adicione os horários sem "P" ao OrderedDict se eles forem a partir da hora atual e dentro de uma hora
        # Adicione os horários sem "P" ao OrderedDict se eles forem a partir da hora atual e dentro de uma hora
        for multiplo in row['multiplos']:
            if multiplo and all(char.isdigit() or char == ':' for char in multiplo):
                hora_multiplo = datetime.strptime(multiplo, "%H:%M").time()
                if hora_atual <= hora_multiplo <= uma_hora_depois:
                    horarios_sem_p[multiplo] = f"{i+1}/{row['multiplos'].index(multiplo) + 1}"  # Adiciona linha/coluna

        # Converta o OrderedDict em uma lista e ordene-a
        horarios_sem_p = dict(sorted(horarios_sem_p.items(), key=lambda x: datetime.strptime(x[0], '%H:%M')))

        # Crie um DataFrame vazio com os horários como cabeçalhos
        # df4 = pd.DataFrame(columns=horarios_sem_p)
        # Adicione 'Horarios' no início da lista de colunas
        horarios_sem_p_keys = list(horarios_sem_p.keys())
        horarios_sem_p_keys.insert(0, 'Horarios')
        # Reindexe o DataFrame para ter as novas colunas
        df4 = df4.reindex(columns=horarios_sem_p_keys)
        # Substitua NaN por uma string vazia
        df4.fillna('', inplace=True)
        # Adicione valores à coluna "Horarios"
        df4.at[0, 'Horarios'] = 'Lin/Col'
        df4.at[1, 'Horarios'] = 'Branco1'
        df4.at[2, 'Horarios'] = 'Branco2'
        df4.at[3, 'Horarios'] = 'Falso'
        df4.at[4, 'Horarios'] = 'Total'

        # Preenche a linha 'Lin/Col' com os valores de horarios_sem_p
        df4.loc[0, list(horarios_sem_p.keys())] = list(horarios_sem_p.values())

# Preencher linhas branco1 e e branco2 do df4

    # Preencher linhas branco1 e e branco2 do df4
    def is_time_close_to(time1_str, time2_str):
        # Converte as strings de tempo para objetos datetime.time
        time1 = datetime.strptime(time1_str, "%H:%M").time()
        time2 = datetime.strptime(time2_str, "%H:%M").time()

        # Calcula a diferença absoluta entre os dois horários
        delta = abs(datetime.combine(date.today(), time1) - datetime.combine(date.today(), time2))

        # Verifica se a diferença é menor ou igual a um minuto
        return delta <= timedelta(minutes=1)

    # Pega os horários prováveis das linhas 3 e 4 de df3

    branco1_times = df3.loc[3].tolist()
    branco2_times = df3.loc[4].tolist()

    # Inicializa as listas
    branco1_list = []
    branco2_list = []

    # Verifica cada horário em df4
    for horario in df4.columns[1:]:  # Ignora a coluna 'Horarios'
        branco1_result = ""
        branco2_result = ""
        for time in branco1_times:
            if is_time_close_to(horario, time):
                branco1_result = "Sim"
                break
        branco1_list.append(branco1_result)

        for time in branco2_times:
            if is_time_close_to(horario, time):
                branco2_result = "Sim"
                break
        branco2_list.append(branco2_result)

    # Atribui as listas às linhas correspondentes

    df4.loc[1, df4.columns[1:]] = branco1_list
    df4.loc[2, df4.columns[1:]] = branco2_list
# FIM Preencher linhas branco1 e e branco2 do df4

# FIM gerar df4

    df = df.drop(columns=['multiplos'])
    # Adicione isso antes de salvar o CSV em intervalos13.py
    df['update_timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    df.to_csv("df.csv", index=False)

    df.to_csv('df.csv', index=False)
    df3.to_csv('df3.csv', index=False)
    df4.to_csv('df4.csv', index=False)


if __name__ == "__main__":
    asyncio.run(main())

end_time = time.time()  # Fim da medição do tempo
print(f"Tempo total de execução: {end_time - start_time} segundos")
