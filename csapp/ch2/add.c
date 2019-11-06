#include <stdio.h>

int main()
{
	unsigned int a, b, c;
	int i,j,k;

	a = i = 50;
	b = j = 100;

	c = a - b;
	k = i - j;

	printf("c = %u (%x), k = %d (%x)\n", c, c, k, k);
}
