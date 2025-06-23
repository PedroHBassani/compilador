import ply.yacc as yacc

# Tokens iguais ao do analisador léxico
tokens = (
    'COMMENT', 'WHITESPACE', 'FLOAT_LITERAL', 'INTEGER_LITERAL',
    'IF', 'ELSE', 'WHILE', 'INT', 'FLOAT', 'VOID', 'RETURN',
    'IDENTIFIER', 'NOT', 'AND', 'OR', 'ASSIGN', 'EQUALS', 'NOT_EQUALS',
    'LESS_THAN_EQ', 'GREATER_THAN_EQ', 'LESS_THAN', 'GREATER_THAN',
    'PLUS', 'MINUS', 'MULTIPLY', 'DIVIDE',
    'LPAREN', 'RPAREN', 'LBRACE', 'RBRACE', 'SEMICOLON', 'COMMA'
)

# Símbolo inicial
start = 'Program'

# Lista de erros sintáticos
syntax_errors = []

# Regras da gramática

def p_Program(p):
    'Program : DeclList'

def p_DeclList(p):
    '''DeclList : Decl DeclList
                | empty'''

def p_Decl(p):
    '''Decl : Type IDENTIFIER DeclRest'''

def p_DeclRest(p):
    '''DeclRest : LPAREN ParamList RPAREN Block
                | ASSIGN Expr SEMICOLON
                | SEMICOLON'''

def p_ParamList(p):
    '''ParamList : Param ParamListRest
                 | empty'''

def p_ParamListRest(p):
    '''ParamListRest : COMMA Param ParamListRest
                     | empty'''

def p_Param(p):
    'Param : Type IDENTIFIER'

def p_Type(p):
    '''Type : INT
            | FLOAT
            | VOID'''

def p_Block(p):
    'Block : LBRACE StatementList RBRACE'

def p_StatementList(p):
    '''StatementList : Statement StatementList
                     | empty'''

def p_Statement(p):
    '''Statement : Decl
                 | Expr SEMICOLON
                 | RETURN Expr SEMICOLON
                 | RETURN SEMICOLON
                 | IF LPAREN Expr RPAREN Block ElsePart
                 | WHILE LPAREN Expr RPAREN Block
                 | Block'''

def p_ElsePart(p):
    '''ElsePart : ELSE Block
                | empty'''

def p_Expr(p):
    '''Expr : Expr PLUS Expr
            | Expr MINUS Expr
            | Expr MULTIPLY Expr
            | Expr DIVIDE Expr
            | Expr EQUALS Expr
            | Expr NOT_EQUALS Expr
            | Expr LESS_THAN Expr
            | Expr GREATER_THAN Expr
            | Expr LESS_THAN_EQ Expr
            | Expr GREATER_THAN_EQ Expr
            | Expr AND Expr
            | Expr OR Expr
            | NOT Expr
            | LPAREN Expr RPAREN
            | IDENTIFIER ASSIGN Expr
            | IDENTIFIER
            | INTEGER_LITERAL
            | FLOAT_LITERAL
            | FunctionCall'''
    # print(f"Expr: {p[1:]}")  # Debugging line to show the expression being parsed
    p[0] = ('expr', p[1:])  # Store the expression in a tuple for further processing

def p_FunctionCall(p):
    'FunctionCall : IDENTIFIER LPAREN ArgList RPAREN'

def p_ArgList(p):
    '''ArgList : Expr ArgListRest
               | empty'''

def p_ArgListRest(p):
    '''ArgListRest : COMMA Expr ArgListRest
                   | empty'''

def p_empty(p):
    'empty :'
    pass

def p_error(p):
    if p:
        msg = f"Erro sintático na linha {p.lineno}: Token inesperado '{p.value}'"
    else:
        msg = "Erro sintático: Fim de arquivo inesperado"
    syntax_errors.append(msg)
    raise SyntaxError(msg)  # <-- lança exceção para interromper parsing

# Constroi o parser
parser = yacc.yacc(debug=True)
