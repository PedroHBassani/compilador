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
DeclRest → LPAREN ParamList RPAREN Block | VarDeclRest  
VarDeclRest → ASSIGN Expr SEMICOLON | SEMICOLON  

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
ReturnStmt → RETURN Expr SEMICOLON | RETURN SEMICOLON  

## Expressões
Expr → Assignment  

Assignment → LogicOr ASSIGN Assignment  
            | LogicOr  

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
