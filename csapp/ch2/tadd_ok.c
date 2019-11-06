#include <stdio.h>
#include <limits.h>

int tadd_ok(int x, int y)
{
	int sum = x + y;
	//TODO: neg and positive cases
	if (sum < 0)
		return 0;
	else
		return 1;
}

int main()
{

	int samples[][2] = {
		{1,2}, 
		{INT_MAX, INT_MIN},
		{INT_MAX, INT_MAX},
		{INT_MIN, INT_MIN},
		{INT_MAX, 1},
		{INT_MIN, -1},
		};
	
	int i;

	for (i=0; i<sizeof(samples)/sizeof(int)/2; i++) {
		int x = samples[i][0];
		int y = samples[i][1];
		int z = tadd_ok(x, y);
		printf("%d + %d:\t %d\n", x, y, z);
	}
}
