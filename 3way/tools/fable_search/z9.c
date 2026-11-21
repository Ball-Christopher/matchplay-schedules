// v27 double round: points Z_9 x 3 classes. Each round = KTS(27): 1 base week developed mod 9 + 4 invariant weeks.
// Lanes rotate with the group. Each round separately lane-balanced (1 or 2), total <=3 (i.e. 2 or 3).
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#define M 9
static uint64_t rs;
static inline uint32_t rnd(){rs^=rs<<13;rs^=rs>>7;rs^=rs<<17;return (uint32_t)(rs>>11);}
int didx[27][27], bud[39];
int wk[2][9][3]; int inv[2][4][2]; int R; // current round
long nodes, cap;
static int take(int a,int b,int c){int i=didx[a][b],j=didx[a][c],k=didx[b][c];bud[i]--;bud[j]--;bud[k]--;
  if(bud[i]<0||bud[j]<0||bud[k]<0){bud[i]++;bud[j]++;bud[k]++;return 0;}return 1;}
static void give(int a,int b,int c){bud[didx[a][b]]++;bud[didx[a][c]]++;bud[didx[b][c]]++;}
int dfs(int t,uint32_t used){
  if(++nodes>cap)return -1;
  if(t==9)return 1;
  int p=0;while(used>>p&1)p++;
  int cq[400],cr[400],n=0;
  for(int q=p+1;q<27;q++)if(!(used>>q&1))for(int r=q+1;r<27;r++)if(!(used>>r&1)){cq[n]=q;cr[n]=r;n++;}
  for(int i=n-1;i>0;i--){int j=rnd()%(i+1);int x=cq[i];cq[i]=cq[j];cq[j]=x;x=cr[i];cr[i]=cr[j];cr[j]=x;}
  for(int i=0;i<n;i++){int q=cq[i],r=cr[i];if(!take(p,q,r))continue;
    wk[R][t][0]=p;wk[R][t][1]=q;wk[R][t][2]=r;
    int res=dfs(t+1,used|1u<<p|1u<<q|1u<<r);give(p,q,r);if(res)return res;}
  return 0;
}
int cnt[2][3][M],rem[2][3],lane[2][9],l0[2][4];long ln,lcap;
static inline int md(int x){x%=M;return x<0?x+M:x;}
static int feas(int r){for(int c=0;c<3;c++){int z=0;for(int i=0;i<M;i++)z+=cnt[r][c][i]==0;if(z>rem[r][c])return 0;}return 1;}
int ldfs(int it,int m0,int m1){
  if(++ln>lcap)return -1;
  if(it==26)return 1;
  int r=it/13,k=it%13; int st=rnd()%M;
  if(k<9){int m=r?m1:m0;
    for(int kk=0;kk<M;kk++){int l=(st+kk)%M; if(it==0){if(kk)break;l=0;} if(m>>l&1)continue;
      int ok=1;
      for(int j=0;j<3;j++){int p=wk[r][k][j];int c=p/9,y=p%9,q=md(l-y); cnt[r][c][q]++;rem[r][c]--; if(cnt[r][c][q]>2||cnt[0][c][q]+cnt[1][c][q]>3)ok=0;}
      int res=0; if(ok&&feas(r))res=ldfs(it+1,r?m0:m0|1<<l,r?m1|1<<l:m1);
      for(int j=0;j<3;j++){int p=wk[r][k][j];int c=p/9,y=p%9,q=md(l-y); cnt[r][c][q]--;rem[r][c]++;}
      if(res){if(res==1)lane[r][k]=l;return res;}
    }
    return 0;}
  int i=k-9,u=inv[r][i][0],v=inv[r][i][1];
  for(int kk=0;kk<M;kk++){int l=(st+kk)%M; int q[3]={l,md(l-u),md(l-v)}; int ok=1;
    for(int c=0;c<3;c++){cnt[r][c][q[c]]++;rem[r][c]--; if(cnt[r][c][q[c]]>2||cnt[0][c][q[c]]+cnt[1][c][q[c]]>3)ok=0;}
    int res=0; if(ok&&feas(r))res=ldfs(it+1,m0,m1);
    for(int c=0;c<3;c++){cnt[r][c][q[c]]--;rem[r][c]++;}
    if(res){if(res==1)l0[r][i]=l;return res;}
  }
  return 0;
}
int canon(int a,int b,int c){int best=1<<30;
  for(int s=0;s<M;s++){int x[3]={a/9*9+(a%9+s)%9,b/9*9+(b%9+s)%9,c/9*9+(c%9+s)%9};
    for(int i=0;i<3;i++)for(int j=i+1;j<3;j++)if(x[j]<x[i]){int t=x[i];x[i]=x[j];x[j]=t;}
    int code=x[0]*729+x[1]*27+x[2];if(code<best)best=code;}return best;}
