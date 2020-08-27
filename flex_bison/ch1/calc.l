/* example 1-5 */
/* recognize tokens for the calculator and print them out */
%{
#include "calc.tab.h"
%}

%%

"+"    {return ADD;}
"-"    {return SUB;}
"*"    {return MUL;}
"/"    {return DIV;}
"|"    {return ABS;}
[0-9]+ {yylval = atoi(yytext); return NUMBER;}
\n     {return EOL;}
[ \t]  { /* NOTHING */}
"("    {return OP;}
")"    {return CP;}
"//".* /* ignore comments */
.      {printf("Mystery character %s\n", yytext);}
%%

