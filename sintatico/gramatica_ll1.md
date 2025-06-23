# Gramática LL1 para a Linguagem CompCCUno

## Tokens
COMMENT, WHITESPACE, FLOAT_LITERAL, INTEGER_LITERAL, IF, ELSE, WHILE, INT, FLOAT, VOID, RETURN, IDENTIFIER, NOT, AND, OR, ASSIGN, EQUALS, NOT_EQUALS, LESS_THAN_EQ, GREATER_THAN_EQ, LESS_THAN, GREATER_THAN, PLUS, MINUS, MULTIPLY, DIVIDE, LPAREN, RPAREN, LBRACE, RBRACE, SEMICOLON, COMMA

## Definições
ε representa produção vazia

## Símbolo inicial
Program → DeclList

## Declarações e definições
DeclList → Decl DeclList 
Decl → Type IDENTIFIER DeclRest  
DeclRest → LPAREN ParamList RPAREN Block | ASSIGN Expr SEMICOLON | SEMICOLON  

ParamList → Param ParamListRest | ε  
ParamListRest → COMMA Param ParamListRest | ε  
Param → Type IDENTIFIER  

Type → INT | FLOAT | VOID  

## Blocos e comandos
Block → LBRACE StmtList RBRACE  
StmtList → Stmt StmtList | ε  
Stmt → ExprStmt  
      | IfStmt  
      | WhileStmt  
      | ReturnStmt  
      | Block  

ExprStmt → Expr SEMICOLON | SEMICOLON  
IfStmt → IF LPAREN Expr RPAREN Stmt ElsePart  
ElsePart → ELSE Stmt | ε  
WhileStmt → WHILE LPAREN Expr RPAREN Stmt  
ReturnStmt → RETURN ReturnStmtRest
ReturnStmtRest → Expr SEMICOLON | SEMICOLON

## Expressões
Expr → Assignment  

Assignment → LogicOr AssignmentRest
AssignmentRest → ASSIGN Assignment | ε

LogicOr → LogicAnd LogicOrRest  
LogicOrRest → OR LogicAnd LogicOrRest | ε  

LogicAnd → Equality LogicAndRest  
LogicAndRest → AND Equality LogicAndRest | ε  

Equality → Relational EqualityRest  
EqualityRest → (EQUALS | NOT_EQUALS) Relational EqualityRest | ε  

Relational → Additive RelationalRest  
RelationalRest → (LESS_THAN | LESS_THAN_EQ | GREATER_THAN | GREATER_THAN_EQ) Additive RelationalRest | ε  

Additive → Multiplicative AdditiveRest  
AdditiveRest → (PLUS | MINUS) Multiplicative AdditiveRest | ε  

Multiplicative → Unary MultiplicativeRest  
MultiplicativeRest → (MULTIPLY | DIVIDE) Unary MultiplicativeRest | ε  

Unary → (NOT | PLUS | MINUS) Unary | Primary  
Primary → IDENTIFIER PrimaryRest  
         | LPAREN Expr RPAREN  
         | INTEGER_LITERAL  
         | FLOAT_LITERAL  
PrimaryRest → LPAREN ArgList RPAREN | ε  

ArgList → Expr ArgListRest | ε  
ArgListRest → COMMA Expr ArgListRest | ε

## Conjuntos First

| Não-Terminal      | Conjunto First                                                                                             |
|-------------------|------------------------------------------------------------------------------------------------------------|
| Program           | { INT, FLOAT, VOID, ε }                                                                                    |
| DeclList          | { INT, FLOAT, VOID, ε }                                                                                    |
| Decl              | { INT, FLOAT, VOID }                                                                                       |
| DeclRest          | { LPAREN, ASSIGN, SEMICOLON }                                                                              |
| ParamList         | { INT, FLOAT, VOID, ε }                                                                                    |
| ParamListRest     | { COMMA, ε }                                                                                               |
| Param             | { INT, FLOAT, VOID }                                                                                       |
| Type              | { INT, FLOAT, VOID }                                                                                       |
| Block             | { LBRACE }                                                                                                 |
| StmtList          | { `First(Stmt)`, ε }                                                                                       |
| Stmt              | { `First(Expr)`, SEMICOLON, IF, WHILE, RETURN, LBRACE }                                                    |
| ExprStmt          | { `First(Expr)`, SEMICOLON }                                                                               |
| IfStmt            | { IF }                                                                                                     |
| ElsePart          | { ELSE, ε }                                                                                                |
| WhileStmt         | { WHILE }                                                                                                  |
| ReturnStmt        | { RETURN }                                                                                                 |
| ReturnStmtRest    | { `First(Expr)`, SEMICOLON }                                                                               |
| Expr              | { `First(Primary)`, NOT, PLUS, MINUS }                                                                     |
| Assignment        | { `First(Expr)` }                                                                                          |
| AssignmentRest    | { ASSIGN, ε }                                                                                              |
| ... (demais expressões) | { `First(Primary)`, NOT, PLUS, MINUS }                                                                     |
| Primary           | { IDENTIFIER, LPAREN, INTEGER_LITERAL, FLOAT_LITERAL }                                                     |

## Conjuntos Follow

| Não-Terminal      | Conjunto Follow                                                                                            |
|-------------------|------------------------------------------------------------------------------------------------------------|
| Program           | { $ }                                                                                                      |
| DeclList          | { $ }                                                                                                      |
| Decl              | { INT, FLOAT, VOID, $ }                                                                                    |
| StmtList          | { RBRACE }                                                                                                 |
| Stmt              | { `First(Stmt)`, RBRACE, ELSE }                                                                            |
| ElsePart          | { `Follow(Stmt)` }                                                                                         |
| Expr              | { SEMICOLON, RPAREN, COMMA }                                                                               |
| Assignment        | { `Follow(Expr)` }                                                                                         |
| AssignmentRest    | { `Follow(Assignment)` }                                                                                   |
| LogicOr           | { ASSIGN, `Follow(Assignment)` }                                                                           |
| LogicAnd          | { OR, `Follow(LogicOr)` }                                                                                  |
| Equality          | { AND, `Follow(LogicAnd)` }                                                                                |
| Relational        | { EQUALS, NOT_EQUALS, `Follow(Equality)` }                                                                 |
| Additive          | { LESS_THAN, LESS_THAN_EQ, GREATER_THAN, GREATER_THAN_EQ, `Follow(Relational)` }                           |
| Multiplicative    | { PLUS, MINUS, `Follow(Additive)` }                                                                        |
| Unary             | { MULTIPLY, DIVIDE, `Follow(Multiplicative)` }                                                             |
| Primary           | { `Follow(Unary)` }                                                                                        |

*Nota: A Tabela de Análise Sintática (Parsing Table) foi omitida deste documento por ser muito extensa, mas está implementada diretamente no código do analisador sintático (`sintatico/parsing_data.py`).*

## Exemplo de Código para Validação

```c
int main() {
    int numeroInteiro = 5;
    float numeroFlutuante = 3.14;
    if (numeroInteiro <= 10) {
        numeroInteiro = numeroInteiro + 2;
    } else {
        numeroInteiro = numeroInteiro - 2;
    }
    while (numeroInteiro < 20 && numeroFlutuante >= 0.0) {
        numeroInteiro = numeroInteiro + 1;
        numeroFlutuante = numeroFlutuante - 0.5;
    }
    return 0;
}
```
}
```
