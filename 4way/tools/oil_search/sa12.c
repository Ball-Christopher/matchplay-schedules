// v=12 direct SA: 11 weeks x 3 groups of 4. cost = A*pairdev + repeats(within blocks) + B*lane excess
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
static unsigned long long s=88172645463325252ULL;
static inline unsigned long long rnd(){s^=s<<13;s^=s>>7;s^=s<<17;return s;}
static inline double ur(){return (double)(rnd()>>11)/9007199254740992.0;}
int W[11][12],blk[11],nb; int pr[12][12],bp[4][12][12],ln[12][3];
int A=4,B=2,RW=1; int dev,rep,lan;
static int cost(){memset(pr,0,sizeof pr);memset(bp,0,sizeof bp);memset(ln,0,sizeof ln);
  for(int w=0;w<11;w++)for(int g=0;g<3;g++){int*q=W[w]+4*g;for(int x=0;x<4;x++){ln[q[x]][g]++;for(int y=x+1;y<4;y++){int a=q[x],b=q[y];if(a>b){int t=a;a=b;b=t;}pr[a][b]++;bp[blk[w]][a][b]++;}}}
  dev=rep=lan=0;
  for(int a=0;a<12;a++){for(int b=a+1;b<12;b++){dev+=(pr[a][b]-3)*(pr[a][b]-3);for(int k=0;k<nb;k++)if(bp[k][a][b]>1)rep+=bp[k][a][b]-1;}
    for(int g=0;g<3;g++){int x=ln[a][g];lan+=x>4?x-4:(x<3?3-x:0);}}
  return A*dev+RW*rep+B*lan;}
int main(int argc,char**argv){ if(getenv("AA"))A=atoi(getenv("AA")); if(getenv("BB"))B=atoi(getenv("BB"));if(getenv("RW"))RW=atoi(getenv("RW"));// seed iters T0 T1 sizes...
  s^=atoll(argv[1])*0x9E3779B97F4A7C15ULL;for(int i=0;i<20;i++)rnd();
  long iters=atol(argv[2]);double T0=atof(argv[3]),T1=atof(argv[4]);
  nb=argc-5;int w=0;for(int k=0;k<nb;k++)for(int j=atoi(argv[5+k]);j>0;j--)blk[w++]=k;
  int gb=1<<30;
  for(int att=0;att<1000000;att++){
    for(int w=0;w<11;w++){for(int i=0;i<12;i++)W[w][i]=i;for(int i=11;i>0;i--){int j=rnd()%(i+1);int t=W[w][i];W[w][i]=W[w][j];W[w][j]=t;}}
    int c=cost();double T=T0;
    for(long it=0;it<iters;it++){if((it&0xff)==0)T=T0*pow(T1/T0,(double)it/iters);
      int w=rnd()%11,x=rnd()%12,y=rnd()%12;if(x/4==y/4)continue;
      int t=W[w][x];W[w][x]=W[w][y];W[w][y]=t;int nc=cost();
      if(nc<=c||ur()<exp(-(nc-c)/T))c=nc;else{t=W[w][x];W[w][x]=W[w][y];W[w][y]=t;}
    }
    cost();
    fprintf(stderr,"dev %d rep %d lan %d\n",dev,rep,lan);if(dev==0){int sc=rep*10+lan;if(sc<gb){gb=sc;printf("REP %d LAN %d :",rep,lan);for(int w=0;w<11;w++)for(int i=0;i<12;i++)printf(" %d",W[w][i]);printf("\n");fflush(stdout);}}
  }
}
