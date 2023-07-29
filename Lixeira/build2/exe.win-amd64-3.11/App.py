from flask import Flask, send_from_directory, render_template
import os

app = Flask(__name__)

@app.route('/')
def home():
    # Verifique se o arquivo 'index.html' existe
    if os.path.exists('D:\\Projeto Intervalos\\index.html'):
        # Se existir, envie o arquivo como resposta
        return send_from_directory('D:\\Projeto Intervalos', 'index.html')
    else:
        # Se não existir, retorne uma mensagem de erro
        return "Arquivo index.html não encontrado."

@app.route('/status')
def status():
    # Verifique se o arquivo 'output.html' existe
    if os.path.exists('D:\\Projeto Intervalos\\output.html'):
        # Se existir, retorne 'done'
        return 'done'
    else:
        # Se não existir, retorne 'processing'
        return 'processing'
@app.route('/output.html')
def output():
    # Verifique se o arquivo 'output.html' existe
    if os.path.exists('D:\\Projeto Intervalos\\output.html'):
        # Se existir, envie o arquivo como resposta
        return send_from_directory('D:\\Projeto Intervalos', 'output.html')
        os.remove("output.html")

    else:
        # Se não existir, retorne uma mensagem de erro
        return "Aguarde! Analisando os dados...."

@app.route('/delete_output', methods=['POST'])
def delete_output():
    if os.path.exists("output.html"):
        os.remove("output.html")
        return "File removed", 200
    else:
        return "No file to remove", 404



if __name__ == '__main__':
    app.run(debug=True)
