// Exhaustive search in the Z2^2-invariant pool: all clash-free 6-sets (blocks), then all triples of blocks with
// pairwise disjoint leaves, then exact cover of the classes missed once by a 5-set.  usage: combo maskfile part nparts
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
int N; uint64_t lo[12000],hi[12000]; char kind[12000][8]; int K=6; int st[8];
#define ALLLO ((1ULL<<60)-1)
#define ALLHI ((1ULL<<18)-1)
typedef struct{uint64_t l,h;int w[6];}blk; blk*B;long nb,cap;
int dst[8];
static int cover(int d,uint64_t xl,uint64_t xh,int nleft){
  if(!xl&&!xh)return nleft==0;
  if(nleft==0)return 0;
  for(int w=0;w<N;w++){ if((lo[w]&~xl)||(hi[w]&~xh))continue;
    if(xl){if(!(lo[w]&(xl&-xl)))continue;}else{if(!(hi[w]&(xh&-xh)))continue;}
    dst[d]=w;if(cover(d+1,xl&~lo[w],xh&~hi[w],nleft-1))return 1;}
  return 0;
}
static void rec(int d,int*cand,int nc,uint64_t ml,uint64_t mh){
  if(d==K){if(nb==cap){cap*=2;B=realloc(B,cap*sizeof(blk));}B[nb].l=ml;B[nb].h=mh;memcpy(B[nb].w,st,sizeof(int)*6);nb++;return;}
  int *nx=malloc(nc*sizeof(int));
  for(int i=0;i<nc;i++){int w=cand[i];int m=0;uint64_t a=lo[w],b=hi[w];for(int j=i+1;j<nc;j++){int v=cand[j];if(!(lo[v]&a)&&!(hi[v]&b))nx[m++]=v;}
    if(m>=K-d-1){st[d]=w;rec(d+1,nx,m,ml|a,mh|b);}}
  free(nx);
}
int main(int argc,char**argv){FILE*f=fopen(argv[1],"r");fscanf(f,"%d",&N);
  for(int i=0;i<N;i++)fscanf(f,"%s %llu %llu",kind[i],(unsigned long long*)&lo[i],(unsigned long long*)&hi[i]);
  int part=atoi(argv[2]),np=atoi(argv[3]);cap=1<<21;B=malloc(cap*sizeof(blk));
  int*c=malloc(N*sizeof(int));for(int i=0;i<N;i++)c[i]=i;rec(0,c,N,0,0);
  fprintf(stderr,"blocks %ld\n",nb);
  int*J=malloc(nb*sizeof(int));long pairs=0,trip=0,found=0;
  for(long i=part;i<nb;i+=np){int m=0;uint64_t a=B[i].l,b=B[i].h;
    for(long j=i+1;j<nb;j++)if((a|B[j].l)==ALLLO&&(b|B[j].h)==ALLHI)J[m++]=j;
    pairs+=m;
    for(int x=0;x<m;x++){blk*p=&B[J[x]];for(int y=x+1;y<m;y++){blk*q=&B[J[y]];if((p->l|q->l)==ALLLO&&(p->h|q->h)==ALLHI){trip++;
      uint64_t xl=ALLLO&~(a&p->l&q->l),xh=ALLHI&~(b&p->h&q->h);
      if(cover(0,xl,xh,5)){found++;printf("FOUND");for(int t=0;t<6;t++)printf(" %d",B[i].w[t]);printf(" |");for(int t=0;t<6;t++)printf(" %d",p->w[t]);printf(" |");for(int t=0;t<6;t++)printf(" %d",q->w[t]);printf(" |");for(int t=0;t<5;t++)printf(" %d",dst[t]);printf("\n");fflush(stdout);}}}}
    if(((i-part)/np)%2000==0)fprintf(stderr,"i %ld pairs %ld triples %ld found %ld\n",i,pairs,trip,found);
  }
  printf("DONE part %d blocks %ld pairs %ld triples %ld found %ld\n",part,nb,pairs,trip,found);return 0;}
