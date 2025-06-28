from collections import defaultdict
import json

grammar = {
    "Program": [["DeclList"]],
    "DeclList": [["Decl", "DeclList"], ["ε"]],
    "Decl": [["Type", "IDENTIFIER", "DeclRest"]],
    "DeclRest": [["LPAREN", "ParamList", "RPAREN", "Block"],
                 ["ASSIGN", "Expr", "SEMICOLON"],
                 ["SEMICOLON"]],
    "ParamList": [["Param", "ParamListRest"], ["ε"]],
    "ParamListRest": [["COMMA", "Param", "ParamListRest"], ["ε"]],
    "Param": [["Type", "IDENTIFIER"]],
    "Type": [["INT"], ["FLOAT"], ["VOID"]],
    "Block": [["LBRACE", "StmtList", "RBRACE"]],
    "StmtList": [["Stmt", "StmtList"], ["ε"]],
    "Stmt": [["ExprStmt"], ["IfStmt"], ["WhileStmt"], ["ReturnStmt"], ["Block"]],
    "ExprStmt": [["Expr", "SEMICOLON"], ["SEMICOLON"]],
    "IfStmt": [["IF", "LPAREN", "Expr", "RPAREN", "Stmt", "ElsePart"]],
    "ElsePart": [["ELSE", "Stmt"], ["ε"]],
    "WhileStmt": [["WHILE", "LPAREN", "Expr", "RPAREN", "Stmt"]],
    "ReturnStmt": [["RETURN", "ReturnStmtRest"]],
    "ReturnStmtRest": [["Expr", "SEMICOLON"], ["SEMICOLON"]],
    "Expr": [["Assignment"]],
    "Assignment": [["LogicOr", "AssignmentRest"]],
    "AssignmentRest": [["ASSIGN", "Assignment"], ["ε"]],
    "LogicOr": [["LogicAnd", "LogicOrRest"]],
    "LogicOrRest": [["OR", "LogicAnd", "LogicOrRest"], ["ε"]],
    "LogicAnd": [["Equality", "LogicAndRest"]],
    "LogicAndRest": [["AND", "Equality", "LogicAndRest"], ["ε"]],
    "Equality": [["Relational", "EqualityRest"]],
    "EqualityRest": [["EQUALS", "Relational", "EqualityRest"],
                     ["NOT_EQUALS", "Relational", "EqualityRest"], ["ε"]],
    "Relational": [["Additive", "RelationalRest"]],
    "RelationalRest": [["LESS_THAN", "Additive", "RelationalRest"],
                       ["LESS_THAN_EQ", "Additive", "RelationalRest"],
                       ["GREATER_THAN", "Additive", "RelationalRest"],
                       ["GREATER_THAN_EQ", "Additive", "RelationalRest"], ["ε"]],
    "Additive": [["Multiplicative", "AdditiveRest"]],
    "AdditiveRest": [["PLUS", "Multiplicative", "AdditiveRest"],
                     ["MINUS", "Multiplicative", "AdditiveRest"], ["ε"]],
    "Multiplicative": [["Unary", "MultiplicativeRest"]],
    "MultiplicativeRest": [["MULTIPLY", "Unary", "MultiplicativeRest"],
                           ["DIVIDE", "Unary", "MultiplicativeRest"], ["ε"]],
    "Unary": [["NOT", "Unary"], ["PLUS", "Unary"], ["MINUS", "Unary"], ["Primary"]],
    "Primary": [["IDENTIFIER", "PrimaryRest"], ["LPAREN", "Expr", "RPAREN"],
                ["INTEGER_LITERAL"], ["FLOAT_LITERAL"]],
    "PrimaryRest": [["LPAREN", "ArgList", "RPAREN"], ["ε"]],
    "ArgList": [["Expr", "ArgListRest"], ["ε"]],
    "ArgListRest": [["COMMA", "Expr", "ArgListRest"], ["ε"]],
}

# Terminais conhecidos
terminals = {
    "COMMENT", "WHITESPACE", "FLOAT_LITERAL", "INTEGER_LITERAL", "IF", "ELSE", "WHILE",
    "INT", "FLOAT", "VOID", "RETURN", "IDENTIFIER", "NOT", "AND", "OR", "ASSIGN",
    "EQUALS", "NOT_EQUALS", "LESS_THAN_EQ", "GREATER_THAN_EQ", "LESS_THAN", "GREATER_THAN",
    "PLUS", "MINUS", "MULTIPLY", "DIVIDE", "LPAREN", "RPAREN", "LBRACE", "RBRACE",
    "SEMICOLON", "COMMA", "ε", "$"
}
non_terminals = set(grammar.keys())

