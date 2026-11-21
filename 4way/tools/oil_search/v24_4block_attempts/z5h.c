// points (g,i): g in Z5 or INF(5), i in H (order 4). base week of 6 transversal blocks; develop by Z5 (5 weeks = oil block 0), then by H (4 oil blocks).
#include <stdio.h>
#include <stdlib.h>
int mode,used[24],blk[6][4],msk[12];long nsol,nodes,lim;
static inline int sub(int a,int b){return mode?(a^b):((a-b)&3);}
static int add(int p,int q){ // returns 0 if fails
  int g=p/4,i=p%4,h=q/4,j=q%4,t,pos;
  if(g==h)return 0;
  if(h==5){t=8+sub(j,i);pos=i;}
  else if(g==5){t=8+sub(i,j);pos=j;}
  else{int d=(h-g+5)%5;if(d>2){d=5-d;int x=i;i=j;j=x;}t=(d-1)*4+sub(j,i);pos=i;}
  if(msk[t]>>pos&1)return 0; if(__builtin_popcount(msk[t])>=3)return 0;
  msk[t]|=1<<pos;return 1;}
static void del(int p,int q){int g=p/4,i=p%4,h=q/4,j=q%4,t,pos;
  if(h==5){t=8+sub(j,i);pos=i;}else if(g==5){t=8+sub(i,j);pos=j;}
  else{int d=(h-g+5)%5;if(d>2){d=5-d;int x=i;i=j;j=x;}t=(d-1)*4+sub(j,i);pos=i;}
  msk[t]&=~(1<<pos);}
void rec(int b){
  nodes++;
  if(nsol>=lim)return;
  if(b==6){nsol++;for(int i=0;i<6;i++)printf("%d %d %d %d  ",blk[i][0],blk[i][1],blk[i][2],blk[i][3]);printf("\n");fflush(stdout);return;}
  int f; if(b<4)f=20+b; else{f=0;while(used[f])f++;}
  blk[b][0]=f;used[f]=1;
  for(int x=0;x<20;x++){if(used[x]||(b>=4&&x<f))continue;
    if(!add(f,x))continue;
    for(int y=x+1;y<20;y++){if(used[y])continue;
      int k=0; if(add(f,y)){k=1; if(add(x,y)){k=2;
      for(int z=y+1;z<20;z++){if(used[z])continue;
        int m=0;
        if(add(f,z)){m=1;if(add(x,z)){m=2;if(add(y,z)){m=3;
          used[x]=used[y]=used[z]=1;blk[b][1]=x;blk[b][2]=y;blk[b][3]=z;
          rec(b+1);used[x]=used[y]=used[z]=0;}}}
        if(m>=3)del(y,z);if(m>=2)del(x,z);if(m>=1)del(f,z);
      }}}
      if(k>=2)del(x,y);if(k>=1)del(f,y);
    }
    del(f,x);
  }
  used[f]=0;
}
int main(int argc,char**argv){mode=atoi(argv[1]);lim=atol(argv[2]);rec(0);fprintf(stderr,"mode %d nodes %ld sols %ld\n",mode,nodes,nsol);}
