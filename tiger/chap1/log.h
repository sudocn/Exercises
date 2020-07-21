#ifndef _LOG_H_
#define _LOG_H_

extern int parse_tree_depth;

void log_level(int level, const char* fmt, ...);

#define log(...)   log_level(parse_tree_depth, __VA_ARGS__)

#ifdef DEBUG
#define debug(...) log(__VA_ARGS__)
#else
#define debug(...) 
#endif /* DEBUG */    

static inline void inc_level() { parse_tree_depth++; };
static inline void dec_level() { parse_tree_depth--; };
#endif /* _LOG_H_ */