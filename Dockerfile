# 1. 指定基础镜像
FROM python:3.12-slim

# 2. 设置工作目录
WORKDIR /app

# 3. 设置时区环境变量（构建时也会生效）
ENV TZ=Asia/Shanghai

# 1. 先把离线包和依赖清单拷进去
COPY ./packages /app/packages
# 4. 先复制依赖文件（利用 Docker 缓存机制：只要 requirements 不变，就不会重新安装）
COPY requirements.txt .

# 5. 执行安装：使用国内源并信任，--no-cache-dir 缩小镜像体积
# 这种写法会优先寻找本地目录，找不到再去联网
RUN pip install --no-cache-dir \
    --no-index \
    --only-binary=:all: \
    --find-links=/app/packages \
    -r requirements.txt

# 6. 复制当前目录下的所有代码到镜像中
COPY . .

# 7. 容器启动时默认执行的命令
CMD ["python", "jobStarter.py"]