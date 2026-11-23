// N=Z2^2-invariant designs with an automorphism sigma cycling oil blocks 1->2->3 (see NOTES.md).
// Items: pool2 (single N-invariant weeks, weight 1; double weeks, weight 2), each a set of the 78 N-classes.
// Enumerate blocks A of weight 6 (items disjoint) with at least 2 classes covered in every sigma-orbit and no
// sigma-fixed class missed; then block D must exactly cover X = classes not covered by all of A, sA, ssA with weight 5.
// usage: sigsearch maskfile sigfile part nparts seed
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
typedef unsigned __int128 u128;
#define NC 78
int N; u128 *msk; int *wt; int sg[NC]; u128 ALL; int orbs[NC][3],norb,osz[NC]; u128 orbm[NC];
int st[8],ns; int dsol[8]; long leaves,found,nodes; int **gb; int *gbn; // global by-class lists
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
  if(coverD(0,X,5)){found++;printf("FOUND A:");for(int i=0;i<ns;i++)printf(" %d",st[i]);printf(" D:");for(int i=0;i<dsol[7];i++)printf(" %d",dsol[i]);printf("\n");fflush(stdout);}
}
// cand: list of items compatible with C (disjoint) ; F forced, M missed
static void rec(u128 C,u128 F,u128 M,int r,int*cand,int nc,int depth){
  nodes++;
  int need=0;for(int o=0;o<norb;o++){int c=pc(orbm[o]&C);int nd=(osz[o]==1?1:2)-c;if(nd>0)need+=nd;}
  int fu=pc(F&~C);if(fu>need)need=fu;
  if(need>10*r)return;
  if(r==0){leaf(C);return;}
  u128 Fu=F&~C;
  if(Fu){int x=low(Fu);u128 xb=(u128)1<<x;
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
  int part=atoi(argv[3]),np=atoi(argv[4]);long seed=atol(argv[5]);
  ALL=((u128)1<<NC)-1;
  int seen[NC]={0};for(int i=0;i<NC;i++)if(!seen[i]){int x=i,k=0;do{seen[x]=1;orbs[norb][k++]=x;orbm[norb]|=(u128)1<<x;x=sg[x];}while(x!=i);osz[norb]=k;norb++;}
  gb=malloc(NC*sizeof(int*));gbn=calloc(NC,sizeof(int));for(int x=0;x<NC;x++){gb[x]=malloc(N*sizeof(int));for(int w=0;w<N;w++)if(msk[w]>>x&1)gb[x][gbn[x]++]=w;}
  // root: forced class 0-orbit branching done by hand so that the work can be split: enumerate root children
  // (decision for orbit of class 0, then item containing the first forced class), take those with index%np==part.
  int*all=malloc(N*sizeof(int));for(int i=0;i<N;i++)all[i]=i;
  srand(seed);
  // shuffle item order for the root level
  for(int i=N-1;i>0;i--){int j=rand()%(i+1);int t=all[i];all[i]=all[j];all[j]=t;}
  u128 un=orbm[0];int idx=0;
  for(int br=0;br<=osz[0];br++){ if(osz[0]==1&&br>0)break;
    u128 F=un,M=0;if(br>0){u128 yb=(u128)1<<orbs[0][br-1];F=un&~yb;M=yb;}
    int x=low(F);u128 xb=(u128)1<<x;int*nx=malloc(N*sizeof(int));
    for(int t=0;t<N;t++){int w=all[t];u128 m=msk[w];if(!(m&xb)||(m&M))continue;
      if((idx++)%np!=part)continue;
      int k=0;for(int q=0;q<N;q++){int v=all[q];if(!(msk[v]&m))nx[k++]=v;}
      st[0]=w;ns=1;rec(m,F,M,6-wt[w],nx,k,1);
      if(idx%(np*50)==part)fprintf(stderr,"root %d nodes %ld leaves %ld found %ld\n",idx,nodes,leaves,found);}
    free(nx);}
  printf("DONE part %d nodes %ld leaves %ld found %ld\n",part,nodes,leaves,found);return 0;}
