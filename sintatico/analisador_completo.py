import re
import tkinter as tk
from tkinter import scrolledtext, ttk, font as tkFont
import json

# =============================================================================
# 1. ANALISADOR LÉXICO
# =============================================================================

# Definição dos tokens usando expressões regulares
token_specification = [
    ('COMMENT',         r'(//.*)|(/\*[\s\S]*?\*/)'),
    ('WHITESPACE',      r'\s+'),
    ('FLOAT_LITERAL',   r'\d+\.\d+'),
    ('INTEGER_LITERAL', r'\d+'),
    ('IF',              r'\bif\b'),
    ('ELSE',            r'\belse\b'),
    ('WHILE',           r'\bwhile\b'),
    ('INT',             r'\bint\b'),
    ('FLOAT',           r'\bfloat\b'),
    ('VOID',            r'\bvoid\b'),
    ('RETURN',          r'\breturn\b'),
    ('IDENTIFIER',      r'[a-zA-Z_][a-zA-Z0-9_]*'),
    ('NOT',             r'!'),
    ('AND',             r'&&'),
    ('OR',              r'\|\|'),
    ('ASSIGN',          r'='),
    ('EQUALS',          r'=='),
    ('NOT_EQUALS',      r'!='),
    ('LESS_THAN_EQ',    r'<='),
    ('GREATER_THAN_EQ', r'>='),
    ('LESS_THAN',       r'<'),
    ('GREATER_THAN',    r'>'),
    ('PLUS',            r'\+'),
    ('MINUS',           r'-'),
    ('MULTIPLY',        r'\*'),
    ('DIVIDE',          r'/'),
    ('LPAREN',          r'\('),
    ('RPAREN',          r'\)'),
    ('LBRACE',          r'\{'),
    ('RBRACE',          r'\}'),
    ('SEMICOLON',       r';'),
    ('COMMA',           r','),
    ('ERROR',           r'.'), # Tudo que não se encaixa nos padrões acima
]

# Compila as expressões regulares para eficiência
token_regex = '|'.join(f'(?P<{pair[0]}>{pair[1]})' for pair in token_specification)
get_token = re.compile(token_regex).match

def analyze_lexical(code):
    """Executa a análise léxica no código fonte."""
    tokens_found = []
    symbol_table = {}
    errors = []
    line_num = 1
    current_pos = 0
    code_len = len(code)

    while current_pos < code_len:
        match = get_token(code, current_pos)

        if not match:
            char = code[current_pos]
            if not char.isspace():
                errors.append(f"Erro léxico não identificado na linha {line_num}: Caractere inesperado '{char}'")
            if char == '\n':
                line_num += 1
            current_pos += 1
            continue

        kind = match.lastgroup
        value = match.group()
        start, end = match.span()

        if kind == 'WHITESPACE':
            line_num += value.count('\n')
        elif kind == 'COMMENT':
            line_num += value.count('\n')
        elif kind == 'ERROR':
            errors.append(f"Erro léxico na linha {line_num}: Caractere inválido '{value}'")
        else:
            token = (kind, value, line_num)
            tokens_found.append(token)
            if kind == 'IDENTIFIER' and value not in symbol_table:
                symbol_table[value] = {'type': 'identifier', 'line': line_num}

        current_pos = end

    return tokens_found, symbol_table, errors

# =============================================================================
# 2. ANALISADOR SINTÁTICO (VERSÃO FINAL CORRIGIDA - SEM LOOP INFINITO)
# =============================================================================

