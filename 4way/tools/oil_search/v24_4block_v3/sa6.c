// Z6 = <sigma> x <tau> semiregular on 24 points p=6*o+i (4 point orbits): sigma: i->i+2 cycles oil blocks 1->2->3,
// tau: i->i+3 fixes every block.  Stored: block A (blocks 2,3 are its sigma images) and block D (5 weeks).
// Week types: 'O' = free base week, stands for the two weeks B, tau(B);  digit f (0,2,4,6) = tau-invariant week
// with f tau-fixed groups {x,tx,y,ty} and (6-f)/2 swapped pairs of groups (g, tau g).
// Counts are per tau-orbit of pairs (144).  cost = WR*sum max(0,c-1) + sum |tot-3|.
// usage: sa6 specA specD seed Thot Tcold iters(M) WR outprefix     e.g. sa6 OO22 O222
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <stdint.h>
static uint64_t s[2];
static inline uint64_t rnd(void){uint64_t a=s[0],b=s[1];s[0]=b;a^=a<<23;s[1]=a^b^(a>>17)^(b>>26);return s[1]+b;}
static inline double urnd(void){return (rnd()>>11)*(1.0/9007199254740992.0);}
#define MW 16
#define TAU(p) (((p)/6)*6+((p)%6+3)%6)
#define SIG(p) (((p)/6)*6+((p)%6+2)%6)
int NW; int wb[MW],wt[MW],wf[MW],wn[MW]; int wk[MW][24]; int gs[MW][24],ge[MW][24];
int pid[24][24],torb[276],istp[276],zorb[144],zm[48][3]; int c[2][144],tot[144]; int WR; long cost;
static inline int ab(int x){return x<0?-x:x;}
static inline void add(int b,int p,int d){int e=torb[p];int old=c[b][e];c[b][e]=old+d;
  cost+=WR*((old+d>1?old+d-1:0)-(old>1?old-1:0));
  if(b){cost+=ab(tot[e]+d-3)-ab(tot[e]-3);tot[e]+=d;}
  else{int z=zorb[e];for(int i=0;i<3;i++){int r=zm[z][i];cost+=ab(tot[r]+d-3)-ab(tot[r]-3);tot[r]+=d;}}}
static void grp(int w,int st,int d){int b=wb[w];int*G=&wk[w][st];int n=ge[w][st]-st;
  if(wt[w]==0){for(int i=0;i<4;i++)for(int j=i+1;j<4;j++){int p=pid[G[i]][G[j]];add(b,p,istp[p]?2*d:d);}}
  else if(n==2){int x=G[0],y=G[1];add(b,pid[x][TAU(x)],d);add(b,pid[y][TAU(y)],d);add(b,pid[x][y],d);add(b,pid[x][TAU(y)],d);}
  else{for(int i=0;i<4;i++)for(int j=i+1;j<4;j++)add(b,pid[G[i]][G[j]],d);}}
static void init(void){memset(c,0,sizeof c);memset(tot,0,sizeof tot);cost=144*3;
  for(int w=0;w<NW;w++){
    if(wt[w]==0){for(int i=0;i<24;i++)wk[w][i]=i;}
    else{for(int i=0;i<12;i++)wk[w][i]=(i/3)*6+i%3+3*(rnd()&1);}
    for(int i=wn[w]-1;i>0;i--){int j=rnd()%(i+1);int t=wk[w][i];wk[w][i]=wk[w][j];wk[w][j]=t;}
    for(int i=0;i<wn[w];i=ge[w][i])grp(w,i,1);}}
static void dump(const char*fn,const char*sa,const char*sd){FILE*f=fopen(fn,"w");fprintf(f,"spec %s %s cost %ld\n",sa,sd,cost);
  for(int w=0;w<NW;w++){fprintf(f,"%c %c:",wb[w]?'D':'A',wt[w]?'0'+wf[w]:'O');for(int i=0;i<wn[w];i++)fprintf(f," %d",wk[w][i]);fprintf(f,"\n");}fclose(f);}
