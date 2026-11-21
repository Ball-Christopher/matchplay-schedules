#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>
// points p = 5*a + i  (class a in 0..3, i in Z5). g: i->i+1, lane->lane+1
static unsigned long long s=88172645463325252ULL;
static inline unsigned long long rnd(){s^=s<<13;s^=s>>7;s^=s<<17;return s;}
int wk[3][20]; // base weeks: positions 4b..4b+3 = block b
int fx[4][4];  // fixed-week transversal offsets c_a
int cnt[4][4][5];int cw[4][4][4][5];int CW=0;
static void add(int p,int q,int v){int W=CW;int a=p/5,i=p%5,b=q/5,j=q%5;
  if(a>b){int t=a;a=b;b=t;t=i;i=j;j=t;}
  int d=(j-i+5)%5; if(a==b){if(d>2)d=5-d;} cnt[a][b][d]+=v;cw[W][a][b][d]+=v;}
static int cost(){int c=0;for(int a=0;a<4;a++)for(int b=a;b<4;b++)for(int d=0;d<5;d++){
  if(a==b){if(d==1||d==2)c+=abs(cnt[a][b][d]-3);} else c+=abs(cnt[a][b][d]-3);}
 for(int w=0;w<4;w++)for(int a=0;a<4;a++)for(int b=a;b<4;b++)for(int d=0;d<5;d++)if(cw[w][a][b][d]>1)c+=cw[w][a][b][d]-1;return c;}
static void build(){memset(cnt,0,sizeof cnt);memset(cw,0,sizeof cw);
  for(int w=0;w<3;w++)for(int b=0;b<5;b++)for(int x=0;x<4;x++)for(int y=x+1;y<4;y++)CW=w,add(wk[w][4*b+x],wk[w][4*b+y],1);
  CW=3;for(int f=0;f<4;f++)for(int x=0;x<4;x++)for(int y=x+1;y<4;y++)add(5*x+fx[f][x],5*y+fx[f][y],1);}
int perms[120][5];int np=0;
static void gen(int*p,int k){if(k==5){memcpy(perms[np++],p,20);return;}for(int i=k;i<5;i++){int t=p[k];p[k]=p[i];p[i]=t;gen(p,k+1);t=p[k];p[k]=p[i];p[i]=t;}}
int H[3][120][4][5];
static int lanes(int*res){
  for(int w=0;w<3;w++)for(int q=0;q<120;q++){memset(H[w][q],0,sizeof H[w][q]);
    for(int b=0;b<5;b++)for(int x=0;x<4;x++){int p=wk[w][4*b+x];H[w][q][p/5][(perms[q][b]-p%5+5)%5]++;}}
  for(int q0=0;q0<120;q0++)for(int q1=0;q1<120;q1++)for(int q2=0;q2<120;q2++){
    int h[4][5];int ok=1;
    for(int a=0;a<4&&ok;a++)for(int d=0;d<5;d++){h[a][d]=H[0][q0][a][d]+H[1][q1][a][d]+H[2][q2][a][d];if(h[a][d]>4){ok=0;break;}}
    if(!ok)continue;
    for(int r=0;r<625;r++){int rr[4]={r%5,r/5%5,r/25%5,r/125};int g[4][5];memcpy(g,h,sizeof g);
      for(int f=0;f<4;f++)for(int a=0;a<4;a++)g[a][(rr[f]-fx[f][a]+5)%5]++;
      int good=1;for(int a=0;a<4&&good;a++)for(int d=0;d<5;d++)if(g[a][d]<3||g[a][d]>4){good=0;break;}
      if(good){res[0]=q0;res[1]=q1;res[2]=q2;for(int f=0;f<4;f++)res[3+f]=rr[f];return 1;}}
  }
  return 0;}
int main(int argc,char**argv){
  if(argc>1)s^=atoll(argv[1])*0x9E3779B97F4A7C15ULL;
  int p0[5]={0,1,2,3,4};gen(p0,0);
  for(int att=0;att<100000;att++){
    for(int w=0;w<3;w++){for(int i=0;i<20;i++)wk[w][i]=i;for(int i=19;i>0;i--){int j=rnd()%(i+1);int t=wk[w][i];wk[w][i]=wk[w][j];wk[w][j]=t;}}
    for(int f=0;f<4;f++){fx[f][0]=0;for(int a=1;a<4;a++)fx[f][a]=rnd()%5;}
    build();int c=cost();double T=1.0;long iters=3000000;
    for(long it=0;it<iters&&c>0;it++){
      if((it&0xfff)==0)T=1.0*pow(0.1,(double)it/iters);
      int nc;
      if(rnd()%8==0){int f=rnd()%4,a=1+rnd()%3,old=fx[f][a];fx[f][a]=rnd()%5;build();nc=cost();
        if(nc<=c||(double)(rnd()>>11)/9007199254740992.0<exp(-(nc-c)/T))c=nc;else{fx[f][a]=old;build();}}
      else{int w=rnd()%3,x=rnd()%20,y=rnd()%20;if(x/4==y/4)continue;int t=wk[w][x];wk[w][x]=wk[w][y];wk[w][y]=t;build();nc=cost();
        if(nc<=c||(double)(rnd()>>11)/9007199254740992.0<exp(-(nc-c)/T))c=nc;else{t=wk[w][x];wk[w][x]=wk[w][y];wk[w][y]=t;build();}}
    }
    fprintf(stderr,"att %d cost %d\n",att,c);
    if(c)continue;
    int res[7];int ok=lanes(res);fprintf(stderr,"  design found, lanes %d\n",ok);
    if(!ok)continue;
    // output 19 weeks, groups in lane order
    for(int w=0;w<3;w++)for(int k=0;k<5;k++){int out[5][4];
      for(int b=0;b<5;b++){int L=(perms[res[w]][b]+k)%5;for(int x=0;x<4;x++){int p=wk[w][4*b+x];out[L][x]=5*(p/5)+(p%5+k)%5;}}
      for(int L=0;L<5;L++)for(int x=0;x<4;x++)printf("%d ",out[L][x]);printf("\n");}
    for(int f=0;f<4;f++){int out[5][4];for(int k=0;k<5;k++){int L=(res[3+f]+k)%5;for(int a=0;a<4;a++)out[L][a]=5*a+(fx[f][a]+k)%5;}
      for(int L=0;L<5;L++)for(int x=0;x<4;x++)printf("%d ",out[L][x]);printf("\n");}
    return 0;
  }
  return 1;}
