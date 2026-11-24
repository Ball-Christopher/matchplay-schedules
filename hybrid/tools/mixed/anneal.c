/* Simulated annealing for format-fair mixed-week single rounds.
   usage: anneal v a2 a3 a4 seed maxsec  type1 type2 ...   where type = g2,g3,g4xk (k weeks of that type)
   Prints weeks (groups) as JSON on success, exit 0; exit 1 on failure. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>
#define MV 64
#define MR 32
int v, R, A[5]; double T0=2.0, COOL=0.9995, TMIN=0.05;
int ng[MR], gstart[MR][MV], gsize[MR][MV], slotg[MR][MV];
int sl[MR][MV], pos[MR][MV];
int meet[MV][MV], fmt[MV][5];
static unsigned long long rs;
static inline unsigned rnd(void){ rs ^= rs<<13; rs ^= rs>>7; rs ^= rs<<17; return (unsigned)(rs>>11); }
static inline double urand(void){ return (rnd() & 0xffffff) / 16777216.0; }
long cost_pairs(void){ long c=0; for(int p=0;p<v;p++)for(int q=p+1;q<v;q++){int m=meet[p][q]-1;c+=m*m;} return c;}
long cost_fmt(void){ long c=0; for(int p=0;p<v;p++)for(int s=2;s<=4;s++){int d=fmt[p][s]-A[s];c+=d*d;} return c;}
void build(void){
  memset(meet,0,sizeof meet); memset(fmt,0,sizeof fmt);
  for(int w=0;w<R;w++) for(int g=0;g<ng[w];g++){ int st=gstart[w][g], s=gsize[w][g];
    for(int i=0;i<s;i++){ int p=sl[w][st+i]; fmt[p][s]++; for(int j=i+1;j<s;j++){int q=sl[w][st+j]; meet[p][q]++; meet[q][p]++;}}}
}
int main(int argc,char**argv){
  v=atoi(argv[1]); A[2]=atoi(argv[2]);A[3]=atoi(argv[3]);A[4]=atoi(argv[4]);
  unsigned long long seed=atoll(argv[5]); double maxsec=atof(argv[6]);
  R=0; if(getenv("T0"))T0=atof(getenv("T0")); if(getenv("COOL"))COOL=atof(getenv("COOL")); if(getenv("TMIN"))TMIN=atof(getenv("TMIN"));
  for(int i=7;i<argc;i++){ int g2,g3,g4,k; sscanf(argv[i],"%d,%d,%dx%d",&g2,&g3,&g4,&k);
    for(int t=0;t<k;t++){ int w=R++, st=0, g=0;
      int sz[3]={4,3,2}, cnt[3]={g4,g3,g2};
      for(int z=0;z<3;z++) for(int c=0;c<cnt[z];c++){ gstart[w][g]=st; gsize[w][g]=sz[z]; for(int u=0;u<sz[z];u++) slotg[w][st+u]=g; st+=sz[z]; g++; }
      ng[w]=g; if(st!=v){fprintf(stderr,"bad type\n");return 2;} } }
  rs = seed*2654435761ULL + 12345; for(int i=0;i<10;i++) rnd();
  clock_t t0=clock(); double WF=2.0;
  for(int restart=0;;restart++){
    for(int w=0;w<R;w++){ for(int i=0;i<v;i++) sl[w][i]=i; for(int i=v-1;i>0;i--){int j=rnd()%(i+1);int t=sl[w][i];sl[w][i]=sl[w][j];sl[w][j]=t;} for(int i=0;i<v;i++) pos[w][sl[w][i]]=i; }
    build(); double E = cost_pairs() + WF*cost_fmt(); double best=E;
    double T=T0; long it=0, lastimp=0;
    while(1){
      it++;
      if((it & 0xfffff)==0){ if((double)(clock()-t0)/CLOCKS_PER_SEC > maxsec){ fprintf(stderr,"fail best=%g restarts=%d\n",best,restart); return 1;} }
      int w=rnd()%R; int a=rnd()%v, b=rnd()%v; int ga=slotg[w][a], gb=slotg[w][b]; if(ga==gb) continue;
      int p=sl[w][a], q=sl[w][b]; int sa=gsize[w][ga], sb=gsize[w][gb];
      double d=0;
      for(int i=0;i<sa;i++){ int x=sl[w][gstart[w][ga]+i]; if(x==p) continue; d += (-2*meet[p][x]+3) + (2*meet[q][x]-1); }
      for(int i=0;i<sb;i++){ int y=sl[w][gstart[w][gb]+i]; if(y==q) continue; d += (2*meet[p][y]-1) + (-2*meet[q][y]+3); }
      if(sa!=sb){ // p: sa->sb, q: sb->sa
        double f=0; int da;
        da=fmt[p][sa]-A[sa]; f += (da-1)*(da-1)-da*da; da=fmt[p][sb]-A[sb]; f += (da+1)*(da+1)-da*da;
        da=fmt[q][sb]-A[sb]; f += (da-1)*(da-1)-da*da; da=fmt[q][sa]-A[sa]; f += (da+1)*(da+1)-da*da;
        d += WF*f; }
      if(d<=0 || urand() < exp(-d/T)){
        for(int i=0;i<sa;i++){ int x=sl[w][gstart[w][ga]+i]; if(x==p) continue; meet[p][x]--;meet[x][p]--; meet[q][x]++;meet[x][q]++; }
        for(int i=0;i<sb;i++){ int y=sl[w][gstart[w][gb]+i]; if(y==q) continue; meet[p][y]++;meet[y][p]++; meet[q][y]--;meet[y][q]--; }
        if(sa!=sb){ fmt[p][sa]--; fmt[p][sb]++; fmt[q][sb]--; fmt[q][sa]++; }
        sl[w][a]=q; sl[w][b]=p; pos[w][q]=a; pos[w][p]=b; E+=d;
        if(E<best-1e-9){best=E; lastimp=it;}
        if(E<0.5) break;
      }
      if(it%2000==0){ T*=COOL; if(T<TMIN) T=TMIN; }
      if(it-lastimp > 40000000L) break;
    }
    if(E<0.5){
      printf("[");
      for(int w=0;w<R;w++){ printf("%s[",w?",\n":""); for(int g=0;g<ng[w];g++){ printf("%s[",g?",":""); for(int i=0;i<gsize[w][g];i++) printf("%s%d",i?",":"",sl[w][gstart[w][g]+i]+1); printf("]"); } printf("]"); }
      printf("]\n"); fprintf(stderr,"ok restarts=%d it=%ld sec=%.1f\n",restart,it,(double)(clock()-t0)/CLOCKS_PER_SEC); return 0; }
  }
}
