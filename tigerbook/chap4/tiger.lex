%{
#include <string.h>
#include "util.h"
#include "tokens.h"
#include "errormsg.h"

int charPos=1;

int yywrap(void)
{
 charPos=1;
 return 1;
}


void adjust(void)
{
 EM_tokPos=charPos;
 charPos+=yyleng;
}

%}

%x COMMENT

%%
[ \t]+	 {adjust();}
"/*"     {adjust(); BEGIN COMMENT;}
<COMMENT>"*/" {adjust(); BEGIN INITIAL;} /* comments */
<COMMENT>. {adjust();}
\n	 {adjust(); EM_newline();}

","	 |
":"  |
";"  |
"("  |
")"  |
"["  |
"]"  |
"{"  |
"}"  |
"."  |
"+"  |
"-"  |
"*"  |
"/"  |
"&"  |
"|"  {adjust(); return yytext[0];}

"="  {adjust(); return EQ;}
"<>" {adjust(); return NEQ;}
"<"  {adjust(); return LT;}
"<=" {adjust(); return LE;}
">"  {adjust(); return GT;}
">=" {adjust(); return GE;}
":=" {adjust(); return ASSIGN;}

array  	 {adjust(); return ARRAY;} /* KEYWORDS */
if  	 {adjust(); return IF;}
then   {adjust(); return THEN;}
else   {adjust(); return ELSE;}
while  	 {adjust(); return WHILE;}
for  	 {adjust(); return FOR;}
to  	 {adjust(); return TO;}
do  	 {adjust(); return DO;}
let  	 {adjust(); return LET;}
in  	 {adjust(); return IN;}
end  	 {adjust(); return END;}
of  	 {adjust(); return OF;}
break 	{adjust(); return BREAK;}
nil  	 {adjust(); return NIL;}
function  	 {adjust(); return FUNCTION;}
var  	 {adjust(); return VAR;}
type  	 {adjust(); return TYPE;}

[0-9]+	 {adjust(); yylval.ival=atoi(yytext); return INT;}
[_a-zA-Z][_a-zA-Z0-9]* {adjust(); yylval.sval=String(yytext); return ID;}
\"[^\"]*\" {adjust(); yytext[yyleng-1] = 0; yylval.sval=String(yytext+1); return STRING;}
.	 {adjust(); EM_error(EM_tokPos,"illegal token %s", yytext);}


