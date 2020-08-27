/* Example 1-1 */
/* run: flex wc.l; cc lex.yy.c -ll */
%{
int chars = 0;
int words = 0;
int lines = 0;
%}

%%

[a-zA-Z]+ { words++; chars += strlen(yytext); }
\n { chars++; lines++; }
.  { chars++; }

%%

main(int argc, char **argv)
{
yylex();
printf("%8d%8d%8d\n", lines, words, chars);
}
