/* example 1-3 */
/* recognize tokens for the calculator and print them out */
%%
"+"    {printf("PLUS\n");}
"-"    {printf("MINUS\n");}
"*"    {printf("TIMES\n");}
"/"    {printf("DIVIDE\n");}
"|"    {printf("ABS\n");}
[0-9]+ {printf("NUMBER %s\n", yytext);}
\n     {printf("NEWLINE\n");}
[ \t]  { /* NOTHING */}
.      {printf("Mystery character %s\n", yytext);}
%%
