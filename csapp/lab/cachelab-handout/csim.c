#include <unistd.h>
#include <stdlib.h>
#include <stdio.h>
#include <getopt.h>
#include <string.h>
#include "cachelab.h"

int verbose = 0;

typedef struct {
	long tag;
	char valid;
	unsigned int rank;
	//char lru_head, lru_tail; /* only used by first elem in one associated set */
} cache_line;

struct cache_info_ {
	int set;		/* number of set index bits */
	int block; 		/* number of block bits (line size in bits) */
	int assoc_size;		/* associativity (number of lines per set) */
	unsigned int hit;
	unsigned int miss;
	unsigned int evict;
	cache_line* cache;
} ci;

int set_size(void) { return 1 << ci.set; }
int line_size(void) { return 1 << ci.block; }
int assoc_size(void) { return ci.assoc_size; }

long tag_id(long addr)
{
	return addr >> (ci.set + ci.block);
}

int tag_match(cache_line *p, long addr)
{
	return p->valid  && (p->tag == tag_id(addr));
}

void tag_update(cache_line *p, long addr)
{
	if (p->valid)  {
		printf("warning: update a valid cache line!\n");
	}

	p->tag = tag_id(addr);
	/* printf("   >> tag %lx\n", p->tag); */
	p->valid = 1;
}

long set_id(long addr)
{
	return (addr >> ci.block) & ((long)set_size() - 1);
}

void report_hit(long addr)
{
	printf(" hit");
	ci.hit++;
}

void report_miss(long addr)
{
	printf(" miss");
	ci.miss++;
}

void report_evict(long addr)
{
	printf(" eviction");
	ci.evict++;
}

void cache_dump()
{
	int i,j;
	cache_line *p = ci.cache;
	if (!verbose)
		return;
	
	for (i=0; i< set_size(); i++) {
		printf("  set %d: ", i);
		for (j=0; j<assoc_size(); j++) {
			printf("%lx/%c/%d ", p->tag, p->valid?'*':'-', p->rank);
			p++;
		}
		printf("\n");
	}
}

int cache_init(int s, int a, int b)
{
	cache_line *p;
	int msize;
	
	
	memset((void*)&ci, sizeof(ci), 0);
	ci.set = s;
	ci.assoc_size = a;
	ci.block = b;
	
	msize = set_size() * assoc_size() * sizeof(cache_line);
	p = (cache_line*)malloc(msize);
	if (!p) {
		printf("Malloc fail! exiting....\n");
		exit(-1);
	}
	
	ci.cache = p;	
	for (int i=0; i<set_size() * assoc_size(); i++) {
		p->valid = 0;
		p->tag = 0;
		p->rank = 0;
		p++;
	}

	if (verbose)
		printf("set_size %d, line_size %d, assoc_size %d\n", set_size(), line_size(), assoc_size());
	cache_dump();
	return 0;
}

void cache_deinit()
{
	if (ci.cache)
		free(ci.cache);
}

