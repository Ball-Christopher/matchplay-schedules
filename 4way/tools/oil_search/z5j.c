// type-level SA. v=24: Z5 on 20 finite points + 4 fixed. 4 base weeks + 3 invariant weeks (blocks: base a -> a, inv f -> f)
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#define V 24
#define NTY 97
static unsigned long long s=88172645463325252ULL;
static inline unsigned long long rnd(){s^=s<<13;s^=s>>7;s^=s<<17;return s;}
static inline double ur(){return (double)(rnd()>>11)/9007199254740992.0;}
int A[4][V],off[3][4];int cnt[NTY],cw[4][NTY],tgt[NTY],RW=1;
static inline int ty(int p,int q){if(p>q){int t=p;p=q;q=t;}
  if(p>=20)return 96; if(q>=20)return 80+(q-20)*4+p/5;
  int a=p/5,i=p%5,b=q/5,j=q%5;int d=(j-i+5)%5;if(a==b&&d>2)d=5-d;return (a*4+b)*5+d;}
static inline void addw(int w,int g,int v){int*q=A[w]+4*g;for(int x=0;x<4;x++)for(int y=x+1;y<4;y++){int t=ty(q[x],q[y]);cnt[t]+=v;cw[w][t]+=v;}}
static inline void addf(int f,int v){for(int x=0;x<4;x++)for(int y=x+1;y<4;y++){int t=ty(5*x+off[f][x],5*y+off[f][y]);cnt[t]+=v;cw[f][t]+=v;}}
static int cost(){int c=0;for(int t=0;t<NTY;t++){if(tgt[t]>=0)c+=abs(cnt[t]-tgt[t]);for(int w=0;w<4;w++)if(cw[w][t]>1)c+=RW*(cw[w][t]-1);}return c+3*cnt[96];}
int main(int argc,char**argv){
  if(getenv("RW"))RW=atoi(getenv("RW"));
  s^=atoll(argv[1])*0x9E3779B97F4A7C15ULL;for(int i=0;i<20;i++)rnd();
  long iters=atol(argv[2]);double T0=atof(argv[3]),T1=atof(argv[4]);
  for(int t=0;t<NTY;t++)tgt[t]=-1;
  for(int a=0;a<4;a++)for(int b=a;b<4;b++)for(int d=0;d<5;d++){if(a==b&&(d==0||d>2))continue;tgt[(a*4+b)*5+d]=3;}
  for(int t=80;t<96;t++)tgt[t]=3;
  for(int att=0;att<1000000;att++){
    for(int a=0;a<4;a++){for(int i=0;i<V;i++)A[a][i]=i;for(int i=V-1;i>0;i--){int j=rnd()%(i+1);int t=A[a][i];A[a][i]=A[a][j];A[a][j]=t;}}
    for(int f=0;f<3;f++){off[f][0]=0;for(int a=1;a<4;a++)off[f][a]=rnd()%5;}
    memset(cnt,0,sizeof cnt);memset(cw,0,sizeof cw);
    for(int w=0;w<4;w++)for(int g=0;g<6;g++)addw(w,g,1);for(int f=0;f<3;f++)addf(f,1);
    int c=cost();double T=T0;int best=c;
    for(long it=0;it<iters&&c>0;it++){if((it&0xfff)==0)T=T0*pow(T1/T0,(double)it/iters);
      if(rnd()%12==0){int f=rnd()%3,a=1+rnd()%3,old=off[f][a];addf(f,-1);off[f][a]=rnd()%5;addf(f,1);int nc=cost();
        if(nc<=c||ur()<exp(-(nc-c)/T))c=nc;else{addf(f,-1);off[f][a]=old;addf(f,1);}}
      else{int w=rnd()%4,x=rnd()%V,y=rnd()%V;if(x/4==y/4)continue;addw(w,x/4,-1);addw(w,y/4,-1);int t=A[w][x];A[w][x]=A[w][y];A[w][y]=t;addw(w,x/4,1);addw(w,y/4,1);int nc=cost();
        if(nc<=c||ur()<exp(-(nc-c)/T))c=nc;else{addw(w,x/4,-1);addw(w,y/4,-1);t=A[w][x];A[w][x]=A[w][y];A[w][y]=t;addw(w,x/4,1);addw(w,y/4,1);}}
      if(c<best)best=c;}
    fprintf(stderr,"att %d end %d best %d\n",att,c,best);
    if(c==0){for(int w=0;w<4;w++){for(int i=0;i<V;i++)printf("%d ",A[w][i]);printf("\n");}for(int f=0;f<3;f++){for(int a=0;a<4;a++)printf("%d ",off[f][a]);printf("\n");}return 0;}
  }return 1;}
