# ARM架构部署指南

本指南帮助您在ARM架构的服务器（例如Oracle Cloud ARM实例）上部署SCC刑事案例RAG聊天机器人。

## 前提条件

1. 安装Docker和Docker Compose：
```bash
# 安装必要依赖
sudo dnf install -y yum-utils device-mapper-persistent-data lvm2

# 添加Docker仓库
sudo dnf config-manager --add-repo=https://download.docker.com/linux/centos/docker-ce.repo

# 安装Docker（对ARM架构使用--nobest）
sudo dnf install -y --nobest docker-ce docker-ce-cli containerd.io

# 启动Docker
sudo systemctl start docker
sudo systemctl enable docker

# 安装Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.3/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

## 镜像部署选项

### 选项1: 使用预构建的多架构镜像（推荐）

此选项使用已经推送到Docker Hub的多架构镜像，自动适配ARM架构：

```bash
# 拉取最新镜像
docker pull arnozeng/scc-backend:latest
docker pull arnozeng/scc-frontend:latest

# 创建环境变量文件
cp .env.example .env
# 编辑.env文件添加您的API密钥
nano .env

# 启动服务
docker-compose up -d
```

### 选项2: 在ARM服务器上本地构建镜像

如果您想在ARM服务器上直接构建镜像：

```bash
# 克隆仓库
git clone https://github.com/arnozeng98/scc-criminal-rag.git
cd scc-criminal-rag

# 创建环境变量文件
cp .env.example .env
# 编辑.env文件添加您的API密钥
nano .env

# 在ARM服务器上构建镜像
docker build -t arnozeng/scc-backend:latest-arm64 -f docker/backend.Dockerfile .
docker build -t arnozeng/scc-frontend:latest-arm64 -f docker/frontend.Dockerfile .

# 修改docker-compose.yml中的镜像标签为latest-arm64
# 或者使用以下命令自动替换
sed -i 's/arnozeng\/scc-backend:latest/arnozeng\/scc-backend:latest-arm64/g' docker-compose.yml
sed -i 's/arnozeng\/scc-frontend:latest/arnozeng\/scc-frontend:latest-arm64/g' docker-compose.yml

# 启动服务
docker-compose up -d
```

## 问题排查

### 执行格式错误 (exec format error)

如果看到以下错误：
```
backend-1  | exec /usr/local/bin/uvicorn: exec format error
```

这表示镜像架构与服务器架构不匹配。解决方法：

1. 使用ARM架构的镜像版本或多架构镜像
2. 在ARM服务器上本地重新构建镜像
3. 安装QEMU支持跨架构执行：
```bash
sudo dnf install -y qemu-user-static
```

### 宝塔(aaPanel)SSL证书集成

如果使用宝塔面板管理SSL证书：

1. 确保证书目录存在：
```bash
mkdir -p /www/server/panel/vhost/cert/scc.arnozeng.com
```

2. 在宝塔面板中申请或上传SSL证书
3. 证书路径应该会自动挂载到容器中

## 数据迁移

从x86服务器迁移到ARM服务器时需要复制数据：

```bash
# 在原服务器上打包数据
tar -czf data.tar.gz ./data

# 将数据传输到新服务器
scp data.tar.gz user@new-arm-server:/path/to/project/

# 在新服务器上解压数据
tar -xzf data.tar.gz
``` 