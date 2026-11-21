// points (g,i) g<6,i<4 = 4g+i. group H of order 4 acts on i (Z4 or Z2^2). 5 base weeks; oil block j = base + j.
// need: no in-group pairs; every cross pair-orbit covered exactly 3 times by distinct pairs.
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
static unsigned long long s;
static inline unsigned rnd(){s^=s<<13;s^=s>>7;s^=s<<17;return (unsigned)(s>>11);}
int mode;int NW=5;
static inline int act(int p,int a){int g=p/4,i=p%4;return 4*g+(mode?(i^a):((i+a)&3));}
int W[5][24],pc[24][24],oc[24][24],orb[24][24]; // orb rep index
int cost;
static inline int f(int c){return abs(c-3);}
void add(int p,int q,int d){
  if(p/4==q/4){cost+=10*d;return;}
  cost-= (pc[p][q]>1?2*(pc[p][q]-1):0); pc[p][q]+=d;pc[q][p]+=d; cost+=(pc[p][q]>1?2*(pc[p][q]-1):0);
  int o=orb[p][q];int a=o/24,b=o%24; cost-=f(oc[a][b]);oc[a][b]+=d;cost+=f(oc[a][b]);
}
void blk(int w,int b,int d){for(int i=0;i<4;i++)for(int j=i+1;j<4;j++)add(W[w][4*b+i],W[w][4*b+j],d);}
int main(int argc,char**argv){
  mode=atoi(argv[1]);s=atoll(argv[2])*2654435761ULL+88172645463325252ULL;long IT=atol(argv[3]);double T0=atof(argv[4]),T1=atof(argv[5]);
  for(int p=0;p<24;p++)for(int q=0;q<24;q++){int best=1<<30;for(int a=0;a<4;a++){int x=act(p,a),y=act(q,a);if(x>y){int t=x;x=y;y=t;}if(x*24+y<best)best=x*24+y;}orb[p][q]=best;}
  for(int att=0;att<100000;att++){
    memset(pc,0,sizeof pc);memset(oc,0,sizeof oc);cost=0;
    for(int a=0;a<24;a++)for(int b=a+1;b<24;b++)if(a/4!=b/4&&orb[a][b]==a*24+b)cost+=3;
    for(int w=0;w<NW;w++){for(int i=0;i<24;i++)W[w][i]=i;for(int i=23;i>0;i--){int j=rnd()%(i+1);int t=W[w][i];W[w][i]=W[w][j];W[w][j]=t;}
      for(int b=0;b<6;b++)blk(w,b,1);}
    int best=cost;
    for(long it=0;it<IT&&cost;it++){
      double T=T0+(T1-T0)*it/IT;
      int w=rnd()%NW,i=rnd()%24,j=rnd()%24;if(i/4==j/4)continue;
      int old=cost;blk(w,i/4,-1);blk(w,j/4,-1);int t=W[w][i];W[w][i]=W[w][j];W[w][j]=t;blk(w,i/4,1);blk(w,j/4,1);
      if(cost>old&&(rnd()%1000000)>=1e6*exp((old-cost)/T)){blk(w,i/4,-1);blk(w,j/4,-1);t=W[w][i];W[w][i]=W[w][j];W[w][j]=t;blk(w,i/4,1);blk(w,j/4,1);}
      if(cost<best)best=cost;
    }
    fprintf(stderr,"att %d end %d best %d\n",att,cost,best);
    if(!cost){for(int w=0;w<NW;w++){for(int i=0;i<24;i++)printf("%d ",W[w][i]);printf("\n");}printf("\n");fflush(stdout);}
  }
}
