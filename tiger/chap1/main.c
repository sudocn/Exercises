#include <stdio.h>
#include <stdarg.h>
#include <string.h>
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


/*
*
*  END of UTILITY FUNCTIONS
*  
*/


/*
*
*  Common Logic
*  
*/

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

typedef int (* action_func_t )(void *);
typedef struct _action_t {
    void *opaque;
    action_func_t action;
} action_t;

static struct {
    action_t stm[3];    // A_compoundStm, A_assignStm, A_printStm
    action_t exp[4];      // A_idExp, A_numExp, A_opExp, A_eseqExp
    action_t elist[2];    // A_pairExpList, A_lastExpLists
    action_t binop[4];    // A_plus,A_minus,A_times,A_div
} semantic_actions;

void init_actions(void)
{
    memset(&semantic_actions, 0, sizeof(semantic_actions));
}
enum action_type {ACTION_STM, ACTION_EXP, ACTION_ELIST, ACTION_BINOP} ;
action_t* get_action(enum action_type at, int at2)
{
    action_t *pa = NULL;
    if (at == ACTION_STM)
        pa = &semantic_actions.stm[at2];
    else if (at == ACTION_EXP)
        pa = &semantic_actions.exp[at2];
    else if (at == ACTION_ELIST)
        pa = &semantic_actions.elist[at2];
    else if (at == ACTION_BINOP)
        pa = &semantic_actions.binop[at2];
    else
        log("ERR: unknown action type");

    return pa;
}

int add_action(enum action_type at, int at2,  action_t *action)
{
    action_t *pa = get_action(at, at2);
    if (pa) {
        pa->opaque = action->opaque;
        pa->action = action->action;
        return 0;
    } else
        return -1;
}

int do_stm(A_stm stm, void *env);

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
    action_t *pact;
    char opchar[] = {'+','-','*', '/'};

    if (exp->kind != A_eseqExp &&
        exp->kind != A_idExp &&
        exp->kind != A_numExp &&
        exp->kind != A_opExp) {
        log("ERR: unknown exp\n");
        return -1;
    }

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
    }

    pact = get_action(ACTION_EXP, (int)exp->kind);
    if (pact && pact->action)
        pact->action(env);

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
    
    if (elist->kind != A_pairExpList && 
        elist->kind != A_lastExpList) {
        log("ERR: unknown exp list\n");
        return -1;
    }

    inc_level();


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
    }

    action_t *pact = get_action(ACTION_ELIST, (int)elist->kind);
    if (pact && pact->action)
        pact->action(env);

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
    
    if (stm->kind != A_compoundStm && 
        stm->kind != A_assignStm &&
        stm->kind != A_printStm) {
        log("ERR: unknown stm\n");
        return -1;
    }
    
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


/* 
 *   Question 1
 */

int inc_para_count(void *env){
    if (env) {
        *((int*)env) += 1;
        log("[argc++]\n");
    }
    return 0;
}

int maxargs(A_stm stm)
{
    int max = -1;
    table_t print_li = Table("HDR", 0, NULL);
    action_t elist_act = {NULL, inc_para_count};

    add_action(ACTION_ELIST, A_pairExpList, &elist_act);
    add_action(ACTION_ELIST, A_lastExpList, &elist_act);
    
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