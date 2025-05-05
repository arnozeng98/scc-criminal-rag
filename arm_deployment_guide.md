# SCC Criminal RAG - ARM服务器部署指南

本指南将帮助您在基于ARM架构(aarch64)的服务器上成功部署SCC刑事案例RAG聊天机器人。

## 前提条件

- ARM架构的服务器(例如Oracle Cloud ARM实例)
- CentOS Stream 8或其他Linux发行版
- 互联网连接

## 步骤1: 安装Docker和Docker Compose

根据您使用的是CentOS Stream 8 aarch64，请运行以下命令安装Docker:

```bash
# 更新仓库
sudo sed -i 's/mirrorlist/#mirrorlist/g' /etc/yum.repos.d/CentOS-*.repo
sudo sed -i 's|#baseurl=http://mirror.centos.org|baseurl=https://mirror.stream.centos.org|g' /etc/yum.repos.d/CentOS-*.repo

# 安装必要依赖
sudo dnf install -y yum-utils device-mapper-persistent-data lvm2

# 清理DNF缓存并更新
sudo dnf clean all
sudo dnf makecache

# 添加Docker仓库
sudo dnf config-manager --add-repo=https://download.docker.com/linux/centos/docker-ce.repo

# 安装Docker（对ARM架构使用--nobest）
sudo dnf install -y --nobest docker-ce docker-ce-cli containerd.io

# 启动Docker并设置开机自启
sudo systemctl start docker
sudo systemctl enable docker

# 安装Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.3/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

## 步骤2: 下载项目代码

```bash
# 克隆项目仓库
git clone https://github.com/arnozeng98/scc-criminal-rag.git
cd scc-criminal-rag
```

## 步骤3: 配置环境变量

```bash
# 复制环境变量示例文件
cp .env.example .env

# 编辑.env文件，设置API密钥
nano .env
```

确保设置了以下环境变量:

```
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx
ANTHROPIC_API_KEY=sk-ant-apixx
DOMAIN=scc.arnozeng.com
ADMIN_EMAIL=arnozeng@outlook.com
```

## 步骤4: 部署服务

我们已经构建并推送了多架构Docker镜像(同时支持x86_64和arm64)，可以直接使用:

```bash
# 拉取最新的多架构镜像
docker pull arnozeng/scc-backend:latest
docker pull arnozeng/scc-frontend:latest

# 使用Docker Compose启动服务
docker-compose up -d
```

## 步骤5: 配置宝塔面板SSL证书（如果使用宝塔面板）

如果您使用宝塔面板管理SSL证书:

1. 确保您的域名已解析到服务器IP
2. 在宝塔面板中为域名申请SSL证书
3. 证书会自动存放在`/www/server/panel/vhost/cert/scc.arnozeng.com/`目录
4. Docker容器已配置挂载该目录

## 步骤6: 验证部署

服务启动后，可以通过以下方法验证部署是否成功:

```bash
# 检查容器运行状态
docker ps

# 查看后端容器日志
docker logs -f scc-criminal-rag-backend-1

# 查看前端容器日志
docker logs -f scc-criminal-rag-frontend-1
```

## 常见问题排查

### 1. "exec format error"错误

如果看到以下错误消息:
```
backend-1  | exec /usr/local/bin/uvicorn: exec format error
```

这表示Docker镜像架构与服务器架构不匹配。我们已经构建了多架构镜像，但如果仍然出现问题，可以尝试:

```bash
# 在服务器上查看CPU架构
uname -m

# 确保Docker能够使用正确的架构
docker info | grep Architecture

# 重新拉取镜像
docker pull --platform linux/arm64 arnozeng/scc-backend:latest
docker pull --platform linux/arm64 arnozeng/scc-frontend:latest
```

### 2. 网络连接问题

如果前端无法连接到后端API，检查:

```bash
# 确认后端容器正在运行
docker ps | grep backend

# 测试后端API健康检查
curl http://localhost:8000/health
```

### 3. SSL证书问题

如果SSL证书配置有误，检查:

```bash
# 确认证书文件存在
ls -la /www/server/panel/vhost/cert/scc.arnozeng.com/

# 确认docker-compose.yml中的挂载配置正确
cat docker-compose.yml | grep ssl

# 检查nginx配置
docker exec -it scc-criminal-rag-frontend-1 cat /etc/nginx/conf.d/default.conf
```

## 数据备份与恢复

定期备份您的数据:

```bash
# 备份数据目录
tar -czf scc_data_backup_$(date +%Y%m%d).tar.gz ./data

# 恢复数据
tar -xzf scc_data_backup_20240505.tar.gz
```

祝您部署顺利！如有其他问题，请参考项目文档或提交Issue。 