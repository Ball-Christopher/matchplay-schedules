#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>
// points p = M*c + i (class c in 0..K-1, i in Z_M). g: i->i+1, lane (m,t)->(m+1,t)
#ifndef M
#define M 3
#endif
#ifndef K
#define K 4
#endif
#ifndef A
#define A 3
#endif
#define T (K/4)
#define V (M*K)
#define NB (V/4)
#define R (V-1)
#define B (R-M*A)
#define HI ((R+NB-1)/NB)
#define LO (R/NB)
static unsigned long long s=88172645463325252ULL;
static inline unsigned long long rnd(){s^=s<<13;s^=s>>7;s^=s<<17;return s;}
static inline double ur(){return (double)(rnd()>>11)/9007199254740992.0;}
int wk[A][V]; int cp[B+1][K],off[B+1][K],lo[B+1][T];
int cnt[K][K][M],h[K][NB]; int cost=0;
static inline int pc(int a,int b,int d,int x){ if(a==b&&(d==0||d>M/2))return 0; return abs(x-3);}
static inline int lc(int x){return LW*(x>HI?x-HI:(x<LO?LO-x:0));}
static void addpair(int p,int q,int v){int a=p/M,i=p%M,b=q/M,j=q%M;
  if(a>b){int t=a;a=b;b=t;t=i;i=j;j=t;}
  int d=(j-i+M)%M; if(a==b){if(d>M/2)d=M-d;}
  cost-=pc(a,b,d,cnt[a][b][d]);cnt[a][b][d]+=v;cost+=pc(a,b,d,cnt[a][b][d]);}
static void addlane(int c,int cell,int v){cost-=lc(h[c][cell]);h[c][cell]+=v;cost+=lc(h[c][cell]);}
static void cb(int w,int b,int v){int*g=wk[w]+4*b;
  for(int x=0;x<4;x++){for(int y=x+1;y<4;y++)addpair(g[x],g[y],v);
    for(int j=0;j<M;j++){} 
    addlane(g[x]/M,((b%M-g[x]%M+M)%M)+M*(b/M),v);}}
static void cf(int f,int v){for(int t=0;t<T;t++){int g[4];for(int x=0;x<4;x++){int c=cp[f][4*t+x];g[x]=M*c+off[f][c];}
  for(int x=0;x<4;x++){for(int y=x+1;y<4;y++)addpair(g[x],g[y],v);
    addlane(g[x]/M,((lo[f][t]-g[x]%M+M)%M)+M*t,v);}}}
int main(int argc,char**argv){
  if(argc>1)s^=atoll(argv[1])*0x9E3779B97F4A7C15ULL; for(int i=0;i<20;i++)rnd();
  long iters=argc>2?atol(argv[2]):20000000; double T0=argc>3?atof(argv[3]):0.8,T1=argc>4?atof(argv[4]):0.12;
  for(int att=0;att<100000;att++){
    memset(cnt,0,sizeof cnt);memset(h,0,sizeof h);cost=0;
    for(int a=0;a<K;a++)for(int b=a;b<K;b++)for(int d=0;d<M;d++)cost+=pc(a,b,d,0);
    for(int c=0;c<K;c++)for(int l=0;l<NB;l++)cost+=lc(0);
    for(int w=0;w<A;w++){for(int i=0;i<V;i++)wk[w][i]=i;for(int i=V-1;i>0;i--){int j=rnd()%(i+1);int t=wk[w][i];wk[w][i]=wk[w][j];wk[w][j]=t;}
      for(int b=0;b<NB;b++)cb(w,b,1);}
    for(int f=0;f<B;f++){for(int c=0;c<K;c++){cp[f][c]=c;off[f][c]=rnd()%M;}
      for(int i=K-1;i>0;i--){int j=rnd()%(i+1);int t=cp[f][i];cp[f][i]=cp[f][j];cp[f][j]=t;}
      for(int t=0;t<T;t++)lo[f][t]=rnd()%M; cf(f,1);}
    double Tm=1.0; int best=1000000;
    for(long it=0;it<iters&&cost>0;it++){
      if((it&0xfff)==0)Tm=T0*pow(T1/T0,(double)it/iters);
      int c0=cost; if(cost<best)best=cost; int r=rnd()%16;
      if(r<10){int w=rnd()%A,x=rnd()%V,y=rnd()%V;if(x/4==y/4)continue;
        cb(w,x/4,-1);cb(w,y/4,-1);int t=wk[w][x];wk[w][x]=wk[w][y];wk[w][y]=t;cb(w,x/4,1);cb(w,y/4,1);
        if(!(cost<=c0||ur()<exp(-(cost-c0)/Tm))){cb(w,x/4,-1);cb(w,y/4,-1);t=wk[w][x];wk[w][x]=wk[w][y];wk[w][y]=t;cb(w,x/4,1);cb(w,y/4,1);}}
      else if(r<12){int w=rnd()%A,x=rnd()%NB,y=rnd()%NB;if(x==y)continue;int t;
        cb(w,x,-1);cb(w,y,-1);for(int q=0;q<4;q++){t=wk[w][4*x+q];wk[w][4*x+q]=wk[w][4*y+q];wk[w][4*y+q]=t;}cb(w,x,1);cb(w,y,1);
        if(!(cost<=c0||ur()<exp(-(cost-c0)/Tm))){cb(w,x,-1);cb(w,y,-1);for(int q=0;q<4;q++){t=wk[w][4*x+q];wk[w][4*x+q]=wk[w][4*y+q];wk[w][4*y+q]=t;}cb(w,x,1);cb(w,y,1);}}
      else { if(B==0)continue; int f=rnd()%B; int sv_cp[K],sv_off[K],sv_lo[T];memcpy(sv_cp,cp[f],sizeof sv_cp);memcpy(sv_off,off[f],sizeof sv_off);memcpy(sv_lo,lo[f],sizeof sv_lo);
        cf(f,-1); int q=rnd()%3;
        if(q==0){off[f][rnd()%K]=rnd()%M;} else if(q==1){lo[f][rnd()%T]=rnd()%M;} else {int x=rnd()%K,y=rnd()%K;int t=cp[f][x];cp[f][x]=cp[f][y];cp[f][y]=t;}
        cf(f,1);
        if(!(cost<=c0||ur()<exp(-(cost-c0)/Tm))){cf(f,-1);memcpy(cp[f],sv_cp,sizeof sv_cp);memcpy(off[f],sv_off,sizeof sv_off);memcpy(lo[f],sv_lo,sizeof sv_lo);cf(f,1);}}
    }
    fprintf(stderr,"att %d cost %d best %d\n",att,cost,best);
    if(cost)continue;
    for(int w=0;w<A;w++)for(int k=0;k<M;k++){int out[NB][4];
      for(int b=0;b<NB;b++){int L=((b%M+k)%M)+M*(b/M);for(int x=0;x<4;x++){int p=wk[w][4*b+x];out[L][x]=M*(p/M)+(p%M+k)%M;}}
      for(int L=0;L<NB;L++)for(int x=0;x<4;x++)printf("%d ",out[L][x]+1);printf("\n");}
    for(int f=0;f<B;f++){int out[NB][4];for(int k=0;k<M;k++)for(int t=0;t<T;t++){int L=(lo[f][t]+k)%M+M*t;for(int x=0;x<4;x++){int c=cp[f][4*t+x];out[L][x]=M*c+(off[f][c]+k)%M;}}
      for(int L=0;L<NB;L++)for(int x=0;x<4;x++)printf("%d ",out[L][x]+1);printf("\n");}
    return 0;
  }
  return 1;}
