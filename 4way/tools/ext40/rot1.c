// 1-rotational base week over Z_q u {inf} (q = v-1, inf = q) for groups of 4 with every
// difference +-d (d = 1..q/2) covered lambda times; developed mod q this is a resolvable
// 2-(v,4,lambda) design.  Base group j stays on lane pair j, so every finite bowler is
// lane-exact; inf is the vacant slot.  Simulated annealing on difference counts.
// Usage: rot1 v lambda seed   -> prints the base week (q+1 points, groups of 4)
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
static unsigned long long s=88172645463325252ULL;
static inline unsigned long long rnd(void){s^=s<<13;s^=s>>7;s^=s<<17;return s;}
int q,lam,v,wk[64],cnt[64];long cost;
static int dif(int a,int b){if(a==q||b==q)return -1;int d=(a-b+q)%q;return d>q-d?q-d:d;}
static void blk(int b,int sg){for(int x=0;x<4;x++)for(int y=x+1;y<4;y++){int d=dif(wk[4*b+x],wk[4*b+y]);if(d<0)continue;
  int w=(2*d==q)?2:1; cost-=labs(cnt[d]-lam); cnt[d]+=sg*w; cost+=labs(cnt[d]-lam);}}
int main(int argc,char**argv){v=atoi(argv[1]);lam=atoi(argv[2]);s^=atoll(argv[3])*0x9E3779B97F4A7C15ULL;q=v-1;
  for(int att=0;att<1000;att++){
    for(int i=0;i<v;i++)wk[i]=i;for(int i=v-1;i>0;i--){int j=rnd()%(i+1);int t=wk[i];wk[i]=wk[j];wk[j]=t;}
    for(int d=0;d<64;d++)cnt[d]=0;cost=0;for(int d=1;d<=q/2;d++)cost+=lam;
    for(int b=0;b<v/4;b++)blk(b,1);
    double T=1.5;long it,N=20000000;
    for(it=0;it<N&&cost>0;it++){if((it&1023)==0)T=1.5*pow(0.02,(double)it/N);
      int x=rnd()%v,y=rnd()%v;if(x/4==y/4)continue;long c0=cost;
      blk(x/4,-1);blk(y/4,-1);int t=wk[x];wk[x]=wk[y];wk[y]=t;blk(x/4,1);blk(y/4,1);
      if(!(cost<=c0||(rnd()>>11)*(1.0/9007199254740992.0)<exp(-(cost-c0)/T))){blk(x/4,-1);blk(y/4,-1);t=wk[x];wk[x]=wk[y];wk[y]=t;blk(x/4,1);blk(y/4,1);}}
    fprintf(stderr,"att %d cost %ld it %ld\n",att,cost,it);
    if(!cost){for(int i=0;i<v;i++)printf("%d ",wk[i]);printf("\n");return 0;}}
  return 1;}