int main(int argc,char**argv){
  const char*sp[2]={argv[1],argv[2]};long seed=atol(argv[3]);double T0=atof(argv[4]),T1=atof(argv[5]);long IT=atol(argv[6])*1000000L;WR=atoi(argv[7]);const char*pre=argv[8];
  s[0]=seed*0x9E3779B97F4A7C15ULL+1;s[1]=seed^0xD1B54A32D192ED03ULL;for(int i=0;i<20;i++)rnd();
  int n=0;for(int a=0;a<24;a++)for(int b=a+1;b<24;b++)pid[a][b]=pid[b][a]=n++;
  for(int p=0;p<276;p++)torb[p]=-1;n=0;
  for(int a=0;a<24;a++)for(int b=a+1;b<24;b++){int p=pid[a][b];if(torb[p]>=0)continue;int q=pid[TAU(a)][TAU(b)];torb[p]=torb[q]=n++;istp[p]=(q==p);}
  for(int e=0;e<144;e++)zorb[e]=-1;n=0;
  for(int a=0;a<24;a++)for(int b=a+1;b<24;b++){int e=torb[pid[a][b]];if(zorb[e]>=0)continue;int x=a,y=b;for(int i=0;i<3;i++){int r=torb[pid[x][y]];zorb[r]=n;zm[n][i]=r;x=SIG(x);y=SIG(y);}n++;}
  NW=0;for(int b=0;b<2;b++)for(const char*q=sp[b];*q;q++){int w=NW++;wb[w]=b;
    if(*q=='O'){wt[w]=0;wn[w]=24;for(int i=0;i<24;i++){gs[w][i]=i&~3;ge[w][i]=(i&~3)+4;}}
    else{int f=*q-'0';wt[w]=1;wf[w]=f;wn[w]=12;for(int i=0;i<12;i++){if(i<2*f){gs[w][i]=i&~1;ge[w][i]=(i&~1)+2;}else{int k=(i-2*f)/4;gs[w][i]=2*f+4*k;ge[w][i]=2*f+4*k+4;}}}}
  long best=1<<30;char fn[256];double expT[64];
  for(int rs=0;;rs++){
    init();long rb=cost;
    for(long it=0;it<IT;it++){
      if((it&0xFFFF)==0){double Tc=T0*pow(T1/T0,(double)it/IT);for(int i=0;i<64;i++)expT[i]=exp(-i/Tc);}
      int w=rnd()%NW;long old=cost;int i,j=-1,ov=0;
      if(wt[w]==1&&(rnd()%3==0)){i=rnd()%12;if(ge[w][i]-gs[w][i]==2)continue;ov=wk[w][i];grp(w,gs[w][i],-1);wk[w][i]=TAU(ov);grp(w,gs[w][i],1);}
      else{i=rnd()%wn[w];j=rnd()%wn[w];if(gs[w][i]==gs[w][j])continue;grp(w,gs[w][i],-1);grp(w,gs[w][j],-1);int t=wk[w][i];wk[w][i]=wk[w][j];wk[w][j]=t;grp(w,gs[w][i],1);grp(w,gs[w][j],1);}
      long d=cost-old;
      if(d>0&&(d>=64||urnd()>=expT[d])){
        if(j<0){grp(w,gs[w][i],-1);wk[w][i]=ov;grp(w,gs[w][i],1);}
        else{grp(w,gs[w][i],-1);grp(w,gs[w][j],-1);int t=wk[w][i];wk[w][i]=wk[w][j];wk[w][j]=t;grp(w,gs[w][i],1);grp(w,gs[w][j],1);}}
      else if(cost<rb){rb=cost;if(cost<best){best=cost;snprintf(fn,256,"%s.best",pre);dump(fn,sp[0],sp[1]);if(cost==0){printf("FOUND seed %ld rs %d it %ld\n",seed,rs,it);fflush(stdout);snprintf(fn,256,"%s.sol",pre);dump(fn,sp[0],sp[1]);return 0;}}}
    }
    printf("spec %s %s seed %ld rs %d runbest %ld best %ld\n",sp[0],sp[1],seed,rs,rb,best);fflush(stdout);
  }
}
