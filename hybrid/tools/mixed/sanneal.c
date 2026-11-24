/* Orbit annealer for Z_m acting on point orbits of any size dividing m, with weeks of any stabiliser.
   Each entry is a base week W invariant under H = <g^(m/d)> (order d), developed into m/d copies g^i W.
   Moves on W commute with H: aligned swap of two H-orbits of equal length, rotation of one H-orbit.
   usage: sanneal seed maxsec < config
   config: m / norb size... / a2 a3 a4 / K / K lines "d ng  s p.. s p.. ..." (0-based points, orbits consecutive)
   prints JSON weeks (1-based) on success. Env: T0 TMIN COOL WF STALL */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>
#define MV 64
#define MR 48
#define MM 64
int v,R,m,A[5],norb,osz[MV],ostart[MV],orbof[MV],G[MM][MV];
int ng[MR], gstart[MR][MV], gsize[MR][MV], slotg[MR][MV], sl[MR][MV], pos[MR][MV];
int meet[MV][MV], fmt[MV][5];
int nent, ed[MR], ew0[MR], ecop[MR], eng[MR], egs[MR][MV], egp[MR][MV][5];
int hn[MR], hlen[MR][MV], horb[MR][MV][MM], hof[MR][MV]; /* H-orbits per entry */
double T0=1.0,TMIN=0.3,COOL=0.9995,WF=2.0;
static unsigned long long rs;
static inline unsigned rnd(void){ rs ^= rs<<13; rs ^= rs>>7; rs ^= rs<<17; return (unsigned)(rs>>11); }
static inline double urand(void){ return (rnd() & 0xffffff) / 16777216.0; }
int logw[1<<16],logp[1<<16],logq[1<<16],nlog;
static inline int fd(int p,int s,int dd){ int d=fmt[p][s]-A[s]; return (d+dd)*(d+dd)-d*d; }
double tr(int w,int p,int q){
  int a=pos[w][p], b=pos[w][q]; int ga=slotg[w][a], gb=slotg[w][b];
  logw[nlog]=w; logp[nlog]=p; logq[nlog]=q; nlog++;
  sl[w][a]=q; sl[w][b]=p; pos[w][q]=a; pos[w][p]=b;
  if(ga==gb) return 0;
  int sa=gsize[w][ga], sb=gsize[w][gb]; double d=0;
  for(int i=0;i<sa;i++){ int x=sl[w][gstart[w][ga]+i]; if(x==q) continue; d += (-2*meet[p][x]+3) + (2*meet[q][x]-1); meet[p][x]--;meet[x][p]--; meet[q][x]++;meet[x][q]++; }
  for(int i=0;i<sb;i++){ int y=sl[w][gstart[w][gb]+i]; if(y==p) continue; d += (2*meet[p][y]-1) + (-2*meet[q][y]+3); meet[p][y]++;meet[y][p]++; meet[q][y]--;meet[y][q]--; }
  if(sa!=sb){ double ff=fd(p,sa,-1); fmt[p][sa]--; ff+=fd(p,sb,1); fmt[p][sb]++; ff+=fd(q,sb,-1); fmt[q][sb]--; ff+=fd(q,sa,1); fmt[q][sa]++; d+=WF*ff; }
  return d;
}
void undo(void){ while(nlog>0){ nlog--; int w=logw[nlog],p=logp[nlog],q=logq[nlog]; tr(w,p,q); nlog--; } }
void build(void){ memset(meet,0,sizeof meet); memset(fmt,0,sizeof fmt);
  for(int w=0;w<R;w++) for(int g=0;g<ng[w];g++){ int st=gstart[w][g], s=gsize[w][g];
    for(int i=0;i<s;i++){ int p=sl[w][st+i]; fmt[p][s]++; for(int j=i+1;j<s;j++){int q=sl[w][st+j]; meet[p][q]++; meet[q][p]++;}}}}
double cost(void){ double C=0; for(int p=0;p<v;p++)for(int q=p+1;q<v;q++){int d=meet[p][q]-1;C+=d*d;}
  for(int p=0;p<v;p++)for(int s=2;s<=4;s++){int d=fmt[p][s]-A[s];C+=WF*d*d;} return C;}
