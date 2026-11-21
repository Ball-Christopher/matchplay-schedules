// lane assignment for a given resolvable design. stdin: v r, then r lines of v ints (1-based).
// mode 0: exhaustive DFS (small), mode 1: SA.  prints solution weeks if found.
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#define MAXV 28
#define MAXR 30
int v,r,n,lo,hi; int W[MAXR][MAXV/4][4]; int perm[MAXR][MAXV/4]; int cnt[MAXV][MAXV/4];
static unsigned long long s=88172645463325252ULL;
static inline unsigned long long rnd(){s^=s<<13;s^=s>>7;s^=s<<17;return s;}
static inline double ur(){return (double)(rnd()>>11)/9007199254740992.0;}
int P[720][6],np=0;
static void gen(int*p,int k){if(k==n){memcpy(P[np++],p,sizeof(int)*6);return;}for(int i=k;i<n;i++){int t=p[k];p[k]=p[i];p[i]=t;gen(p,k+1);t=p[k];p[k]=p[i];p[i]=t;}}
long nodes=0;
static int dfs(int w){ nodes++; if(w==r)return 1; int rem=r-w-1;
  for(int q=0;q<(w==0?1:np);q++){int ok=1;
    for(int b=0;b<n;b++)for(int x=0;x<4;x++)cnt[W[w][b][x]][P[q][b]]++;
    for(int b=0;b<n&&ok;b++)for(int x=0;x<4&&ok;x++){int p=W[w][b][x];if(cnt[p][P[q][b]]>hi)ok=0;}
    if(ok)for(int p=0;p<v&&ok;p++)for(int L=0;L<n;L++)if(cnt[p][L]+rem<lo){ok=0;break;}
    if(ok){memcpy(perm[w],P[q],sizeof(int)*n); if(dfs(w+1))return 1;}
    for(int b=0;b<n;b++)for(int x=0;x<4;x++)cnt[W[w][b][x]][P[q][b]]--;}
  return 0;}
static inline int lc(int x){return x>hi?x-hi:(x<lo?lo-x:0);}
static void out(){for(int w=0;w<r;w++){int inv[6];for(int b=0;b<n;b++)inv[perm[w][b]]=b;for(int L=0;L<n;L++)for(int x=0;x<4;x++)printf("%d ",W[w][inv[L]][x]+1);printf("\n");}}
int main(int argc,char**argv){int mode=atoi(argv[1]); if(argc>2)s^=atoll(argv[2])*0x9E3779B97F4A7C15ULL; for(int i=0;i<20;i++)rnd();
  long iters=argc>3?atol(argv[3]):100000000; double T0=argc>4?atof(argv[4]):0.5,T1=argc>5?atof(argv[5]):0.1;
  if(scanf("%d %d",&v,&r)!=2)return 2; n=v/4; lo=r/n; hi=(r+n-1)/n;
  for(int w=0;w<r;w++)for(int b=0;b<n;b++)for(int x=0;x<4;x++){scanf("%d",&W[w][b][x]);W[w][b][x]--;}
  if(mode==0){int p0[6]={0,1,2,3,4,5};gen(p0,0);int ok=dfs(0);fprintf(stderr,"dfs %s nodes %ld\n",ok?"FEASIBLE":"INFEASIBLE",nodes);if(ok)out();return !ok;}
  int cost=0,best=1<<30;
  for(int w=0;w<r;w++){for(int b=0;b<n;b++)perm[w][b]=b;for(int i=n-1;i>0;i--){int j=rnd()%(i+1);int t=perm[w][i];perm[w][i]=perm[w][j];perm[w][j]=t;}
    for(int b=0;b<n;b++)for(int x=0;x<4;x++)cnt[W[w][b][x]][perm[w][b]]++;}
  for(int p=0;p<v;p++)for(int L=0;L<n;L++)cost+=lc(cnt[p][L]);
  double T=T0;
  for(long it=0;it<iters&&cost>0;it++){ if((it&0xfff)==0)T=T0*pow(T1/T0,(double)it/iters);
    int w=rnd()%r,a=rnd()%n,b=rnd()%n;if(a==b)continue;int La=perm[w][a],Lb=perm[w][b];int d=0;
    for(int x=0;x<4;x++){int p=W[w][a][x],q=W[w][b][x];
      d+=lc(cnt[p][La]-1)-lc(cnt[p][La])+lc(cnt[p][Lb]+1)-lc(cnt[p][Lb]);
      d+=lc(cnt[q][Lb]-1)-lc(cnt[q][Lb])+lc(cnt[q][La]+1)-lc(cnt[q][La]);}
    if(d<=0||ur()<exp(-d/T)){for(int x=0;x<4;x++){int p=W[w][a][x],q=W[w][b][x];cnt[p][La]--;cnt[p][Lb]++;cnt[q][Lb]--;cnt[q][La]++;}
      perm[w][a]=Lb;perm[w][b]=La;cost+=d;if(cost<best)best=cost;}
  }
  fprintf(stderr,"sa cost %d best %d\n",cost,best); if(cost==0)out(); return cost!=0;}
