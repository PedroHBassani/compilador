from collections import defaultdict

grammar = {
    "Program": [["DeclList"]],
    "DeclList": [["Decl", "DeclList"], []],
    "Decl": [["Type", "IDENTIFIER", "DeclRest"]],
    "DeclRest": [["LPAREN", "ParamList", "RPAREN", "Block"],
                 ["ASSIGN", "Expr", "SEMICOLON"],
                 ["SEMICOLON"]],
    "ParamList": [["Param", "ParamListRest"], []],
    "ParamListRest": [["COMMA", "Param", "ParamListRest"], []],
    "Param": [["Type", "IDENTIFIER"]],
    "Type": [["INT"], ["FLOAT"], ["VOID"]],
    "Block": [["LBRACE", "StmtList", "RBRACE"]],
    "StmtList": [["Stmt", "StmtList"], []],
    "Stmt": [["ExprStmt"],
             ["IfStmt"],
             ["WhileStmt"],
             ["ReturnStmt"],
             ["Block"]],
    "ExprStmt": [["Expr", "SEMICOLON"], ["SEMICOLON"]],
    "IfStmt": [["IF", "LPAREN", "Expr", "RPAREN", "Stmt", "ElsePart"]],
    "ElsePart": [["ELSE", "Stmt"], []],
    "WhileStmt": [["WHILE", "LPAREN", "Expr", "RPAREN", "Stmt"]],
    "ReturnStmt": [["RETURN", "ReturnStmtRest"]],
    "ReturnStmtRest": [["Expr", "SEMICOLON"], ["SEMICOLON"]],
    "Expr": [["Assignment"]],
    "Assignment": [["LogicOr", "AssignmentRest"]],
    "AssignmentRest": [["ASSIGN", "Assignment"], []],
    "LogicOr": [["LogicAnd", "LogicOrRest"]],
    "LogicOrRest": [["OR", "LogicAnd", "LogicOrRest"], []],
    "LogicAnd": [["Equality", "LogicAndRest"]],
    "LogicAndRest": [["AND", "Equality", "LogicAndRest"], []],
    "Equality": [["Relational", "EqualityRest"]],
    "EqualityRest": [["EQUALS", "Relational", "EqualityRest"],
                     ["NOT_EQUALS", "Relational", "EqualityRest"], []],
    "Relational": [["Additive", "RelationalRest"]],
    "RelationalRest": [["LESS_THAN", "Additive", "RelationalRest"],
                       ["LESS_THAN_EQ", "Additive", "RelationalRest"],
                       ["GREATER_THAN", "Additive", "RelationalRest"],
                       ["GREATER_THAN_EQ", "Additive", "RelationalRest"], []],
    "Additive": [["Multiplicative", "AdditiveRest"]],
    "AdditiveRest": [["PLUS", "Multiplicative", "AdditiveRest"],
                    ["MINUS", "Multiplicative", "AdditiveRest"], []],
    "Multiplicative": [["Unary", "MultiplicativeRest"]],
    "MultiplicativeRest": [["MULTIPLY", "Unary", "MultiplicativeRest"],
                          ["DIVIDE", "Unary", "MultiplicativeRest"], []],
    "Unary": [["NOT", "Unary"],
              ["PLUS", "Unary"],
              ["MINUS", "Unary"],
              ["Primary"]],
    "Primary": [["IDENTIFIER", "PrimaryRest"],
                ["LPAREN", "Expr", "RPAREN"],
                ["INTEGER_LITERAL"],
                ["FLOAT_LITERAL"]],
    "PrimaryRest": [["LPAREN", "ArgList", "RPAREN"], []],
    "ArgList": [["Expr", "ArgListRest"], []],
    "ArgListRest": [["COMMA", "Expr", "ArgListRest"], []],
}

non_terminals = set(grammar.keys())
all_symbols = set()
for prods in grammar.values():
    for prod in prods:
        all_symbols.update(prod)
terminals = all_symbols - non_terminals

EPSILON = "ε"

FIRST = defaultdict(set)

def compute_first():
    changed = True
    while changed:
        changed = False
        for nt in non_terminals:
            for production in grammar[nt]:
                if production == []:  # produção vazia
                    if EPSILON not in FIRST[nt]:
                        FIRST[nt].add(EPSILON)
                        changed = True
                    continue

                for sym in production:
                    if sym in terminals:
                        sym_first = {sym}
                    else:
                        sym_first = FIRST[sym]

                    before = len(FIRST[nt])
                    FIRST[nt].update(sym_first - {EPSILON})
                    after = len(FIRST[nt])

                    if EPSILON in sym_first:
                        # continua para o próximo símbolo da produção
                        pass
                    else:
                        break
                else:
                    # todos símbolos produzem epsilon
                    if EPSILON not in FIRST[nt]:
                        FIRST[nt].add(EPSILON)
                        changed = True
                if after > before:
                    changed = True

FOLLOW = defaultdict(set)
start_symbol = "Program"
FOLLOW[start_symbol].add("$")

def compute_follow():
    changed = True
    while changed:
        changed = False
        for nt in non_terminals:
            for production in grammar[nt]:
                for i, B in enumerate(production):
                    if B in non_terminals:
                        beta = production[i+1:]
                        first_beta = set()

                        if beta == []:
                            first_beta.add(EPSILON)
                        else:
                            for sym in beta:
                                if sym in terminals:
                                    sym_first = {sym}
                                else:
                                    sym_first = FIRST[sym]

                                first_beta.update(sym_first - {EPSILON})

                                if EPSILON in sym_first:
                                    continue
                                else:
                                    break
                            else:
                                first_beta.add(EPSILON)

                        before = len(FOLLOW[B])
                        FOLLOW[B].update(first_beta - {EPSILON})

                        if EPSILON in first_beta:
                            FOLLOW[B].update(FOLLOW[nt])

                        after = len(FOLLOW[B])
                        if after > before:
                            changed = True

compute_first()
compute_follow()

def format_set(s):
    return "{" + ", ".join(sorted(sym if sym != EPSILON else "ε" for sym in s)) + "}"

print("Símbolos não-terminais e seus conjuntos FIRST:")
for nt in sorted(non_terminals):
    print(f"FIRST({nt}) = {format_set(FIRST[nt])}")

print("\nSímbolos não-terminais e seus conjuntos FOLLOW:")
for nt in sorted(non_terminals):
    print(f"FOLLOW({nt}) = {format_set(FOLLOW[nt])}")
