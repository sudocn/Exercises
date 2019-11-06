
delim [ \t\n]
ws {delim}+
letter [_A-Za-z]
digi [0-9]
id {letter}({letter}|{digi})*
number {digi}+(\.{digi}+)?([Ee][+-]?{digi}+)?

%%
 /* {ws} {} */
int	{printf("float");}
{id} {printf("%s", yytext);}

%%

main()
{
 yylex();
}
