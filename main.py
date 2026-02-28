import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json

# ==========================================
# PROCESSAMENTO DOS ARQUIVOS
# ==========================================
def processar_arquivos():
    pasta = filedialog.askdirectory(title="Selecione a pasta com arquivos MPF")
    if not pasta:
        return

    substituicoes = []
    insercoes = []

    # ---- Ler substituições ----
    for item in tabela_sub.get_children():
        procurar, substituir = tabela_sub.item(item)["values"]
        if procurar != "":
            substituicoes.append((procurar, substituir))

    # ---- Ler inserções ----
    for item in tabela_ins.get_children():
        linha_texto, numero_linha = tabela_ins.item(item)["values"]
        if linha_texto != "" and numero_linha != "":
            try:
                insercoes.append((int(numero_linha), linha_texto))
            except:
                pass

    arquivos_processados = 0

    for arquivo in os.listdir(pasta):
        if arquivo.lower().endswith(".mpf"):
            caminho = os.path.join(pasta, arquivo)

            with open(caminho, "r", encoding="utf-8", errors="ignore") as f:
                linhas = f.readlines()

            # ---- Substituições ----
            if substituicoes:
                novo_conteudo = []
                for linha in linhas:
                    for procurar, substituir in substituicoes:
                        linha = linha.replace(procurar, substituir)
                    novo_conteudo.append(linha)
                linhas = novo_conteudo

            # ---- Inserções ----
            if insercoes:
                insercoes_ordenadas = sorted(insercoes, reverse=True)
                for numero_linha, texto in insercoes_ordenadas:
                    if 0 < numero_linha <= len(linhas):
                        linhas.insert(numero_linha - 1, texto + "\n")

            with open(caminho, "w", encoding="utf-8") as f:
                f.writelines(linhas)

            arquivos_processados += 1

    messagebox.showinfo("Concluído", f"{arquivos_processados} arquivos processados.")


# ==========================================
# EDIÇÃO DE CÉLULAS
# ==========================================
def editar_celula(event, tabela):
    item = tabela.identify_row(event.y)
    coluna = tabela.identify_column(event.x)

    if not item:
        return

    x, y, largura, altura = tabela.bbox(item, coluna)
    valor = tabela.set(item, coluna)

    entry = tk.Entry(tabela)
    entry.place(x=x, y=y, width=largura, height=altura)
    entry.insert(0, valor)
    entry.focus()

    def salvar(event):
        tabela.set(item, coluna, entry.get())
        entry.destroy()

    entry.bind("<Return>", salvar)
    entry.bind("<FocusOut>", lambda e: entry.destroy())


def adicionar_linha(tabela):
    tabela.insert("", "end", values=("", ""))


def remover_linha(tabela):
    for item in tabela.selection():
        tabela.delete(item)






def salvar_preset():
    arquivo = filedialog.asksaveasfilename(
        defaultextension=".json",
        filetypes=[("Arquivo JSON", "*.json")],
        title="Salvar Preset"
    )
    if not arquivo:
        return

    dados = {
        "substituicoes": [],
        "insercoes": []
    }

    # Salvar substituições
    for item in tabela_sub.get_children():
        procurar, substituir = tabela_sub.item(item)["values"]
        if procurar != "":
            dados["substituicoes"].append([procurar, substituir])

    # Salvar inserções
    for item in tabela_ins.get_children():
        linha_texto, numero_linha = tabela_ins.item(item)["values"]
        if linha_texto != "" and numero_linha != "":
            dados["insercoes"].append([linha_texto, numero_linha])

    with open(arquivo, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4)

    messagebox.showinfo("Sucesso", "Preset salvo com sucesso!")









def carregar_preset():
    arquivo = filedialog.askopenfilename(
        filetypes=[("Arquivo JSON", "*.json")],
        title="Carregar Preset"
    )
    if not arquivo:
        return

    with open(arquivo, "r", encoding="utf-8") as f:
        dados = json.load(f)

    tabela_sub.delete(*tabela_sub.get_children())
    tabela_ins.delete(*tabela_ins.get_children())

    for procurar, substituir in dados.get("substituicoes", []):
        tabela_sub.insert("", "end", values=(procurar, substituir))

    for linha_texto, numero_linha in dados.get("insercoes", []):
        tabela_ins.insert("", "end", values=(linha_texto, numero_linha))

    messagebox.showinfo("Sucesso", "Preset carregado!")
# ==========================================
# INTERFACE
# ==========================================
root = tk.Tk()
root.title("Editor MPF Industrial")
root.geometry("800x500")

notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)

# ==========================================
# ABA 1 - SUBSTITUIÇÃO
# ==========================================
aba_sub = ttk.Frame(notebook)
notebook.add(aba_sub, text="Substituição")

colunas_sub = ("Procurar", "Substituir")
tabela_sub = ttk.Treeview(aba_sub, columns=colunas_sub, show="headings")

tabela_sub.heading("Procurar", text="Comando a Substituir")
tabela_sub.heading("Substituir", text="Novo Comando")

tabela_sub.column("Procurar", width=350)
tabela_sub.column("Substituir", width=350)

tabela_sub.pack(fill="both", expand=True, padx=10, pady=10)
tabela_sub.bind("<Double-1>", lambda e: editar_celula(e, tabela_sub))

for _ in range(5):
    tabela_sub.insert("", "end", values=("", ""))

frame_sub = ttk.Frame(aba_sub)
frame_sub.pack(pady=5)

ttk.Button(frame_sub, text="Adicionar", command=lambda: adicionar_linha(tabela_sub)).pack(side="left", padx=5)
ttk.Button(frame_sub, text="Remover", command=lambda: remover_linha(tabela_sub)).pack(side="left", padx=5)

# ==========================================
# ABA 2 - INSERÇÃO
# ==========================================
aba_ins = ttk.Frame(notebook)
notebook.add(aba_ins, text="Inserção de Linhas")

colunas_ins = ("Linha a Inserir", "Número da Linha")
tabela_ins = ttk.Treeview(aba_ins, columns=colunas_ins, show="headings")

tabela_ins.heading("Linha a Inserir", text="Linha a Inserir")
tabela_ins.heading("Número da Linha", text="Linha Nº")

tabela_ins.column("Linha a Inserir", width=450)
tabela_ins.column("Número da Linha", width=150)

tabela_ins.pack(fill="both", expand=True, padx=10, pady=10)
tabela_ins.bind("<Double-1>", lambda e: editar_celula(e, tabela_ins))

for _ in range(5):
    tabela_ins.insert("", "end", values=("", ""))

frame_ins = ttk.Frame(aba_ins)
frame_ins.pack(pady=5)

ttk.Button(frame_ins, text="Adicionar", command=lambda: adicionar_linha(tabela_ins)).pack(side="left", padx=5)
ttk.Button(frame_ins, text="Remover", command=lambda: remover_linha(tabela_ins)).pack(side="left", padx=5)


frame_preset = ttk.Frame(root)
frame_preset.pack(pady=5)

ttk.Button(frame_preset, text="Salvar Preset", command=salvar_preset).pack(side="left", padx=5)
ttk.Button(frame_preset, text="Carregar Preset", command=carregar_preset).pack(side="left", padx=5)

# ==========================================
# BOTÃO PRINCIPAL
# ==========================================
ttk.Button(root, text="PROCESSAR ARQUIVOS MPF", command=processar_arquivos).pack(pady=10)

root.mainloop()