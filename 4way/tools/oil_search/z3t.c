// type-level SA. v=24: Z3 on 8 classes p=a*3+i. 7 base weeks + 2 invariant weeks; block ids argv[5] (9 digits)
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#define V 24
#define NTY 192
static unsigned long long s=88172645463325252ULL;
static inline unsigned long long rnd(){s^=s<<13;s^=s>>7;s^=s<<17;return s;}
static inline double ur(){return (double)(rnd()>>11)/9007199254740992.0;}
int A[7][V],sl[2][8],off[2][8],bid[9];int cnt[NTY],cw[4][NTY],tgt[NTY],RW=1;
static inline int ty(int p,int q){if(p>q){int t=p;p=q;q=t;}
  int a=p/3,i=p%3,b=q/3,j=q%3;int d=(j-i+3)%3;if(a==b)d=1;return (a*8+b)*3+d;}
static inline void addw(int w,int g,int v){int*q=A[w]+4*g;int B=bid[w];for(int x=0;x<4;x++)for(int y=x+1;y<4;y++){int t=ty(q[x],q[y]);cnt[t]+=v;cw[B][t]+=v;}}
static inline void addf(int f,int v){int B=bid[7+f];for(int g=0;g<2;g++)for(int x=0;x<4;x++)for(int y=x+1;y<4;y++){int a=sl[f][4*g+x],b=sl[f][4*g+y];int t=ty(3*a+off[f][a],3*b+off[f][b]);cnt[t]+=v;cw[B][t]+=v;}}
static int cost(){int c=0;for(int t=0;t<NTY;t++){if(tgt[t]>=0)c+=abs(cnt[t]-tgt[t]);for(int w=0;w<4;w++)if(cw[w][t]>1)c+=RW*(cw[w][t]-1);}return c;}
int main(int argc,char**argv){
  if(getenv("RW"))RW=atoi(getenv("RW"));
  s^=atoll(argv[1])*0x9E3779B97F4A7C15ULL;for(int i=0;i<20;i++)rnd();
  long iters=atol(argv[2]);double T0=atof(argv[3]),T1=atof(argv[4]);for(int i=0;i<9;i++)bid[i]=argv[5][i]-'0';
  for(int t=0;t<NTY;t++)tgt[t]=-1;
  for(int a=0;a<8;a++)for(int b=a;b<8;b++)for(int d=0;d<3;d++){if(a==b&&d!=1)continue;tgt[(a*8+b)*3+d]=3;}
  for(int att=0;att<1000000;att++){
    for(int a=0;a<7;a++){for(int i=0;i<V;i++)A[a][i]=i;for(int i=V-1;i>0;i--){int j=rnd()%(i+1);int t=A[a][i];A[a][i]=A[a][j];A[a][j]=t;}}
    for(int f=0;f<2;f++){for(int a=0;a<8;a++){sl[f][a]=a;off[f][a]=rnd()%3;}for(int i=7;i>0;i--){int j=rnd()%(i+1);int t=sl[f][i];sl[f][i]=sl[f][j];sl[f][j]=t;}}
    memset(cnt,0,sizeof cnt);memset(cw,0,sizeof cw);
    for(int w=0;w<7;w++)for(int g=0;g<6;g++)addw(w,g,1);for(int f=0;f<2;f++)addf(f,1);
    int c=cost();double T=T0;int best=c;
    for(long it=0;it<iters&&c>0;it++){if((it&0xfff)==0)T=T0*pow(T1/T0,(double)it/iters);
      if(rnd()%20==0){int f=rnd()%2;int so[8],oo[8];memcpy(so,sl[f],sizeof so);memcpy(oo,off[f],sizeof oo);addf(f,-1);
        if(rnd()%2)off[f][rnd()%8]=rnd()%3;else{int x=rnd()%8,y=rnd()%8;int t=sl[f][x];sl[f][x]=sl[f][y];sl[f][y]=t;}
        addf(f,1);int nc=cost();
        if(nc<=c||ur()<exp(-(nc-c)/T))c=nc;else{addf(f,-1);memcpy(sl[f],so,sizeof so);memcpy(off[f],oo,sizeof oo);addf(f,1);}}
      else{int w=rnd()%7,x=rnd()%V,y=rnd()%V;if(x/4==y/4)continue;addw(w,x/4,-1);addw(w,y/4,-1);int t=A[w][x];A[w][x]=A[w][y];A[w][y]=t;addw(w,x/4,1);addw(w,y/4,1);int nc=cost();
        if(nc<=c||ur()<exp(-(nc-c)/T))c=nc;else{addw(w,x/4,-1);addw(w,y/4,-1);t=A[w][x];A[w][x]=A[w][y];A[w][y]=t;addw(w,x/4,1);addw(w,y/4,1);}}
      if(c<best)best=c;}
    fprintf(stderr,"att %d end %d best %d\n",att,c,best);
    if(c==0){for(int w=0;w<7;w++){for(int i=0;i<V;i++)printf("%d ",A[w][i]);printf("\n");}for(int f=0;f<2;f++){for(int a=0;a<8;a++)printf("%d %d ",sl[f][a],off[f][a]);printf("\n");}return 0;}
  }return 1;}
