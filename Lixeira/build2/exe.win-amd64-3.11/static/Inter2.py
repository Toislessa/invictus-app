import tkinter as tk
from tkinter import messagebox
import subprocess
from datetime import datetime


def execute_code():
    button.config(text="Processando...")
    button.update()
    print(f"Running")  # Adicione esta linha
    subprocess.run(["./myenv/Scripts/python", "intervalos3.py"])
    messagebox.showinfo("Information", "Código executado")
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