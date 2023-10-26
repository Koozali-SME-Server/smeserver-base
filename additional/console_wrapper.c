#include <unistd.h>
#define CONSOLE_PATH "/sbin/e-smith/console.pl"
int main(ac, av)
char **av;
{
    execv(CONSOLE_PATH, av);
    return 0;
}
