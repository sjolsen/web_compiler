#include <stdio.h>
#include <stdlib.h>

int main(int argc, char** argv) {
  int a = 1, b = 1;
  for (int i = 0; i < 10; ++i) {
    printf("%d ", a);
    b = b + a;
    a = b - a;
  }
  printf("\n");
  return EXIT_SUCCESS;
}
