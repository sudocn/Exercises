#ifndef _TABLE_H_
#define _TABLE_H_

#include "util.h"
#include "log.h"
#include "list.h"

typedef struct __table *table_t;
struct __table {
    struct list_head list;
    string id; 
    int value; 
    //table_t tail;
};

static inline table_t Table(string id, int value)
{
    table_t t = checked_malloc(sizeof(*t)); 
    t->id=id; 
    t->value=value; 
    return t;
}

static inline table_t table_add(table_t item, table_t head)
{
    list_add(&item->list, &head->list);
    return item;
}

static inline table_t lookup(string token, table_t table)
{
    table_t t;
    list_for_each_entry(t, &table->list, list) {
        debug("id %s, v %d\n", t->id, t->value);
        if (!strcmp(t->id, token)) {
            return t;
        }
    }
    return (table_t) NULL;
}

static inline void table_dump(table_t table)
{
    table_t t;
    log("== dump table %s == \n", table->id);
    list_for_each_entry(t, &table->list, list) {
        log("id %s, v %d\n", t->id, t->value);
    }
}
#endif /* _TABLE_H_ */