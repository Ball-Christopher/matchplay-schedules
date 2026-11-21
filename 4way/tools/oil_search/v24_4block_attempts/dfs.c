#include <stdio.h>
#include <stdlib.h>
int okd[23],cnt[12],st[12][3],used[23],blk[6][4];long nsol=0,nodes=0;
static int addpair(int x,int y){int d=(y-x+23)%23,a=x;if(d>11){d=23-d;a=y;}
  if(cnt[d]>=3)return 0;for(int i=0;i<cnt[d];i++)if(!okd[(st[d][i]-a+23)%23])return 0;
  st[d][cnt[d]++]=a;return 1;}
static void delpair(int x,int y){int d=(y-x+23)%23;if(d>11)d=23-d;cnt[d]--;}
void rec(int b){
  nodes++;
  if(b==6){nsol++;for(int i=0;i<6;i++)printf("%d %d %d %d  ",blk[i][0],blk[i][1],blk[i][2],blk[i][3]);printf("\n");fflush(stdout);return;}
  int f=0;while(used[f])f++;
  blk[b][0]=f;used[f]=1;
  for(int x=f+1;x<23;x++){if(used[x])continue;
    if(!addpair(f,x))continue;
    for(int y=x+1;y<23;y++){if(used[y])continue;
      int k=0; if(addpair(f,y)){k=1; if(addpair(x,y)){k=2;
      for(int z=y+1;z<23;z++){if(used[z])continue;
        int m=0;
        if(addpair(f,z)){m=1;if(addpair(x,z)){m=2;if(addpair(y,z)){m=3;
          used[x]=used[y]=used[z]=1;blk[b][1]=x;blk[b][2]=y;blk[b][3]=z;
          rec(b+1);used[x]=used[y]=used[z]=0;}}}
        if(m>=3)delpair(y,z);if(m>=2)delpair(x,z);if(m>=1)delpair(f,z);
      }}}
      if(k>=2)delpair(x,y);if(k>=1)delpair(f,y);
    }
    delpair(f,x);
  }
  used[f]=0;
}
int main(int argc,char**argv){
  int lo=0,hi=0,mask=atoi(argv[1]);
  for(int d=0;d<23;d++){int e=d>11?23-d:d;okd[d]=e>0&&((mask>>e)&1);}
  for(int q=1;q<23;q++)for(int r=q+1;r<23;r++){
    if(!okd[q]||!okd[r]||!okd[r-q])continue;
    // canonical: 0 is one of three; all translations putting another at 0 give dup, fine
    blk[0][0]=-1;blk[0][1]=0;blk[0][2]=q;blk[0][3]=r;
    used[0]=used[q]=used[r]=1;
    addpair(0,q);addpair(0,r);addpair(q,r);
    rec(1);
    delpair(0,q);delpair(0,r);delpair(q,r);used[0]=used[q]=used[r]=0;
    fprintf(stderr,"q=%d r=%d nodes=%ld sols=%ld\n",q,r,nodes,nsol);
  }
}
