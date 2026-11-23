/* Generic difference-family annealer for base weeks under a cyclic group, with optional tie
   (week k = phi^k(week 0)) and oil-block clash penalty.
   tie = L: weeks come in runs of L, week f*L+j = phi^j(week f*L) (L=1: all weeks free; L=nb: one free week).
   Input (file): n nb tie nt / phi[n] / type[n][n] / target[nt] / weight[nt] / forb[nb][nt]
   Usage: sa spec seed iters T0 Tend A [restarts]
   cost = sum_t w_t (tot_t - target_t)^2 + A * sum_{k,t} max(0, cnt[k][t]+forb[k][t]-1)
   Prints "SOL cost=0 seed=.. | week0 | week1 ..." (points, groups of 4) when cost 0. */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>
#define MAXN 64
#define MAXT 400
#define MAXB 6
static int n,nb,tie,nt,phik[MAXB][MAXN],type[MAXN][MAXN],target[MAXT],wt[MAXT],forb[MAXB][MAXT];
static int cnt[MAXB][MAXT],tot[MAXT],mem[MAXB][MAXN/4][4],blk[MAXB][MAXN],pos[MAXB][MAXN];
static long cost; static int A;
static unsigned long long s[2];
static inline unsigned long long rnd(void){unsigned long long s1=s[0],s0=s[1];s[0]=s0;s1^=s1<<23;s[1]=s1^s0^(s1>>17)^(s0>>26);return s[1]+s0;}
static inline double urnd(void){return (rnd()>>11)*(1.0/9007199254740992.0);}
static inline void add(int k,int t,int d){
  int o=tot[t]-target[t]; cost-= (long)wt[t]*o*o; tot[t]+=d; o+=d; cost+=(long)wt[t]*o*o;
  int c=cnt[k][t]+forb[k][t]; if(c>1) cost-=(long)A*(c-1); cnt[k][t]+=d; c+=d; if(c>1) cost+=(long)A*(c-1);
}
static void swapk(int k,int p,int q){
  int bp=blk[k][p],bq=blk[k][q],ip=pos[k][p],iq=pos[k][q];
  for(int j=0;j<4;j++){ if(j!=ip) add(k,type[p][mem[k][bp][j]],-1); if(j!=iq) add(k,type[q][mem[k][bq][j]],-1);}
  mem[k][bp][ip]=q; mem[k][bq][iq]=p; blk[k][p]=bq; blk[k][q]=bp; pos[k][p]=iq; pos[k][q]=ip;
  for(int j=0;j<4;j++){ if(j!=ip) add(k,type[q][mem[k][bp][j]],1); if(j!=iq) add(k,type[p][mem[k][bq][j]],1);}
}
int main(int argc,char**argv){
  FILE*f=fopen(argv[1],"r"); int seed=atoi(argv[2]); long iters=atol(argv[3]); double T0=atof(argv[4]),T1=atof(argv[5]); A=atoi(argv[6]);
  int restarts=argc>7?atoi(argv[7]):1; int phi[MAXN];
  if(fscanf(f,"%d %d %d %d",&n,&nb,&tie,&nt)!=4) return 1;
  for(int i=0;i<n;i++) fscanf(f,"%d",&phi[i]);
  for(int i=0;i<n;i++) for(int j=0;j<n;j++) fscanf(f,"%d",&type[i][j]);
  for(int t=0;t<nt;t++) fscanf(f,"%d",&target[t]);
  for(int t=0;t<nt;t++) fscanf(f,"%d",&wt[t]);
  for(int k=0;k<nb;k++) for(int t=0;t<nt;t++) fscanf(f,"%d",&forb[k][t]);
  for(int i=0;i<n;i++) phik[0][i]=i;
  if(tie<1)tie=1; for(int k=0;k<nb;k++) for(int i=0;i<n;i++) phik[k][i]= (k%tie==0)? i : phi[phik[k-1][i]];
  long gbest=1L<<60;
  for(int r=0;r<restarts;r++){
    s[0]=0x9E3779B97F4A7C15ULL*(seed*1000+r+1); s[1]=0xD1B54A32D192ED03ULL^(seed*7919+r); for(int i=0;i<20;i++) rnd();
    int perm[MAXN];
    memset(cnt,0,sizeof cnt); memset(tot,0,sizeof tot); cost=0;
    for(int t=0;t<nt;t++) cost+=(long)wt[t]*target[t]*target[t];
    for(int k=0;k<nb;k++){
      if(k%tie==0){ for(int i=0;i<n;i++) perm[i]=i; for(int i=n-1;i>0;i--){int j=rnd()%(i+1);int x=perm[i];perm[i]=perm[j];perm[j]=x;} }
      for(int i=0;i<n;i++){ int p= phik[k][perm[i]]; mem[k][i/4][i%4]=p; blk[k][p]=i/4; pos[k][p]=i%4; }
      for(int b=0;b<n/4;b++) for(int i=0;i<4;i++) for(int j=i+1;j<4;j++) add(k,type[mem[k][b][i]][mem[k][b][j]],1);
    }
    long best=cost; double T=T0, al=pow(T1/T0,1.0/iters);
    for(long it=0;it<iters&&cost>0;it++,T*=al){
      int p=rnd()%n,q=rnd()%n; int f=(rnd()%(nb/tie))*tie; if(blk[f][p]==blk[f][q]) continue;
      long old=cost;
      for(int j=0;j<tie;j++) swapk(f+j,phik[f+j][p],phik[f+j][q]);
      if(cost>old && urnd()>=exp((old-cost)/T)){ for(int j=0;j<tie;j++) swapk(f+j,phik[f+j][p],phik[f+j][q]); }
      if(cost<best) best=cost;
    }
    if(best<gbest) gbest=best;
    if(cost==0){ printf("SOL seed=%d r=%d",seed,r); for(int k=0;k<nb;k++){ printf(" |"); for(int b=0;b<n/4;b++) for(int j=0;j<4;j++) printf(" %d",mem[k][b][j]); } printf("\n"); fflush(stdout); if(getenv("ONE")) return 0; }
    else if(getenv("VERB")) { printf("best=%ld end=%ld\n",best,cost); fflush(stdout);} 
  }
  printf("DONE best=%ld\n",gbest); return 0;
}
