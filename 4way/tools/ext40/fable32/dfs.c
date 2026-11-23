/* Exact DFS for one tied base week: partition n points into blocks of 4 such that every pair's type is allowed
   (cap 1, used at most once) and every type-orbit gets exactly need[orbit] pairs (sum need = 6n/4).
   Input: n nt norb / order[n] / type[n][n] / cap[nt] / orb[nt] / need[norb].  Usage: dfs spec nodelimit [maxsol] [seed] */
#include <stdio.h>
#include <stdlib.h>
#define MAXN 64
#define MAXT 400
static int n,nt,norb,ord[MAXN],type[MAXN][MAXN],cap[MAXT],orb[MAXT],need[MAXT],used[MAXN],blocks[MAXN/4][4];
static long nodes,limit; static int nsol,maxsol;
static int take(int t){ if(!cap[t]||!need[orb[t]]) return 0; cap[t]=0; need[orb[t]]--; return 1; }
static void give(int t){ cap[t]=1; need[orb[t]]++; }
static void rec(int nb){
  if(nsol>=maxsol||nodes>limit) return;
  if(nb==n/4){ nsol++; printf("SOL"); for(int b=0;b<nb;b++) for(int j=0;j<4;j++) printf(" %d",blocks[b][j]); printf("\n"); fflush(stdout); return; }
  nodes++;
  int i0=0; while(used[ord[i0]]) i0++;
  int p=ord[i0]; used[p]=1; blocks[nb][0]=p;
  for(int i1=i0+1;i1<n;i1++){ int a=ord[i1]; if(used[a]) continue; int t1=type[p][a]; if(!take(t1)) continue;
    for(int i2=i1+1;i2<n;i2++){ int b=ord[i2]; if(used[b]) continue; int t2=type[p][b]; if(!take(t2)) continue;
      int t3=type[a][b]; if(!take(t3)){ give(t2); continue; }
      for(int i3=i2+1;i3<n;i3++){ int c=ord[i3]; if(used[c]) continue;
        int u1=type[p][c]; if(!take(u1)) continue;
        int u2=type[a][c]; if(!take(u2)){ give(u1); continue; }
        int u3=type[b][c]; if(!take(u3)){ give(u2); give(u1); continue; }
        used[a]=used[b]=used[c]=1; blocks[nb][1]=a; blocks[nb][2]=b; blocks[nb][3]=c;
        rec(nb+1);
        used[a]=used[b]=used[c]=0; give(u3); give(u2); give(u1);
        if(nsol>=maxsol||nodes>limit) break;
      }
      give(t3); give(t2);
      if(nsol>=maxsol||nodes>limit) break;
    }
    give(t1);
    if(nsol>=maxsol||nodes>limit) break;
  }
  used[p]=0;
}
int main(int argc,char**argv){
  FILE*f=fopen(argv[1],"r"); limit=atol(argv[2]); maxsol=argc>3?atoi(argv[3]):1; int seed=argc>4?atoi(argv[4]):0;
  if(fscanf(f,"%d %d %d",&n,&nt,&norb)!=3) return 1;
  for(int i=0;i<n;i++) fscanf(f,"%d",&ord[i]);
  for(int i=0;i<n;i++) for(int j=0;j<n;j++) fscanf(f,"%d",&type[i][j]);
  for(int t=0;t<nt;t++) fscanf(f,"%d",&cap[t]);
  for(int t=0;t<nt;t++) fscanf(f,"%d",&orb[t]);
  for(int o=0;o<norb;o++) fscanf(f,"%d",&need[o]);
  if(seed){ srand(seed); for(int i=n-1;i>0;i--){ int j=rand()%(i+1); int x=ord[i]; ord[i]=ord[j]; ord[j]=x; } }
  rec(0);
  printf("DONE nodes=%ld sols=%d %s\n",nodes,nsol,nodes>limit?"LIMIT":"EXHAUSTED");
  return 0;
}
