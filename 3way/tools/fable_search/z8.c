// v24: Z_8 x 3 classes, 2 base weeks developed + 7 invariant weeks; lanes rotate with group.
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
static uint64_t rs;
static inline uint32_t rnd(){rs^=rs<<13;rs^=rs>>7;rs^=rs<<17;return (uint32_t)(rs>>11);}
int didx[24][24], bud[36];
int wk[2][8][3]; int inv[7][2];
long nodes, cap;
static int take(int a,int b,int c){
  int i=didx[a][b],j=didx[a][c],k=didx[b][c];
  bud[i]--;bud[j]--;bud[k]--;
  if(bud[i]<0||bud[j]<0||bud[k]<0){bud[i]++;bud[j]++;bud[k]++;return 0;}
  return 1;
}
static void give(int a,int b,int c){bud[didx[a][b]]++;bud[didx[a][c]]++;bud[didx[b][c]]++;}
int lanesolve();
int found=0;
int dfs(int w,int t,uint32_t used){
  if(++nodes>cap) return -1;
  if(t==8){
    if(w==0) return dfs(1,0,0);
    return 1;
  }
  int p=0; while(used>>p&1)p++;
  int cq[300],cr[300],n=0;
  for(int q=p+1;q<24;q++) if(!(used>>q&1)) for(int r=q+1;r<24;r++) if(!(used>>r&1)){cq[n]=q;cr[n]=r;n++;}
  for(int i=n-1;i>0;i--){int j=rnd()%(i+1);int x=cq[i];cq[i]=cq[j];cq[j]=x;x=cr[i];cr[i]=cr[j];cr[j]=x;}
  for(int i=0;i<n;i++){
    int q=cq[i],r=cr[i];
    if(!take(p,q,r))continue;
    wk[w][t][0]=p;wk[w][t][1]=q;wk[w][t][2]=r;
    int res=dfs(w,t+1,used|1u<<p|1u<<q|1u<<r);
    give(p,q,r);
    if(res)return res;
  }
  return 0;
}
// lanes
int cnt[3][8]; int lane[2][8], l0[7]; long ln, lcap;
int ldfs(int it,int m0,int m1){
  if(++ln>lcap)return -1;
  if(it==23)return 1;
  int st=rnd()&7;
  if(it<16){
    int w=it>>3,t=it&7; int m=w?m1:m0;
    for(int k=0;k<8;k++){int l=(st+k)&7; if(m>>l&1)continue; if(it==0&&k>0)break;
      if(it==0)l=0;
      int ok=1,j;
      for(j=0;j<3;j++){int p=wk[w][t][j];int c=p>>3,y=p&7; if(++cnt[c][(l-y)&7]>3)ok=0;}
      if(ok){lane[w][t]=l; int r=ldfs(it+1,w?m0:m0|1<<l,w?m1|1<<l:m1); if(r){for(j=0;j<3;j++){int p=wk[w][t][j];cnt[p>>3][(l-(p&7))&7]--;}return r;}}
      for(j=0;j<3;j++){int p=wk[w][t][j];cnt[p>>3][(l-(p&7))&7]--;}
    }
    return 0;
  }
  int i=it-16,u=inv[i][0],v=inv[i][1];
  for(int k=0;k<8;k++){int l=(st+k)&7;
    if(cnt[0][l]>=3||cnt[1][(l-u)&7]>=3||cnt[2][(l-v)&7]>=3)continue;
    cnt[0][l]++;cnt[1][(l-u)&7]++;cnt[2][(l-v)&7]++;
    l0[i]=l; int r=ldfs(it+1,m0,m1);
    cnt[0][l]--;cnt[1][(l-u)&7]--;cnt[2][(l-v)&7]--;
    if(r)return r;
  }
  return 0;
}
int canon(int a,int b,int c){ // min code over translates
  int best=1<<30;
  for(int s=0;s<8;s++){int x[3]={ (a&~7)|((a+s)&7),(b&~7)|((b+s)&7),(c&~7)|((c+s)&7)};
    for(int i=0;i<3;i++)for(int j=i+1;j<3;j++)if(x[j]<x[i]){int t=x[i];x[i]=x[j];x[j]=t;}
    int code=x[0]*576+x[1]*24+x[2]; if(code<best)best=code;}
  return best;
}
int main(int argc,char**argv){
  rs=argc>1?strtoull(argv[1],0,10)*0x9E3779B97F4A7C15ULL+1:88172645463325252ULL;
  int want=argc>2?atoi(argv[2]):1;
  for(int p=0;p<24;p++)for(int q=0;q<24;q++){ if(p==q)continue;
    int c=p>>3,x=p&7,c2=q>>3,x2=q&7;
    if(c==c2){int d=(x2-x)&7; if(d>4)d=8-d; didx[p][q]=c*4+d-1;}
    else if(c<c2){int pi=c==0?(c2==1?0:1):2; didx[p][q]=12+pi*8+((x2-x)&7);}
    else {int pi=c2==0?(c==1?0:1):2; didx[p][q]=12+pi*8+((x-x2)&7);}
  }
  long tries=0,designs=0;
  while(found<want){
    tries++;
    for(int i=0;i<36;i++)bud[i]=2; for(int c=0;c<3;c++)bud[c*4+3]=1;
    int n=0,guard=0;
    while(n<7&&guard<1000){guard++; int u=rnd()&7,v=rnd()&7; int dup=0; for(int i=0;i<n;i++)if(inv[i][0]==u&&inv[i][1]==v)dup=1; if(dup)continue;
      int a=12+u,b=20+v,c=28+((v-u)&7); if(bud[a]<1||bud[b]<1||bud[c]<1)continue; bud[a]--;bud[b]--;bud[c]--; inv[n][0]=u;inv[n][1]=v;n++;}
    if(n<7)continue;
    nodes=0;cap=300000;
    int r=dfs(0,0,0);
    if(r!=1)continue;
    designs++;
    // distinct triple orbits
    int codes[16],ok=1; for(int w=0;w<2;w++)for(int t=0;t<8;t++)codes[w*8+t]=canon(wk[w][t][0],wk[w][t][1],wk[w][t][2]);
    for(int i=0;i<16;i++)for(int j=i+1;j<16;j++)if(codes[i]==codes[j])ok=0;
    for(int i=0;i<16;i++)for(int j=0;j<7;j++)if(codes[i]==canon(0,8+inv[j][0],16+inv[j][1]))ok=0;
    if(!ok)continue;
    int lr=0;
    for(int rep=0;rep<20&&lr!=1;rep++){memset(cnt,0,sizeof cnt);ln=0;lcap=2000000;lr=ldfs(0,0,0);}
    fprintf(stderr,"tries %ld designs %ld lane result %d\n",tries,designs,lr);
    if(lr!=1)continue;
    found++;
    // output weeks
    int weeks[23][24];
    for(int w=0;w<2;w++)for(int i=0;i<8;i++)for(int t=0;t<8;t++){int l=(lane[w][t]+i)&7; for(int j=0;j<3;j++){int p=wk[w][t][j]; weeks[w*8+i][l*3+j]=((p&~7)|((p+i)&7))+1;}}
    for(int k=0;k<7;k++)for(int j=0;j<8;j++){int l=(l0[k]+j)&7; weeks[16+k][l*3]=(j&7)+1; weeks[16+k][l*3+1]=8+((inv[k][0]+j)&7)+1; weeks[16+k][l*3+2]=16+((inv[k][1]+j)&7)+1;}
    printf("SOLUTION\n");
    for(int w=0;w<23;w++){for(int i=0;i<24;i++)printf("%d ",weeks[w][i]);printf("\n");}
    fflush(stdout);
  }
}
