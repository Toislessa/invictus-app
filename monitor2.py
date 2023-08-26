import requests
import time
from datetime import datetime, timedelta
import subprocess
import sys
import csv
import pandas as pd
subprocess.call([sys.executable, "intervalos13_1.py"])
def read_csv_for_grid():
    try:
        df = pd.read_csv("df1.csv")
        return df
    except Exception as e:
        return pd.DataFrame()

def write_current_result1(result):
    with open('df1.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(result)

def write_current_result(result):
    with open('current_result.txt', 'w') as file:
        file.write(str(result[0]) + ',' + result[1])

def get_api_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except (requests.HTTPError, requests.RequestException, ValueError):
        return None

before_result = ()

while True:
    resultado = get_api_data("https://api-v2.blaze.com/api/roulette_games/current")
    if resultado is None or resultado['status'] != 'rolling':
        time.sleep(0.5)
        continue

    created_at_datetime = datetime.strptime(resultado['created_at'], "%Y-%m-%dT%H:%M:%S.%fZ")
    created_at_datetime = created_at_datetime - timedelta(hours=3)
    created_at_str = created_at_datetime.strftime("%H:%M")
    current_result = (
        int(resultado['roll']),
        created_at_str,
    )

    if before_result != current_result:
        before_result = current_result
        write_current_result(current_result)  # Escreve o resultado atual em um arquivo        print(f'Novo resultado: {current_result}')
        write_current_result1(current_result)  # Escreve o resultado atual em um arquivo        print(f'Novo resultado: {current_result}')

        print(f'Gerando novos dados em {datetime.now()}')
        #subprocess.call([sys.executable, "intervalos13_1.py"])
        subprocess.call([sys.executable, "grafico3.py"])
        subprocess.call([sys.executable, "intervalos13.py"])

    time.sleep(0.5)
