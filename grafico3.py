import requests
from bs4 import BeautifulSoup
import csv
import time

start_time = time.time()  # Iniciar a medição do tempo

print("Running grafico3 Aguarde.....")
url = "https://historicosblaze.com/blaze/doubles"
headers = {'User-Agent': 'Mozilla/5.0'}

# Usar uma sessão para reutilizar a conexão TCP
with requests.Session() as session:
    session.headers.update(headers)

    try:
        response = session.get(url)
        response.raise_for_status()  # Levantar uma exceção para códigos de status 4xx e 5xx

        soup = BeautifulSoup(response.text, 'html.parser')
        element = soup.find('div', class_='double-popover')

        content = element['data-bs-content'] if element else None
        soup_content = BeautifulSoup(content, 'html.parser') if content else None

        profit_line = None
        if soup_content:
            for line in soup_content.find_all('p', class_='fs-sm'):
                if 'Durante essa rodada' in line.text:
                    profit_line = line
                    break

        profit = profit_line.find('strong').text if profit_line else "Valor não encontrado"
        profit = profit.replace('R$', '').strip()

        stone = element.find('div', class_='number').find('span').text if element else "Valor não encontrado"
        time_value = element.find('div', class_='time-compact').text if element else "Valor não encontrado"

        with open('output.csv', mode='r') as file:
            reader = csv.reader(file)
            rows = list(reader)

        rows.insert(1, [profit, stone, time_value])

        with open('output.csv', mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(rows)

    except requests.exceptions.RequestException as e:
        print(f"Erro ao acessar a página: {e}")

end_time = time.time()  # Parar a medição do tempo
execution_time = end_time - start_time
print(f"Tempo de execução: {execution_time} segundos")
