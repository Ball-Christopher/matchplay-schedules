/* Conflict-directed tabu search (social-golfer style) for format-fair mixed single rounds.
   usage: tabu v a2 a3 a4 seed maxsec type...  (type = g2,g3,g4xk). Cost = sum max(0,meet-1) + WF*format deviation.
   Prints JSON weeks on success. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#define MV 64
#define MR 40
int v,R,A[5],WF=1;
int ng[MR],gstart[MR][MV],gsize[MR][MV],slotg[MR][MV],sl[MR][MV],pos[MR][MV];
int meet[MV][MV],fmt[MV][5]; long tabu[MR][MV][MV];
static unsigned long long rs;
static inline unsigned rnd(void){ rs^=rs<<13; rs^=rs>>7; rs^=rs<<17; return (unsigned)(rs>>11); }
static inline int fp(int m){ return m>1? m-1:0; }
static inline int dinc(int m){ return m>=1?1:0; }   /* fp(m+1)-fp(m) */
static inline int ddec(int m){ return m>=2?-1:0; }  /* fp(m-1)-fp(m) */
static inline int fdev(int d){ return d<0?-d:d; }
int delta(int w,int a,int b){
  int ga=slotg[w][a],gb=slotg[w][b],p=sl[w][a],q=sl[w][b],sa=gsize[w][ga],sb=gsize[w][gb],d=0;
  for(int i=0;i<sa;i++){int x=sl[w][gstart[w][ga]+i]; if(x==p)continue; d+=ddec(meet[p][x])+dinc(meet[q][x]);}
  for(int i=0;i<sb;i++){int y=sl[w][gstart[w][gb]+i]; if(y==q)continue; d+=dinc(meet[p][y])+ddec(meet[q][y]);}
  if(sa!=sb){ int f=0;
    f+=fdev(fmt[p][sa]-1-A[sa])-fdev(fmt[p][sa]-A[sa]); f+=fdev(fmt[p][sb]+1-A[sb])-fdev(fmt[p][sb]-A[sb]);
    f+=fdev(fmt[q][sb]-1-A[sb])-fdev(fmt[q][sb]-A[sb]); f+=fdev(fmt[q][sa]+1-A[sa])-fdev(fmt[q][sa]-A[sa]); d+=WF*f; }
  return d;
}
void doswap(int w,int a,int b){
  int ga=slotg[w][a],gb=slotg[w][b],p=sl[w][a],q=sl[w][b],sa=gsize[w][ga],sb=gsize[w][gb];
  for(int i=0;i<sa;i++){int x=sl[w][gstart[w][ga]+i]; if(x==p)continue; meet[p][x]--;meet[x][p]--;meet[q][x]++;meet[x][q]++;}
  for(int i=0;i<sb;i++){int y=sl[w][gstart[w][gb]+i]; if(y==q)continue; meet[p][y]++;meet[y][p]++;meet[q][y]--;meet[y][q]--;}
  if(sa!=sb){fmt[p][sa]--;fmt[p][sb]++;fmt[q][sb]--;fmt[q][sa]++;}
  sl[w][a]=q;sl[w][b]=p;pos[w][q]=a;pos[w][p]=b;
}
int total(void){ int c=0; for(int p=0;p<v;p++)for(int q=p+1;q<v;q++)c+=fp(meet[p][q]); for(int p=0;p<v;p++)for(int s=2;s<=4;s++)c+=WF*fdev(fmt[p][s]-A[s]); return c;}
void build(void){ memset(meet,0,sizeof meet); memset(fmt,0,sizeof fmt);
  for(int w=0;w<R;w++)for(int g=0;g<ng[w];g++){int st=gstart[w][g],s=gsize[w][g]; for(int i=0;i<s;i++){int p=sl[w][st+i]; fmt[p][s]++; for(int j=i+1;j<s;j++){int q=sl[w][st+j];meet[p][q]++;meet[q][p]++;}}}}
