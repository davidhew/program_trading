#!/bin/sh

echo "--- 1. 清理本地冲突并拉取代码 ---"
# 强行删除本地产生的 .log 文件，避免 Git 冲突
rm -f *.log

#test
# 强行重置本地分支到远程最新状态
git pull

# 2. 停止并移除旧容器（确保配置更新生效）
docker-compose down

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
    docker-compose build --pull=false dashboard quant_bot

    # 启动所有服务
    docker-compose up -d

    # 打印一下当前容器状态，确认是否两个都在跑
    docker ps

    # 5. 查看日志
    docker logs -f stock_analyzer
fi