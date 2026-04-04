#!/bin/sh

# 1. 拉取最新代码
git pull

# 2. 停止并移除旧容器（确保配置更新生效）
docker-compose stop

# 3. 参数解析：判断是否为 test 模式
# 使用 $1 获取脚本后的第一个参数
if [ "$1" == "mode=test" ]; then
    echo "检测到测试模式，准备运行 main.py..."

    # 测试模式通常使用 run，运行完即销毁（--rm），不影响正式容器
    APP_ENV=test docker-compose run --rm quant_bot python main.py

else
    echo "进入生产模式，准备启动全量服务..."

    # 4. 构建并启动
    # --pull=false 确保使用你本地 Mac Mini 上的离线包，不尝试从远程仓库拉取基础镜像
    docker-compose build --pull=false
    docker-compose up -d

    # 5. 查看日志
    docker logs -f stock_analyzer
fi