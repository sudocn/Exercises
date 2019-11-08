
delim [ \t\n]
ws {delim}+

%%

{ws}	{printf( " ");}

%%

main()
{
 yylex();
}
