from collections import defaultdict

# --- Gramática da linguagem CompCCUno ---
grammar = {
    "Program": [["DeclList"]],
    "DeclList": [["Decl", "DeclList"]],
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
    "SEMICOLON", "COMMA", "ε"
}
non_terminals = set(grammar.keys())

# FIRST e FOLLOW
first = defaultdict(set)
follow = defaultdict(set)

# FIRST
def compute_first(symbol):
    if symbol in terminals:
        return {symbol}
    if "ε" in first[symbol]:
        return first[symbol]
    for production in grammar[symbol]:
        for sym in production:
            sym_first = compute_first(sym)
            first[symbol].update(sym_first - {"ε"})
            if "ε" not in sym_first:
                break
        else:
            first[symbol].add("ε")
    return first[symbol]

for nt in grammar:
    compute_first(nt)

# FOLLOW
start_symbol = "Program"
follow[start_symbol].add("$")
changed = True
while changed:
    changed = False
    for head, productions in grammar.items():
        for production in productions:
            trailer = follow[head].copy()
            for i in reversed(range(len(production))):
                sym = production[i]
                if sym in non_terminals:
                    if not trailer.issubset(follow[sym]):
                        follow[sym].update(trailer)
                        changed = True
                    if "ε" in first[sym]:
                        trailer = trailer.union(first[sym] - {"ε"})
                    else:
                        trailer = first[sym]
                else:
                    trailer = compute_first(sym)

# FIRST de uma sequência
def first_of_sequence(symbols):
    result = set()
    for sym in symbols:
        sym_first = compute_first(sym)
        result.update(sym_first - {"ε"})
        if "ε" not in sym_first:
            break
    else:
        result.add("ε")
    return result

# TABELA LL(1)
ll1_table = defaultdict(dict)
for head, productions in grammar.items():
    for production in productions:
        production_first = first_of_sequence(production)
        for terminal in production_first - {"ε"}:
            ll1_table[head][terminal] = production
        if "ε" in production_first:
            for terminal in follow[head]:
                ll1_table[head][terminal] = production

# Mostrar resultado
for nt in sorted(ll1_table):
    print(f"{nt}:")
    for t in sorted(ll1_table[nt]):
        print(f"  {t:>20} -> {ll1_table[nt][t]}")
