import requests
from bs4 import BeautifulSoup
import csv
import locale
import time

start_time = time.time()  # Iniciar a medição do tempo

# Configurar a localização para o formato brasileiro
locale.setlocale(locale.LC_ALL, 'pt_BR.utf8')

url = "https://historicosblaze.com/blaze/doubles?limit=2500&q%5Bnumber_eq%5D=&q%5Bnumber_cont%5D=&parity=all&q%5Bcreated_on_gteq%5D=&q%5Bcreated_on_lteq%5D=&hour=&minute=&q%5Bcolor_cont%5D=&commit=Filtrar"
headers = {'User-Agent': 'Mozilla/5.0'}

# Usar uma sessão para reutilizar a conexão TCP
with requests.Session() as session:
    session.headers.update(headers)

    try:
        response = session.get(url)
        response.raise_for_status()  # Levantar uma exceção para códigos de status 4xx e 5xx

        soup = BeautifulSoup(response.text, 'html.parser')
        elements = soup.find_all('div', class_='double-popover')

        with open('output.csv', mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Resultado', 'Pedra', 'Hora'])

            for element in elements:
                content = element['data-bs-content']
                soup_content = BeautifulSoup(content, 'html.parser')

                profit_lines = soup_content.find_all('p', class_='fs-sm')
                for line in profit_lines:
                    if 'Durante essa rodada' in line.text:
                        profit = line.find('strong').text.replace('R$', '').replace(' ', '')
                        formatted_value = locale.format_string('%.2f', float(profit.replace('.', '').replace(',', '.')), grouping=True)

                        stone = element.find('div', class_='number').find('span').text
                        time_value = element.find('div', class_='time-compact').text

                        writer.writerow([formatted_value, stone, time_value])
                        break

    except requests.exceptions.RequestException as e:
        print(f"Erro ao acessar a página: {e}")

end_time = time.time()  # Parar a medição do tempo
execution_time = end_time - start_time
print(f"Tempo de execução: {execution_time} segundos")

