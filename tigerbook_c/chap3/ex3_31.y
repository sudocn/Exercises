%{
int yylex(void);
void yyerror(char *s) { EM_error(EM_tokPos, "%s", s); } %}
%token ID WHILE BEGIN END DO IF THEN ELSE SEMI ASSIGN %start prog
%%
prog: stmlist
stm : ID ASSIGN ID
| WHILE ID DO stm
| BEGIN stmlist END
| IF ID THEN stm
| IF ID THEN stm ELSE stm
stmlist : stm
| stmlist SEMI stm