/* apply point transposition (x,y) of the base week of entry e to all its copies */
double etr(int e,int x,int y){ double d=0; for(int i=0;i<ecop[e];i++) d+=tr(ew0[e]+i,G[i][x],G[i][y]); return d; }
double move(int e){ /* random H-commuting move on entry e */
  double d=0; int p=rnd()%v;
  int o=hof[e][p], L=hlen[e][o];
  if(L>1 && rnd()%4==0){
    /* rotate orbit o by one step: product of transpositions (p0 pj) j=1..L-1 */
    int *P=horb[e][o]; int r=1+rnd()%(L-1); for(int t=0;t<r;t++) for(int j=1;j<L;j++) d+=etr(e,P[0],P[j]); return d; }
  int q=rnd()%v, o2=hof[e][q]; if(o2==o || hlen[e][o2]!=L) return 1e9;
  int *P=horb[e][o], *Q=horb[e][o2]; int sh=rnd()%L;
  for(int j=0;j<L;j++) d+=etr(e,P[j],Q[(j+sh)%L]);
  return d;
}
void setgroups(int w,int n,int*sizes){ int st=0; ng[w]=n; for(int g=0;g<n;g++){gstart[w][g]=st;gsize[w][g]=sizes[g];for(int u=0;u<sizes[g];u++)slotg[w][st+u]=g;st+=sizes[g];} }
int main(int argc,char**argv){
  unsigned long long seed=atoll(argv[1]); double maxsec=atof(argv[2]);
  if(getenv("T0"))T0=atof(getenv("T0")); if(getenv("TMIN"))TMIN=atof(getenv("TMIN")); if(getenv("COOL"))COOL=atof(getenv("COOL")); if(getenv("WF"))WF=atof(getenv("WF"));
  long stall = getenv("STALL")? atol(getenv("STALL")) : 30000000L;
  if(scanf("%d %d",&m,&norb)!=2) return 2; v=0;
  for(int o=0;o<norb;o++){ scanf("%d",&osz[o]); ostart[o]=v; for(int k=0;k<osz[o];k++) orbof[v+k]=o; v+=osz[o]; }
  for(int i=0;i<m;i++) for(int p=0;p<v;p++){ int o=orbof[p]; G[i][p]=ostart[o]+(p-ostart[o]+i)%osz[o]; }
  scanf("%d %d %d %d",&A[2],&A[3],&A[4],&nent); R=0;
  for(int e=0;e<nent;e++){ scanf("%d %d",&ed[e],&eng[e]); ecop[e]=m/ed[e]; ew0[e]=R; R+=ecop[e];
    for(int g=0;g<eng[e];g++){ scanf("%d",&egs[e][g]); for(int u=0;u<egs[e][g];u++) scanf("%d",&egp[e][g][u]); }
    int h=m/ed[e]; int seen[MV]={0}; hn[e]=0;
    for(int p=0;p<v;p++) if(!seen[p]){ int o=hn[e]++, x=p, L=0; while(!seen[x]){ seen[x]=1; horb[e][o][L++]=x; hof[e][x]=o; x=G[h%m][x]; } hlen[e][o]=L; }
    /* check invariance of the base partition under h */
    int grp[MV]; for(int g=0;g<eng[e];g++) for(int u=0;u<egs[e][g];u++) grp[egp[e][g][u]]=g;
    for(int g=0;g<eng[e];g++){ int g2=grp[G[h%m][egp[e][g][0]]]; for(int u=0;u<egs[e][g];u++) if(grp[G[h%m][egp[e][g][u]]]!=g2){ fprintf(stderr,"entry %d not invariant\n",e); return 3; } }
  }
  if(R>MR||v>MV){ fprintf(stderr,"too big\n"); return 3; }
  rs=seed*2654435761ULL+12345; for(int i=0;i<10;i++) rnd();
  clock_t t0=clock(); double gbest=1e18;
  for(int restart=0;;restart++){
    for(int e=0;e<nent;e++) for(int i=0;i<ecop[e];i++){ int w=ew0[e]+i, st=0; setgroups(w,eng[e],egs[e]);
      for(int g=0;g<eng[e];g++) for(int u=0;u<egs[e][g];u++){ int p=G[i][egp[e][g][u]]; sl[w][st]=p; pos[w][p]=st; st++; } }
    build();
    for(int e=0;e<nent;e++) for(int k=0;k<200;k++){ nlog=0; move(e); } /* randomise within shape */
    build(); double E=cost(), best=E; double T=T0; long it=0,lastimp=0;
    while(1){ it++;
      if((it&0xfffff)==0 && (double)(clock()-t0)/CLOCKS_PER_SEC>maxsec){ fprintf(stderr,"fail best=%g restarts=%d\n",gbest<best?gbest:best,restart); return 1; }
      int e=rnd()%nent; nlog=0; double d=move(e);
      if(d>1e8){ undo(); continue; }
      if(d<=0 || urand()<exp(-d/T)){ E+=d; if(E<best-1e-9){best=E;lastimp=it;} if(E<0.5) break; }
      else undo();
      if(it%1000==0){ T*=COOL; if(T<TMIN)T=TMIN; }
      if(it-lastimp>stall) break;
    }
    if(best<gbest) gbest=best;
    if(E<0.5){ printf("[");
      for(int w=0;w<R;w++){ printf("%s[",w?",\n":""); for(int g=0;g<ng[w];g++){ printf("%s[",g?",":""); for(int i=0;i<gsize[w][g];i++) printf("%s%d",i?",":"",sl[w][gstart[w][g]+i]+1); printf("]"); } printf("]"); }
      printf("]\n"); fprintf(stderr,"ok restarts=%d sec=%.1f\n",restart,(double)(clock()-t0)/CLOCKS_PER_SEC); return 0; }
  }
}
