# Projeto do Analisador Léxico (AL) do Mini Compilador

Este documento detalha o projeto do analisador léxico conforme os requisitos da seção 1.2.1.

## 1. Definição e Descrição dos Tokens

Os seguintes tokens são reconhecidos pela linguagem do mini compilador:

*   **`COMMENT`**: Comentários de linha (iniciados por `//`) ou de bloco (delimitados por `/*` e `*/`). São reconhecidos mas ignorados para análise posterior.
*   **`WHITESPACE`**: Sequências de espaços, tabulações (`\t`) e novas linhas (`\n`). São reconhecidos mas ignorados para análise posterior, exceto pela contagem de linhas.
*   **`FLOAT_LITERAL`**: Literais numéricos de ponto flutuante (ex: `3.14`, `10.0`, `0.5`). Consistem em um ou mais dígitos, seguidos por um ponto (`.`), seguido por um ou mais dígitos.
*   **`INTEGER_LITERAL`**: Literais numéricos inteiros (ex: `123`, `0`, `42`). Consistem em um ou mais dígitos.
*   **`KEYWORD`**: Palavras reservadas da linguagem com significado fixo. Inclui: `if`, `else`, `while`, `int`, `float`, `void`, `return`.
*   **`IDENTIFIER`**: Nomes definidos pelo programador para variáveis, funções, etc. Devem começar com uma letra (a-z, A-Z) ou underscore (`_`), seguidos por zero ou mais letras, dígitos (0-9) ou underscores.
*   **`OPERATOR`**: Símbolos que representam operações. Inclui: `==`, `!=`, `<=`, `>=`, `+`, `-`, `*`, `/`, `=`, `<`, `>`.
*   **`SEPARATOR`**: Símbolos usados para agrupar ou separar elementos do código. Inclui: `(`, `)`, `{`, `}`, `;`, `,`.
*   **`ERROR`**: Qualquer caractere que não se encaixe em nenhuma das categorias acima. Indica um erro léxico.

## 2. Especificação dos Tokens com Expressões Regulares (ER)

As expressões regulares usadas para especificar cada token são (conforme implementado em Python):

*   **`COMMENT`**: `(//.*)|(/\*[\s\S]*?\*/)`
*   **`WHITESPACE`**: `\s+`
*   **`FLOAT_LITERAL`**: `\d+\.\d+`
*   **`INTEGER_LITERAL`**: `\d+`
*   **`KEYWORD`**: `\b(if|else|while|int|float|void|return)\b` (Verificado após identificar um `IDENTIFIER`)
*   **`IDENTIFIER`**: `[a-zA-Z_][a-zA-Z0-9_]*`
*   **`OPERATOR`**: `==|!=|<=|>=|\+|-|\*|/|=|<|>` (A ordem é importante para garantir que `==` seja reconhecido antes de `=`)
*   **`SEPARATOR`**: `\(|\)|\{|\}|;|,`
*   **`ERROR`**: `.` (Qualquer caractere único não correspondido pelas regras anteriores)

## 3. Reconhecimento por Autômato Finito Determinístico (AFD) - Descrição

Um AFD para reconhecer esses tokens teria, conceitualmente, os seguintes estados e transições:

1.  **`START` (Estado Inicial):** O estado inicial. Lê o próximo caractere.
    *   Se for letra ou `_`, transita para `IN_IDENTIFIER`.
    *   Se for dígito, transita para `IN_INTEGER`.
    *   Se for `/`, transita para `MAYBE_COMMENT_OR_DIVIDE`.
    *   Se for `=`, transita para `MAYBE_EQUAL_OR_ASSIGN`.
    *   Se for `<`, transita para `MAYBE_LESS_OR_LE`.
    *   Se for `>`, transita para `MAYBE_GREATER_OR_GE`.
    *   Se for `!`, transita para `MAYBE_NOT_EQUAL`.
    *   Se for `+`, `-`, `*`, transita para `ACCEPT_OPERATOR` (estado final).
    *   Se for `(`, `)`, `{`, `}`, `;`, `,`, transita para `ACCEPT_SEPARATOR` (estado final).
    *   Se for espaço, `\t`, `\n`, transita para `IN_WHITESPACE`.
    *   Se for `.`, transita para `ERROR_STATE` (ou poderia iniciar um float se a regra fosse diferente).
    *   Qualquer outro caractere, transita para `ACCEPT_ERROR` (estado final).

2.  **`IN_IDENTIFIER`:** Está lendo um identificador.
    *   Se for letra, dígito ou `_`, permanece em `IN_IDENTIFIER`.
    *   Qualquer outro caractere: Transita para `ACCEPT_IDENTIFIER` (estado final, consome o identificador lido até agora) e o caractere atual é reprocessado a partir do estado `START`.

