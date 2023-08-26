import pandas as pd
import os
import asyncio
import aiohttp
import time
from datetime import datetime, timedelta, date

start_time = time.time()  # Início da medição do tempo

async def fetch(session, url):
    async with session.get(url) as response:
        return await response.json()

def read_current_result():
    try:
        with open('current_result1.txt', 'r') as file:
            result = file.readline().strip().split(',')
            return int(result[0]), result[1]
    except:
        return None

async def main():
    print("Running intervalos13_1. Aguarde.....")
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
            rolls_2.append(roll_2)
            created_at_str_2 = created_at_datetime_2.strftime("%H:%M")
            times_2.append(created_at_str_2)
            sequence_2.append((roll_2, created_at_str_2, created_at_datetime_2))
            rolls.append(roll)
            times.append(created_at_str)
            sequence.append((roll, created_at_str, created_at_datetime))

    current_result = read_current_result()
    if current_result:
        rolls.reverse()
        rolls_2.reverse()
        times.reverse()
        times_2.reverse()
        rolls_2.insert(0, current_result[0])
        times_2.insert(0, current_result[1])
        rolls.insert(0, current_result[0])
        times.insert(0, current_result[1])
        rolls.reverse()
        rolls_2.reverse()
        times.reverse()
        times_2.reverse()

    max_len = max(len(rolls), len(times), len(rolls_2), len(times_2))

    rolls += [None] * (max_len - len(rolls))
    times += [None] * (max_len - len(times))
    rolls_2 += [None] * (max_len - len(rolls_2))  # Adicione esta linha
    times_2 += [None] * (max_len - len(times_2))  # Adicione esta linha

    df1 = pd.DataFrame({
        "Números": rolls,
        "Horários": times,

    })

    df1.to_csv('df1.csv', index=False)


if __name__ == "__main__":
    asyncio.run(main())

end_time = time.time()  # Fim da medição do tempo
print(f"Tempo total de execução: {end_time - start_time} segundos")