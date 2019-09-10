#include <stdio.h>

int __attribute__((fastcall)) factorial(char* a, int n) {
	if (n == 0)
		return 1;

	int res = factorial(a, n-1)-n;
	printf("%s( %d ) = %d\n", a, n, res);

	return res;
}


int main(int argc,char *argv[])
{
	int x;
	while(scanf("%d", &x) == 1)
	{
		factorial("factorial", x);
	}

	return 0;
}
