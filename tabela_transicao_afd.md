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
