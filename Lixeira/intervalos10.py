import time
import requests
from datetime import datetime, timedelta
from collections import Counter
import pandas as pd
import webbrowser
import sys
from flask import Flask, render_template
import pandas as pd
import numpy as np
import os

# sys.path.append('D:\\Projeto Intervalos\\myenv\\Lib\\site-packages\\jinja2')


def main():
    print("Running intervalos.py")
    #Delete the output.html file if it exists
    if os.path.exists("../output.html"):
        os.remove("../output.html")
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
    multiplos_14 = [[] for _ in range(206)]  # Lista para armazenar os múltiplos de 14
    pagou = [[] for _ in range(206)]  # Lista para armazenar as mensagens de pagamento
    multiplos_14_dict = {}  # Dicionário para mapear os horários dos múltiplos de 14 aos seus índices
    multiplos_14_before = [[] for _ in range(206)]  # Lista para armazenar os horários um minuto antes dos múltiplos de 14
    multiplos_14_after = [[] for _ in range(206)]  # Lista para armazenar os horários um minuto depois dos múltiplos de 14
    p_placed_indices = []  # Lista para armazenar os índices das linhas que já tiveram um "P" colocado nelas
    todas_as_listas_de_multiplos = []
    p_placed_indices = []
    for page in reversed(range(1, total_pages)):
        result_json = (requests.get("https://blaze.com/api/roulette_games/history?page=" + str(page))).json()
        resultados = reversed(result_json['records'])
        # p_placed = False  # Variável de controle para verificar se um "P" já foi colocado
        for resultado in resultados:
            roll = resultado['roll']
            created_at = resultado['created_at']
            print(f"roll:{roll}")
            print(f"created_at:{created_at}")
            created_at_datetime = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%S.%fZ")
            created_at_datetime = created_at_datetime - timedelta(hours=3)

            if created_at_datetime.date() != datetime.now().date():
                continue

            created_at_str = created_at_datetime.strftime("%H:%M")

            rolls.append(roll)
            times.append(created_at_str)

            if roll == 0:

                # Nova análise de probabilidades
                zeros_indices = [i for i, roll in enumerate(rolls) if roll == 0]
                zeros_horarios = [times[i] for i in zeros_indices]

                zeros_numeros_antecessores = []
                zeros_numeros_sucessores = []

                for zero_index in zeros_indices:
                    antecessores = []
                    sucessores = []
                    count = 0

                    # Capturar os três números anteriores ao zero
                    i = zero_index - 1
                    while count < 3 and i >= 0:
                        if rolls[i] != 0:  # note que aqui estamos comparando com o número 0, não a string '0'
                            antecessores.append(rolls[i])
                            count += 1
                        i -= 1

                    # Resetar o contador
                    count = 0

                    # Capturar os três números posteriores ao zero
                    i = zero_index + 1
                    while count < 3 and i < len(rolls):
                        if rolls[i] != 0:  # note que aqui estamos comparando com o número 0, não a string '0'
                            sucessores.append(rolls[i])
                            count += 1
                        i += 1

                    zeros_numeros_antecessores.append(antecessores)
                    zeros_numeros_sucessores.append(sucessores)

                # Garantir que nenhum zero esteja presente nos conjuntos de números antecessores e posteriores
                for i, numeros_antecessores in enumerate(zeros_numeros_antecessores):
                    zeros_numeros_antecessores[i] = [num for num in numeros_antecessores if num != '0']
                for i, numeros_sucessores in enumerate(zeros_numeros_sucessores):
                    zeros_numeros_sucessores[i] = [num for num in numeros_sucessores if num != '0']

                # Em caso de falta de três números anteriores ou posteriores, registrar os números disponíveis
                for i, numeros_antecessores in enumerate(zeros_numeros_antecessores):
                    if len(numeros_antecessores) < 3:
                        zeros_numeros_antecessores[i] = rolls[zero_index - len(numeros_antecessores):zero_index][
                                                        ::-1] + numeros_antecessores[::-1]
                for i, numeros_sucessores in enumerate(zeros_numeros_sucessores):
                    if len(numeros_sucessores) < 3:
                        zeros_numeros_sucessores[i] = numeros_sucessores + rolls[zero_index + 1:zero_index + 1 + (
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
                    print(f"Minuto: {zeros_horarios_uniq[i]}")
                    print(f"Números antes: {', '.join(map(str, zeros_numeros_antecessores_uniq[i]))}")
                    print(f"Números depois: {', '.join(map(str, zeros_numeros_sucessores_uniq[i]))}")
                    print("Horários prováveis:")
                    for j, horario_provavel in enumerate(zeros_horarios_provaveis[i]):
                        print(f"E{j + 1} - {horario_provavel}")
                    print()

            if roll == 0:
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
                p_placed1 = False  # Redefina a variável de controle para False quando um novo zero for sorteado
                Lata = False
                Antes = False
                Depois = False
                Lata1=0
                Antes1=0
                Depois1=0

                # Adicione os múltiplos de 14 a esta lista
                for i in range(14, 206, 14):
                    next_time = (created_at_datetime + timedelta(minutes=i)).strftime("%H:%M")
                    multiplos_14.append(next_time)

                print(f"Lista de múltiplos criada para este zero: {multiplos_14}")

                # Adicione esta lista de múltiplos à lista de todas as listas de múltiplos
                todas_as_listas_de_multiplos.append(multiplos_14)

                # Crie a "lista do zero"
                zero_list = [created_at_str,
                             (created_at_datetime - timedelta(minutes=1)).strftime("%H:%M"),
                             (created_at_datetime + timedelta(minutes=1)).strftime("%H:%M")]

                print(f"Lista do zero criada: {zero_list}")

                # Procure a "lista do zero" em todas as listas de múltiplos, exceto a última (que acabamos de criar)
                for zero_time in zero_list:

                    # Inverta a ordem das listas de múltiplos para verificar as listas mais antigas primeiro
                    for multiplos in reversed(todas_as_listas_de_multiplos[:-1]):
                        # Se "P" já está na lista, ignore esta lista

                        if any("P" in s for s in multiplos):
                            continue
                        if zero_time in multiplos:
                            index = multiplos.index(zero_time)

                            if zero_time == zero_list[0]:  # horário exato
                                multiplos[index] = f"P {zero_time} Lata"
                                print(f"P colocado em {zero_time} (horário exato) na lista de múltiplos: {multiplos}")
                                Lata = True
                                Lata1= Lata1 + 1
                            elif zero_time == zero_list[1]:  # um minuto antes
                                multiplos[index] = f"P {zero_time} Depois"
                                print(f"P colocado em {zero_time} (um minuto antes) na lista de múltiplos: {multiplos}")
                                Depois = True
                                Depois1 = Depois1 + 1
                            elif zero_time == zero_list[2]:  # um minuto depois
                                multiplos[index] = f"P {zero_time} Antes"
                                print(f"P colocado em {zero_time} (um minuto depois) na lista de múltiplos: {multiplos}")
                                Antes = True
                                Antes1 = Antes1 + 1

                            print(f"Lata: {Lata}")
                            print(f"Antes: {Antes}")
                            print(f"Depois: {Depois}")
                            if sum([Lata, Antes, Depois]) > 1:
                                # Se sim, remova o "P" do último multiplos[index]
                                multiplos[index] = zero_time
                                print(f" multiplos[index]: {multiplos[index]}")


                            print(f"Lata1: {Lata1}")
                            if Lata1 > 1:
                                # Se sim, remova o "P" do último multiplos[index]
                                multiplos[index] = zero_time
                                print(f" multiplos[index]: {multiplos[index]}")
                            print(f"Antes1: {Antes1}")
                            if Antes1 > 1:
                                # Se sim, remova o "P" do último multiplos[index]
                                multiplos[index] = zero_time
                                print(f" multiplos[index]: {multiplos[index]}")
                            print(f"Depois1: {Depois1}")
                            if Depois1 > 1:
                                # Se sim, remova o "P" do último multiplos[index]
                                multiplos[index] = zero_time
                                print(f" multiplos[index]: {multiplos[index]}")


                            print(f"zero_times: {zero_times}")
                            # Adicione um "P" ao horário do zero que gerou a lista de zeros
                            for i in range(len(zero_times)):
                                if zero_times[i] == zero_list[0]:
                                    zero_times[i] = f"P {zero_list[0]}"
                                    print(f"zero_times fim: {zero_times}")
                                    break


                # Imprima todas as listas de múltiplos
                #print("Todas as listas de múltiplos:")
                #for lista in todas_as_listas_de_multiplos:
                    #print(lista)

                # No final do processo, verifique 'zero_times' novamente
                #for i, timeP in enumerate(zero_times):
                    # Se o horário atual em 'zero_times' tem um "P"
                    #if "P" in timeP:
                        # Verifique se há outro horário igual sem "P" em 'zero_times'
                        #for j, other_time in enumerate(zero_times):
                            #if other_time == timeP[2:]:
                                # Se houver, adicione "P" a ele
                                #zero_times[j] = f"P {other_time}"

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
        "Número de Vezes": frequencias,
    })

    # Preencha as listas mais curtas com None até que todas as listas tenham o mesmo comprimento
    max_len = max(len(zero_times), len(payers), len(cycles), len(missing_numbers))
    zero_times += [None] * (max_len - len(zero_times))
    payers += [None] * (max_len - len(payers))
    cycles += [None] * (max_len - len(cycles))
    missing_numbers += [None] * (max_len - len(missing_numbers))

    df2 = pd.DataFrame({
        "Branco": zero_times,
        "Pagador": payers,
        "Ciclo": cycles,
        "Falta Pagar": missing_numbers,
    })

    def get_ith_multiple(multiplos, i):
        try:
            return multiplos[i]
        except IndexError:
            return None

    # Adicione as colunas "224" a "14" ao DataFrame df2
    for i in range(14, 206, 14):  # Altere 197 para 226
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
    df["Pagador"] = df["Pagador"].apply(lambda x: f'<div style="position: relative; text-align: center;"><img src="./static/ciclo1.png" width="60" height="60"><span style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); color: white;">{x[:-1]}</span></div>' if isinstance(x, str) and x.endswith("F") else x)

    # Substitua os zeros na coluna "Brancos" pela URL da imagem correspondente
    #df["Branco"] = df["Branco"].replace({0: "D:\\pythonProject1\\static\\0.jpeg"})

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
    df["Branco 1"] = df["Branco 1"].apply(lambda x: f'<img src="./static/0.jpeg" width="50" height="50"><br>{x}' if ":" in x else x)
    df["Branco 2"] = df["Branco 2"].apply(lambda x: f'<img src="./static/0.jpeg" width="50" height="50"><br>{x}' if ":" in x else x)

    # Adicione a imagem acima do horário na coluna "Branco" Df2
    #df["Branco"] = df["Branco"].apply(lambda x: f'<img src="./static/0.jpeg" width="50" height="50"><br>{x}' if ":" in x else x)

    # Adicione a imagem acima do horário na coluna "Branco" Df2
    df["Branco"] = df["Branco"].apply(
        lambda x: f'<img src="./static/pago3.jpeg" width="50" height="50"><br>{x}' if "P" in x else (
            f'<img src="./static/0.jpeg" width="50" height="50"><br>{x}' if ":" in x else x))

    # Adicione a imagem à coluna "Intervalo"
    #df["Intervalo"] = df["Intervalo"].apply(lambda x: f'<div style="position: relative; text-align: center;"><img src="D:\\pythonProject1\\static\\intervalo2.png" width="50" height="50"><span style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); color: black;">{x}</span></div>' if pd.notnull(x) else "")

    # Adicione a imagem à coluna "Intervalo" apenas se a célula estiver preenchida
    df["Casas"] = df["Casas"].apply(lambda x: f'<div style="position: relative; text-align: center;"><img src="./static/intervalo1.png" width="50" height="55"><span style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); color: black;">{x}</span></div>' if x != "" else "")

    # Adicione a imagem à coluna "frequencias" apenas se a célula estiver preenchida
    df["Número de Vezes"] = df["Número de Vezes"].apply(lambda x: f'<div style="position: relative; text-align: center;"><img src="./static/freq.png" width="50" height="55"><span style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); color: white;">{x}</span></div>' if x != "" else "")

    # Cria uma lista com os nomes das colunas
    columns = [str(i) for i in range(14, 206, 14)]  # Cria uma lista com os nomes das colunas
    for column in columns:
        df[column] = df[column].apply(lambda x: f'<div style="text-align: center;"><img src="./static/pago.png" width="30" height="30"><br><div>{x[2:]}</div></div>'if isinstance(x, str) and x.startswith('P ') else x)

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
    html = html.replace('<td', '<td style="width: 80px;text-align: center; background-color: #0f1923; color: white; font-size: 0.8em; font-weight: bold; border: 2px solid #1a242d; padding: 0;"')
    html = html.replace('<thead>', '<thead style="background-color: #282d37;">')
    html = html.replace('<td>', '<td style="background-color: #282d37;">')

    # Adicione a declaração do charset UTF-8
    html = '<!DOCTYPE html>\n<html>\n<head>\n<meta charset="UTF-8">\n</head>\n<body>\n' + html
    
    # Adicione o código JavaScript ao HTML
    html += """
    
    <script>
    window.onload = function() {
    fetch('http://127.0.0.1:5000/delete_output', {
        method: 'POST',
    })
    .then(response => response.text())
    .then(data => console.log(data))
    .catch((error) => {
        console.error('Error:', error);
    });
};
    </script>
    """

    # Escreva o HTML em um arquivo
    with open("../output.html", "w") as f:
        f.write(html)

    webbrowser.open('../output.html')

if __name__ == "__main__":
    main()

