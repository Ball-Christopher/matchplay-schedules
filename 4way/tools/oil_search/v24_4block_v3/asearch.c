// N=Z2^2-invariant designs with an automorphism sigma cycling oil blocks 1->2->3 (see NOTES.md).
// Items: pool2 (single N-invariant weeks, weight 1; double weeks, weight 2), each a set of the 78 N-classes.
// Enumerate blocks A of weight 6 (items disjoint) with at least 2 classes covered in every sigma-orbit and no
// sigma-fixed class missed; then block D must exactly cover X = classes not covered by all of A, sA, ssA with weight 5.
// asearch variant: the fourth block's class set X is given (Xlo Xhi); block A must cover every class outside X
// and exactly two classes of every sigma-orbit inside X.  usage: asearch maskfile sigfile Xlo Xhi maxfound
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
typedef unsigned __int128 u128;
#define NC 78
int N; u128 *msk; int *wt; int sg[NC]; u128 ALL; int orbs[NC][3],norb,osz[NC]; u128 orbm[NC];
u128 XD;long maxfound;int st[8],ns; int dsol[8]; long leaves,found,nodes; int **gb; int *gbn; // global by-class lists
static inline int pc(u128 x){return __builtin_popcountll((uint64_t)x)+__builtin_popcountll((uint64_t)(x>>64));}
static inline int low(u128 x){uint64_t l=(uint64_t)x;return l?__builtin_ctzll(l):64+__builtin_ctzll((uint64_t)(x>>64));}
static u128 sig(u128 x){u128 r=0;while(x){int i=low(x);x&=x-1;r|=(u128)1<<sg[i];}return r;}
static int coverD(int d,u128 X,int r){
  if(!X){if(r==0){dsol[7]=d;return 1;}return 0;} if(r<=0)return 0;
  int x=low(X);
  for(int t=0;t<gbn[x];t++){int w=gb[x][t];if((msk[w]&~X)||wt[w]>r)continue;dsol[d]=w;if(coverD(d+1,X&~msk[w],r-wt[w]))return 1;}
  return 0;
}
static void leaf(u128 C){
  leaves++;u128 c1=sig(C),c2=sig(c1);u128 X=ALL&~(C&c1&c2);
  if(X==XD){found++;printf("FOUND A:");for(int i=0;i<ns;i++)printf(" %d",st[i]);printf("\n");fflush(stdout);if(found>=maxfound)exit(0);}
}
// cand: list of items compatible with C (disjoint) ; F forced, M missed
static void rec(u128 C,u128 F,u128 M,int r,int*cand,int nc,int depth){
  nodes++;
  for(int o=0;o<norb;o++)if(orbm[o]&XD){int c=pc(orbm[o]&C);if(c==osz[o])return;if(c==2)M|=orbm[o]&~C;}
  int need=0;for(int o=0;o<norb;o++){int c=pc(orbm[o]&C);int nd=(osz[o]==1?1:2)-c;if(nd>0)need+=nd;}
  int fu=pc(F&~C);if(fu>need)need=fu;
  if(need>10*r)return;
  if(r==0){leaf(C);return;}
  u128 Fu=F&~C;
  if(Fu){int cn[NC]={0};for(int t=0;t<nc;t++){int w=cand[t];u128 m=msk[w];if((m&M)||wt[w]>r)continue;m&=Fu;while(m){cn[low(m)]++;m&=m-1;}}
    int x=-1,bc=1<<30;{u128 t=Fu;while(t){int y=low(t);t&=t-1;if(cn[y]<bc){bc=cn[y];x=y;}}}
    if(bc==0)return;
    u128 xb=(u128)1<<x;
    int*nx=malloc(nc*sizeof(int));
    for(int t=0;t<nc;t++){int w=cand[t];u128 m=msk[w];if(!(m&xb)||(m&M)||wt[w]>r)continue;
      int k=0;for(int q=0;q<nc;q++){int v=cand[q];if(!(msk[v]&m))nx[k++]=v;}
      st[ns++]=w;rec(C|m,F,M,r-wt[w],nx,k,depth+1);ns--;}
    free(nx);return;}
  for(int o=0;o<norb;o++){ if(osz[o]==1){if(!(orbm[o]&C)){rec(C,F|orbm[o],M,r,cand,nc,depth);return;}continue;}
    u128 un=orbm[o]&~C;int c=3-pc(un);
    if(c<2){ if(un&M){rec(C,F|(un&~M),M,r,cand,nc,depth);return;}
      rec(C,F|un,M,r,cand,nc,depth);
      u128 t=un;while(t){int y=low(t);t&=t-1;u128 yb=(u128)1<<y;rec(C,F|(un&~yb),M|yb,r,cand,nc,depth);}
      return;}
    if(c==2&&!(un&M)&&!(un&F)){rec(C,F|un,M,r,cand,nc,depth);rec(C,F,M|un,r,cand,nc,depth);return;}
  }
}
int main(int argc,char**argv){FILE*f=fopen(argv[1],"r");fscanf(f,"%d",&N);msk=malloc(N*sizeof(u128));wt=malloc(N*sizeof(int));char kind[16];
  for(int i=0;i<N;i++){unsigned long long lo,hi;fscanf(f,"%s %d %llu %llu",kind,&wt[i],&lo,&hi);msk[i]=(u128)lo|((u128)hi<<60);}
  f=fopen(argv[2],"r");for(int i=0;i<NC;i++)fscanf(f,"%d",&sg[i]);
  XD=(u128)strtoull(argv[3],0,10)|((u128)strtoull(argv[4],0,10)<<60);maxfound=atol(argv[5]);
  ALL=((u128)1<<NC)-1;
  int seen[NC]={0};for(int i=0;i<NC;i++)if(!seen[i]){int x=i,k=0;do{seen[x]=1;orbs[norb][k++]=x;orbm[norb]|=(u128)1<<x;x=sg[x];}while(x!=i);osz[norb]=k;norb++;}
  gb=malloc(NC*sizeof(int*));gbn=calloc(NC,sizeof(int));for(int x=0;x<NC;x++){gb[x]=malloc(N*sizeof(int));for(int w=0;w<N;w++)if(msk[w]>>x&1)gb[x][gbn[x]++]=w;}
  int*all=malloc(N*sizeof(int));int k=0;for(int i=0;i<N;i++)all[k++]=i;
  // orbits inside X: exactly one class missed, so an orbit with all three in X and ... is handled by rec's branching; forbid nothing here
  ns=0;rec(0,ALL&~XD,0,6,all,k,0);
  printf("DONE nodes %ld leaves %ld found %ld\n",nodes,leaves,found);return 0;}
