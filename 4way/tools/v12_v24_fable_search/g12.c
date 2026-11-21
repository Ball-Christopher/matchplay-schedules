// G = Z2^2 x Z3 acting semiregularly on v=12*NC points; Z3 rotates lanes (m,t)->(m+1,t), Z2^2 fixes lanes.
// week types: A free (orbit 12), B Z3-stabilised (orbit 4), D <kappa>xZ3-stabilised (orbit 2), E coset week (orbit 1)
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#ifndef NC
#define NC 2
#endif
#define V (12*NC)
#define NL (3*NC)
#define R (V-1)
#define HI ((R+NL-1)/NL)
#define LO (R/NL)
#define MX 12
static unsigned long long s=88172645463325252ULL;
static inline unsigned long long rnd(){s^=s<<13;s^=s>>7;s^=s<<17;return s;}
static inline double ur(){return (double)(rnd()>>11)/9007199254740992.0;}
int na,nb,nd,ne;
typedef struct { int A[MX][V]; int Bcp[MX][4*NC],Boff[MX][4*NC],Blo[MX][NC];
  int Dk[MX],Dcp[MX][2*NC],Doff[MX][2*NC],Dlo[MX][NC]; int Eo[MX][NC],Etr[MX][NC]; } St;
St st,sv; int W[R][NL][4]; int pr[V][V],ln[V][NL];
static inline int pt(int c,int h,int i){return c*12+h*3+i;}
static inline int act(int p,int h,int k){int c=p/12,hh=(p%12)/3,i=p%3;return pt(c,hh^h,(i+k)%3);}
static inline int actL(int L,int k){return (L%3+k)%3+3*(L/3);}
static int expand(){int w=0;
  for(int a=0;a<na;a++)for(int h=0;h<4;h++)for(int k=0;k<3;k++){for(int b=0;b<NL;b++)for(int x=0;x<4;x++)W[w][actL(b,k)][x]=act(st.A[a][4*b+x],h,k);w++;}
  for(int b=0;b<nb;b++)for(int h=0;h<4;h++){for(int t=0;t<NC;t++)for(int k=0;k<3;k++)for(int x=0;x<4;x++){int o=st.Bcp[b][4*t+x];
      W[w][(st.Blo[b][t]+k)%3+3*t][x]=act(pt(o/4,o%4,st.Boff[b][o]),h,k);}w++;}
  for(int d=0;d<nd;d++){int kap=st.Dk[d];int rho=kap==1?2:1; int reps[2]={0,rho};
    for(int q=0;q<2;q++){for(int t=0;t<NC;t++)for(int k=0;k<3;k++)for(int y=0;y<2;y++){int o=st.Dcp[d][2*t+y];int c=o/2,h=reps[o%2];int p=pt(c,h,st.Doff[d][o]);
        int L=(st.Dlo[d][t]+k)%3+3*t; W[w][L][2*y]=act(p,q?rho:0,k);W[w][L][2*y+1]=act(p,(q?rho:0)^kap,k);}w++;}}
  for(int e=0;e<ne;e++){for(int c=0;c<NC;c++)for(int i=0;i<3;i++)for(int h=0;h<4;h++)W[w][(i+st.Eo[e][c])%3+3*st.Etr[e][c]][h]=pt(c,h,i);w++;}
  return w;}
static int cost(){expand();memset(pr,0,sizeof pr);memset(ln,0,sizeof ln);
  for(int w=0;w<R;w++)for(int L=0;L<NL;L++){int*g=W[w][L];for(int x=0;x<4;x++){ln[g[x]][L]++;for(int y=x+1;y<4;y++){pr[g[x]][g[y]]++;pr[g[y]][g[x]]++;}}}
  int c=0;for(int p=0;p<V;p++){for(int q=p+1;q<V;q++)c+=abs(pr[p][q]-3);for(int L=0;L<NL;L++){int x=ln[p][L];c+=LW*(x>HI?x-HI:(x<LO?LO-x:0));}}
  return c;}
