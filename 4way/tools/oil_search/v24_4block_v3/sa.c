// Joint annealing for a resolvable 2-(24,4,3) design in 4 clash-free blocks 6+6+6+5.
// mode 0: unsymmetric, 23 weeks.  mode 1: Z3 (x -> same triple, next) cycles three 6-week
// blocks; store block A (6 weeks) and block D (5 weeks).
// usage: sa mode seed T iters_per_restart(millions) WR outprefix
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <stdint.h>
static uint64_t s[2];
static inline uint64_t rnd(void){uint64_t a=s[0],b=s[1];s[0]=b;a^=a<<23;s[1]=a^b^(a>>17)^(b>>26);return s[1]+b;}
static inline double urnd(void){return (rnd()>>11)*(1.0/9007199254740992.0);}
int mode,NW,NB; int wb[23]; int wk[23][24]; int pos[23][24];
int pid[24][24]; int orb[276]; int orbm[92][3];
int c[4][276]; int tot[276]; int o[92]; int WR; long cost;
static inline int ab(int x){return x<0?-x:x;}
static inline void add(int b,int p,int d){
  int old=c[b][p]; c[b][p]=old+d;
  cost+=WR*((old+d>1?old+d-1:0)-(old>1?old-1:0));
  if(mode==2)return;
  if(mode==0||b==1){cost+=ab(tot[p]+d-3)-ab(tot[p]-3);tot[p]+=d;}
  else{int q=orb[p];for(int i=0;i<3;i++){int r=orbm[q][i];cost+=ab(tot[r]+d-3)-ab(tot[r]-3);tot[r]+=d;}}
}
static void addgroup(int w,int g,int d){int*G=&wk[w][g*4];for(int i=0;i<4;i++)for(int j=i+1;j<4;j++)add(wb[w],pid[G[i]][G[j]],d);}
static void init(void){
  memset(c,0,sizeof c);memset(tot,0,sizeof tot);cost=0;if(mode!=2)for(int p=0;p<276;p++)cost+=3;
  for(int w=0;w<NW;w++){for(int i=0;i<24;i++)wk[w][i]=i;for(int i=23;i>0;i--){int j=rnd()%(i+1);int t=wk[w][i];wk[w][i]=wk[w][j];wk[w][j]=t;}
    for(int i=0;i<24;i++)pos[w][wk[w][i]]=i;for(int g=0;g<6;g++)addgroup(w,g,1);}
}
static void swapm(int w,int i,int j){ // positions i,j in different groups
  int a=wk[w][i],b=wk[w][j],gi=i&~3,gj=j&~3,B=wb[w];
  for(int t=gi;t<gi+4;t++)if(t!=i)add(B,pid[a][wk[w][t]],-1),add(B,pid[b][wk[w][t]],1);
  for(int t=gj;t<gj+4;t++)if(t!=j)add(B,pid[b][wk[w][t]],-1),add(B,pid[a][wk[w][t]],1);
  wk[w][i]=b;wk[w][j]=a;
}
static void dump(const char*fn){FILE*f=fopen(fn,"w");fprintf(f,"mode %d cost %ld\n",mode,cost);
  for(int w=0;w<NW;w++){fprintf(f,"%d:",wb[w]);for(int i=0;i<24;i++)fprintf(f," %d",wk[w][i]);fprintf(f,"\n");}fclose(f);}
int main(int argc,char**argv){
  mode=atoi(argv[1]);long seed=atol(argv[2]);double T=atof(argv[3]);long IT=atol(argv[4])*1000000L;WR=atoi(argv[5]);const char*pre=argv[6];
  s[0]=seed*0x9E3779B97F4A7C15ULL+1;s[1]=seed^0xD1B54A32D192ED03ULL;for(int i=0;i<20;i++)rnd();
  int n=0;for(int a=0;a<24;a++)for(int b=a+1;b<24;b++)pid[a][b]=pid[b][a]=n++;
  #define SG(x) (((x)/3)*3+((x)%3+1)%3)
  for(int p=0;p<276;p++)orb[p]=-1;n=0;
  for(int a=0;a<24;a++)for(int b=a+1;b<24;b++){int p=pid[a][b];if(orb[p]>=0)continue;int x=a,y=b;for(int i=0;i<3;i++){int q=pid[x][y];orb[q]=n;orbm[n][i]=q;x=SG(x);y=SG(y);}n++;}
  if(mode==2){NW=argc>8?atoi(argv[8]):6;for(int w=0;w<NW;w++)wb[w]=0;}
  else if(mode==0){NW=23;for(int w=0;w<23;w++)wb[w]=w/6;}
  else{NW=11;for(int w=0;w<11;w++)wb[w]=w<6?0:1;}
  long best=1<<30;char fn[256];
  for(int rs=0;;rs++){
    init();long rb=cost;
    double expT[64];double T0=argc>7?atof(argv[7]):T;
    for(long it=0;it<IT;it++){
      if((it&0xFFFFF)==0){double Tc=T0*pow(T/T0,(double)it/IT);for(int i=0;i<64;i++)expT[i]=exp(-i/Tc);}
      int w=rnd()%NW;int i=rnd()%24,j=rnd()%24;if((i>>2)==(j>>2))continue;
      long old=cost;swapm(w,i,j);long d=cost-old;
      if(d>0&&(d>=64||urnd()>=expT[d])){swapm(w,i,j);}
      else if(cost<rb){rb=cost;if(cost<best){best=cost;snprintf(fn,256,"%s.best",pre);dump(fn);if(cost==0){printf("FOUND seed %ld rs %d it %ld\n",seed,rs,it);fflush(stdout);snprintf(fn,256,"%s.sol%d",pre,rs);dump(fn);return 0;}}}
    }
    printf("seed %ld T %.3f rs %d runbest %ld cur %ld best %ld\n",seed,T,rs,rb,cost,best);fflush(stdout);
  }
}
