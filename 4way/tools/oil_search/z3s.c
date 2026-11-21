// v=24, Z3 x 8 classes, two-phase type-level SA. Phase 1: blocks A,B (2 base weeks each) clash-free with disjoint leaves.
// Phase 2: block C (2 base) + D (1 base + 2 invariant) completing every type to 3.
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#define V 24
#define NTY 192
static unsigned long long s=88172645463325252ULL;
static inline unsigned long long rnd(){s^=s<<13;s^=s>>7;s^=s<<17;return s;}
static inline double ur(){return (double)(rnd()>>11)/9007199254740992.0;}
int A[4][V],P1[4][V],sl[2][8],off[2][8],bid[6];int cnt[NTY],cw[2][NTY],tgt[NTY],valid[NTY],RW=1,nbw,niw,phase;
static inline int ty(int p,int q){if(p>q){int t=p;p=q;q=t;}
  int a=p/3,i=p%3,b=q/3,j=q%3;int d=(j-i+3)%3;if(a==b)d=1;return (a*8+b)*3+d;}
static inline void addw(int w,int g,int v){int*q=A[w]+4*g;int B=bid[w];for(int x=0;x<4;x++)for(int y=x+1;y<4;y++){int t=ty(q[x],q[y]);cnt[t]+=v;cw[B][t]+=v;}}
static inline void addf(int f,int v){int B=bid[nbw+f];for(int g=0;g<2;g++)for(int x=0;x<4;x++)for(int y=x+1;y<4;y++){int a=sl[f][4*g+x],b=sl[f][4*g+y];int t=ty(3*a+off[f][a],3*b+off[f][b]);cnt[t]+=v;cw[B][t]+=v;}}
static int cost(){int c=0;for(int t=0;t<NTY;t++){if(!valid[t])continue;if(phase==1)c+=(cnt[t]==0);else c+=abs(cnt[t]-tgt[t]);for(int w=0;w<2;w++)if(cw[w][t]>1)c+=RW*(cw[w][t]-1);}return c;}
static int solve(long iters,double T0,double T1,int natt){
  for(int att=0;att<natt;att++){
    for(int a=0;a<nbw;a++){for(int i=0;i<V;i++)A[a][i]=i;for(int i=V-1;i>0;i--){int j=rnd()%(i+1);int t=A[a][i];A[a][i]=A[a][j];A[a][j]=t;}}
    for(int f=0;f<niw;f++){for(int a=0;a<8;a++){sl[f][a]=a;off[f][a]=rnd()%3;}for(int i=7;i>0;i--){int j=rnd()%(i+1);int t=sl[f][i];sl[f][i]=sl[f][j];sl[f][j]=t;}}
    memset(cnt,0,sizeof cnt);memset(cw,0,sizeof cw);
    for(int w=0;w<nbw;w++)for(int g=0;g<6;g++)addw(w,g,1);for(int f=0;f<niw;f++)addf(f,1);
    int c=cost();double T=T0;
    for(long it=0;it<iters&&c>0;it++){if((it&0xfff)==0)T=T0*pow(T1/T0,(double)it/iters);
      if(niw&&rnd()%12==0){int f=rnd()%niw;int so[8],oo[8];memcpy(so,sl[f],sizeof so);memcpy(oo,off[f],sizeof oo);addf(f,-1);
        if(rnd()%2)off[f][rnd()%8]=rnd()%3;else{int x=rnd()%8,y=rnd()%8;int t=sl[f][x];sl[f][x]=sl[f][y];sl[f][y]=t;}
        addf(f,1);int nc=cost();
        if(nc<=c||ur()<exp(-(nc-c)/T))c=nc;else{addf(f,-1);memcpy(sl[f],so,sizeof so);memcpy(off[f],oo,sizeof oo);addf(f,1);}}
      else{int w=rnd()%nbw,x=rnd()%V,y=rnd()%V;if(x/4==y/4)continue;addw(w,x/4,-1);addw(w,y/4,-1);int t=A[w][x];A[w][x]=A[w][y];A[w][y]=t;addw(w,x/4,1);addw(w,y/4,1);int nc=cost();
        if(nc<=c||ur()<exp(-(nc-c)/T))c=nc;else{addw(w,x/4,-1);addw(w,y/4,-1);t=A[w][x];A[w][x]=A[w][y];A[w][y]=t;addw(w,x/4,1);addw(w,y/4,1);}}
    }
    fprintf(stderr,"  phase %d att %d c %d\n",phase,att,c);
    if(c==0)return 1;
  }return 0;}
static void emit(int w,int blk){for(int k=0;k<3;k++){printf("%d:",blk);for(int i=0;i<V;i++){int p=A[w][i];printf(" %d",(p/3)*3+(p%3+k)%3);}printf("\n");}}
int main(int argc,char**argv){
  if(getenv("RW"))RW=atoi(getenv("RW"));
  s^=atoll(argv[1])*0x9E3779B97F4A7C15ULL;for(int i=0;i<20;i++)rnd();
  long iters=atol(argv[2]);double T0=atof(argv[3]),T1=atof(argv[4]);int natt=atoi(argv[5]);
  for(int a=0;a<8;a++)for(int b=a;b<8;b++)for(int d=0;d<3;d++){if(a==b&&d!=1)continue;valid[(a*8+b)*3+d]=1;}
  for(int trial=0;trial<100000;trial++){
    phase=1;nbw=4;niw=0;bid[0]=bid[1]=0;bid[2]=bid[3]=1;
    if(!solve(iters,T0,T1,1000))continue;
    memcpy(P1,A,sizeof P1);for(int t=0;t<NTY;t++)tgt[t]=3-cnt[t];
    phase=2;nbw=3;niw=2;bid[0]=bid[1]=0;bid[2]=1;bid[3]=bid[4]=1;
    if(!solve(iters,T0,T1,natt))continue;
    int C[4][V];memcpy(C,A,sizeof C);memcpy(A,P1,sizeof P1);
    emit(0,0);emit(1,0);emit(2,1);emit(3,1);memcpy(A,C,sizeof C);emit(0,2);emit(1,2);emit(2,3);
    for(int f=0;f<2;f++){printf("3:");for(int g=0;g<2;g++)for(int k=0;k<3;k++)for(int x=0;x<4;x++){int a=sl[f][4*g+x];printf(" %d",3*a+(off[f][a]+k)%3);}printf("\n");}
    return 0;
  }return 1;}
