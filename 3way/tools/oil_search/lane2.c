// lane SA: stdin: v n r then r*n*3 ints (0-based). argv: seed iters T
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>
int v,n,r,BW[64][16][3],best=1<<30,W[64][16][3],cnt[64][16],lo,hi;
static unsigned long long s[2];
static inline unsigned long long rnd(){unsigned long long a=s[0],b=s[1];s[0]=b;a^=a<<23;s[1]=a^b^(a>>17)^(b>>26);return s[1]+b;}
static inline int pen(int c){int d=c>hi?c-hi:(c<lo?lo-c:0);return d*d;}
int main(int argc,char**argv){
  int seed=atoi(argv[1]);long long iters=atoll(argv[2]);double T=atof(argv[3]);
  s[0]=seed*2654435761ULL+1;s[1]=88172645463325252ULL^seed;
  scanf("%d %d %d",&v,&n,&r);lo=r/n;hi=(r+n-1)/n;
  for(int w=0;w<r;w++)for(int g=0;g<n;g++)for(int k=0;k<3;k++)scanf("%d",&W[w][g][k]);
  for(int w=0;w<r;w++)for(int g=n-1;g>0;g--){int j=rnd()%(g+1);for(int k=0;k<3;k++){int t=W[w][g][k];W[w][g][k]=W[w][j][k];W[w][j][k]=t;}}
  for(int w=0;w<r;w++)for(int g=0;g<n;g++)for(int k=0;k<3;k++)cnt[W[w][g][k]][g]++;
  int cost=0;for(int p=0;p<v;p++)for(int l=0;l<n;l++)cost+=pen(cnt[p][l]);
  double ex[64];for(int i=0;i<64;i++)ex[i]=exp(-i/T);
  long long it;
  for(it=0;it<iters&&cost;it++){
    int w=rnd()%r,a=rnd()%n,b=rnd()%n;if(a==b)continue;int d=0;
    for(int k=0;k<3;k++){int p=W[w][a][k];d+=pen(cnt[p][a]-1)+pen(cnt[p][b]+1)-pen(cnt[p][a])-pen(cnt[p][b]);
      p=W[w][b][k];d+=pen(cnt[p][b]-1)+pen(cnt[p][a]+1)-pen(cnt[p][b])-pen(cnt[p][a]);}
    if(d<=0||(d<64&&(rnd()>>11)*(1.0/9007199254740992.0)<ex[d])){
      for(int k=0;k<3;k++){int p=W[w][a][k],q=W[w][b][k];cnt[p][a]--;cnt[p][b]++;cnt[q][b]--;cnt[q][a]++;W[w][a][k]=q;W[w][b][k]=p;}
      cost+=d; if(cost<best){best=cost;memcpy(BW,W,sizeof W);}}
  }
  fprintf(stderr,"seed %d best %d iters %lld\n",seed,best,it);memcpy(W,BW,sizeof W);
  {for(int w=0;w<r;w++){for(int g=0;g<n;g++)for(int k=0;k<3;k++)printf("%d ",W[w][g][k]);printf("\n");}return 0;}
  return 1;}
