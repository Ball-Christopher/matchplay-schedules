// Z_M semiregular on V=M*C points p=a*M+i; lanes NL=V/4 in NT=NL/M tracks, rotated by the group. C=4*NT.
// NA base weeks (orbit M) + NI invariant weeks. cost = A*sum (pr-3)^2 + RW*block repeats + B*lane excess
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#ifndef M
#define M 3
#endif
#ifndef NT
#define NT 1
#endif
#define C (4*NT)
#define V (M*C)
#define NL (M*NT)
#define R (V-1)
#define HI ((R+NL-1)/NL)
#define LO (R/NL)
#define MX 12
static unsigned long long s=88172645463325252ULL;
static inline unsigned long long rnd(){s^=s<<13;s^=s>>7;s^=s<<17;return s;}
static inline double ur(){return (double)(rnd()>>11)/9007199254740992.0;}
int NA,NI,nblk; int bA[MX],bI[MX];
typedef struct{int A[MX][V]; int sl[MX][C],off[MX][C],lo[MX][NT];} St;
St st,sv; int W[R][NL][4],wb[R]; int pr[V][V],bp[6][V][V],ln[V][NL]; int AW=4,BW=2,RW=1; int dev,rep,lan;
static void expand(){int w=0;
  for(int a=0;a<NA;a++)for(int k=0;k<M;k++){wb[w]=bA[a];for(int b=0;b<NL;b++){int L=(b/M)*M+(b%M+k)%M;for(int x=0;x<4;x++){int p=st.A[a][4*b+x];W[w][L][x]=(p/M)*M+(p%M+k)%M;}}w++;}
  for(int f=0;f<NI;f++){wb[w]=bI[f];for(int t=0;t<NT;t++)for(int k=0;k<M;k++){int L=t*M+(st.lo[f][t]+k)%M;for(int x=0;x<4;x++){int a=st.sl[f][4*t+x];W[w][L][x]=a*M+(st.off[f][a]+k)%M;}}w++;}
}
static int cost(){expand();memset(pr,0,sizeof pr);memset(bp,0,sizeof bp);memset(ln,0,sizeof ln);
  for(int w=0;w<R;w++)for(int L=0;L<NL;L++){int*g=W[w][L];for(int x=0;x<4;x++){ln[g[x]][L]++;for(int y=x+1;y<4;y++){int a=g[x],b=g[y];if(a>b){int t=a;a=b;b=t;}pr[a][b]++;bp[wb[w]][a][b]++;}}}
  dev=rep=lan=0;
  for(int a=0;a<V;a++){for(int b=a+1;b<V;b++){int d=pr[a][b]-3;dev+=d*d;for(int k=0;k<nblk;k++)if(bp[k][a][b]>1)rep+=bp[k][a][b]-1;}
    for(int L=0;L<NL;L++){int x=ln[a][L];lan+=x>HI?x-HI:(x<LO?LO-x:0);}}
  return AW*dev+RW*rep+BW*lan;}
static void shuf(int*a,int n){for(int i=n-1;i>0;i--){int j=rnd()%(i+1);int t=a[i];a[i]=a[j];a[j]=t;}}
static void init(){for(int a=0;a<NA;a++){for(int i=0;i<V;i++)st.A[a][i]=i;shuf(st.A[a],V);}
  for(int f=0;f<NI;f++){for(int a=0;a<C;a++){st.sl[f][a]=a;st.off[f][a]=rnd()%M;}shuf(st.sl[f],C);for(int t=0;t<NT;t++)st.lo[f][t]=rnd()%M;}}
static void move(){int tot=NA*10+NI*2;int r=rnd()%tot;
  if(r<NA*10){int a=rnd()%NA;int x,y;do{x=rnd()%V;y=rnd()%V;}while(x/4==y/4);
    if(rnd()%8==0){int bx=x/4,by=y/4;for(int q=0;q<4;q++){int t=st.A[a][4*bx+q];st.A[a][4*bx+q]=st.A[a][4*by+q];st.A[a][4*by+q]=t;}}
    else{int t=st.A[a][x];st.A[a][x]=st.A[a][y];st.A[a][y]=t;}return;}
  int f=rnd()%NI;int q=rnd()%(NT>1?4:3);
  if(q<2)st.off[f][rnd()%C]=rnd()%M;else if(q==2)st.lo[f][rnd()%NT]=rnd()%M;
  else{int x=rnd()%C,y=rnd()%C;int t=st.sl[f][x];st.sl[f][x]=st.sl[f][y];st.sl[f][y]=t;}}
static void out(){cost();printf("DEV %d REP %d LAN %d :",dev,rep,lan);for(int w=0;w<R;w++){printf(" |%d|",wb[w]);for(int L=0;L<NL;L++)for(int x=0;x<4;x++)printf(" %d",W[w][L][x]+1);}printf("\n");fflush(stdout);}
int main(int argc,char**argv){ // seed iters T0 T1 NA NI blockids(NA+NI) ; env AW BW RW STOP0
  if(getenv("AW"))AW=atoi(getenv("AW"));if(getenv("BW"))BW=atoi(getenv("BW"));if(getenv("RW"))RW=atoi(getenv("RW"));
  s^=atoll(argv[1])*0x9E3779B97F4A7C15ULL;for(int i=0;i<20;i++)rnd();
  long iters=atol(argv[2]);double T0=atof(argv[3]),T1=atof(argv[4]);NA=atoi(argv[5]);NI=atoi(argv[6]);
  if(NA*M+NI!=R){fprintf(stderr,"bad mix\n");return 2;}
  for(int i=0;i<NA;i++){bA[i]=atoi(argv[7+i]);if(bA[i]>=nblk)nblk=bA[i]+1;}
  for(int i=0;i<NI;i++){bI[i]=atoi(argv[7+NA+i]);if(bI[i]>=nblk)nblk=bI[i]+1;}
  int gb=1<<30;
  for(int att=0;att<1000000;att++){init();int c=cost();double T=T0;
    for(long it=0;it<iters&&c>0;it++){if((it&0xff)==0)T=T0*pow(T1/T0,(double)it/iters);
      sv=st;move();int nc=cost();if(nc<=c||ur()<exp(-(nc-c)/T))c=nc;else st=sv;}
    cost();fprintf(stderr,"att %d dev %d rep %d lan %d\n",att,dev,rep,lan);
    if(dev==0){int sc=rep*100+lan;if(sc<gb){gb=sc;out();}if(sc==0)return 0;}
  }
  return 1;}
