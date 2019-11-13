void lower1(char *s)
{
        long i;

        for (i=0; i<strlen(s); i++) {
                if (s[i] >= 'A' && s[i] <= 'Z')
                        s[i] -= 'A' - 'a';
        }
}

void lower2(char *s)
{
        long i;
        long len = strlen(s);

        for (i=0; i<len; i++) {
                if (s[i] >= 'A' && s[i] <= 'Z')
                        s[i] -= 'A' - 'a';
        }
}

int main()
{
        char *str = 'this is a test string';

        lower1(str);

        lower2(str);
}
