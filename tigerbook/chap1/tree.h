#ifndef __TREE_H__
#define __TREE_H__
#include "list.h"

struct tree_node_t;

typedef struct tree_node_t {
    struct tree_node_t *sibling;

} tree_node_t;



#endif /* __TREE_H__ */