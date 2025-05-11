import re
import tkinter as tk
from tkinter import scrolledtext
from tkinter import ttk
import tkinter.font as tkFont

# Definição dos tokens usando expressões regulares
token_specification = [
    ('COMMENT',       r'(//.*)|(/\*[\s\S]*?\*/)'),
    ('WHITESPACE',    r'\s+'),
    ('FLOAT_LITERAL', r'\d+\.\d+'),
    ('INTEGER_LITERAL', r'\d+'),
    ('IF',            r'\bif\b'),
    ('ELSE',          r'\belse\b'),
    ('WHILE',         r'\bwhile\b'),
    ('INT',           r'\bint\b'),
    ('FLOAT',         r'\bfloat\b'),
    ('VOID',          r'\bvoid\b'),
    ('RETURN',        r'\breturn\b'),
    ('IDENTIFIER',    r'[a-zA-Z_][a-zA-Z0-9_]*'),
    ('NOT',           r'!'),
    ('AND',           r'&&'),
    ('OR',            r'\|\|'),
    ('ASSIGN',        r'='),
    ('EQUALS',        r'=='),
    ('NOT_EQUALS',    r'!='),
    ('LESS_THAN_EQ',  r'<='),
    ('GREATER_THAN_EQ',r'>='),
    ('LESS_THAN',     r'<'),
    ('GREATER_THAN',  r'>'),
    ('PLUS',          r'\+'),
    ('MINUS',         r'-'),
    ('MULTIPLY',      r'\*'),
    ('DIVIDE',        r'/'),
    ('LPAREN',        r'\('),
    ('RPAREN',        r'\)'),
    ('LBRACE',        r'\{'),
    ('RBRACE',        r'\}'),
    ('SEMICOLON',     r';'),
    ('COMMA',         r','),
    ('ERROR',         r'.'), # Tudo que não se encaixa nos padrões acima
]

# Compila as expressões regulares
token_regex = '|'.join(f'(?P<{pair[0]}>{pair[1]})' for pair in token_specification)
get_token = re.compile(token_regex).match

def analyze(code):
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
            if value.startswith('/*'):
                line_num += value.count('\n')
        elif kind == 'ERROR':
            errors.append(f"Erro léxico na linha {line_num}: Caractere inválido '{value}'")
            if value == '\n':
                 line_num += 1
        else:
            token = (kind, value, line_num)
            tokens_found.append(token)
            if kind == 'IDENTIFIER' and value not in symbol_table:
                symbol_table[value] = {'type': 'identifier', 'line': line_num}

        current_pos = end

    return tokens_found, symbol_table, errors

# Função para atualizar os números das linhas
def update_line_numbers(*args):
    line_numbers.config(state=tk.NORMAL)
    line_numbers.delete('1.0', tk.END)
    try:
        num_lines = code_input.index('end-1c').split('.')[0]
        line_numbers_string = "\n".join(str(i) for i in range(1, int(num_lines) + 1))
    except tk.TclError:
        line_numbers_string = "1"
    except ValueError:
        line_numbers_string = "1"
    line_numbers.insert('1.0', line_numbers_string)
    line_numbers.config(state=tk.DISABLED)
    try:
        line_numbers.yview_moveto(code_input.yview()[0])
    except tk.TclError:
        pass

# Função para sincronizar a rolagem vertical
def sync_scroll(*args):
    line_numbers.yview_moveto(args[0])
    code_input.yview_moveto(args[0])
    update_line_numbers()

# Função chamada quando o conteúdo do code_input muda
def on_content_changed(event=None):
    update_line_numbers()
    root.after(1, update_line_numbers)


def run_analysis():
    source_code = code_input.get("1.0", tk.END)

    tokens_output.config(state=tk.NORMAL)
    symbol_table_output.config(state=tk.NORMAL)
    errors_output.config(state=tk.NORMAL)
    tokens_output.delete("1.0", tk.END)
    symbol_table_output.delete("1.0", tk.END)
    errors_output.delete("1.0", tk.END)

    tokens, symbols, errors_list = analyze(source_code)

    tokens_output.insert(tk.END, "--- Tokens Reconhecidos ---\n")
    if tokens:
        for token in tokens:
            tokens_output.insert(tk.END, f"Tipo: {token[0]:<15} Lexema: {token[1]:<15} Linha: {token[2]}\n")
    else:
        tokens_output.insert(tk.END, "Nenhum token reconhecido.\n")

    symbol_table_output.insert(tk.END, "--- Tabela de Símbolos (Identificadores) ---\n")
    if symbols:
        for name, info in symbols.items():
             symbol_table_output.insert(tk.END, f"Nome: {name:<15} Info: {info}\n")
    else:
        symbol_table_output.insert(tk.END, "Nenhum identificador encontrado.\n")

    errors_output.insert(tk.END, "--- Relatório de Erros ---\n")
    if errors_list:
        for error in errors_list:
            errors_output.insert(tk.END, f"{error}\n")
    else:
        errors_output.insert(tk.END, "Nenhum erro léxico encontrado.\n")

    tokens_output.config(state=tk.DISABLED)
    symbol_table_output.config(state=tk.DISABLED)
    errors_output.config(state=tk.DISABLED)


# Configuração da janela principal
root = tk.Tk()
root.title("Analisador Léxico")
root.geometry("800x700")