class AnalisadorSintatico:
    def __init__(self, tabela_parsing):
        self.tabela = tabela_parsing
        if tabela_parsing:
            self.nao_terminais = set(tabela_parsing.keys())
        else:
            self.nao_terminais = set()

    def parse(self, tokens):
        """
        Analisa a lista de tokens com uma estratégia de recuperação de erros robusta 
        que previne loops infinitos.
        """
        entrada = list(tokens)
        last_line = entrada[-1][2] if entrada else 1
        entrada.append(('$', '$', last_line))

        pilha = [('$', None), ('Program', None)]
        erros_sintaticos = []
        
        # O loop principal continua enquanto a pilha não estiver vazia.
        # A condição de sucesso é a pilha conter apenas '$' e a entrada também ser '$'.
        while pilha:
            topo_pilha_tipo, _ = pilha[-1]
            token_atual_tipo, token_atual_valor, token_atual_linha = entrada[0]

            # Condição de Sucesso
            if topo_pilha_tipo == '$':
                if token_atual_tipo == '$':
                    # Fim da análise bem-sucedida
                    return erros_sintaticos
                else:
                    # Erro: Pilha vazia, mas ainda há tokens na entrada
                    erro_msg = f"Erro Sintático na linha {token_atual_linha}: Código continua após o fim esperado do programa."
                    if not erros_sintaticos or erros_sintaticos[-1] != erro_msg:
                        erros_sintaticos.append(erro_msg)
                    return erros_sintaticos

            # Caso 1: Topo da pilha é um terminal
            if topo_pilha_tipo not in self.nao_terminais:
                if topo_pilha_tipo == token_atual_tipo:
                    # Match! Avança na pilha e na entrada.
                    pilha.pop()
                    entrada.pop(0)
                else:
                    # ERRO de terminal não correspondente.
                    erro_msg = f"Erro Sintático na linha {token_atual_linha}: Esperado '{topo_pilha_tipo}', mas encontrou '{token_atual_tipo}'."
                    if not erros_sintaticos or erros_sintaticos[-1] != erro_msg:
                        erros_sintaticos.append(erro_msg)
                    
                    # CORREÇÃO DO LOOP: Descarta o que era esperado da pilha para tentar continuar.
                    pilha.pop()
            
            # Caso 2: Topo da pilha é um não-terminal
            else:
                try:
                    producao = self.tabela[topo_pilha_tipo][token_atual_tipo]
                    pilha.pop()
                    if producao[0] != 'ε':
                        for simbolo in reversed(producao):
                            pilha.append((simbolo, token_atual_linha))
                except KeyError:
                    # ERRO de não-terminal (transição não existe).
                    erro_msg = f"Erro Sintático na linha {token_atual_linha}: Token inesperado '{token_atual_tipo}'."
                    if not erros_sintaticos or erros_sintaticos[-1] != erro_msg:
                        erros_sintaticos.append(erro_msg)

                    # CORREÇÃO DO LOOP: Descarta o token da entrada que causou o erro para garantir progresso.
                    entrada.pop(0)
                    if not entrada: # Segurança caso o erro seja no último token antes do '$'
                        return erros_sintaticos
                    
# =============================================================================
# 3. SETUP DO ANALISADOR E DA GUI
# =============================================================================

# Carregar a tabela de parsing do arquivo JSON
try:
    with open('tabela_parsing.json', 'r', encoding='utf-8') as f:
        tabela_parsing = json.load(f)
except FileNotFoundError:
    print("ERRO CRÍTICO: Arquivo 'tabela_parsing.json' não encontrado!")
    tabela_parsing = {}
except json.JSONDecodeError:
    print("ERRO CRÍTICO: O arquivo 'tabela_parsing.json' não é um JSON válido!")
    tabela_parsing = {}

# Instanciar o analisador sintático com a tabela carregada
analisador_sintatico = AnalisadorSintatico(tabela_parsing)

# --- Funções da Interface Gráfica ---

def run_analysis():
    """Função principal chamada pelo botão 'Analisar Código'."""
    source_code = code_input.get("1.0", tk.END)

    # Limpa as saídas antigas
    for widget in [tokens_output, symbol_table_output, errors_output]:
        widget.config(state=tk.NORMAL)
        widget.delete("1.0", tk.END)

    # --- Análise Léxica ---
    tokens, symbols, lexical_errors = analyze_lexical(source_code)

    # Exibe resultados da Análise Léxica
    tokens_output.insert(tk.END, "--- Tokens Reconhecidos ---\n")
    if tokens:
        for token in tokens:
            tokens_output.insert(tk.END, f"Tipo: {token[0]:<15} Lexema: {token[1]:<15} Linha: {token[2]}\n")

    symbol_table_output.insert(tk.END, "--- Tabela de Símbolos (Identificadores) ---\n")
    if symbols:
        for name, info in symbols.items():
            symbol_table_output.insert(tk.END, f"Nome: {name:<15} Info: {info}\n")

    # --- Análise Sintática ---
    errors_output.insert(tk.END, "--- Relatório de Erros ---\n")
    
    if lexical_errors:
        for error in lexical_errors:
            errors_output.insert(tk.END, f"{error}\n")
        errors_output.insert(tk.END, "\nAnálise sintática não executada devido a erros léxicos.\n")
    elif not tabela_parsing:
        errors_output.insert(tk.END, "Análise sintática não pode ser executada. Tabela de parsing não foi carregada.\n")
    else:
        syntactic_errors = analisador_sintatico.parse(tokens)
        if syntactic_errors:
            errors_output.insert(tk.END, "\n--- Erros Sintáticos ---\n")
            for error in syntactic_errors:
                errors_output.insert(tk.END, f"{error}\n")
        else:
            errors_output.insert(tk.END, "Nenhum erro léxico ou sintático encontrado.\nAnálise concluída com sucesso!")

    # Desabilita a edição das caixas de saída
    for widget in [tokens_output, symbol_table_output, errors_output]:
        widget.config(state=tk.DISABLED)

