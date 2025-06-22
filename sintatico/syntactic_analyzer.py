# -*- coding: utf-8 -*-

from parsing_data import terminals, non_terminals, parsing_table, follow_sets

class SyntacticAnalyzer:
    def __init__(self, tokens):
        self.tokens = tokens
        if not self.tokens or self.tokens[-1][0] != '$':
            self.tokens.append(('$', '$', -1))  # Marcador de fim de arquivo
        self.token_index = 0
        self.stack = ['$', 'Program']
        self.errors = []

    def current_token(self):
        return self.tokens[self.token_index]

    def advance(self):
        if self.token_index < len(self.tokens) - 1:
            self.token_index += 1

    def parse(self):
        while len(self.stack) > 1: # Continua enquanto a pilha não estiver vazia (exceto pelo '$')
            top = self.stack[-1]
            token_type, lexeme, line = self.current_token()

            if top in terminals:
                if top == token_type:
                    self.stack.pop()
                    self.advance()
                else:
                    self.report_error(f"Esperado '{top}', mas encontrado '{lexeme}'")
                    # Modo Pânico: Pop da pilha, mas não avança o token, deixa o não-terminal lidar
                    self.stack.pop()
            elif top in non_terminals:
                try:
                    production = parsing_table[top][token_type]
                    self.stack.pop()
                    if production[0] != 'ε':
                        for symbol in reversed(production):
                            self.stack.append(symbol)
                except KeyError:
                    self.report_error(f"Entrada inesperada '{lexeme}' ao processar '{top}'")
                    self.panic_mode(top)
            else: # Símbolo não é terminal nem não-terminal (ex: 'ε')
                self.stack.pop()


        if self.current_token()[0] != '$' and not self.errors:
             self.report_error("Código extra encontrado após o final do programa.")

        if not self.errors:
            print("Análise sintática concluída com sucesso.")
        
        return self.errors

    def report_error(self, message):
        token_type, lexeme, line = self.current_token()
        if line != -1:
            error_message = f"Erro sintático na linha {line}: {message}"
        else:
            error_message = f"Erro sintático no final do arquivo: {message}"
        
        if error_message not in self.errors:
            self.errors.append(error_message)

    def panic_mode(self, non_terminal):
        # Descarta tokens até encontrar um que esteja no conjunto Follow do não-terminal
        follow = follow_sets.get(non_terminal, set())
        follow.add('$') # Sempre podemos sincronizar no final do arquivo

        token_type, _, _ = self.current_token()
        while token_type not in follow:
            self.advance()
            token_type, _, _ = self.current_token()
            if token_type == '$': # Para evitar loop infinito
                break
        
        # Remove o não-terminal da pilha para continuar a análise
        if self.stack and self.stack[-1] == non_terminal:
             self.stack.pop()


def analyze_syntax(tokens):
    """
    Função principal para iniciar a análise sintática.
    Recebe uma lista de tokens do analisador léxico.
    Retorna uma lista de erros sintáticos.
    """
    analyzer = SyntacticAnalyzer(tokens)
    errors = analyzer.parse()
    return errors

if __name__ == '__main__':
    #
    # Para testar seu código, modifique a lista de tokens abaixo.
    # Esta lista simula a saída de um analisador léxico.
    # Cada tupla representa um token: (TIPO, 'lexema', linha)
    #
    
    # --- Exemplo de código válido para teste ---
    # int main() { int x = 5; return x; }
    sample_tokens = [
        ('INT', 'int', 1),
        ('IDENTIFIER', 'main', 1),
        ('LPAREN', '(', 1),
        ('RPAREN', ')', 1),
        ('LBRACE', '{', 1),
        ('INT', 'int', 2),
        ('IDENTIFIER', 'x', 2),
        ('ASSIGN', '=', 2),
        ('INTEGER_LITERAL', '5', 2),
        ('SEMICOLON', ';', 2),
        ('RETURN', 'return', 3),
        ('IDENTIFIER', 'x', 3),
        ('SEMICOLON', ';', 3),
        ('RBRACE', '}', 4),
    ]

    print("--- Teste com código válido ---")
    errors = analyze_syntax(sample_tokens)

    if errors:
        print("\nErros sintáticos encontrados:")
        for error in errors:
            print(error)
    else:
        # A mensagem de sucesso já é impressa pela função parse()
        pass

    print("\n--- Teste com código inválido ---")
    # Código inválido: "int main( { ... }" (faltando um ')' )
    invalid_tokens = [
        ('INT', 'int', 1),
        ('IDENTIFIER', 'main', 1),
        ('LPAREN', '(', 1),
        # 'RPAREN' está faltando aqui
        ('LBRACE', '{', 1),
        ('RBRACE', '}', 2),
    ]
    errors_invalid = analyze_syntax(invalid_tokens)
    if errors_invalid:
        print("\nErros sintáticos encontrados (esperado):")
        for error in errors_invalid:
            print(error)
