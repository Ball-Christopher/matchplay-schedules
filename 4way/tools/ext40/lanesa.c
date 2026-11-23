// General lane annealer: reorder groups within weeks so each bowler's lane-pair counts are
// floor/ceil.  Input (stdin): r v k, then r lines of v point ids (0-based, groups of k).
// Output: best weeks (same format) and the number of bowlers off on stderr.
// Usage: lanesa seed restarts iters < weeks.txt
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>
static unsigned long long s=88172645463325252ULL;
static inline unsigned long long rnd(void){s^=s<<13;s^=s>>7;s^=s<<17;return s;}
int r,v,k,n,W[64][64],G[64][16],B[64][16],lc[64][16],lo,hi;
int IGN=-1;
static inline int pen(int c){return c<lo?lo-c:(c>hi?c-hi:0);}
#define PEN(p,c) ((p)==IGN?0:pen(c))
int main(int argc,char**argv){s^=atoll(argv[1])*0x9E3779B97F4A7C15ULL;int R=atoi(argv[2]);long N=atol(argv[3]);
  if(scanf("%d %d %d",&r,&v,&k)!=3)return 2;n=v/k;lo=r/n;hi=(r+n-1)/n;
  for(int w=0;w<r;w++)for(int i=0;i<v;i++)if(scanf("%d",&W[w][i])!=1)return 2;
  long best=1L<<40; if(getenv("IGN"))IGN=atoi(getenv("IGN"));
  for(int rs=0;rs<R;rs++){
    int keep=argc>4;double T0=keep?atof(argv[4]):1.0;
    for(int w=0;w<r;w++){for(int g=0;g<n;g++)G[w][g]=g;if(!keep)for(int g=n-1;g>0;g--){int j=rnd()%(g+1);int t=G[w][g];G[w][g]=G[w][j];G[w][j]=t;}}
    memset(lc,0,sizeof lc);
    for(int w=0;w<r;w++)for(int g=0;g<n;g++)for(int x=0;x<k;x++)lc[W[w][g*k+x]][G[w][g]]++;
    long c=0;for(int p=0;p<v;p++)for(int L=0;L<n;L++)c+=PEN(p,lc[p][L]);
    double T=T0;
    for(long it=0;it<N&&c>0;it++){if((it&1023)==0)T=T0*pow(0.02,(double)it/N);
      int w=rnd()%r,a=rnd()%n,b=rnd()%n;if(a==b)continue;int la=G[w][a],lb=G[w][b];long d=0;
      for(int x=0;x<k;x++){int p=W[w][a*k+x];d-=PEN(p,lc[p][la])+PEN(p,lc[p][lb]);lc[p][la]--;lc[p][lb]++;d+=PEN(p,lc[p][la])+PEN(p,lc[p][lb]);}
      for(int x=0;x<k;x++){int p=W[w][b*k+x];d-=PEN(p,lc[p][la])+PEN(p,lc[p][lb]);lc[p][lb]--;lc[p][la]++;d+=PEN(p,lc[p][la])+PEN(p,lc[p][lb]);}
      if(d<=0||(rnd()>>11)*(1.0/9007199254740992.0)<exp(-d/T)){G[w][a]=lb;G[w][b]=la;c+=d;}
      else{for(int x=0;x<k;x++){int p=W[w][a*k+x];lc[p][la]++;lc[p][lb]--;}for(int x=0;x<k;x++){int p=W[w][b*k+x];lc[p][lb]++;lc[p][la]--;}}}
    if(c<best){best=c;memcpy(B,G,sizeof G);}
    fprintf(stderr,"restart %d cost %ld best %ld\n",rs,c,best);if(best==0)break;}
  for(int w=0;w<r;w++){int out[64];for(int g=0;g<n;g++)for(int x=0;x<k;x++)out[B[w][g]*k+x]=W[w][g*k+x];for(int i=0;i<v;i++)printf("%d ",out[i]);printf("\n");}
  return 0;}