# --- Funções Auxiliares da GUI (sem alterações) ---

def update_line_numbers(*args):
    line_numbers.config(state=tk.NORMAL)
    line_numbers.delete('1.0', tk.END)
    try:
        num_lines = code_input.index('end-1c').split('.')[0]
        line_numbers_string = "\n".join(str(i) for i in range(1, int(num_lines) + 1))
        line_numbers.insert('1.0', line_numbers_string)
    finally:
        line_numbers.config(state=tk.DISABLED)
        line_numbers.yview_moveto(code_input.yview()[0])

def on_content_changed(event=None):
    update_line_numbers()

# =============================================================================
# 4. CONSTRUÇÃO DA INTERFACE GRÁFICA (GUI)
# =============================================================================

# Configuração da janela principal
root = tk.Tk()
root.title("Analisador Léxico e Sintático")
root.geometry("850x700")
style = ttk.Style(root)
style.theme_use('clam')

# Frame principal
main_frame = ttk.Frame(root, padding="10")
main_frame.pack(fill=tk.BOTH, expand=True)

# --- Seção de Entrada ---
input_frame = ttk.LabelFrame(main_frame, text="Código Fonte", padding="5")
input_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
input_frame.columnconfigure(1, weight=1)
input_frame.rowconfigure(0, weight=1)

# Widget para números de linha
line_numbers = tk.Text(input_frame, width=4, padx=3, takefocus=0, border=0,
                       background='#f0f0f0', state=tk.DISABLED, wrap=tk.NONE,
                       font=("Courier New", 10))
line_numbers.grid(row=0, column=0, sticky='ns')

# Widget de entrada de código
code_input = scrolledtext.ScrolledText(input_frame, wrap=tk.WORD, height=15,
                                       font=("Courier New", 10), undo=True)
code_input.grid(row=0, column=1, sticky='nsew')

# Vincula a rolagem dos números de linha com o texto
code_input.vbar.config(command=lambda *args: (line_numbers.yview(*args), code_input.yview(*args)))
line_numbers.config(yscrollcommand=code_input.vbar.set)

# Vincula eventos para atualizar números de linha
for event_name in ['<KeyRelease>', '<MouseWheel>', '<<Paste>>', '<<Cut>>', '<Configure>']:
    code_input.bind(event_name, on_content_changed)
    
# Código de exemplo
default_code = """int main() {
    int a = 10;
    if (a > 5) {
        a = a + 1;
    }
    return 0;
}

// Teste de erro sintático
float b = 20.5
"""
code_input.insert('1.0', default_code)
on_content_changed()

# --- Botão de Análise ---
analyze_button = ttk.Button(main_frame, text="Analisar Código", command=run_analysis, style='Accent.TButton')
style.configure('Accent.TButton', font=('Segoe UI', 10, 'bold'))
analyze_button.pack(pady=10, ipady=4)

# --- Seção de Saída ---
notebook = ttk.Notebook(main_frame)
notebook.pack(fill=tk.BOTH, expand=True)

# Função para criar abas
def create_tab(parent, title):
    frame = ttk.Frame(parent, padding="5")
    parent.add(frame, text=title)
    output_widget = scrolledtext.ScrolledText(frame, wrap=tk.WORD, height=10, state=tk.DISABLED, font=("Courier New", 9))
    output_widget.pack(fill=tk.BOTH, expand=True)
    return output_widget

tokens_output = create_tab(notebook, 'Tokens')
symbol_table_output = create_tab(notebook, 'Tabela de Símbolos')
errors_output = create_tab(notebook, 'Relatório de Erros')

# Inicia o loop principal da GUI
root.mainloop()