void line_access(long addr)
{
	int offset = set_id(addr) * assoc_size();
	int i;

	cache_line *cur = ci.cache + offset;

	if (verbose)
		printf("\n  line: set_id %ld, offset %d, tag %lx\n", set_id(addr), offset, tag_id(addr));


	/* loop assoc and find out:
	 * 1. has invalid slot? slot num;
	 * 2. has match tag? slot num
	 * 3. lowest rank (for eviction)? */
	int empty_slot, match_slot, evict_slot;
	unsigned rank = 0;
	empty_slot = match_slot = evict_slot = -1;
	for (i=0; i<assoc_size(); i++) {
		cache_line *p = cur+i;
		
		if (p->valid) {
			p->rank++;
			if (tag_match(p, addr))
				match_slot = i;
			if (p->rank > rank) {
				rank = p->rank;
				evict_slot = i;
			}
		} else {
			if (empty_slot < 0)
				empty_slot = i;
		}
	}

	/* return if hit */
	if (match_slot >= 0) {
		(cur+match_slot)->rank = 0;
		report_hit(addr);
	} else { /* miss */		
		cache_line *pslot;

		report_miss(addr);
		
		/* add if has empty slot */
		if (empty_slot >= 0) {
			pslot = cur + empty_slot;
		} else { /* no empty slot, eviction */
			if (evict_slot < 0) {
				printf("error! no low rank slot found!");
				exit(-1);
			}
			/* do eviction */
			pslot = cur+evict_slot;
			pslot->valid = 0;
			pslot->rank = 0;
			report_evict(pslot->tag << (ci.set + ci.block));
		}
		tag_update(pslot, addr);
		/* for (i=0; i<assoc_size(); i++) { */
		/* 	if (!(cur+i)->valid) { */
		/* 		tag_update(cur+i, addr); */
		/* 		return; */
		/* 	} */
		/* }	 */
	}
		
	/* for (i=0; i<assoc_size(); i++) { */
	/* 	if (tag_match(cur+i, addr)) { */
	/* 		(cur+i)->rank++; */
	/* 		report_hit(addr); */
	/* 		return; */
	/* 	} */
	/* } */

	

	
	/* TODO: LRU */
	/* cache_line *ev = cur; */
	/* do eviction */
/* 	ev->valid =0; */
/* 	report_evict(ev->tag << (ci.set + ci.block)); */
/* 	tag_update(ev, addr); */
}

void line_load(long addr)
{
	line_access(addr);
}

void line_store(long addr)
{
	line_access(addr);
}

void line_modify(long addr)
{
	line_load(addr);
	line_store(addr);
}

void line_operation(char op, long addr)
{
	switch (op) {
	case 'L':
		line_load(addr);
		break;
	case 'S':
		line_store(addr);
		break;
	case 'M':
		line_modify(addr);
		break;
	default:
		printf("UNKONWN oper: %c\n", op);
	}
}

/*
 * cmd syntax: [space]operation address,size 
 * cmd examples (leading space removed)
L 10,1
M 20,1
L 22,1
S 18,1
*/
void cache_operation(char *cmd)
{
	char op = cmd[0];
	char *sep;
	long addr, size;

	/* 1. parse input  */
	addr = strtol(cmd+2, &sep, 16);
	size = strtol(sep+1, &sep, 16);
	//printf("addr %lx, size %lx\n", addr, size);

	/* 2. split to cache lines if size > line size */
	int lines = size / line_size();
	if (size % line_size())
		lines++;
		
	/* 3. operate on lines */
	for (int i = 0; i < lines; i++) { 
		line_operation(op, addr);
		addr += line_size();
	}
}

int main(int argc, char **argv)
{
    int set, assoc, block, ch;
    char *filename;
    FILE *fp;
    char buf[128];

    while ((ch = getopt(argc, argv, "s:E:b:t:v")) != -1) {
        switch (ch) {
            case 's':
                set = atoi(optarg);
                break;
            case 'E':
                assoc = atoi(optarg);
                break;
            case 'b':
                block = atoi(optarg);
                break;
            case 't':
                filename = (char*) optarg;
                fp = fopen(filename, "r");
                if (!fp) {
                    printf("open file %s fail!\n", filename);
                }
                break;
            case 'v':
                verbose = 1;
                break;
            default:
                break;
        }
    }
    if (verbose)
        printf(" s:%d E:%d b:%d t:%s\n", set, assoc, block, filename);

    cache_init(set, assoc, block);

    while (fgets(buf, 128, fp) != NULL) {
        char *tail = buf + strlen(buf) - 1;
        while (*tail == '\n' || *tail == '\r')
                *tail-- = '\0';

        if (buf[0] == 'I') {
            if (verbose)
                printf("%s", buf);
                printf("ignore\n");
            continue;
        }else if (buf[0] == ' ') {
            char *p = buf+1;
            printf("%s", p);
	    cache_operation(p);
	    putchar('\n');
	    cache_dump();
        } else {
            printf("%s", buf);
            printf("warning: unknown command\n");
        }

    }
    printSummary(ci.hit, ci.miss, ci.evict);

//    printf("sizeof int %d, sizeof long %d\n", (int)sizeof(int), (int)sizeof(long));

    cache_deinit();
    return 0;
}
