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

/*
*
*  END of UTILITY FUNCTIONS
*  
*/

int maxargs(A_stm stm);

int MAX(int n1, int n2)
{   
    return n1 > n2 ? n1 : n2;
}

/* Question 1 */

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
int max_exp(A_exp exp)
{
    int max = 0;
    int n1, n2;
    char opchar[] = {'+','-','*', '/'};

    inc_level();

    switch (exp->kind) {
    case A_eseqExp:
        log("exp.eseq\n");
        n1 = maxargs(exp->u.eseq.stm);
        n2 = max_exp(exp->u.eseq.exp);
        max = MAX(n1, n2);
        break;
    case A_idExp:
        log("exp.id %s\n", exp->u.id);
        break;
    case A_numExp:
        log("exp.num %d\n", exp->u.num);
        break;
    case A_opExp:
        log("exp.op %c\n", opchar[exp->u.op.oper]);
        n1 = max_exp(exp->u.op.left);
        n2 = max_exp(exp->u.op.right);
        max = MAX(n1, n2);
        break;
    default:
        log("ERR: unknown exp\n");
    }

    //log("[max %d]\n", max);
    dec_level();
    return max;
}

/*
struct A_expList_ {enum {A_pairExpList, A_lastExpList} kind;
                   union {struct {A_exp head; A_expList tail;} pair;
                          A_exp last;
                         } u;
                  };
*/
int max_elist(A_expList elist, void *output)
{
    int max, n1, n2;
    max = 0;

    inc_level();

    if (output)
        *((int*)output) += 1;
    switch (elist->kind) {
    case A_pairExpList:
        log("elist.pair\n");
        n1 = max_exp(elist->u.pair.head);
        n2 = max_elist(elist->u.pair.tail, output);
        max = MAX(n1, n2);
        break;
    case A_lastExpList:
        log("elist.last\n");
        max = max_exp(elist->u.last);
        break;
    default:
        log("ERR: unknown exp list\n");
    }

    //log("[max %d]\n", max);
    dec_level();
    return max;
}

/*
struct A_stm_ {enum {A_compoundStm, A_assignStm, A_printStm} kind;
             union {struct {A_stm stm1, stm2;} compound;
                    struct {string id; A_exp exp;} assign;
                    struct {A_expList exps;} print;
                   } u;
            };
*/
int maxargs(A_stm stm)
{
    int max = 0;
    int n1, n2;
    
    inc_level();

    switch (stm->kind) {
    case A_compoundStm: 
        log("stm.compound ;\n");
        n1 = maxargs(stm->u.compound.stm1);
        n2 = maxargs(stm->u.compound.stm2);
        max = MAX(n1, n2);
        break;
    case A_assignStm: 
        log("stm.assign :=\n");
        inc_level();
        log("id %s\n", stm->u.assign.id);
        dec_level();
        max = max_exp(stm->u.assign.exp);        
        break;
    case A_printStm: 
        log("stm.print print\n");
        int cnt = 0;
        max_elist(stm->u.print.exps, (void*)&cnt);
        max = cnt;
        break;
    default: 
        log("ERR: unkonwn stm\n");
        max = -1;
    } //switch

    //log("[max %d]\n", max);
    dec_level();
    return max;
}


/* Question 2 */
void interp(A_stm stm)
{

}

int main()
{
    printf("max args: %d\n", maxargs(prog()));

    return 0;
}