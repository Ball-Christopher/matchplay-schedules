// Lane pairs by annealing: reorder the 6 groups of each week so that every bowler is on every lane pair 3 or 4 times.
// usage: lanes design.txt out.txt seed itersM Thot Tcold
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdint.h>
static uint64_t s[2];
static inline uint64_t rnd(void){uint64_t a=s[0],b=s[1];s[0]=b;a^=a<<23;s[1]=a^b^(a>>17)^(b>>26);return s[1]+b;}
static inline double urnd(void){return (rnd()>>11)*(1.0/9007199254740992.0);}
int wk[23][6][4],cnt[24][6];
static inline int pen(int c){return c<3?3-c:(c>4?c-4:0);}
int main(int argc,char**argv){FILE*f=fopen(argv[1],"r");for(int w=0;w<23;w++)for(int g=0;g<6;g++)for(int i=0;i<4;i++)fscanf(f,"%d",&wk[w][g][i]);
  long seed=atol(argv[3]);long IT=atol(argv[4])*1000000L;double T0=atof(argv[5]),T1=atof(argv[6]);
  s[0]=seed*0x9E3779B97F4A7C15ULL+1;s[1]=seed^0xD1B54A32D192ED03ULL;for(int i=0;i<20;i++)rnd();
  int best=1<<30;
  for(int rs=0;rs<1000;rs++){
    for(int w=0;w<23;w++)for(int g=5;g>0;g--){int j=rnd()%(g+1);for(int i=0;i<4;i++){int t=wk[w][g][i];wk[w][g][i]=wk[w][j][i];wk[w][j][i]=t;}}
    for(int p=0;p<24;p++)for(int l=0;l<6;l++)cnt[p][l]=0;
    for(int w=0;w<23;w++)for(int g=0;g<6;g++)for(int i=0;i<4;i++)cnt[wk[w][g][i]][g]++;
    int cost=0;for(int p=0;p<24;p++)for(int l=0;l<6;l++)cost+=pen(cnt[p][l]);
    double e[16];
    for(long it=0;it<IT&&cost;it++){
      if((it&0xFFFF)==0){double T=T0*pow(T1/T0,(double)it/IT);for(int i=0;i<16;i++)e[i]=exp(-i/T);}
      int w=rnd()%23,a=rnd()%6,b=rnd()%6;if(a==b)continue;int d=0;
      for(int i=0;i<4;i++){int p=wk[w][a][i];d+=pen(cnt[p][a]-1)-pen(cnt[p][a])+pen(cnt[p][b]+1)-pen(cnt[p][b]);p=wk[w][b][i];d+=pen(cnt[p][b]-1)-pen(cnt[p][b])+pen(cnt[p][a]+1)-pen(cnt[p][a]);}
      if(d<=0||(d<16&&urnd()<e[d])){for(int i=0;i<4;i++){int p=wk[w][a][i],q=wk[w][b][i];cnt[p][a]--;cnt[p][b]++;cnt[q][b]--;cnt[q][a]++;wk[w][a][i]=q;wk[w][b][i]=p;}cost+=d;if(cost<best){best=cost;}}
    }
    if(cost==0){f=fopen(argv[2],"w");for(int w=0;w<23;w++){for(int g=0;g<6;g++)for(int i=0;i<4;i++)fprintf(f,"%d ",wk[w][g][i]);fprintf(f,"\n");}fclose(f);printf("%s LANES EXACT rs %d\n",argv[1],rs);return 0;}
    printf("%s rs %d end cost %d best %d\n",argv[1],rs,cost,best);fflush(stdout);
    if(rs>=atoi(argc>7?argv[7]:"0"))break;
  }
  return 1;}
