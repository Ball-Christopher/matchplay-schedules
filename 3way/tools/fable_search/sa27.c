// round 2 = round-1 design (roles), free per-week lane order; objective = min-cost assignment role->bowler
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <stdint.h>
#define N 27
#define W 13
#define L 9
static uint64_t rs;
static inline uint32_t rnd(){rs^=rs<<13;rs^=rs>>7;rs^=rs<<17;return (uint32_t)(rs>>11);}
int R1[W][N]; int c1[N][L], c2[N][L]; int grp[W][L][3]; int perm[W][L]; // perm[w][g]=lane
int C[N+1][N+1]; int match[N+1];
static inline int off(int x){return x<2?2-x:(x>3?x-3:0);}
int hung(){
  static int u[N+1],v[N+1],p[N+1],way[N+1],minv[N+1];char used[N+1];
  memset(u,0,sizeof u);memset(v,0,sizeof v);memset(p,0,sizeof p);
  for(int i=1;i<=N;i++){p[0]=i;int j0=0;for(int j=0;j<=N;j++){minv[j]=1<<29;used[j]=0;}
    do{used[j0]=1;int i0=p[j0],delta=1<<29,j1=0;
      for(int j=1;j<=N;j++)if(!used[j]){int cur=C[i0][j]-u[i0]-v[j];if(cur<minv[j]){minv[j]=cur;way[j]=j0;}if(minv[j]<delta){delta=minv[j];j1=j;}}
      for(int j=0;j<=N;j++)if(used[j]){u[p[j]]+=delta;v[j]-=delta;}else minv[j]-=delta;
      j0=j1;}while(p[j0]!=0);
    do{int j1=way[j0];p[j0]=p[j1];j0=j1;}while(j0);}
  for(int j=1;j<=N;j++)match[p[j]]=j; // bowler i -> role j
  return -v[0];
}
void col(int r){for(int b=0;b<N;b++){int s=0;for(int l=0;l<L;l++)s+=off(c1[b][l]+c2[r][l]);C[b+1][r+1]=s;}}
int main(int argc,char**argv){
  rs=strtoull(argv[1],0,10)*0x9E3779B97F4A7C15ULL+1; double T0=atof(argv[2]),T1=atof(argv[3]); long iters=atol(argv[4]);
  FILE*f=fopen("v27.txt","r");for(int w=0;w<W;w++)for(int i=0;i<N;i++){fscanf(f,"%d",&R1[w][i]);R1[w][i]--;}
  for(int w=0;w<W;w++)for(int g=0;g<L;g++)for(int j=0;j<3;j++){c1[R1[w][g*3+j]][g]++;grp[w][g][j]=R1[w][g*3+j];}
  for(int w=0;w<W;w++){for(int g=0;g<L;g++)perm[w][g]=g;for(int g=L-1;g>0;g--){int j=rnd()%(g+1);int t=perm[w][g];perm[w][g]=perm[w][j];perm[w][j]=t;}
    for(int g=0;g<L;g++)for(int j=0;j<3;j++)c2[grp[w][g][j]][perm[w][g]]++;}
  for(int r=0;r<N;r++)col(r);
  int cost=hung(),best=cost;
  for(long it=0;it<iters&&cost>0;it++){
    double T=T0*pow(T1/T0,(double)it/iters);
    int w=rnd()%W,g=rnd()%L,h=rnd()%(L-1);if(h>=g)h++;
    int lg=perm[w][g],lh=perm[w][h];
    for(int j=0;j<3;j++){c2[grp[w][g][j]][lg]--;c2[grp[w][g][j]][lh]++;c2[grp[w][h][j]][lh]--;c2[grp[w][h][j]][lg]++;}
    int save[N][6];
    for(int j=0;j<3;j++){int a=grp[w][g][j],b=grp[w][h][j];for(int i=0;i<N;i++){save[i][j]=C[i+1][a+1];save[i][3+j]=C[i+1][b+1];}col(a);col(b);}
    int nc=hung();
    if(nc<=cost||(rnd()&0xFFFFFF)/16777216.0<exp((cost-nc)/T)){cost=nc;perm[w][g]=lh;perm[w][h]=lg;if(cost<best){best=cost;fprintf(stderr,"seed %s it %ld best %d\n",argv[1],it,best);}}
    else{
      for(int j=0;j<3;j++){c2[grp[w][g][j]][lg]++;c2[grp[w][g][j]][lh]--;c2[grp[w][h][j]][lh]++;c2[grp[w][h][j]][lg]--;}
      for(int j=0;j<3;j++){int a=grp[w][g][j],b=grp[w][h][j];for(int i=0;i<N;i++){C[i+1][a+1]=save[i][j];C[i+1][b+1]=save[i][3+j];}}
    }
  }
  if(cost==0){hung(); // role r -> bowler
    int inv[N];for(int b=0;b<N;b++)inv[match[b+1]-1]=b;
    printf("SOLUTION\n");
    for(int w=0;w<W;w++){int out[N];for(int g=0;g<L;g++)for(int j=0;j<3;j++)out[perm[w][g]*3+j]=inv[grp[w][g][j]]+1;for(int i=0;i<N;i++)printf("%d ",out[i]);printf("\n");}
  } else fprintf(stderr,"seed %s final %d best %d\n",argv[1],cost,best);
}
