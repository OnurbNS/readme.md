# Importações
import tkinter as tk
from tkinter import ttk, messagebox
import random
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ===================== Funções Utilitárias =====================

def criar_populacao(tamanho_populacao, num_variacoes, num_elementos):
    return [[random.choice(range(num_variacoes)) for _ in range(num_elementos)] for _ in range(tamanho_populacao)]

def fitness(individuo, taxa_conversao_esperada):
    return sum(1 for i, taxa in enumerate(individuo) if taxa == taxa_conversao_esperada[i]) / len(taxa_conversao_esperada)

def selecionar_pais(populacao, taxa_conversao_esperada):
    pontuacoes = [fitness(individuo, taxa_conversao_esperada) for individuo in populacao]
    indice_pais = np.argsort(pontuacoes)[-2:]  # Seleciona os 2 melhores indivíduos
    return [populacao[i] for i in indice_pais]

def crossover(pais):
    ponto_corte = random.randint(1, len(pais[0]) - 1)
    return [
        pais[0][:ponto_corte] + pais[1][ponto_corte:],
        pais[1][:ponto_corte] + pais[0][ponto_corte:]
    ]

def mutacao_orientada(individuo, probabilidade_variacoes, num_variacoes):
    if random.random() < 0.1:  # 10% de chance de mutação
        indice_mutacao = random.randint(0, len(individuo) - 1)
        individuo[indice_mutacao] = np.random.choice(range(num_variacoes), p=probabilidade_variacoes)

def gerar_probabilidade_variacoes(resultados_anteriores, num_variacoes):
    contagem = [0] * num_variacoes
    for resultado in resultados_anteriores:
        if isinstance(resultado, list):  # Verifica se é uma lista
            for res in resultado:
                contagem[res] += 1
        else:
            contagem[resultado] += 1
    total = sum(contagem)
    return [c / total if total > 0 else 1 / num_variacoes for c in contagem]

# ===================== Algoritmo Genético =====================

def algoritmo_genetico(num_geracoes, tamanho_populacao, num_variacoes, taxa_conversao_esperada, num_elementos, resultados_anteriores=None):
    populacao = criar_populacao(tamanho_populacao, num_variacoes, num_elementos)
    resultados_anteriores = resultados_anteriores or []
    historico_fitness = []

    for geracao in range(num_geracoes):
        pontuacoes = [fitness(individuo, taxa_conversao_esperada) for individuo in populacao]
        melhor_individuo = max(populacao, key=lambda x: fitness(x, taxa_conversao_esperada))
        melhor_fitness = fitness(melhor_individuo, taxa_conversao_esperada)
        historico_fitness.append(melhor_fitness)

        if melhor_fitness == 1.0:
            return melhor_individuo, historico_fitness
        
        pais = selecionar_pais(populacao, taxa_conversao_esperada)
        nova_populacao = []
        for _ in range(tamanho_populacao // 2):
            nova_populacao.extend(crossover(pais))

        resultados_anteriores.extend(individuo for individuo in nova_populacao)
        probabilidade_variacoes = gerar_probabilidade_variacoes(resultados_anteriores, num_variacoes)

        for individuo in nova_populacao:
            mutacao_orientada(individuo, probabilidade_variacoes, num_variacoes)

        populacao = nova_populacao

    return max(populacao, key=lambda x: fitness(x, taxa_conversao_esperada)), historico_fitness

# ===================== Interface Gráfica =====================

def rodar_algoritmo():
    try:
        num_elementos = int(entry_elementos.get())
        num_variacoes = int(entry_variacoes.get())
        num_geracoes = int(entry_geracoes.get())
        tamanho_populacao = int(entry_populacao.get())

        # Corrigir o erro de sintaxe na condição
        if num_elementos <= 0 or num_variacoes <= 0 or num_geracoes <= 0 or tamanho_populacao <= 0:
            raise ValueError("Os valores devem ser positivos!")

        taxa_conversao_esperada = [random.choice(range(num_variacoes)) for _ in range(num_elementos)]
        melhor_layout, historico_fitness = algoritmo_genetico(
            num_geracoes, tamanho_populacao, num_variacoes, taxa_conversao_esperada, num_elementos
        )

        # Exibir o melhor layout na tabela
        for row in tabela.get_children():
            tabela.delete(row)
        
        for i, valor in enumerate(melhor_layout):
            tabela.insert("", "end", values=(f"Elemento {i+1}", f"Variação {valor+1}"))

        # Atualizar gráfico
        ax.clear()
        ax.plot(range(len(historico_fitness)), historico_fitness, marker='o', linestyle='-', color='b')
        ax.set_title("Evolução da Taxa de Conversão")
        ax.set_xlabel("Geração")
        ax.set_ylabel("Fitness")
        canvas.draw()

    except ValueError:
        messagebox.showerror("Erro", "Por favor, insira valores válidos e positivos!")

# Criando a interface gráfica
root = tk.Tk()
root.title("Otimização de Campanha A/B com Algoritmo Genético")

# Layout da interface
tk.Label(root, text="Número de Elementos:").grid(row=0, column=0, padx=5, pady=5)
entry_elementos = tk.Entry(root)
entry_elementos.grid(row=0, column=1, padx=5, pady=5)

tk.Label(root, text="Número de Variações por Elemento:").grid(row=1, column=0, padx=5, pady=5)
entry_variacoes = tk.Entry(root)
entry_variacoes.grid(row=1, column=1, padx=5, pady=5)

tk.Label(root, text="Número de Gerações:").grid(row=2, column=0, padx=5, pady=5)
entry_geracoes = tk.Entry(root)
entry_geracoes.grid(row=2, column=1, padx=5, pady=5)

tk.Label(root, text="Tamanho da População:").grid(row=3, column=0, padx=5, pady=5)
entry_populacao = tk.Entry(root)
entry_populacao.grid(row=3, column=1, padx=5, pady=5)

# Botão para rodar o algoritmo
button_rodar = tk.Button(root, text="Rodar Algoritmo", command=rodar_algoritmo)
button_rodar.grid(row=4, column=0, columnspan=2, pady=10)

# Tabela para mostrar o melhor layout
tabela = ttk.Treeview(root, columns=("Elemento", "Melhor Variação"), show="headings")
tabela.heading("Elemento", text="Elemento")
tabela.heading("Melhor Variação", text="Melhor Variação")
tabela.grid(row=5, column=0, columnspan=2, pady=10)

# Gráfico da evolução da conversão
fig, ax = plt.subplots(figsize=(4, 3))
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().grid(row=6, column=0, columnspan=2)

# Iniciar a interface
root.mainloop()