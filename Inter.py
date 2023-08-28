import tkinter as tk
from datetime import datetime
import intervalos12
import subprocess
import sys
import time
import webbrowser
import asyncio
# Inicie o servidor Flask em um processo separado
flask_process = subprocess.Popen([sys.executable, "app1.py"])
time.sleep(0.5)  # Aguarde um pouco para o servidor Flask iniciar
# webbrowser.open('http://127.0.0.1:5000/')  # Abra a URL no navegador padrão

def execute_code():
    button.config(text="Processando...", state="disabled")  # Desabilite o botão
    button.update()
    print(f"Running")  # Adicione esta linha
    #intervalos12.main()  # Modifique esta linha
    #messagebox.showinfo("Information", "Código executado")
    button.config(text="Gerar Relatório", state="normal")  # Habilite o botão novamente
    asyncio.run(intervalos12.main())

root = tk.Tk()
root.title("INTERVALO DE BRANCOS POR DIA")
root.configure(bg='#1a242d')

# Defina o tamanho da janela para 800x600
root.geometry("350x150")

# Desabilite o botão de maximizar
root.resizable(False, False)

# Centralize a janela
window_width = 350
window_height = 150
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
position_top = int(screen_height / 2 - window_height / 2)
position_right = int(screen_width / 2 - window_width / 2)
root.geometry(f"{window_width}x{window_height}+{position_right}+{position_top}")

label = tk.Label(root, text="Data e Hora Atual: " + datetime.now().strftime("%d/%m/%Y, %H:%M:%S"), bg='#1a242d', fg='white')
label.pack(pady=10)

button = tk.Button(root, text="Gerar Relatório", command=execute_code, bg='#272262', fg='white')
button.pack(pady=10)

root.mainloop()

# Quando o programa terminar, encerre o processo Flask
flask_process.terminate()