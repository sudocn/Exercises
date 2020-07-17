#include <stdio.h>
#include <stdarg.h>
#include "log.h"

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
//#define log(...)   log_level(parse_tree_depth, __VA_ARGS__)
// void inc_level() { parse_tree_depth++; };
// void dec_level() { parse_tree_depth--; };