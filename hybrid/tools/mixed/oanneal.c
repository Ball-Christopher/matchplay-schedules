/* Orbit annealer: points Z_m x c classes + f fixed points; group Z_m (x->x+1 on classes, fixes F).
   Weeks are free base weeks (developed into m weeks) or G-invariant weeks (explicit initial partition,
   moved only by G-commuting permutations: shift one class, swap two classes, swap two fixed points).
   usage: oanneal seed maxsec < config
   config: m c f / a2 a3 a4 / K / K lines: "F g2 g3 g4" or "I ng  s p.. s p.. ..." (point ids: class a,x -> a*m+x; fixed j -> c*m+j)
   prints JSON weeks (1-based ids, base copies consecutive) on success. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>
#define MV 64
#define MR 40
int v,R,m,c,f,A[5];
int ng[MR], gstart[MR][MV], gsize[MR][MV], slotg[MR][MV], sl[MR][MV], pos[MR][MV];
int meet[MV][MV], fmt[MV][5];
int nent, entkind[MR], entw0[MR], entT[MR][3]; int invg[MR][MV][5], invn[MR], invs[MR][MV];
double T0=1.0,TMIN=0.3,COOL=0.9995,WF=2.0;
static unsigned long long rs;
static inline unsigned rnd(void){ rs ^= rs<<13; rs ^= rs>>7; rs ^= rs<<17; return (unsigned)(rs>>11); }
static inline double urand(void){ return (rnd() & 0xffffff) / 16777216.0; }
static inline int gact(int p,int i){ if(p>=c*m) return p; int a=p/m,x=p%m; return a*m+(x+i)%m; }
int logw[4096],logp[4096],logq[4096],nlog;
static inline int fd(int p,int s,int dd){ int d=fmt[p][s]-A[s]; return (d+dd)*(d+dd)-d*d; }
double tr(int w,int p,int q){ /* swap p,q in week w; returns delta */
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
void setgroups(int w,int n,int*sizes){ int st=0; ng[w]=n; for(int g=0;g<n;g++){gstart[w][g]=st;gsize[w][g]=sizes[g];for(int u=0;u<sizes[g];u++)slotg[w][st+u]=g;st+=sizes[g];} }
int main(int argc,char**argv){
  unsigned long long seed=atoll(argv[1]); double maxsec=atof(argv[2]);
  if(getenv("T0"))T0=atof(getenv("T0")); if(getenv("TMIN"))TMIN=atof(getenv("TMIN")); if(getenv("COOL"))COOL=atof(getenv("COOL")); if(getenv("WF"))WF=atof(getenv("WF"));
  long stall = getenv("STALL")? atol(getenv("STALL")) : 30000000L;
  if(scanf("%d %d %d %d %d %d %d",&m,&c,&f,&A[2],&A[3],&A[4],&nent)!=7) return 2;
  v=c*m+f; R=0;
  for(int e=0;e<nent;e++){ char k[4]; scanf("%s",k); entkind[e]=k[0]; entw0[e]=R;
    if(k[0]=='F'){ scanf("%d %d %d",&entT[e][0],&entT[e][1],&entT[e][2]); R+=m; }
    else { scanf("%d",&invn[e]); for(int g=0;g<invn[e];g++){ scanf("%d",&invs[e][g]); for(int u=0;u<invs[e][g];u++) scanf("%d",&invg[e][g][u]); } R+=1; } }
  rs=seed*2654435761ULL+12345; for(int i=0;i<10;i++) rnd();
  clock_t t0=clock();
  for(int restart=0;;restart++){
    for(int e=0;e<nent;e++){ int w=entw0[e];
      if(entkind[e]=='F'){ int sizes[MV],n=0; for(int z=0;z<entT[e][2];z++)sizes[n++]=4; for(int z=0;z<entT[e][1];z++)sizes[n++]=3; for(int z=0;z<entT[e][0];z++)sizes[n++]=2;
        int perm[MV]; for(int i=0;i<v;i++)perm[i]=i; for(int i=v-1;i>0;i--){int j=rnd()%(i+1);int t=perm[i];perm[i]=perm[j];perm[j]=t;}
        for(int i=0;i<m;i++){ setgroups(w+i,n,sizes); for(int s=0;s<v;s++){ sl[w+i][s]=gact(perm[s],i); pos[w+i][sl[w+i][s]]=s; } } }
      else { int st=0; setgroups(w,invn[e],invs[e]); for(int g=0;g<invn[e];g++) for(int u=0;u<invs[e][g];u++){ sl[w][st]=invg[e][g][u]; pos[w][sl[w][st]]=st; st++; } }
    }
    build(); double E=cost(), best=E; double T=T0; long it=0,lastimp=0;
    while(1){ it++;
      if((it&0xfffff)==0 && (double)(clock()-t0)/CLOCKS_PER_SEC>maxsec){ fprintf(stderr,"fail best=%g restarts=%d\n",best,restart); return 1; }
      int e=rnd()%nent, w=entw0[e]; nlog=0; double d=0;
      if(entkind[e]=='F'){ int a=rnd()%v,b=rnd()%v; if(slotg[w][a]==slotg[w][b]) continue; int p=sl[w][a],q=sl[w][b];
        for(int i=0;i<m;i++) d+=tr(w+i,gact(p,i),gact(q,i)); }
      else { int r=rnd()%3;
        if(r==0){ int a=rnd()%c; for(int x=1;x<m;x++) d+=tr(w,a*m,a*m+x); }
        else if(r==1){ int a=rnd()%c,b=rnd()%c; if(a==b) continue; for(int x=0;x<m;x++) d+=tr(w,a*m+x,b*m+x); }
        else { if(f<2) continue; int i=rnd()%f,j=rnd()%f; if(i==j) continue; d+=tr(w,c*m+i,c*m+j); } }
      if(d<=0 || urand()<exp(-d/T)){ E+=d; if(E<best-1e-9){best=E;lastimp=it;} if(E<0.5) break; }
      else undo();
      if(it%1000==0){ T*=COOL; if(T<TMIN)T=TMIN; }
      if(it-lastimp>stall) break;
    }
    if(E<0.5){ printf("[");
      for(int w=0;w<R;w++){ printf("%s[",w?",\n":""); for(int g=0;g<ng[w];g++){ printf("%s[",g?",":""); for(int i=0;i<gsize[w][g];i++) printf("%s%d",i?",":"",sl[w][gstart[w][g]+i]+1); printf("]"); } printf("]"); }
      printf("]\n"); fprintf(stderr,"ok restarts=%d sec=%.1f\n",restart,(double)(clock()-t0)/CLOCKS_PER_SEC); return 0; }
  }
}
