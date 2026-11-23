// Resolvable 2-(40,4,1) as (Z_13 x 3) u {inf} (point 13*class+i, inf = 39), the analogue of
// the library's v28 (Z_9 x 3 u inf): one base week of 10 groups whose pairs cover every
// pair orbit exactly once (39 mixed, 18 pure, 3 inf-orbits = 60 = 10 x 6), developed mod 13.
// Randomised DFS (smallest free point first) with a node limit and restarts.
// Usage: dfs13 seed ndesigns [nodelimit]   -> lines of 40 point ids (base week, groups of 4)
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define M 13
#define V 40
#define INF 39
static unsigned long long s=88172645463325252ULL;
static inline unsigned long long rnd(void){s^=s<<13;s^=s>>7;s^=s<<17;return s;}
static int orb(int p,int q){
  if(p==INF||q==INF){int x=p==INF?q:p;return 57+x/M;}
  int a=p/M,i=p%M,b=q/M,j=q%M;if(a>b){int t=a;a=b;b=t;t=i;i=j;j=t;}
  if(a!=b){int pi=(a==0&&b==1)?0:(a==0&&b==2)?1:2;return pi*M+(j-i+M)%M;}
  int d=(j-i+M)%M;if(d>M-d)d=M-d;return 39+a*6+(d-1);}
int used[64],inuse[V],blk[V],nb,perm[V];long nodes,NL;
int PSI=0,MU=3; static int psi(int p){if(p==INF)return INF;return M*((p/M+1)%3)+(MU*(p%M))%M;}
static int place(int*B,int*pts,int*orbs,int*np,int*no){int imgs[3][4];int ni=0;int cur[4];memcpy(cur,B,16);
  for(int k=0;k<(PSI?3:1);k++){int dup=0;for(int j=0;j<ni;j++){int same=1;for(int x=0;x<4&&same;x++){int f=0;for(int y=0;y<4;y++)if(imgs[j][y]==cur[x])f=1;if(!f)same=0;}if(same)dup=1;}
    if(!dup)memcpy(imgs[ni++],cur,16);for(int x=0;x<4;x++)cur[x]=psi(cur[x]);}
  *np=0;*no=0;
  for(int j=0;j<ni;j++){for(int x=0;x<4;x++){int p=imgs[j][x];if(inuse[p])return 0;for(int k=0;k<*np;k++)if(pts[k]==p)return 0;pts[(*np)++]=p;}
    for(int x=0;x<4;x++)for(int y=x+1;y<4;y++){int o=orb(imgs[j][x],imgs[j][y]);if(used[o])return 0;for(int k=0;k<*no;k++)if(orbs[k]==o)return 0;orbs[(*no)++]=o;}}
  for(int k=0;k<*np;k++)inuse[pts[k]]=1;for(int k=0;k<*no;k++)used[orbs[k]]=1;for(int j=0;j<ni;j++){memcpy(&blk[4*nb],imgs[j],16);nb++;}return ni;}
static int dfs(void){
  if(++nodes>NL)return 0;
  int p=-1;for(int i=0;i<V;i++)if(!inuse[perm[i]]){p=perm[i];break;}
  if(p<0)return 1;
  for(int qi=0;qi<V;qi++){int q=perm[qi];if(q==p||inuse[q])continue;int o1=orb(p,q);if(used[o1])continue;
    for(int ri=qi+1;ri<V;ri++){int r=perm[ri];if(r==p||inuse[r])continue;int o2=orb(p,r),o3=orb(q,r);if(used[o2]||used[o3]||o2==o3||o1==o2||o1==o3)continue;
      for(int ti=ri+1;ti<V;ti++){int t=perm[ti];if(t==p||inuse[t])continue;
        int B[4]={p,q,r,t},pts[12],orbs[18],np,no;int ni=place(B,pts,orbs,&np,&no);
        if(ni){if(dfs())return 1;for(int k=0;k<np;k++)inuse[pts[k]]=0;for(int k=0;k<no;k++)used[orbs[k]]=0;nb-=ni;}
        if(nodes>NL)return 0;}}}
  return 0;}
int main(int argc,char**argv){s^=atoll(argv[1])*0x9E3779B97F4A7C15ULL;for(int i=0;i<10;i++)rnd();
  int nd=atoi(argv[2]); if(getenv("PSI")){PSI=1;MU=atoi(getenv("PSI"));}NL=argc>3?atol(argv[3]):200000;int found=0;long tries=0;
  while(found<nd){tries++;memset(used,0,sizeof used);memset(inuse,0,sizeof inuse);nb=0;nodes=0;
    for(int i=0;i<V;i++)perm[i]=i;for(int i=V-1;i>0;i--){int j=rnd()%(i+1);int t=perm[i];perm[i]=perm[j];perm[j]=t;}
    if(dfs()){found++;for(int i=0;i<V;i++)printf("%d ",blk[i]);printf("\n");fflush(stdout);fprintf(stderr,"found %d after %ld tries\n",found,tries);}}
  return 0;}
