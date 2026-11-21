// 1-rotational Z23+inf base week; differences each 3x; week-offsets of same-difference pairs differ by 6..11 (mod +-)
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>
#define INF 23
static unsigned long long s;
static inline unsigned rnd(){s^=s<<13;s^=s>>7;s^=s<<17;return (unsigned)(s>>11);}
int p[24]; // p[i]: point at slot i; block = i/4
int okd[23];
int cost(){
  int cnt[12]={0}, st[12][40]; int c=0;
  for(int b=0;b<6;b++)for(int i=0;i<4;i++)for(int j=i+1;j<4;j++){
    int x=p[b*4+i],y=p[b*4+j];
    if(x==INF||y==INF)continue;
    int d=(y-x+23)%23,a=x; if(d>11){d=23-d;a=y;}
    st[d][cnt[d]++]=a;
  }
  for(int d=1;d<=11;d++){
    c+=3*abs(cnt[d]-3);
    for(int i=0;i<cnt[d];i++)for(int j=i+1;j<cnt[d];j++) if(!okd[(st[d][i]-st[d][j]+23)%23])c++;
  }
  // inf block
  for(int b=0;b<6;b++){int has=0;for(int i=0;i<4;i++)if(p[b*4+i]==INF)has=1;
    if(has)for(int i=0;i<4;i++)for(int j=i+1;j<4;j++){int x=p[b*4+i],y=p[b*4+j];if(x!=INF&&y!=INF&&!okd[(x-y+23)%23])c++;}}
  return c;
}
int main(int argc,char**argv){
  s=argc>1?atoll(argv[1])*2654435761ULL+88172645463325252ULL:88172645463325252ULL;
  int lo=argc>2?atoi(argv[2]):6, hi=argc>3?atoi(argv[3]):11;
  for(int d=0;d<23;d++){int e=d>11?23-d:d;okd[d]=(e>=lo&&e<=hi);}
  int found=0;
  for(long rs=0;rs<1000000&&found<20;rs++){
    for(int i=0;i<24;i++)p[i]=i;
    for(int i=23;i>0;i--){int j=rnd()%(i+1);int t=p[i];p[i]=p[j];p[j]=t;}
    int c=cost();double T=1.5;
    for(long it=0;it<3000000&&c;it++){
      int i=rnd()%24,j=rnd()%24;if(i/4==j/4)continue;
      int t=p[i];p[i]=p[j];p[j]=t;int n=cost();
      if(n<=c||(rnd()%1000000)<1e6*exp((c-n)/T))c=n;else{t=p[i];p[i]=p[j];p[j]=t;}
      T=1.5-1.2*(it/3000000.0);
    }
    if(!c){found++;for(int i=0;i<24;i++)printf("%d ",p[i]);printf("\n");fflush(stdout);}
    else fprintf(stderr,"restart %ld end cost %d\n",rs,c);
  }
}
