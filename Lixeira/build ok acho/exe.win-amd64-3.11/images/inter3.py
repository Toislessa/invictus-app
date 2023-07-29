import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import os  # Adicione esta linha
import subprocess

def execute_code():
    button.config(text="Processando...")
    button.update()
    intervalos_script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "intervalos.py")
    print(f"Running {intervalos_script_path}")  # Adicione esta linha
    with open("output.log", "w") as f:
        subprocess.run(["./myenv/Scripts/python", intervalos_script_path], stdout=f, stderr=f)
    #messagebox.showinfo("Information", "Código executado")
    button.config(text="Gerar Relatório")

root = tk.Tk()
root.title("INTERVALO DE BRANCOS POR DIA")
root.configure(bg='#1a242d')

# Defina o tamanho da janela para 800x600
root.geometry("350x150")

# Desabilite o botão de maximizar
root.resizable(False, False)

label = tk.Label(root, text="Data e Hora Atual: " + datetime.now().strftime("%d/%m/%Y, %H:%M:%S"), bg='#1a242d', fg='white')
label.pack(pady=10)

button = tk.Button(root, text="Gerar Relatório", command=execute_code, bg='#272262', fg='white')
button.pack(pady=10)

root.mainloop()
