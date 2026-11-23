// Lane pairs with sigma acting on the lanes as pi = (0 1 2)(3 4 5) throughout: block 2 = sigma(block 1) with lanes
// rotated by pi, block 3 by pi^2, and every week of block 4 is sigma-invariant with lane(sigma g) = pi(lane g).
// Free choices: group order of the 6 weeks of block 1 (720 each); for each block-4 week which group-orbit goes on
// which track and two rotations (18 each).  Annealing.  sigma: point 4a+u -> 4*sa[a]+phi[u].
// usage: lanes_eq design.txt out.txt seed itersM Thot Tcold restarts sigvariant
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdint.h>
static uint64_t s[2];
static inline uint64_t rnd(void){uint64_t a=s[0],b=s[1];s[0]=b;a^=a<<23;s[1]=a^b^(a>>17)^(b>>26);return s[1]+b;}
static inline double urnd(void){return (rnd()>>11)*(1.0/9007199254740992.0);}
int wk[23][6][4],cnt[24][6],cost; int sa[6]={1,2,0,4,5,3}; int phi[4]={0,1,2,3}; int pi[6]={1,2,0,4,5,3};
static inline int sg(int p){return 4*sa[p/4]+phi[p&3];}
static inline int pen(int c){return c<3?3-c:(c>4?c-4:0);}
static inline void bump(int p,int l,int d){cost-=pen(cnt[p][l]);cnt[p][l]+=d;cost+=pen(cnt[p][l]);}
static void putA(int w,int g,int l,int d){for(int i=0;i<4;i++){int p=wk[w][g][i];bump(p,l,d);bump(sg(p),pi[l],d);bump(sg(sg(p)),pi[pi[l]],d);}}
int ord[6][6]; int dorb[5][2][3]; int dpar[5][3]; int dl[5][6]; // dl[k][g] = lane of group g
static void dlanes(int k){int t=dpar[k][0];for(int j=0;j<3;j++){dl[k][dorb[k][0][j]]=3*t+(j+dpar[k][1])%3;dl[k][dorb[k][1][j]]=3*(1-t)+(j+dpar[k][2])%3;}}
static void putD(int k,int d){for(int g=0;g<6;g++)for(int i=0;i<4;i++)bump(wk[18+k][g][i],dl[k][g],d);}
static int has(int w,int g,int p){for(int i=0;i<4;i++)if(wk[w][g][i]==p)return 1;return 0;}
int main(int argc,char**argv){FILE*f=fopen(argv[1],"r");for(int w=0;w<23;w++)for(int g=0;g<6;g++)for(int i=0;i<4;i++)fscanf(f,"%d",&wk[w][g][i]);
  long seed=atol(argv[3]);long IT=atol(argv[4])*1000000L;double T0=atof(argv[5]),T1=atof(argv[6]);int RS=atoi(argv[7]);
  if(argc>8&&atoi(argv[8])==1){phi[1]=2;phi[2]=3;phi[3]=1;}
  for(int k=0;k<5;k++){int nx[6],seen[6]={0},no=0;for(int g=0;g<6;g++){int q=sg(wk[18+k][g][0]);nx[g]=-1;for(int h=0;h<6;h++)if(has(18+k,h,q))nx[g]=h;}
    for(int g=0;g<6;g++)if(!seen[g]){int x=g;for(int j=0;j<3;j++){dorb[k][no][j]=x;seen[x]=1;x=nx[x];}if(x!=g||no>1){fprintf(stderr,"bad D week\n");return 2;}no++;}}
  s[0]=seed*0x9E3779B97F4A7C15ULL+1;s[1]=seed^0xD1B54A32D192ED03ULL;for(int i=0;i<20;i++)rnd();
  int best=1<<30;
  for(int rs=0;rs<RS;rs++){
    for(int p=0;p<24;p++)for(int l=0;l<6;l++)cnt[p][l]=0;cost=24*6*3;
    for(int w=0;w<6;w++){for(int l=0;l<6;l++)ord[w][l]=l;for(int l=5;l>0;l--){int j=rnd()%(l+1);int t=ord[w][l];ord[w][l]=ord[w][j];ord[w][j]=t;}for(int l=0;l<6;l++)putA(w,ord[w][l],l,1);}
    for(int k=0;k<5;k++){dpar[k][0]=rnd()%2;dpar[k][1]=rnd()%3;dpar[k][2]=rnd()%3;dlanes(k);putD(k,1);}
    double e[32];
    for(long it=0;it<IT&&cost;it++){
      if((it&0xFFFF)==0){double T=T0*pow(T1/T0,(double)it/IT);for(int i=0;i<32;i++)e[i]=exp(-i/T);}
      int old=cost;
      if(rnd()%4==0){int k=rnd()%5;int o0=dpar[k][0],o1=dpar[k][1],o2=dpar[k][2];putD(k,-1);int c=rnd()%3;if(c==0)dpar[k][0]^=1;else dpar[k][c]=(dpar[k][c]+1+rnd()%2)%3;dlanes(k);putD(k,1);
        int d=cost-old;if(d<=0||(d<32&&urnd()<e[d])){if(cost<best)best=cost;}else{putD(k,-1);dpar[k][0]=o0;dpar[k][1]=o1;dpar[k][2]=o2;dlanes(k);putD(k,1);}}
      else{int w=rnd()%6,a=rnd()%6,b=rnd()%6;if(a==b)continue;int ga=ord[w][a],gb=ord[w][b];
        putA(w,ga,a,-1);putA(w,gb,b,-1);putA(w,ga,b,1);putA(w,gb,a,1);int d=cost-old;
        if(d<=0||(d<32&&urnd()<e[d])){ord[w][a]=gb;ord[w][b]=ga;if(cost<best)best=cost;}
        else{putA(w,ga,b,-1);putA(w,gb,a,-1);putA(w,ga,a,1);putA(w,gb,b,1);}}
    }
    if(cost==0){f=fopen(argv[2],"w");
      for(int fw=0;fw<23;fw++){
        for(int l=0;l<6;l++){int g=-1;
          if(fw>=18){for(int h=0;h<6;h++)if(dl[fw-18][h]==l)g=h;}
          else{int blk=fw/6,l0=l;for(int j=0;j<blk;j++){int q=0;while(pi[q]!=l0)q++;l0=q;}g=ord[fw-6*blk][l0];}
          for(int i=0;i<4;i++)fprintf(f,"%d ",wk[fw][g][i]);}
        fprintf(f,"\n");}
      fclose(f);printf("%s LANES EXACT rs %d\n",argv[1],rs);return 0;}
  }
  printf("%s best %d\n",argv[1],best);return 1;}
