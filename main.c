#include <stdio.h>
#include "filter1.h"

int main()
{
  filter1Type *f;

  f = filter1_create();
  filter1_init(f);
  while(!feof(stdin)) {
    double f;
    fscanf(stdin, "%lf", &f);
    fprintf(stdout, "%13.10lf\n", f);
  }
  /*filter1_filterBlock( filter1Type * pThis, float * pInput, float * pOutput, unsigned int count );*/
  filter1_destroy(f);
}
