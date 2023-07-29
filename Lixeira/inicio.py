import time
import requests
import json
from datetime import datetime, timedelta
import schedule
from flask_socketio import SocketIO
import threading

total_pages = 11
last_sequence = None
socketio = None
before_result = ()
current_result = ()
sequence_fetched = False

def get_api_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except requests.RequestException as err:
        print(f'Other error occurred: {err}')
    except ValueError:
        print('Invalid JSON')
    return None

def write_to_file(filename, data):
    with open(filename, 'w') as f:
        f.write(json.dumps(data))

def get_sequence():
    print('Inicio get sequencia')
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
    print('Sequence:', sequence)
    write_to_file('sequence.json', sequence)
    return sequence

def blaze_now_results():
    print('Inicio Blaze now')
    global before_result
    global current_result
    global last_sequence
    global sequence_fetched
    resultado = get_api_data("https://api-v2.blaze.com/api/roulette_games/current")
    if resultado is None:
        return
    if resultado['status'] == 'rolling':
        print('resultado:', resultado['status'])
        created_at_datetime = datetime.strptime(resultado['created_at'], "%Y-%m-%dT%H:%M:%S.%fZ")
        created_at_datetime = created_at_datetime - timedelta(hours=3)
        created_at_str = created_at_datetime.strftime("%H:%M")
        current_result = (
            int(resultado['roll']),
            created_at_str,
        )
        print('Atualizando resultado anterior')
        if before_result != current_result:
            before_result = current_result
            if not sequence_fetched:
                sequence = get_sequence()
                sequence_fetched = True
            print('New Sequence:', str(current_result))
            write_to_file('current_result.json', current_result)

def run_threaded(job_func):
    job_thread = threading.Thread(target=job_func)
    job_thread.start()

schedule.every(0.1).seconds.do(run_threaded, blaze_now_results)

while True:
    schedule.run_pending()
    time.sleep(0.1)
