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

table_t global_table;
#define INIT_ENV()    {global_table = Table("HEAD", 0); INIT_LIST_HEAD(&global_table->list);}
#define LOOKUP(id)      lookup(id, global_table)

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
action_t* get_action(enum action_type at, int sub_type)
{
    action_t *pa = NULL;
    if (at == ACTION_STM)
        pa = &semantic_actions.stm[sub_type];
    else if (at == ACTION_EXP)
        pa = &semantic_actions.exp[sub_type];
    else if (at == ACTION_ELIST)
        pa = &semantic_actions.elist[sub_type];
    else if (at == ACTION_BINOP)
        pa = &semantic_actions.binop[sub_type];
    else
        log("ERR: unknown action type");

    return pa;
}

int set_action(enum action_type at, int sub_type,  action_t *action)
{
    action_t *pa = get_action(at, sub_type);
    if (pa) {
        pa->opaque = action->opaque;
        pa->action = action->action;
        return 0;
    } else
        return -1;
}

void clr_action(enum action_type at, int sub_type)
{
    action_t act = {NULL, NULL};
    set_action(at, sub_type, &act);
}

#define _TRIGGER_ACT(type, sub_type, env, act_time) \
do { \
    action_t *pact = get_action(type, (int)sub_type); \
    if (pact && pact->action) \
        pact->action(env, act_time); \
} while (0)

#define TRIGGER_PRE_ACT(type, sub_type, env) _TRIGGER_ACT(type, sub_type, env, ACTION_TIME_PRE)
#define TRIGGER_POST_ACT(type, sub_type, env) _TRIGGER_ACT(type, sub_type, env, ACTION_TIME_POST)

/*
 *
 * 
 * 
 * 
 * 
 */


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
    TRIGGER_PRE_ACT(ACTION_EXP, exp->kind, env);

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

    TRIGGER_POST_ACT(ACTION_EXP, exp->kind, env);
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
    TRIGGER_PRE_ACT(ACTION_ELIST, elist->kind, env);

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

    TRIGGER_POST_ACT(ACTION_ELIST, elist->kind, env);
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

    TRIGGER_PRE_ACT(ACTION_STM, (int)stm->kind, env);

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
        do_elist(stm->u.print.exps, env);
        break;
    default: 
        log("ERR: unkonwn stm\n");
        r = -1;
    } //switch

    TRIGGER_POST_ACT(ACTION_STM, stm->kind, env);
    dec_level();
    return r;
}


/* 
 *   Question 1
 */

int action_print_stm(table_t env, enum action_time time) 
{
    log("[%s:%d - %s]\n", __FUNCTION__, __LINE__, time==ACTION_TIME_PRE?"pre":"post");
    if (!env)
        return 0;
    
    if (time == ACTION_TIME_PRE) {
        table_add(Table(String("__print_args"), 0), env);
    } else if (time == ACTION_TIME_POST) {
        table_t t = LOOKUP("__print_args");
        log("[print w/ %d args]\n", t->value);
        //list_add(&t->list, (struct list_head *)env);
    }
    return 0;
}

int action_elist(table_t env, enum action_time time){
    log("[%s:%d - %s]\n", __FUNCTION__, __LINE__, time==ACTION_TIME_PRE?"pre":"post");
    if (!env)
        return 0;

    if (time == ACTION_TIME_PRE) {

    } else if (time == ACTION_TIME_POST) {
        table_t t = LOOKUP("__print_args");
        if (t) {
            t->value += 1;
            log("[argc++]\n");
        }
    } 
    return 0;
}

int maxargs(A_stm stm)
{
    int max = -1;
    LIST_HEAD(print_li); // = Table("HDR", 0, NULL);
    action_t elist_act = {NULL, action_elist};

    set_action(ACTION_ELIST, A_pairExpList, &elist_act);
    set_action(ACTION_ELIST, A_lastExpList, &elist_act);

    action_t prt_act = {NULL, action_print_stm};
    set_action(ACTION_STM, A_printStm, &prt_act);
    
    do_stm(stm, global_table);
    
    table_t p;
    list_for_each_entry(p, &global_table->list, list) {
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

    INIT_ENV();
    printf("global_table %p\n", global_table);
    table_t t = LOOKUP("HEAD");
    if (t)
        printf("%s %d\n", t->id, t->value);

    printf("max args: %d\n", maxargs(prog()));

    table_dump(global_table);
    return 0;
}