static void shuf(int*a,int n){for(int i=n-1;i>0;i--){int j=rnd()%(i+1);int t=a[i];a[i]=a[j];a[j]=t;}}
static void init(){
  for(int a=0;a<na;a++){for(int i=0;i<V;i++)st.A[a][i]=i;shuf(st.A[a],V);}
  for(int b=0;b<nb;b++){for(int i=0;i<4*NC;i++){st.Bcp[b][i]=i;st.Boff[b][i]=rnd()%3;}shuf(st.Bcp[b],4*NC);for(int t=0;t<NC;t++)st.Blo[b][t]=rnd()%3;}
  for(int d=0;d<nd;d++){st.Dk[d]=1+d%3;for(int i=0;i<2*NC;i++){st.Dcp[d][i]=i;st.Doff[d][i]=rnd()%3;}shuf(st.Dcp[d],2*NC);for(int t=0;t<NC;t++)st.Dlo[d][t]=rnd()%3;}
  for(int e=0;e<ne;e++)for(int c=0;c<NC;c++){st.Eo[e][c]=rnd()%3;st.Etr[e][c]=c;}}
static void move(){int tot=na*20+nb*6+nd*3+ne*1;int r=rnd()%tot;
  if(r<na*20){int a=rnd()%na;int x,y;do{x=rnd()%V;y=rnd()%V;}while(x/4==y/4);
    if(rnd()%8==0){int bx=x/4,by=y/4;for(int q=0;q<4;q++){int t=st.A[a][4*bx+q];st.A[a][4*bx+q]=st.A[a][4*by+q];st.A[a][4*by+q]=t;}}
    else{int t=st.A[a][x];st.A[a][x]=st.A[a][y];st.A[a][y]=t;}return;}
  r-=na*20;
  if(r<nb*6){int b=rnd()%nb;int q=rnd()%4;if(q<2)st.Boff[b][rnd()%(4*NC)]=rnd()%3;else if(q==2)st.Blo[b][rnd()%NC]=rnd()%3;
    else{int x=rnd()%(4*NC),y=rnd()%(4*NC);int t=st.Bcp[b][x];st.Bcp[b][x]=st.Bcp[b][y];st.Bcp[b][y]=t;}return;}
  r-=nb*6;
  if(r<nd*3){int d=rnd()%nd;int q=rnd()%5;if(q<2)st.Doff[d][rnd()%(2*NC)]=rnd()%3;else if(q==2)st.Dlo[d][rnd()%NC]=rnd()%3;else if(q==3)st.Dk[d]=1+rnd()%3;
    else{int x=rnd()%(2*NC),y=rnd()%(2*NC);int t=st.Dcp[d][x];st.Dcp[d][x]=st.Dcp[d][y];st.Dcp[d][y]=t;}return;}
  {int e=rnd()%ne;if(rnd()%2||NC==1)st.Eo[e][rnd()%NC]=rnd()%3;else{int t=st.Etr[e][0];st.Etr[e][0]=st.Etr[e][1];st.Etr[e][1]=t;}}}
int main(int argc,char**argv){
  na=atoi(argv[1]);nb=atoi(argv[2]);nd=atoi(argv[3]);ne=atoi(argv[4]);
  if(12*na+4*nb+2*nd+ne!=R){fprintf(stderr,"bad mix\n");return 2;}
  s^=atoll(argv[5])*0x9E3779B97F4A7C15ULL;for(int i=0;i<20;i++)rnd();
  long iters=atol(argv[6]);double T0=atof(argv[7]),T1=atof(argv[8]);int natt=argc>9?atoi(argv[9]):1000000;
  int gbest=1<<30;
  for(int att=0;att<natt;att++){init();int c=cost();double T=T0;int best=c;
    for(long it=0;it<iters&&c>0;it++){if((it&0xff)==0)T=T0*pow(T1/T0,(double)it/iters);
      sv=st;move();int nc=cost();if(nc<=c||ur()<exp(-(nc-c)/T)){c=nc;if(c<best)best=c;}else st=sv;}
    if(best<gbest){gbest=best;fprintf(stderr,"mix %d %d %d %d att %d end %d best %d\n",na,nb,nd,ne,att,c,best);}
    if(c==0){cost();for(int w=0;w<R;w++){for(int L=0;L<NL;L++)for(int x=0;x<4;x++)printf("%d ",W[w][L][x]+1);printf("\n");}return 0;}
  }
  fprintf(stderr,"mix %d %d %d %d FAILED gbest %d\n",na,nb,nd,ne,gbest);return 1;}
