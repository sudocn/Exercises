#include <stdio.h>

void multstore(long, long, long *);

int flags(int, int);

int main()
{
        long d;

        flags(2, 3);

        multstore(2, 3, &d);
        printf("2 * 3 -- > %ld\n", d);
        return 0;
}

long mult2(long a, long b)
{
        long s = a * b;
        return s;
}
