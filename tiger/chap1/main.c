#include <stdio.h>
#include <string.h>
#include "tree.h"
#include "log.h"
#include "table.h"
#include "prog1.h"

/*
*
*  UTILITY FUNCTIONS
*  
*/

int MAX(int n1, int n2)
{   
    return n1 > n2 ? n1 : n2;
}


/*
*
*  Common Logic
*  
*/

typedef struct {
    struct list_head list;
    union {
        int i;
        void *p;
    };
} item_t;

item_t *Item()
{
    item_t *p = checked_malloc(sizeof(item_t));
    return p;
}

enum action_time { ACTION_TIME_PRE, ACTION_TIME_POST, ACTION_TIME_MED};
typedef int (* action_func_t )(table_t, enum action_time);
typedef struct  {
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

int set_action(enum action_type at, int at2,  action_t *action)
{
    action_t *pa = get_action(at, at2);
    if (pa) {
        pa->opaque = action->opaque;
        pa->action = action->action;
        return 0;
    } else
        return -1;
}

void clr_action(enum action_type at, int at2)
{
    action_t act = {NULL, NULL};
    set_action(at, at2, &act);
}


int do_stm(A_stm stm, table_t env);

/*
struct A_exp_ {enum {A_idExp, A_numExp, A_opExp, A_eseqExp} kind;
             union {string id;
                    int num;
                    struct {A_exp left; A_binop oper; A_exp right;} op;
                    struct {A_stm stm; A_exp exp;} eseq;
                   } u;
            };
*/
int do_exp(A_exp exp, table_t env)
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
        pact->action(env, ACTION_TIME_POST);

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
int do_elist(A_expList elist, table_t env)
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
        pact->action(env, ACTION_TIME_POST);

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
int do_stm(A_stm stm, table_t env)
{
    int r = 0;
    
    if (stm->kind != A_compoundStm && 
        stm->kind != A_assignStm &&
        stm->kind != A_printStm) {
        log("ERR: unknown stm\n");
        return -1;
    }
    
    inc_level();

    action_t *pact = get_action(ACTION_ELIST, (int)stm->kind);
    item_t *it = Item();
    if (pact && pact->action)
        pact->action((void*)it, ACTION_TIME_PRE);

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
        //do_elist(stm->u.print.exps, (void*)&cnt);
        break;
    default: 
        log("ERR: unkonwn stm\n");
        r = -1;
    } //switch

    if (pact && pact->action)
        pact->action((void*)it, ACTION_TIME_POST);

    dec_level();
    return r;
}


/* 
 *   Question 1
 */

int action_print_stm(table_t env, enum action_time time) 
{
    if (!env)
        return 0;
    
    if (time == ACTION_TIME_PRE) {
        log("[action print - pre]");
        ((item_t*)env)->i = 0;
    } else if (time == ACTION_TIME_POST) {
        int cnt;
        log("[action print - post]");
        log("[print w/ %d args]\n", cnt);
        table_t t = Table("print", cnt);
        //list_add(&t->list, (struct list_head *)env);
    }
    return 0;
}
int action_inc_para_count(table_t env, enum action_time time){
    if (!env)
        return 0;

    if (time == ACTION_TIME_PRE) {

    } else if (time == ACTION_TIME_POST) {
        *((int*)env) += 1;
        log("[argc++]\n");
    } 
    return 0;
}

int maxargs(A_stm stm)
{
    int max = -1;
    LIST_HEAD(print_li); // = Table("HDR", 0, NULL);
    action_t elist_act = {NULL, action_inc_para_count};

    set_action(ACTION_ELIST, A_pairExpList, &elist_act);
    set_action(ACTION_ELIST, A_lastExpList, &elist_act);
    
    do_stm(stm, (void*)&print_li);
    
    table_t p;
    list_for_each_entry(p, &print_li, list) {
        printf("pr %s %d\n", p->id, p->value);
        if (p->value > max)
            max = p->value;
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
    tree_node_t *node;

}


/*  Main */
int main()
{
    /*
    LIST_HEAD(tab);
    
    table_t te = Table(String("a"), 1);
    list_add(&te->list, &tab);
    te = Table(String("b"), 2);
    list_add(&te->list, &tab);
    te = Table(String("c"), 3);
    list_add(&te->list, &tab);

    list_for_each_entry(te, &tab, list) {
        printf("%s %d\n", te->id, te->value);

    }
    */

    printf("max args: %d\n", maxargs(prog()));

    return 0;
}