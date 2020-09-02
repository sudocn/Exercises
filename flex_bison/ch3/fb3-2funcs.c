#include <stdio.h>
#include <stdlib.h>
#include <stdarg.h>
#include <string.h>
#include <math.h>
#include "fb3-2.h"


void *assure_malloc(size_t s)
{
    void *p = malloc(s);
    if (!p) {
        yyerror("OOM!");
        exit(1);
    }
    return p;
}

static unsigned symhash(char *sym)
{
    unsigned int hash = 0;
    unsigned c;

    while (c = *sym++)
        hash = hash * 9 ^ c;

    return hash;
}

struct symbol * lookup(char *sym)
{
    struct symbol *sp = &symtab[symhash(sym)%NHASH];
    int scount = NHASH;

    while (--scount >= 0) {
        if (sp->name && !strcmp(sp->name, sym))
            return sp;
        
        if (!sp->name) {
            sp->name = strdup(sym);
            sp->value = 0;
            sp->func = NULL;
            sp->syms = NULL;
            return sp;
        }

        if (++sp >= symtab + NHASH)
            sp = symtab;
    }
    yyerror("symbol table overflow\n");
    abort();
}

struct ast *newast(int nodetype, struct ast *l, struct ast *r)
{
    struct ast *a = assure_malloc(sizeof(struct ast));

    a->nodetype = nodetype;
    a->l = l;
    a->r = r;
    return a;
}

struct ast *newnum(double d)
{
    struct numval *a = assure_malloc(sizeof(struct numval));

    a->nodetype = 'K';
    a->number = d;
    return (struct ast*)a;
}

struct ast *newcmp(int cmptype, struct ast *l, struct ast *r)
{
    struct ast *a = assure_malloc(sizeof(struct ast));

    a->nodetype = '0' + cmptype;
    a->l = l;
    a->r = r;
    return a;
}

struct ast *newfunc(int functype, struct ast *l)
{
    struct fncall *a = assure_malloc(sizeof(struct fncall));

    a->nodetype = 'F';
    a->l = l;
    a->functype = functype;
    return (struct ast*)a;
}

struct ast *newcall(struct symbol *s, struct ast *l)
{
    struct ufncall *a = assure_malloc(sizeof(struct ufncall));

    a->nodetype = 'C';
    a->l = l;
    a->s = s;
    return (struct ast*)a;
}

struct ast *newref(struct symbol *s)
{
    struct symref *a = assure_malloc(sizeof(struct symref));

    a->nodetype = 'N';
    a->s = s;
    return (struct ast*)a;
}

struct ast *newasgn(struct symbol *s, struct ast *v)
{
    struct symasgn *a = assure_malloc(sizeof(struct symasgn));

    a->nodetype = '=';
    a->s = s;
    a->v = v;
    return (struct ast*)a;
}

struct ast *newflow(int nodetype, struct ast *cond, struct ast *tl, struct ast *el)
{
    struct flow *a = assure_malloc(sizeof(struct flow));

    a->nodetype = 'nodetype';
    a->cond = cond;
    a->tl = tl;
    a->el = el;
    return (struct ast*)a;
}

void treefree(struct ast *a)
{
    switch (a->nodetype){
    case '+':
    case '-':
    case '*':
    case '/':
    case '1':
    case '2':
    case '3':
    case '4':
    case '5':
    case '6':
        treefree(a->r);
        /* fall through */
    case '|':
    case 'M':
    case 'C':
    case 'F':
        treefree(a->l);
        /* fall through */
    case 'K':
    case 'N':
        break;
    case '=':
        free(((struct symasn *)a)->v);
        break;
    case 'I':
    case 'W':
        free(((struct flow*)a)->cond);
        if (((struct flow*)a)->tl)
            treefree(((struct flow*)a)->tl);
        if (((struct flow*)a)->el)
            treefree(((struct flow*)a)->el);
        break;
    default:
        printf("internal error: free bad node %c\n", a->nodetype);
    }
    free(a);
}

struct symlist *newsymlist(struct symbol *sym, struct symlist *next)
{
    struct symlist *sl = assure_malloc(sizeof(struct symlist));

    sl->sym = sym;
    sl->next = next;
    return sl;
}

void symlistfree(struct symlist *sl)
{
    struct symlist *nsl;
    while (sl) {
        nsl = sl->next;
        free(sl);
        sl = nsl;
    }
}

/*********************************************/

double eval(struct ast *a)
{
    double v;

    switch (a->nodetype) {
    case 'K': 
        v = ((struct numval *)a)->number;
        break;
    case '+':
        v = eval(a->l) + eval(a->r); 
        break;
    case '-':
        v = eval(a->l) - eval(a->r); 
        break;
    case '*':
        v = eval(a->l) * eval(a->r); 
        break;
    case '/':
        v = eval(a->l) / eval(a->r); 
        break;
    case '|':
        v = eval(a->l);
        if (v < 0)
            v = -v; 
        break;
    case 'M':
        v = -eval(a->l);
        break;
    }
    return v;
}

void yyerror(char *s, ...)
{
    va_list ap;
    va_start(ap, s);
    fprintf(stderr, "%d: error: ", yylineno);
    vfprintf(stderr, s, ap);
    fprintf(stderr, "\n");
}

extern int yydebug;
int main()
{
    yydebug =1;
    printf("> ");
    return yyparse();
}