# FIRST e FOLLOW
first = defaultdict(set)
follow = defaultdict(set)

# --- Cálculo do FIRST ---
changed = True
while changed:
    changed = False
    for head, productions in grammar.items():
        for production in productions:
            # Regra 3: Se X -> Y1Y2...Yk, então FIRST(X) inclui FIRST(Y1) (exceto ε)
            for symbol in production:
                if symbol in terminals:
                    if symbol not in first[head]:
                        first[head].add(symbol)
                        changed = True
                    break
                # symbol is non-terminal
                for f in first[symbol]:
                    if f != 'ε' and f not in first[head]:
                        first[head].add(f)
                        changed = True
                if 'ε' not in first[symbol]:
                    break
            else:
                # Regra 2: Se X -> ε ou X -> Y1Y2...Yk e todos os Yi -> ε, então ε está em FIRST(X)
                if 'ε' not in first[head]:
                    first[head].add('ε')
                    changed = True


# --- Cálculo do FOLLOW ---
start_symbol = "Program"
follow[start_symbol].add("$")

for _ in range(len(non_terminals) * 2): # Iterar para garantir a convergência
    for head, productions in grammar.items():
        for production in productions:
            trailer = follow[head].copy()
            for i in reversed(range(len(production))):
                symbol = production[i]
                if symbol in non_terminals:
                    # Regra 2: A -> αBβ, então FOLLOW(B) inclui FIRST(β) - {ε}
                    if not trailer.issubset(follow[symbol]):
                         follow[symbol].update(trailer)
                    # Regra 3: A -> αB ou A -> αBβ onde FIRST(β) contém ε
                    if 'ε' in trailer:
                        for f in follow[head]:
                            if f not in follow[symbol]:
                                follow[symbol].add(f)
                
                # Atualiza o trailer para o próximo símbolo à esquerda
                if symbol in non_terminals and 'ε' in first[symbol]:
                    trailer.update(t for t in first[symbol] if t != 'ε')
                elif symbol in non_terminals:
                    trailer = first[symbol].copy()
                else: # Terminal
                    trailer = {symbol}

# FIRST de uma sequência
def first_of_sequence(symbols):
    result = set()
    epsilon_in_all = True
    for sym in symbols:
        sym_first = first[sym] if sym in non_terminals else {sym}
        result.update(sym_first - {"ε"})
        if "ε" not in sym_first:
            epsilon_in_all = False
            break
    if epsilon_in_all:
        result.add("ε")
    return result

# TABELA LL(1)
ll1_table = defaultdict(dict)
for head, productions in grammar.items():
    for production in productions:
        production_first = first_of_sequence(production)
        for terminal in production_first - {"ε"}:
            if terminal in ll1_table[head]:
                print(f"CONFLITO em Tabela[{head}][{terminal}]!")
            ll1_table[head][terminal] = production
        if "ε" in production_first:
            for terminal in follow[head]:
                if terminal in ll1_table[head]:
                   print(f"CONFLITO em Tabela[{head}][{terminal}]!")
                ll1_table[head][terminal] = production

# --- INÍCIO DA SEÇÃO DE EXPORTAÇÃO ---

# Converte o defaultdict para um dict padrão para uma saída JSON mais limpa
regular_ll1_table = {k: v for k, v in ll1_table.items()}

# Define o nome do arquivo de saída
output_filename = 'tabela_ll1.json'

# Escreve o dicionário no arquivo JSON
with open(output_filename, 'w', encoding='utf-8') as json_file:
    # json.dump escreve o objeto no arquivo
    # indent=4 formata o JSON para ser legível
    # ensure_ascii=False garante que caracteres como 'ε' sejam salvos corretamente
    json.dump(regular_ll1_table, json_file, indent=4, ensure_ascii=False)

print(f"\n✅ Tabela LL(1) foi exportada com sucesso para o arquivo: '{output_filename}'")

# --- FIM DA SEÇÃO DE EXPORTAÇÃO ---


# Mostrar resultado no console
print("\n--- Tabela LL(1) no Console ---")
for nt in sorted(ll1_table):
    print(f"\n{nt}:")
    for t in sorted(ll1_table[nt]):
        print(f"  '{t}' -> {ll1_table[nt][t]}")