int conflicted(int w,int a){ int g=slotg[w][a],p=sl[w][a]; for(int i=0;i<gsize[w][g];i++){int x=sl[w][gstart[w][g]+i]; if(x!=p&&meet[p][x]>1) return 1;}
  int s=gsize[w][g]; return fmt[p][s]>A[s]; }
int main(int argc,char**argv){
  v=atoi(argv[1]);A[2]=atoi(argv[2]);A[3]=atoi(argv[3]);A[4]=atoi(argv[4]);
  unsigned long long seed=atoll(argv[5]); double maxsec=atof(argv[6]); if(getenv("WF"))WF=atoi(getenv("WF"));
  long maxstall=getenv("STALL")?atol(getenv("STALL")):20000;
  R=0; for(int i=7;i<argc;i++){int g2,g3,g4,k; sscanf(argv[i],"%d,%d,%dx%d",&g2,&g3,&g4,&k);
    for(int t=0;t<k;t++){int w=R++,st=0,g=0,sz[3]={4,3,2},cnt[3]={g4,g3,g2};
      for(int z=0;z<3;z++)for(int cc=0;cc<cnt[z];cc++){gstart[w][g]=st;gsize[w][g]=sz[z];for(int u=0;u<sz[z];u++)slotg[w][st+u]=g;st+=sz[z];g++;} ng[w]=g;}}
  rs=seed*2654435761ULL+99; for(int i=0;i<10;i++)rnd();
  clock_t t0=clock();
  for(int restart=0;;restart++){
    for(int w=0;w<R;w++){for(int i=0;i<v;i++)sl[w][i]=i; for(int i=v-1;i>0;i--){int j=rnd()%(i+1);int t=sl[w][i];sl[w][i]=sl[w][j];sl[w][j]=t;} for(int i=0;i<v;i++)pos[w][sl[w][i]]=i;}
    build(); memset(tabu,0,sizeof tabu);
    int E=total(),best=E; long it=0,last=0;
    while(E>0){ it++;
      if((it&1023)==0 && (double)(clock()-t0)/CLOCKS_PER_SEC>maxsec){fprintf(stderr,"fail best=%d restarts=%d\n",best,restart);return 1;}
      int bd=1<<30,bw=-1,ba=0,bb=0,nb=0;
      for(int w=0;w<R;w++) for(int a=0;a<v;a++){ if(!conflicted(w,a)) continue;
        for(int b=0;b<v;b++){ if(slotg[w][a]==slotg[w][b]) continue;
          int p=sl[w][a],q=sl[w][b]; int d=delta(w,a,b);
          int ok = tabu[w][p][q]<it || E+d<best;
          if(!ok) continue;
          if(d<bd){bd=d;bw=w;ba=a;bb=b;nb=1;} else if(d==bd && rnd()%(++nb)==0){bw=w;ba=a;bb=b;} } }
      if(bw<0) continue;
      int p=sl[bw][ba],q=sl[bw][bb]; doswap(bw,ba,bb); E+=bd;
      int ten=4+rnd()%10; tabu[bw][p][q]=tabu[bw][q][p]=it+ten;
      if(E<best){best=E;last=it;}
      if(it-last>maxstall){ /* perturb */ for(int k=0;k<3;k++){int w=rnd()%R,a=rnd()%v,b=rnd()%v; if(slotg[w][a]!=slotg[w][b]){E+=delta(w,a,b);doswap(w,a,b);}} last=it; best=E; if(rnd()%20==0) break; }
    }
    if(E==0){ printf("[");
      for(int w=0;w<R;w++){printf("%s[",w?",\n":"");for(int g=0;g<ng[w];g++){printf("%s[",g?",":"");for(int i=0;i<gsize[w][g];i++)printf("%s%d",i?",":"",sl[w][gstart[w][g]+i]+1);printf("]");}printf("]");}
      printf("]\n"); fprintf(stderr,"ok restarts=%d it=%ld sec=%.1f\n",restart,it,(double)(clock()-t0)/CLOCKS_PER_SEC); return 0;}
  }
}
