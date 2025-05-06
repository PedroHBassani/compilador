## 4. Tabela de Transição (Simplificada)

Esta tabela representa uma visão simplificada das transições do AFD. As colunas representam categorias de caracteres de entrada. As linhas representam os estados (alguns estados intermediários e de aceitação foram omitidos ou combinados para brevidade). `ACC` indica aceitação do token anterior e reinício, `SKIP` ignora e continua, `ERR` indica erro.

| Estado      | Letra/`_` | Dígito | `.`  | `/`  | `*`  | `=`  | `<`  | `>`  | `!`  | `+`,`-` | `(`,`)`,`,`{`,`}`,`;` | WS   | Outro |
| :---------- | :-------- | :----- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :------ | :------------------- | :--- | :---- |
| **START**   | ID        | INT    | ERR  | OP/S | OP\* | OP=S | OP<S | OP>S | OP!S | OP      | SEP                  | SKIP | ERR   |
| **ID**      | ID        | ID     | ACC  | ACC  | ACC  | ACC  | ACC  | ACC  | ACC  | ACC     | ACC                  | ACC  | ACC   |
| **INT**     | ACC       | INT    | FLTP | ACC  | ACC  | ACC  | ACC  | ACC  | ACC  | ACC     | ACC                  | ACC  | ACC   |
| **FLTP**    | ERR       | FLT    | ERR  | ERR  | ERR  | ERR  | ERR  | ERR  | ERR  | ERR     | ERR                  | ERR  | ERR   |
| **FLT**     | ACC       | FLT    | ACC  | ACC  | ACC  | ACC  | ACC  | ACC  | ACC  | ACC     | ACC                  | ACC  | ACC   |
| **OP/S**    | ACC       | ACC    | ACC  | LCOM | BCOM | ACC  | ACC  | ACC  | ACC  | ACC     | ACC                  | ACC  | ACC   |
| **OP=S**    | ACC       | ACC    | ACC  | ACC  | ACC  | OP== | ACC  | ACC  | ACC  | ACC     | ACC                  | ACC  | ACC   |
| **OP<S**    | ACC       | ACC    | ACC  | ACC  | ACC  | OP<= | ACC  | ACC  | ACC  | ACC     | ACC                  | ACC  | ACC   |
| **OP>S**    | ACC       | ACC    | ACC  | ACC  | ACC  | OP>= | ACC  | ACC  | ACC  | ACC     | ACC                  | ACC  | ACC   |
| **OP!S**    | ACC       | ACC    | ACC  | ACC  | ACC  | OP!= | ACC  | ACC  | ERR  | ACC     | ACC                  | ACC  | ERR   |
| **LCOM**    | LCOM      | LCOM   | LCOM | LCOM | LCOM | LCOM | LCOM | LCOM | LCOM | LCOM    | LCOM                 | START| LCOM  |
| **BCOM**    | BCOM      | BCOM   | BCOM | BCOM | BCOM*| BCOM | BCOM | BCOM | BCOM | BCOM    | BCOM                 | BCOM | BCOM  |
| **BCOM***   | BCOM      | BCOM   | BCOM | START| BCOM*| BCOM | BCOM | BCOM | BCOM | BCOM    | BCOM                 | BCOM | BCOM  |
| **OP\***, **OP**, **SEP** | ACC       | ACC    | ACC  | ACC  | ACC  | ACC  | ACC  | ACC  | ACC  | ACC     | ACC                  | ACC  | ACC   |
| **OP==,!=,<=,>=**| ACC       | ACC    | ACC  | ACC  | ACC  | ACC  | ACC  | ACC  | ACC  | ACC     | ACC                  | ACC  | ACC   |
| **SKIP**    | START     | START  | START| START| START| START| START| START| START| START   | START                | SKIP | START |
| **ERR**     | ERR       | ERR    | ERR  | ERR  | ERR  | ERR  | ERR  | ERR  | ERR  | ERR     | ERR                  | ERR  | ERR   |

*Nota: Esta tabela é uma abstração. A implementação real usando ER ou código condicional lida com muitas dessas transições implicitamente.*


Tabela de transição

| Estado Atual | Entrada           | Próximo Estado |
| ------------ | ----------------- | -------------- |
| q0           | letra, \_         | q1             |
| q0           | dígito            | q2             |
| q0           | /                 | q5             |
| q0           | =                 | q8             |
| q0           | <                 | q10            |
| q0           | >                 | q12            |
| q0           | !                 | q14            |
| q0           | +, -, \*          | q16            |
| q0           | (, ), {, }, ;, ,  | q17            |
| q0           | WS                | q18            |
| q0           | .                 | q\_err         |
| q0           | Outro             | q\_err         |
| q1           | letra, dígito, \_ | q1             |
| q1           | Outro             | q1\_acc        |
| q2           | dígito            | q2             |
| q2           | .                 | q3             |
| q2           | Outro             | q2\_acc        |
| q3           | dígito            | q4             |
| q3           | Outro             | q\_err         |
| q4           | dígito            | q4             |
| q4           | Outro             | q4\_acc        |
| q5           | /                 | q6             |
| q5           | \*                | q7             |
| q5           | Outro             | q16            |
| q6           | Não-\n            | q6             |
| q6           | \n                | q0             |
| q7           | \*                | q7a            |
| q7           | Não-\*            | q7             |
| q7a          | /                 | q0             |
| q7a          | \*                | q7a            |
| q7a          | Não-/,\*          | q7             |
| q8           | =                 | q9             |
| q8           | Outro             | q16            |
| q10          | =                 | q11            |
| q10          | Outro             | q16            |
| q12          | =                 | q13            |
| q12          | Outro             | q16            |
| q14          | =                 | q15            |
| q14          | Outro             | q\_err         |
| q18          | WS                | q18            |
| q18          | Outro             | q0             |
