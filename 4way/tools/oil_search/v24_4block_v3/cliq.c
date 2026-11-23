// Count / list clash-free sets of K weeks from the pool (class masks disjoint).  usage: cliq maskfile K [dump]
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
int N; uint64_t lo[12000],hi[12000]; char kind[12000][8]; long cnt; int K; int st[8]; FILE*out;
static void rec(int d,int*cand,int nc,uint64_t ml,uint64_t mh){
  if(d==K){cnt++;if(out){fwrite(st,sizeof(int),K,out);}return;}
  int *nx=malloc(nc*sizeof(int));
  for(int i=0;i<nc;i++){int w=cand[i];int m=0;for(int j=i+1;j<nc;j++){int v=cand[j];if(!(lo[v]&lo[w])&&!(hi[v]&hi[w]))nx[m++]=v;}
    if(m>=K-d-1){st[d]=w;rec(d+1,nx,m,ml|lo[w],mh|hi[w]);}}
  free(nx);
}
int main(int argc,char**argv){FILE*f=fopen(argv[1],"r");K=atoi(argv[2]);out=argc>3?fopen(argv[3],"wb"):NULL;fscanf(f,"%d",&N);
  for(int i=0;i<N;i++)fscanf(f,"%s %llu %llu",kind[i],(unsigned long long*)&lo[i],(unsigned long long*)&hi[i]);
  int *c=malloc(N*sizeof(int));for(int i=0;i<N;i++)c[i]=i;
  // only first-level index range from argv[4],argv[5] if given
  rec(0,c,N,0,0);printf("K=%d count %ld\n",K,cnt);return 0;}