3.  **`IN_INTEGER`:** Está lendo um inteiro.
    *   Se for dígito, permanece em `IN_INTEGER`.
    *   Se for `.`, transita para `MAYBE_FLOAT`.
    *   Qualquer outro caractere: Transita para `ACCEPT_INTEGER` (estado final) e o caractere atual é reprocessado a partir de `START`.

4.  **`MAYBE_FLOAT`:** Leu um inteiro seguido de um ponto.
    *   Se for dígito, transita para `IN_FLOAT`.
    *   Qualquer outro caractere: Indica um erro ou fim do token inteiro (depende da especificação exata, na nossa ER atual, o `.` seria um erro se não seguido por dígito após um número). Na implementação atual com ER, `\d+\.\d+` trata isso diretamente. Um AFD precisaria de mais estados ou lógica de lookahead/backtracking. Para simplificar, vamos assumir que a ER lida com isso. Se fôssemos modelar estritamente: caractere inválido aqui levaria a aceitar o inteiro anterior e tratar o `.` como erro.

5.  **`IN_FLOAT`:** Está lendo a parte decimal de um float.
    *   Se for dígito, permanece em `IN_FLOAT`.
    *   Qualquer outro caractere: Transita para `ACCEPT_FLOAT` (estado final) e o caractere atual é reprocessado a partir de `START`.

6.  **`MAYBE_COMMENT_OR_DIVIDE`:** Leu um `/`.
    *   Se for `/`, transita para `IN_LINE_COMMENT`.
    *   Se for `*`, transita para `IN_BLOCK_COMMENT`.
    *   Qualquer outro caractere: Transita para `ACCEPT_OPERATOR` (aceita `/` como divisão) e o caractere atual é reprocessado a partir de `START`.

7.  **`IN_LINE_COMMENT`:** Está dentro de um comentário de linha.
    *   Se for `\n`, transita para `START` (fim do comentário).
    *   Qualquer outro caractere: Permanece em `IN_LINE_COMMENT`.

8.  **`IN_BLOCK_COMMENT`:** Está dentro de um comentário de bloco.
    *   Se for `*`, transita para `MAYBE_END_BLOCK_COMMENT`.
    *   Qualquer outro caractere: Permanece em `IN_BLOCK_COMMENT`.

9.  **`MAYBE_END_BLOCK_COMMENT`:** Leu um `*` dentro de um comentário de bloco.
    *   Se for `/`, transita para `START` (fim do comentário).
    *   Se for `*`, permanece em `MAYBE_END_BLOCK_COMMENT`.
    *   Qualquer outro caractere: Retorna para `IN_BLOCK_COMMENT`.

10. **`MAYBE_EQUAL_OR_ASSIGN`:** Leu um `=`.
    *   Se for `=`, transita para `ACCEPT_OPERATOR` (aceita `==`).
    *   Qualquer outro caractere: Transita para `ACCEPT_OPERATOR` (aceita `=`) e o caractere atual é reprocessado a partir de `START`.

11. **`MAYBE_LESS_OR_LE`:** Leu um `<`.
    *   Se for `=`, transita para `ACCEPT_OPERATOR` (aceita `<=`).
    *   Qualquer outro caractere: Transita para `ACCEPT_OPERATOR` (aceita `<`) e o caractere atual é reprocessado a partir de `START`.

12. **`MAYBE_GREATER_OR_GE`:** Leu um `>`.
    *   Se for `=`, transita para `ACCEPT_OPERATOR` (aceita `>=`).
    *   Qualquer outro caractere: Transita para `ACCEPT_OPERATOR` (aceita `>`) e o caractere atual é reprocessado a partir de `START`.

13. **`MAYBE_NOT_EQUAL`:** Leu um `!`.
    *   Se for `=`, transita para `ACCEPT_OPERATOR` (aceita `!=`).
    *   Qualquer outro caractere: Transita para `ACCEPT_ERROR` (pois `!` sozinho não é um operador válido) e o caractere atual é reprocessado a partir de `START`.

14. **`IN_WHITESPACE`:** Está lendo whitespace.
    *   Se for espaço, `\t`, `\n`, permanece em `IN_WHITESPACE`.
    *   Qualquer outro caractere: Transita para `START` (ignora o whitespace acumulado) e o caractere atual é reprocessado.

15. **Estados Finais (`ACCEPT_*`):** Indicam que um token foi reconhecido. O token é registrado (ou ignorado, como no caso de `COMMENT` e `WHITESPACE`), e a análise recomeça do estado `START` com o próximo caractere não consumido (ou o caractere que causou a saída do estado anterior, se aplicável).

16. **`ERROR_STATE`:** Estado alcançado por transições inválidas não explicitamente tratadas (embora a regra `ERROR` na ER simplifique isso).

## 4. Diagrama do AFD

O diagrama visual do Autômato Finito Determinístico (AFD) descrito acima pode ser gerado a partir do arquivo `afd_lexico.dot`.
