import schedule
import pandas as pd
import time
from threading import Thread

def init(socketio):
    thread = Thread(target=main, args=(socketio,))
    thread.start()

def calculate_pairs(numbers):
    last_zero_index = None
    for i, num in enumerate(numbers[::-1]):
        if num == 0:
            last_zero_index = len(numbers) - i - 1
            break

    last_number_index = len(numbers) - 1 # Índice do último número

    list1, list2 = [], []
    numbers_list1, numbers_list2 = [], []
    sum1, sum2 = 0, 0

    # Cálculo da lista 1
    for num in numbers[last_zero_index - 1::-1]:
        if pd.notna(num):
            value = int(num) if num != 0 else 6
            sum1 += value
            list1.append(sum1)
            numbers_list1.append(value)
            if len(list1) == 10:
                break

    # Cálculo da lista 2
    for num in numbers[last_number_index::-1]: # Iniciando a leitura a partir do último número sorteado (inclusive)
        if pd.notna(num):
            value = int(num) if num != 0 else 6
            sum2 += value
            list2.append(sum2)
            numbers_list2.append(value)
            if len(list2) == 10:
                break

    return list1, list2, numbers_list1, numbers_list2 # Invertendo apenas a lista de números 2


def print_results(list1, list2, numbers_list1, numbers_list2):
    print("Números para cálculo da Lista 1:", numbers_list1)
    print("Lista 1:", list1)
    print("Números para cálculo da Lista 2:", numbers_list2)
    print("Lista 2:", list2)
    correspondences = set(list1) & set(list2)
    if correspondences:
        print("Correspondências encontradas:", correspondences)
    else:
        print("Nenhuma correspondência encontrada.")

def main(socketio):
    previous_length = 0
    while True:
        try:
            df = pd.read_csv('df.csv')
            numbers = df['Números'].tolist()
            if len(numbers) > previous_length:
                previous_length = len(numbers)
                list1, list2, numbers_list1, numbers_list2 = calculate_pairs(numbers)
                print_results(list1, list2, numbers_list1, numbers_list2)
                correspondences = set(list1) & set(list2)
                socketio.emit('new number', {'correspondences': list(correspondences)})
        except pd.errors.EmptyDataError:
            print("O arquivo CSV está vazio ou foi removido. Continuando...")
        time.sleep(2)

if __name__ == '__main__':
    # A linha abaixo foi removida porque você não deve inicializar o socketio aqui.
    # soma2.init(socketio)
    pass
