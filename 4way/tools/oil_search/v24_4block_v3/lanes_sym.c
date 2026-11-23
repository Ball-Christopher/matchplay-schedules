// Lane pairs with the block-cycling automorphism sigma imposed on the lanes: block 2 = sigma(block 1) with the lane
// pairs permuted by pi, block 3 likewise with pi^2; block 4 free.  Annealing over the group order of the 6 weeks
// of block 1 and the 5 weeks of block 4.  sigma: point 4a+u -> 4*sa[a]+u, sa = (0 1 2)(3 4 5).
// usage: lanes_sym design.txt out.txt seed itersM Thot Tcold pitype(0: (012)(345), 1: (012), 2: identity) restarts
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdint.h>
static uint64_t s[2];
static inline uint64_t rnd(void){uint64_t a=s[0],b=s[1];s[0]=b;a^=a<<23;s[1]=a^b^(a>>17)^(b>>26);return s[1]+b;}
static inline double urnd(void){return (rnd()>>11)*(1.0/9007199254740992.0);}
int wk[23][6][4],cnt[24][6],cost; int sa[6]={1,2,0,4,5,3}; int pi[6];
static inline int sg(int p){return 4*sa[p/4]+(p&3);}
static inline int pen(int c){return c<3?3-c:(c>4?c-4:0);}
static inline void bump(int p,int l,int d){cost-=pen(cnt[p][l]);cnt[p][l]+=d;cost+=pen(cnt[p][l]);}
static void put(int w,int g,int l,int d){ // stored week index w in 0..10 (0-5: A, 6-10: D = file weeks 18..22)
  int fw=w<6?w:w+12;
  for(int i=0;i<4;i++){int p=wk[fw][g][i];bump(p,l,d);if(w<6){bump(sg(p),pi[l],d);bump(sg(sg(p)),pi[pi[l]],d);}}}
int ord[11][6]; // ord[w][l] = group on lane l
int main(int argc,char**argv){FILE*f=fopen(argv[1],"r");for(int w=0;w<23;w++)for(int g=0;g<6;g++)for(int i=0;i<4;i++)fscanf(f,"%d",&wk[w][g][i]);
  long seed=atol(argv[3]);long IT=atol(argv[4])*1000000L;double T0=atof(argv[5]),T1=atof(argv[6]);int pt=atoi(argv[7]);int RS=atoi(argv[8]);
  int P[3][6]={{1,2,0,4,5,3},{1,2,0,3,4,5},{0,1,2,3,4,5}};for(int i=0;i<6;i++)pi[i]=P[pt][i];
  s[0]=seed*0x9E3779B97F4A7C15ULL+1;s[1]=seed^0xD1B54A32D192ED03ULL;for(int i=0;i<20;i++)rnd();
  int best=1<<30;
  for(int rs=0;rs<RS;rs++){
    for(int p=0;p<24;p++)for(int l=0;l<6;l++)cnt[p][l]=0;cost=24*6*3;
    for(int w=0;w<11;w++){for(int l=0;l<6;l++)ord[w][l]=l;for(int l=5;l>0;l--){int j=rnd()%(l+1);int t=ord[w][l];ord[w][l]=ord[w][j];ord[w][j]=t;}for(int l=0;l<6;l++)put(w,ord[w][l],l,1);}
    double e[32];
    for(long it=0;it<IT&&cost;it++){
      if((it&0xFFFF)==0){double T=T0*pow(T1/T0,(double)it/IT);for(int i=0;i<32;i++)e[i]=exp(-i/T);}
      int w=rnd()%11,a=rnd()%6,b=rnd()%6;if(a==b)continue;int old=cost;int ga=ord[w][a],gb=ord[w][b];
      put(w,ga,a,-1);put(w,gb,b,-1);put(w,ga,b,1);put(w,gb,a,1);int d=cost-old;
      if(d<=0||(d<32&&urnd()<e[d])){ord[w][a]=gb;ord[w][b]=ga;if(cost<best)best=cost;}
      else{put(w,ga,b,-1);put(w,gb,a,-1);put(w,ga,a,1);put(w,gb,b,1);}
    }
    if(cost==0){f=fopen(argv[2],"w");
      for(int fw=0;fw<23;fw++){int blk=fw/6;if(fw>=18)blk=3;
        for(int l=0;l<6;l++){int g;
          if(blk==3)g=ord[fw-12][l];else{int l0=l;for(int j=0;j<blk;j++){int q=0;while(pi[q]!=l0)q++;l0=q;}g=ord[fw-6*blk][l0];}
          for(int i=0;i<4;i++)fprintf(f,"%d ",wk[fw][g][i]);}
        fprintf(f,"\n");}
      fclose(f);printf("%s LANES EXACT pi %d rs %d\n",argv[1],pt,rs);return 0;}
  }
  printf("%s pi %d best %d\n",argv[1],pt,best);return 1;}
