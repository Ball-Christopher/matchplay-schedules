// Z2^2-invariant pool + sigma cycling blocks 1..3: enumerate clash-free 6-sets A (class masks disjoint) whose
// covered set C has C | sigma(C) = all (leave meets every sigma-orbit at most once); then block D must cover
// exactly X = classes not covered by all three of A, sA, s^2A: exact cover by 5 pool weeks.
// usage: cliqs maskfile sigfile part nparts
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
int N; uint64_t lo[12000],hi[12000]; char kind[12000][8]; long cnt,pass,found; int K=6; int st[8]; int sg[2][64];
#define ALLLO ((1ULL<<60)-1)
#define ALLHI ((1ULL<<18)-1)
static void sig(uint64_t l,uint64_t h,uint64_t*ol,uint64_t*oh){uint64_t a=0,b=0;while(l){int i=__builtin_ctzll(l);l&=l-1;a|=1ULL<<sg[0][i];}while(h){int i=__builtin_ctzll(h);h&=h-1;b|=1ULL<<sg[1][i];}*ol=a;*oh=b;}
int dst[8];
static int cover(int d,uint64_t xl,uint64_t xh,int nleft){
  if(!xl&&!xh)return nleft==0;
  if(nleft==0)return 0;
  // lowest class
  for(int w=0;w<N;w++){ if((lo[w]&~xl)||(hi[w]&~xh))continue;
    if(xl){if(!(lo[w]&(xl&-xl)))continue;}else{if(!(hi[w]&(xh&-xh)))continue;}
    dst[d]=w;if(cover(d+1,xl&~lo[w],xh&~hi[w],nleft-1))return 1;}
  return 0;
}
static void leaf(uint64_t cl,uint64_t ch){
  cnt++;uint64_t l1,h1,l2,h2;sig(cl,ch,&l1,&h1);
  if((cl|l1)!=ALLLO||(ch|h1)!=ALLHI)return;
  sig(l1,h1,&l2,&h2);pass++;
  uint64_t xl=ALLLO&~(cl&l1&l2),xh=ALLHI&~(ch&h1&h2);
  if(cover(0,xl,xh,5)){found++;printf("FOUND A:");for(int i=0;i<6;i++)printf(" %d",st[i]);printf(" D:");for(int i=0;i<5;i++)printf(" %d",dst[i]);printf("\n");fflush(stdout);}
}
static void rec(int d,int*cand,int nc,uint64_t ml,uint64_t mh){
  if(d==K){leaf(ml,mh);return;}
  int *nx=malloc(nc*sizeof(int));
  for(int i=0;i<nc;i++){int w=cand[i];int m=0;uint64_t a=lo[w],b=hi[w];for(int j=i+1;j<nc;j++){int v=cand[j];if(!(lo[v]&a)&&!(hi[v]&b))nx[m++]=v;}
    if(m>=K-d-1){st[d]=w;rec(d+1,nx,m,ml|a,mh|b);}}
  free(nx);
}
int main(int argc,char**argv){FILE*f=fopen(argv[1],"r");fscanf(f,"%d",&N);
  for(int i=0;i<N;i++)fscanf(f,"%s %llu %llu",kind[i],(unsigned long long*)&lo[i],(unsigned long long*)&hi[i]);
  f=fopen(argv[2],"r");for(int i=0;i<60;i++)fscanf(f,"%d",&sg[0][i]);for(int i=0;i<18;i++)fscanf(f,"%d",&sg[1][i]);
  int part=atoi(argv[3]),np=atoi(argv[4]);
  for(int w=part;w<N;w+=np){int *nx=malloc(N*sizeof(int));int m=0;for(int v=w+1;v<N;v++)if(!(lo[v]&lo[w])&&!(hi[v]&hi[w]))nx[m++]=v;st[0]=w;rec(1,nx,m,lo[w],hi[w]);free(nx);
    if((w/np)%20==0){fprintf(stderr,"w %d cnt %ld pass %ld found %ld\n",w,cnt,pass,found);}}
  printf("DONE part %d: 6-sets %ld pass %ld found %ld\n",part,cnt,pass,found);return 0;}
