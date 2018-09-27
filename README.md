# 配置与部署

## 安装依赖软件

### ubuntu16.04LTS

略。

### go(1.11)

安装go，apt-get安装的是1.6，不满足使用，卸载；百度到方法，从官方下载二进制包(1.11)进行安装；同时将环境变量设置到文件/etc/profile.d/golang.sh：

```shell
# shellcheck shell=sh

export GOROOT=/opt/go
export GOPATH=~/go_workspace
export PATH=$PATH:$GOROOT/bin:$GOPATH/bin

mkdir -p $GOPATH
```

### solar

```go get -u github.com/qtumproject/solar/cli/solar```

### solc

 下载[solc-static-linux](https://github.com/ethereum/solidity/releases/download/v0.4.24/solc-static-linux)并部署到系统中，改名solc，所在目录在$PATH中。

### qtum

```shell
#已从量子链官方fork
git clone https://github.com/danX-4q/qtum.git --recursive
cd qtum

#为我们调研工作创建的分支；基准版本为量子链的v0.14.17；可能将来有多个基准版本
git checkout rd-base-v0.14.17
```

根据《[README.md](https://github.com/danX-4q/qtum/blob/rd-base-v0.14.17/README.md)》的《Build on Ubuntu》章节编译、安装、部署。请注意，configure时指定--prefix。

## 配置qtum软件包环境

前提：qtum在configure时指定--prefix目录${QTUM_PREFIX}

修改global--env/envconfig.py：```QTUM_PREFIX```指向configure时的${QTUM_PREFIX}；```NODEX__QTUM_DATADIR```指向qtum的数据目录；```QTUM_DFT_NODE```默认的节点名称，envconfig.py可在单机部署多个节点，但指定默认节点可简化一些操作。

## 生成环境相关的文件

```shell
cd global--env/ && ./auto-gen.py #需先cd进入目录
```

## 部署环境相关的文件

```shell
cd global--env/ && ./deploy.py #需先cd进入目录
```

部署过程，因为要设置qtum软件包的PATH环境变量，需要输入root的密码。

如果PATH环境有调整，请重新登录shell和桌面；或执行以下命令使单个登录会话更新：

```shell
. /etc/profile.d/qtum-path.sh
```

## 删除部署环境相关的文件

```shell
cd global--env/ && ./distclean.py #需先cd进入目录
```

删除过程，略过qtum软件包的PATH环境变量设置。此脚本一般在重复部署时使用，按需执行。

# 执行场景

## 公共说明

* 目录s[0...n]__xxx，每个目录对应一种场景。s0\_\_genesis仅需在每次部署之后执行一次，它是其它各场景的前置条件。

* 每个场景，执行./run.py，同时输出日志rt-data/run.log；./run.py的go_step_by_step函数，即当前场景下执行的步骤。

* 每个场景，在s0之后，都可独立、多次执行。

## 创世(s0__genesis)

```shell
wrp-qtumd			#启动服务
cd s0__genesis/
chmod +x *.py
./run.py
```

## RPC传输COIN(s1__rpc-transfer-coin)

```shell
cd s1__rpc-transfer-coin/
chmod +x *.py
./run.py
```

## ERC20传输TOKEN(s2__erc20-transfer-token)

```shell
cd s2__erc20-transfer-token/
chmod +x *.py
./run.py
```

## 合约传输COIN(s3__contract-transfer-coin)

```shell
cd s3__contract-transfer-coin/
chmod +x *.py
./run.py
```

## 合约创建合约(s4_contract-inner-create-contract)

待添加

## 合约调用合约(s5_contract-inner-call-contract)

待添加