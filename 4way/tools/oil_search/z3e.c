// v=24, Z3 x 8 classes, decomposed: type leaves L1..L4 chosen first, then each block solved separately by SA.
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#define V 24
#define NTY 192
static unsigned long long s=88172645463325252ULL;
static inline unsigned long long rnd(){s^=s<<13;s^=s>>7;s^=s<<17;return s;}
static inline double ur(){return (double)(rnd()>>11)/9007199254740992.0;}
int A[2][V],sl[2][8],off[2][8];int cnt[NTY],tgt[NTY],nbw,niw;
static inline int ty(int p,int q){if(p>q){int t=p;p=q;q=t;}
  int a=p/3,i=p%3,b=q/3,j=q%3;int d=(j-i+3)%3;if(a==b)d=1;return (a*8+b)*3+d;}
static int c;
static inline void bump(int t,int v){c-=abs(cnt[t]-tgt[t]);cnt[t]+=v;c+=abs(cnt[t]-tgt[t]);}
static inline void addw(int w,int g,int v){int*q=A[w]+4*g;for(int x=0;x<4;x++)for(int y=x+1;y<4;y++)bump(ty(q[x],q[y]),v);}
static inline void addf(int f,int v){for(int g=0;g<2;g++)for(int x=0;x<4;x++)for(int y=x+1;y<4;y++){int a=sl[f][4*g+x],b=sl[f][4*g+y];bump(ty(3*a+off[f][a],3*b+off[f][b]),v);}}
static int solve(long iters,double T0,double T1,int natt){
  for(int att=0;att<natt;att++){
    for(int a=0;a<nbw;a++){for(int i=0;i<V;i++)A[a][i]=i;for(int i=V-1;i>0;i--){int j=rnd()%(i+1);int t=A[a][i];A[a][i]=A[a][j];A[a][j]=t;}}
    for(int f=0;f<niw;f++){for(int a=0;a<8;a++){sl[f][a]=a;off[f][a]=rnd()%3;}for(int i=7;i>0;i--){int j=rnd()%(i+1);int t=sl[f][i];sl[f][i]=sl[f][j];sl[f][j]=t;}}
    memset(cnt,0,sizeof cnt);c=0;for(int t=0;t<NTY;t++)c+=tgt[t];
    for(int w=0;w<nbw;w++)for(int g=0;g<6;g++)addw(w,g,1);for(int f=0;f<niw;f++)addf(f,1);
    double T=T0;
    for(long it=0;it<iters&&c>0;it++){if((it&0xfff)==0)T=T0*pow(T1/T0,(double)it/iters);int oc=c;
      if(niw&&rnd()%10==0){int f=rnd()%niw;int so[8],oo[8];memcpy(so,sl[f],sizeof so);memcpy(oo,off[f],sizeof oo);addf(f,-1);
        if(rnd()%2)off[f][rnd()%8]=rnd()%3;else{int x=rnd()%8,y=rnd()%8;int t=sl[f][x];sl[f][x]=sl[f][y];sl[f][y]=t;}
        addf(f,1);
        if(!(c<=oc||ur()<exp(-(c-oc)/T))){addf(f,-1);memcpy(sl[f],so,sizeof so);memcpy(oo,oo,0);memcpy(off[f],oo,sizeof oo);addf(f,1);}}
      else{int w=rnd()%nbw,x=rnd()%V,y=rnd()%V;if(x/4==y/4)continue;addw(w,x/4,-1);addw(w,y/4,-1);int t=A[w][x];A[w][x]=A[w][y];A[w][y]=t;addw(w,x/4,1);addw(w,y/4,1);
        if(!(c<=oc||ur()<exp(-(c-oc)/T))){addw(w,x/4,-1);addw(w,y/4,-1);t=A[w][x];A[w][x]=A[w][y];A[w][y]=t;addw(w,x/4,1);addw(w,y/4,1);}}
    }
    if(c==0)return 1;
  }return 0;}
static void emit(int blk){
  for(int w=0;w<nbw;w++)for(int k=0;k<3;k++){printf("%d:",blk);for(int i=0;i<V;i++){int p=A[w][i];printf(" %d",(p/3)*3+(p%3+k)%3);}printf("\n");}
  for(int f=0;f<niw;f++){printf("%d:",blk);for(int g=0;g<2;g++)for(int k=0;k<3;k++)for(int x=0;x<4;x++){int a=sl[f][4*g+x];printf(" %d",3*a+(off[f][a]+k)%3);}printf("\n");}}
int main(int argc,char**argv){
  s^=atoll(argv[1])*0x9E3779B97F4A7C15ULL;for(int i=0;i<20;i++)rnd();
  long iters=atol(argv[2]);double T0=atof(argv[3]),T1=atof(argv[4]);int natt=atoi(argv[5]);
  for(int trial=0;trial<100000;trial++){
    int leave[NTY];memset(leave,-1,sizeof leave);
    int mt[21][4],md[21];int n=0;
    for(int d=0;d<3;d++){int pm[8];for(int i=0;i<8;i++)pm[i]=i;for(int i=7;i>0;i--){int j=rnd()%(i+1);int t=pm[i];pm[i]=pm[j];pm[j]=t;}
      for(int r=0;r<7;r++){for(int k=0;k<4;k++){int x=k==0?7:(r+k)%7,y=k==0?r:(r-k+7)%7;x=pm[x];y=pm[y];if(x>y){int t=x;x=y;y=t;}mt[n][k]=(x*8+y)*3+d;}n++;}}
    int ord[21];for(int i=0;i<21;i++)ord[i]=i;for(int i=20;i>0;i--){int j=rnd()%(i+1);int t=ord[i];ord[i]=ord[j];ord[j]=t;}
    for(int i=0;i<21;i++){int L=i<5?0:i<10?1:i<15?2:3;for(int k=0;k<4;k++)leave[mt[ord[i]][k]]=L;}
    for(int a=0;a<8;a++)leave[(a*8+a)*3+1]=3;
    int ok=1;
    // hardest first? block 3 (1 base + 2 inv), then 0..2. buffer output
    static char buf[1<<16];setvbuf(stdout,buf,_IOFBF,sizeof buf);
    for(int bi=0;bi<4&&ok;bi++){int blk=bi;
      for(int t=0;t<NTY;t++)tgt[t]=(leave[t]>=0&&leave[t]!=blk)?1:0;
      nbw=blk==3?1:2;niw=blk==3?2:0;
      ok=solve(iters,T0,T1,natt);fprintf(stderr,"trial %d block %d ok %d (c=%d)\n",trial,blk,ok,c);
      if(ok)emit(blk);}
    if(ok){fflush(stdout);return 0;}
    fflush(stdout);freopen(argv[6],"w",stdout); // discard partial
  }return 1;}
