// v=24: Z5 on 20 finite points p=a*5+i (a<4) + 4 fixed points 20..23. 4 base weeks (x5) + 3 invariant weeks.
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#define V 24
#define R 23
static unsigned long long s=88172645463325252ULL;
static inline unsigned long long rnd(){s^=s<<13;s^=s>>7;s^=s<<17;return s;}
static inline double ur(){return (double)(rnd()>>11)/9007199254740992.0;}
typedef struct{int A[4][V];int off[3][4];}St; St st,sv;
int W[R][6][4],wb[R],pr[V][V],bp[4][V][V];int AW=1,RW=1,dev,rep;
static inline int act(int p,int k){return p>=20?p:(p/5)*5+(p%5+k)%5;}
static void expand(){int w=0;
  for(int a=0;a<4;a++)for(int k=0;k<5;k++){wb[w]=a;for(int b=0;b<6;b++)for(int x=0;x<4;x++)W[w][b][x]=act(st.A[a][4*b+x],k);w++;}
  for(int f=0;f<3;f++){wb[w]=f;for(int k=0;k<5;k++)for(int a=0;a<4;a++)W[w][k][a]=a*5+(st.off[f][a]+k)%5;for(int x=0;x<4;x++)W[w][5][x]=20+x;w++;}}
static int cost(){expand();memset(pr,0,sizeof pr);memset(bp,0,sizeof bp);
  for(int w=0;w<R;w++)for(int L=0;L<6;L++){int*g=W[w][L];if(g[0]>=20&&g[1]>=20&&g[2]>=20&&g[3]>=20)continue;for(int x=0;x<4;x++)for(int y=x+1;y<4;y++){int a=g[x],b=g[y];if(a>b){int t=a;a=b;b=t;}pr[a][b]++;bp[wb[w]][a][b]++;}}
  dev=rep=0;
  for(int a=0;a<V;a++)for(int b=a+1;b<V;b++){int t=(a>=20&&b>=20)?0:3;int d=pr[a][b]-t;dev+=d<0?-d:d;for(int k=0;k<4;k++)if(bp[k][a][b]>1)rep+=bp[k][a][b]-1;}
  return AW*dev+RW*rep;}
static void shuf(int*a,int n){for(int i=n-1;i>0;i--){int j=rnd()%(i+1);int t=a[i];a[i]=a[j];a[j]=t;}}
int main(int argc,char**argv){
  if(getenv("AW"))AW=atoi(getenv("AW"));if(getenv("RW"))RW=atoi(getenv("RW"));
  s^=atoll(argv[1])*0x9E3779B97F4A7C15ULL;for(int i=0;i<20;i++)rnd();
  long iters=atol(argv[2]);double T0=atof(argv[3]),T1=atof(argv[4]);
  for(int att=0;att<1000000;att++){
    for(int a=0;a<4;a++){for(int i=0;i<V;i++)st.A[a][i]=i;shuf(st.A[a],V);}
    for(int f=0;f<3;f++)for(int a=0;a<4;a++)st.off[f][a]=rnd()%5;
    int c=cost();double T=T0;
    for(long it=0;it<iters&&c>0;it++){if((it&0xff)==0)T=T0*pow(T1/T0,(double)it/iters);
      sv=st;
      if(rnd()%10==0)st.off[rnd()%3][1+rnd()%3]=rnd()%5;
      else{int a=rnd()%4,x,y;do{x=rnd()%V;y=rnd()%V;}while(x/4==y/4);int t=st.A[a][x];st.A[a][x]=st.A[a][y];st.A[a][y]=t;}
      int nc=cost();if(nc<=c||ur()<exp(-(nc-c)/T))c=nc;else st=sv;}
    cost();fprintf(stderr,"att %d dev %d rep %d\n",att,dev,rep);
    if(c==0){for(int w=0;w<R;w++){printf("%d:",wb[w]);for(int L=0;L<6;L++)for(int x=0;x<4;x++)printf(" %d",W[w][L][x]);printf("\n");}return 0;}
  }return 1;}
