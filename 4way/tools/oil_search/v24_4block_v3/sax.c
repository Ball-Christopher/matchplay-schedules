// Z3-invariant design search: sigma (x -> next in its triple) is semiregular and FIXES every oil block.
// A block is made of O-weeks (a free base week, developed x3) and I-weeks (sigma-invariant: two base
// groups of 4 on 8 distinct triples, developed into 6 groups).  Everything is counted per sigma pair-orbit
// (92 orbits: 8 pure, 84 mixed).  cost = WR*sum_blocks,orbits max(0,c-1) + sum_orbits |total-3|.
// usage: sax spec seed Thot Tcold iters(M) WR outprefix     spec e.g. 13131312 = (O,I) per block
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <stdint.h>
static uint64_t s[2];
static inline uint64_t rnd(void){uint64_t a=s[0],b=s[1];s[0]=b;a^=a<<23;s[1]=a^b^(a>>17)^(b>>26);return s[1]+b;}
static inline double urnd(void){return (rnd()>>11)*(1.0/9007199254740992.0);}
#define MW 40
int NW; int wb[MW],wt[MW],wn[MW]; int wk[MW][24];
int pid[24][24],orb[276]; int c[4][92],tot[92]; int WR; long cost;
static inline int ab(int x){return x<0?-x:x;}
static inline void add(int b,int p,int d){int q=orb[p];int old=c[b][q];c[b][q]=old+d;
  cost+=WR*((old+d>1?old+d-1:0)-(old>1?old-1:0));cost+=ab(tot[q]+d-3)-ab(tot[q]-3);tot[q]+=d;}
static void addgroup(int w,int g,int d){int*G=&wk[w][g*4];for(int i=0;i<4;i++)for(int j=i+1;j<4;j++)add(wb[w],pid[G[i]][G[j]],d);}
static void init(void){memset(c,0,sizeof c);memset(tot,0,sizeof tot);cost=92*3;
  for(int w=0;w<NW;w++){
    if(wt[w]==0){for(int i=0;i<24;i++)wk[w][i]=i;for(int i=23;i>0;i--){int j=rnd()%(i+1);int t=wk[w][i];wk[w][i]=wk[w][j];wk[w][j]=t;}}
    else{int p[8];for(int i=0;i<8;i++)p[i]=i;for(int i=7;i>0;i--){int j=rnd()%(i+1);int t=p[i];p[i]=p[j];p[j]=t;}for(int i=0;i<8;i++)wk[w][i]=3*p[i]+rnd()%3;}
    for(int g=0;g<wn[w]/4;g++)addgroup(w,g,1);}}
static void setp(int w,int i,int v){ // replace slot i by point v
  int gi=i&~3,B=wb[w],a=wk[w][i];for(int t=gi;t<gi+4;t++)if(t!=i)add(B,pid[a][wk[w][t]],-1),add(B,pid[v][wk[w][t]],1);wk[w][i]=v;}
static void swapm(int w,int i,int j){int a=wk[w][i],b=wk[w][j],gi=i&~3,gj=j&~3,B=wb[w];
  for(int t=gi;t<gi+4;t++)if(t!=i)add(B,pid[a][wk[w][t]],-1),add(B,pid[b][wk[w][t]],1);
  for(int t=gj;t<gj+4;t++)if(t!=j)add(B,pid[b][wk[w][t]],-1),add(B,pid[a][wk[w][t]],1);
  wk[w][i]=b;wk[w][j]=a;}
static void dump(const char*fn,const char*spec){FILE*f=fopen(fn,"w");fprintf(f,"spec %s cost %ld\n",spec,cost);
  for(int w=0;w<NW;w++){fprintf(f,"%d %c:",wb[w],wt[w]?'I':'O');for(int i=0;i<wn[w];i++)fprintf(f," %d",wk[w][i]);fprintf(f,"\n");}fclose(f);}
int main(int argc,char**argv){
  const char*spec=argv[1];long seed=atol(argv[2]);double T0=atof(argv[3]),T1=atof(argv[4]);long IT=atol(argv[5])*1000000L;WR=atoi(argv[6]);const char*pre=argv[7];
  s[0]=seed*0x9E3779B97F4A7C15ULL+1;s[1]=seed^0xD1B54A32D192ED03ULL;for(int i=0;i<20;i++)rnd();
  int n=0;for(int a=0;a<24;a++)for(int b=a+1;b<24;b++)pid[a][b]=pid[b][a]=n++;
  #define SG(x) (((x)/3)*3+((x)%3+1)%3)
  for(int p=0;p<276;p++)orb[p]=-1;n=0;
  for(int a=0;a<24;a++)for(int b=a+1;b<24;b++){int p=pid[a][b];if(orb[p]>=0)continue;int x=a,y=b;for(int i=0;i<3;i++){orb[pid[x][y]]=n;x=SG(x);y=SG(y);}n++;}
  NW=0;for(int b=0;b<4;b++){for(int i=0;i<spec[2*b]-'0';i++){wb[NW]=b;wt[NW]=0;wn[NW]=24;NW++;}for(int i=0;i<spec[2*b+1]-'0';i++){wb[NW]=b;wt[NW]=1;wn[NW]=8;NW++;}}
  long best=1<<30;char fn[256];double expT[64];
  for(int rs=0;;rs++){
    init();long rb=cost;
    for(long it=0;it<IT;it++){
      if((it&0xFFFF)==0){double Tc=T0*pow(T1/T0,(double)it/IT);for(int i=0;i<64;i++)expT[i]=exp(-i/Tc);}
      int w=rnd()%NW;long old=cost;int i,j,ov=0,kind;
      if(wt[w]==1&&(rnd()&1)){kind=1;i=rnd()%8;ov=wk[w][i];int v=(ov/3)*3+(ov%3+1+rnd()%2)%3;setp(w,i,v);}
      else{kind=0;i=rnd()%wn[w];j=rnd()%wn[w];if((i>>2)==(j>>2))continue;swapm(w,i,j);}
      long d=cost-old;
      if(d>0&&(d>=64||urnd()>=expT[d])){if(kind)setp(w,i,ov);else swapm(w,i,j);}
      else if(cost<rb){rb=cost;if(cost<best){best=cost;snprintf(fn,256,"%s.best",pre);dump(fn,spec);if(cost==0){printf("FOUND seed %ld rs %d it %ld\n",seed,rs,it);fflush(stdout);snprintf(fn,256,"%s.sol",pre);dump(fn,spec);return 0;}}}
    }
    printf("spec %s seed %ld rs %d runbest %ld best %ld\n",spec,seed,rs,rb,best);fflush(stdout);
  }
}
