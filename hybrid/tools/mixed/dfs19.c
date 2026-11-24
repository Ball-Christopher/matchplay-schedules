/* Exhaustive search for v=19, mix 0/3/4 in 7 weeks, after the reduction in sat19.py:
   U = 3x4 grid (bowlers 0..11, row r = p/4, col c = p%4), Z = 12..18.
   A-week i (i=0..2): fixed quad = row i, plus 5 triples on the other 15 bowlers.
   B-week j (j=0..3): fixed triple = column j, plus 4 quads on the other 16 bowlers.
   Every couple meets exactly once. Z symmetry: a Z bowler not yet placed anywhere is interchangeable
   with any other such, so only the smallest one is tried. Prints a solution or "none" with node count.
   usage: dfs19 [maxsec] */
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#define V 19
typedef unsigned int u32;
u32 met[V]; int wk_order[7]; int gsz[7]; u32 fixedg[7];
int sol[7][V]; long long nodes=0; int placed[V]; /* placed[z] = number of groups containing z so far */
u32 avail; int W; double maxsec; clock_t t0;
int grp[7][6][4], ng[7];
static int lowbit(u32 x){ return __builtin_ctz(x); }
int week(int w);
int fill(int w, u32 left){
  if(!left) return week(w+1);
  nodes++;
  if((nodes&0xfffff)==0 && (double)(clock()-t0)/CLOCKS_PER_SEC>maxsec){ printf("timeout nodes=%lld\n",nodes); exit(2); }
  int p=lowbit(left); u32 rest=left&~(1u<<p)&~met[p];
  int s=gsz[w];
  /* choose s-1 partners from rest, increasing, mutually unmet */
  int cand[V], nc=0; for(u32 x=rest;x;x&=x-1) cand[nc++]=lowbit(x);
  int fresh_used=0; (void)fresh_used;
  for(int a=0;a<nc;a++){ int q=cand[a];
    if(q>=12 && placed[q]==0){ int skip=0; for(int z=12;z<q;z++) if(placed[z]==0 && ((left>>z)&1) && !((met[p]>>z)&1) && z!=p) { skip=1; break; } if(skip) continue; }
    u32 r2=rest&~met[q];
    for(int b=a+1;b<nc;b++){ int t=cand[b]; if(!((r2>>t)&1)) continue;
      if(t>=12 && placed[t]==0){ int skip=0; for(int z=12;z<t;z++) if(z!=q && placed[z]==0 && ((left>>z)&1) && !((met[p]>>z)&1) && !((met[q]>>z)&1)) { skip=1; break; } if(skip) continue; }
      if(s==3){
        int g[3]={p,q,t};
        for(int i=0;i<3;i++){ placed[g[i]]++; for(int j=0;j<3;j++) if(i!=j) met[g[i]]|=1u<<g[j]; }
        int k=ng[w]++; grp[w][k][0]=p; grp[w][k][1]=q; grp[w][k][2]=t;
        if(fill(w, left&~(1u<<p|1u<<q|1u<<t))) return 1;
        ng[w]--;
        for(int i=0;i<3;i++){ placed[g[i]]--; for(int j=0;j<3;j++) if(i!=j) met[g[i]]&=~(1u<<g[j]); }
      } else {
        u32 r3=r2&~met[t];
        for(int c=b+1;c<nc;c++){ int u=cand[c]; if(!((r3>>u)&1)) continue;
          if(u>=12 && placed[u]==0){ int skip=0; for(int z=12;z<u;z++) if(z!=q && z!=t && placed[z]==0 && ((left>>z)&1) && !((met[p]>>z)&1) && !((met[q]>>z)&1) && !((met[t]>>z)&1)) { skip=1; break; } if(skip) continue; }
          int g[4]={p,q,t,u};
          for(int i=0;i<4;i++){ placed[g[i]]++; for(int j=0;j<4;j++) if(i!=j) met[g[i]]|=1u<<g[j]; }
          int k=ng[w]++; grp[w][k][0]=p; grp[w][k][1]=q; grp[w][k][2]=t; grp[w][k][3]=u;
          if(fill(w, left&~(1u<<p|1u<<q|1u<<t|1u<<u))) return 1;
          ng[w]--;
          for(int i=0;i<4;i++){ placed[g[i]]--; for(int j=0;j<4;j++) if(i!=j) met[g[i]]&=~(1u<<g[j]); }
        }
      }
    }
  }
  return 0;
}
int week(int w){
  if(w==7) return 1;
  ng[w]=0; return fill(w, ((1u<<V)-1)&~fixedg[w]);
}
int main(int argc,char**argv){
  maxsec = argc>1? atof(argv[1]) : 1e9; t0=clock();
  for(int i=0;i<3;i++){ gsz[i]=3; fixedg[i]=0; for(int c=0;c<4;c++) fixedg[i]|=1u<<(4*i+c); }
  for(int j=0;j<4;j++){ gsz[3+j]=4; fixedg[3+j]=0; for(int r=0;r<3;r++) fixedg[3+j]|=1u<<(4*r+j); }
  for(int w=0;w<7;w++) for(int p=0;p<V;p++) if((fixedg[w]>>p)&1) met[p]|=fixedg[w]&~(1u<<p);
  int ok=week(0);
  if(ok){ printf("FOUND nodes=%lld\n",nodes); for(int w=0;w<7;w++){ for(int k=0;k<ng[w];k++){ printf("["); for(int i=0;i<gsz[w];i++) printf("%d%s",grp[w][k][i]+1,i<gsz[w]-1?",":""); printf("] "); } printf("\n"); } return 0; }
  printf("none nodes=%lld sec=%.1f\n",nodes,(double)(clock()-t0)/CLOCKS_PER_SEC); return 1;
}