int design(int r){ R=r;
  for(;;){
    for(int i=0;i<39;i++)bud[i]=1;
    int n=0,guard=0;
    while(n<4&&guard<1000){guard++;int u=rnd()%M,v=rnd()%M;int a=12+u,b=21+v,c=30+md(v-u);if(bud[a]<1||bud[b]<1||bud[c]<1)continue;bud[a]--;bud[b]--;bud[c]--;inv[r][n][0]=u;inv[r][n][1]=v;n++;}
    if(n<4)continue;
    nodes=0;cap=2000000; if(dfs(0,0)==1)return 1;
  }
}
int main(int argc,char**argv){
  rs=strtoull(argv[1],0,10)*0x9E3779B97F4A7C15ULL+1;
  for(int p=0;p<27;p++)for(int q=0;q<27;q++){if(p==q)continue;int c=p/9,x=p%9,c2=q/9,x2=q%9;
    if(c==c2){int d=md(x2-x);if(d>4)d=9-d;didx[p][q]=c*4+d-1;}
    else if(c<c2){int pi=c==0?(c2==1?0:1):2;didx[p][q]=12+pi*9+md(x2-x);}
    else{int pi=c2==0?(c==1?0:1):2;didx[p][q]=12+pi*9+md(x-x2);}}
  for(long tries=1;;tries++){
    design(0);design(1);
    int codes[26],n=0,ok=1;
    for(int r=0;r<2;r++){for(int t=0;t<9;t++)codes[n++]=canon(wk[r][t][0],wk[r][t][1],wk[r][t][2]);for(int i=0;i<4;i++)codes[n++]=canon(0,9+inv[r][i][0],18+inv[r][i][1]);}
    for(int i=0;i<26;i++)for(int j=i+1;j<26;j++)if(codes[i]==codes[j])ok=0;
    if(!ok)continue;
    int lr=0;
    for(int rep=0;rep<10&&lr!=1;rep++){memset(cnt,0,sizeof cnt);for(int r=0;r<2;r++)for(int c=0;c<3;c++)rem[r][c]=13;ln=0;lcap=5000000;lr=ldfs(0,0,0);}
    fprintf(stderr,"try %ld lane result %d\n",tries,lr);
    if(lr!=1)continue;
    printf("SOLUTION\n");
    for(int r=0;r<2;r++){
      for(int i=0;i<9;i++){int out[27];for(int t=0;t<9;t++){int l=(lane[r][t]+i)%9;for(int j=0;j<3;j++){int p=wk[r][t][j];out[l*3+j]=p/9*9+(p%9+i)%9+1;}}for(int k=0;k<27;k++)printf("%d ",out[k]);printf("\n");}
      for(int k=0;k<4;k++){int out[27];for(int j=0;j<9;j++){int l=(l0[r][k]+j)%9;out[l*3]=j+1;out[l*3+1]=9+(inv[r][k][0]+j)%9+1;out[l*3+2]=18+(inv[r][k][1]+j)%9+1;}for(int q=0;q<27;q++)printf("%d ",out[q]);printf("\n");}
    }
    return 0;
  }
}
