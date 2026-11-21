// 4-colour the 138 blocks of a 1-rotational design so blocks sharing a pair differ; per point per colour <=7
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
int B[138][4],nb[138][16],nn[138],col[138],pc[24][4];long nodes,lim;
int rec(int done){
  if(done==138)return 1;
  if(++nodes>lim)return -1;
  int best=-1,bs=-1,bm=0;
  for(int b=0;b<138;b++)if(col[b]<0){int m=0;for(int i=0;i<nn[b];i++)if(col[nb[b][i]]>=0)m|=1<<col[nb[b][i]];
    for(int c=0;c<4;c++)for(int k=0;k<4;k++)if(pc[B[b][k]][c]>=7)m|=1<<c;
    int sat=__builtin_popcount(m);if(sat==4)return 0;if(sat>bs){bs=sat;best=b;bm=m;if(sat==3)break;}}
  for(int c=0;c<4;c++)if(!(bm>>c&1)){col[best]=c;for(int k=0;k<4;k++)pc[B[best][k]][c]++;
    int r=rec(done+1);if(r)return r;
    for(int k=0;k<4;k++)pc[B[best][k]][c]--;col[best]=-1;}
  return 0;
}
int main(int argc,char**argv){lim=atol(argv[1]);int v[24];char line[400];
  while(fgets(line,400,stdin)){
    char*p=line;for(int i=0;i<24;i++)v[i]=strtol(p,&p,10);
    for(int b=0;b<6;b++)for(int t=0;t<23;t++)for(int k=0;k<4;k++)B[b*23+t][k]=v[b*4+k]<0?23:(v[b*4+k]+t)%23;
    for(int a=0;a<138;a++){nn[a]=0;for(int b=0;b<138;b++)if(a!=b){int sh=0;for(int i=0;i<4;i++)for(int j=0;j<4;j++)sh+=B[a][i]==B[b][j];if(sh>=2)nb[a][nn[a]++]=b;}}
    memset(col,-1,sizeof col);memset(pc,0,sizeof pc);nodes=0;
    col[0]=0;for(int k=0;k<4;k++)pc[B[0][k]][0]++;
    int r=rec(1);
    if(r){line[strcspn(line,"\n")]=0;printf("%s | %d",line,r);if(r==1)for(int b=0;b<138;b++)printf(" %d",col[b]);printf("\n");fflush(stdout);}
  }
}
