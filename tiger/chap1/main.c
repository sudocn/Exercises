#include <stdio.h>
#include <stdarg.h>
#include "prog1.h"

void log_level(int level, const char* fmt, ...)
{
    char *indent = "    "; // tab indent = 4
	va_list arg_list;
	int my_arg;

	va_start(arg_list, fmt);

	//Print until zero
    /*
	for (my_arg = num_args; my_arg != 0; my_arg = va_arg(arg_list, int))
		printf("%d\n", my_arg);
    */
    for (int i=0; i < level; i++)
        printf("%s", indent);

    vprintf(fmt, arg_list);
	va_end(arg_list);
}

int parse_tree_depth = 0;
#define log(...)   log_level(parse_tree_depth, __VA_ARGS__)
/*inline*/ 
void inc_level() { parse_tree_depth++; };
/*inline*/ 
void dec_level() { parse_tree_depth--; };

int MAX(int n1, int n2)
{   
    return n1 > n2 ? n1 : n2;
}

typedef struct __table *table_t;
struct __table {string id; int value; table_t tail;};
table_t Table(string id, int value, table_t tail) 
{
    table_t t = checked_malloc(sizeof(*t)); 
    t->id=id; 
    t->value=value; 
    t->tail=tail; 
    return t;
}

/*
*
*  END of UTILITY FUNCTIONS
*  
*/

/* 
 *   Question 1
 */

int do_stm(A_stm stm, void *env);

/* max args of an EXP */
/*
struct A_exp_ {enum {A_idExp, A_numExp, A_opExp, A_eseqExp} kind;
             union {string id;
                    int num;
                    struct {A_exp left; A_binop oper; A_exp right;} op;
                    struct {A_stm stm; A_exp exp;} eseq;
                   } u;
            };
*/
int do_exp(A_exp exp, void *env)
{
    int r = 0;
    char opchar[] = {'+','-','*', '/'};

    inc_level();

    switch (exp->kind) {
    case A_eseqExp:
        log("exp.eseq\n");
        do_stm(exp->u.eseq.stm, env);
        do_exp(exp->u.eseq.exp, env);
        break;
    case A_idExp:
        log("exp.id %s\n", exp->u.id);
        break;
    case A_numExp:
        log("exp.num %d\n", exp->u.num);
        break;
    case A_opExp:
        log("exp.op %c\n", opchar[exp->u.op.oper]);
        do_exp(exp->u.op.left, env);
        do_exp(exp->u.op.right, env);
        break;
    default:
        log("ERR: unknown exp\n");
    }

    dec_level();
    return r;
}

/*
struct A_expList_ {enum {A_pairExpList, A_lastExpList} kind;
                   union {struct {A_exp head; A_expList tail;} pair;
                          A_exp last;
                         } u;
                  };
*/
int do_elist(A_expList elist, void *env)
{
    int r;
    r = 0;

    inc_level();

    if (env) {
        *((int*)env) += 1;
        log("[argc++]\n");
    }
    switch (elist->kind) {
    case A_pairExpList:
        log("elist.pair\n");
        do_exp(elist->u.pair.head, env);
        do_elist(elist->u.pair.tail, env);
        break;
    case A_lastExpList:
        log("elist.last\n");
        do_exp(elist->u.last, env);
        break;
    default:
        log("ERR: unknown exp list\n");
    }

    dec_level();
    return r;
}

/*
struct A_stm_ {enum {A_compoundStm, A_assignStm, A_printStm} kind;
             union {struct {A_stm stm1, stm2;} compound;
                    struct {string id; A_exp exp;} assign;
                    struct {A_expList exps;} print;
                   } u;
            };
*/
int do_stm(A_stm stm, void *env)
{
    int r = 0;
    
    inc_level();

    switch (stm->kind) {
    case A_compoundStm: 
        log("stm.compound ;\n");
        do_stm(stm->u.compound.stm1, env);
        do_stm(stm->u.compound.stm2, env);
        break;
    case A_assignStm: 
        log("stm.assign :=\n");
        inc_level();
        log("id %s\n", stm->u.assign.id);
        dec_level();
        do_exp(stm->u.assign.exp, env);        
        break;
    case A_printStm: 
        log("stm.print print\n");
        int cnt = 0;
        do_elist(stm->u.print.exps, (void*)&cnt);
        log("[print w/ %d args]\n", cnt);
        ((table_t)env)->tail = Table("print", cnt, ((table_t)env)->tail);
        break;
    default: 
        log("ERR: unkonwn stm\n");
        r = -1;
    } //switch

    dec_level();
    return r;
}

int maxargs(A_stm stm)
{
    int max = -1;
    table_t print_li = Table("HDR", 0, NULL);
    
    do_stm(stm, (void*)print_li);
    
    table_t p = print_li->tail;
    while (p) {
        printf("pr %s %d %p\n", p->id, p->value, p->tail);
        if (p->value > max)
            max = p->value;
        p = p->tail;
    }
    return max;
}

/* 
 *   Question 2 
 */

void interp_exp(A_exp exp)
{

}

void interp_stm(A_stm stm)
{

}

void interp(A_stm stm)
{

}

/*  Main */
int main()
{
    printf("max args: %d\n", maxargs(prog()));

    return 0;
}