# Estilo
style = ttk.Style()
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
                       background='lightgrey', state=tk.DISABLED, wrap=tk.NONE,
                       font=("Courier New", 10))
line_numbers.grid(row=0, column=0, sticky='ns')

# Widget de entrada de código
code_input = scrolledtext.ScrolledText(input_frame, wrap=tk.WORD, height=15,
                                              font=("Courier New", 10), undo=True)
code_input.grid(row=0, column=1, sticky='nsew')

# Código padrão
default_code = """/*
  Exemplo de Código para Análise Léxica
  Este código demonstra o uso de todos os tokens definidos.
*/

// Comentário de linha

/*
  Comentário
  de
  bloco
*/

int main() {
    // Declarações e inicializações
    int numeroInteiro = 123;
    float numeroFlutuante = 45.67;
    void funcaoSemRetorno; // Embora 'void' seja mais para funções

    // Estruturas de controle
    if (numeroInteiro > 100) {
        numeroInteiro = numeroInteiro - 10;
    } else {
        numeroInteiro = numeroInteiro + 10;
    }

    while (numeroInteiro < 150 && numeroFlutuante >= 40.0) {
        numeroInteiro = numeroInteiro + 1;
        if (numeroInteiro == 130 || numeroFlutuante < 42.0) {
            numeroFlutuante = numeroFlutuante + 0.5;
        }
    }

    // Operadores
    int a = 5;
    int b = 10;
    int soma = a + b;
    int subtracao = b - a;
    int multiplicacao = a * b;
    int divisao = b / a; // Divisão inteira
    float divisaoFlutuante = 10.0 / 4.0;

    // Operadores de comparação e lógicos
    if (a < b && b > 0) {
        // Verdadeiro
    }
    if (a <= 5 || b >= 10) {
        // Verdadeiro
    }
    if (a == b) {
        // Falso
    }
    if (a != b) {
        // Verdadeiro
    }
    if (!(a > b)) { // NOT
        // Verdadeiro
    }

    // Atribuição
    a = 20;

    // Chamada de função e retorno
    // outraFuncao(numeroInteiro, numeroFlutuante);
    return 0;

    // Erros léxicos intencionais para teste
    int @variavelInvalida = 1;
    float $outroErro = 2.0;
    # Comentário inválido
}

// Outra função de exemplo
void outraFuncao(int param1, float param2) {
    int resultado = param1 * 2;
    // return; // Retorno opcional para void
}
"""
code_input.insert('1.0', default_code)
code_input.edit_reset()

# Configura a sincronização de rolagem
scrollbar = code_input.vbar
code_input['yscrollcommand'] = lambda *args: (scrollbar.set(*args), sync_scroll(*args))

# Vincula eventos para atualizar números de linha
code_input.bind('<KeyRelease>', on_content_changed)
code_input.bind('<MouseWheel>', on_content_changed)
code_input.bind('<<Paste>>', on_content_changed)
code_input.bind('<<Cut>>', on_content_changed)
code_input.bind('<Configure>', on_content_changed)

# --- Botão de Análise ---
analyze_button = ttk.Button(main_frame, text="Analisar Código", command=run_analysis)
analyze_button.pack(pady=10)

# --- Seção de Saída ---
output_frame = ttk.Frame(main_frame)
output_frame.pack(fill=tk.BOTH, expand=True)

output_frame.columnconfigure(0, weight=1)
output_frame.rowconfigure(1, weight=1)

# Abas para os resultados
notebook = ttk.Notebook(output_frame)

# Frame e ScrolledText para Tokens
tokens_frame = ttk.Frame(notebook, padding="5")
tokens_label = ttk.Label(tokens_frame, text="Tokens Reconhecidos:")
tokens_label.pack(anchor=tk.W)
tokens_output = scrolledtext.ScrolledText(tokens_frame, wrap=tk.WORD, height=10, state=tk.DISABLED, font=("Courier New", 9))
tokens_output.pack(fill=tk.BOTH, expand=True)

# Frame e ScrolledText para Tabela de Símbolos
symbols_frame = ttk.Frame(notebook, padding="5")
symbols_label = ttk.Label(symbols_frame, text="Tabela de Símbolos:")
symbols_label.pack(anchor=tk.W)
symbol_table_output = scrolledtext.ScrolledText(symbols_frame, wrap=tk.WORD, height=10, state=tk.DISABLED, font=("Courier New", 9))
symbol_table_output.pack(fill=tk.BOTH, expand=True)

# Frame e ScrolledText para Erros
errors_frame = ttk.Frame(notebook, padding="5")
errors_label = ttk.Label(errors_frame, text="Relatório de Erros:")
errors_label.pack(anchor=tk.W)
errors_output = scrolledtext.ScrolledText(errors_frame, wrap=tk.WORD, height=10, state=tk.DISABLED, font=("Courier New", 9))
errors_output.pack(fill=tk.BOTH, expand=True)

# Adiciona os frames como abas no Notebook
notebook.add(tokens_frame, text='Tokens')
notebook.add(symbols_frame, text='Tabela de Símbolos')
notebook.add(errors_frame, text='Erros')

notebook.pack(fill=tk.BOTH, expand=True)

# Atualiza os números de linha inicialmente
on_content_changed()

# Inicia o loop principal da GUI
root.mainloop()

