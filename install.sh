#!/bin/bash
# OKX BEST ROUTE 一键安装脚本

echo "🛣️ 安装 OKX BEST ROUTE..."
echo ""

# 检查OpenClaw目录
OPENCLAW_SKILLS="$HOME/.openclaw/workspace/skills"

if [ ! -d "$OPENCLAW_SKILLS" ]; then
    echo "❌ 错误: 未找到OpenClaw目录"
    echo "请确保已安装OpenClaw"
    exit 1
fi

echo "✅ 找到OpenClaw目录"

# 检查okx-dex技能是否存在（依赖）
if [ ! -d "$OPENCLAW_SKILLS/okx-dex" ]; then
    echo "⚠️ 警告: 未找到okx-dex技能"
    echo "请先安装OKX DEX技能，或确保已配置OKX API"
fi

# 进入skills目录
cd "$OPENCLAW_SKILLS"

# 克隆仓库
echo "📥 下载OKX BEST ROUTE..."
if [ -d "okx-best-route" ]; then
    echo "⚠️ 目录已存在，更新代码..."
    cd okx-best-route
    git pull
else
    git clone https://github.com/yourusername/okx-best-route.git
    cd okx-best-route
fi

# 检查API配置
echo ""
echo "🔑 检查API配置..."
CRED_FILE="$HOME/.openclaw/workspace/.credentials/okx-api.txt"

if [ -f "$CRED_FILE" ]; then
    echo "✅ 找到OKX API配置"
else
    echo "⚠️ 未找到OKX API配置"
    echo ""
    echo "请创建配置文件: $CRED_FILE"
    echo "内容格式:"
    echo "OKX_API_KEY=你的API_KEY"
    echo "OKX_SECRET_KEY=你的SECRET_KEY"
    echo "OKX_PASSPHRASE=你的PASSPHRASE"
    echo ""
    echo "获取方式: https://www.okx.com/account/my-api"
fi

# 测试运行
echo ""
echo "🧪 测试运行..."
python3 best_route.py 2>&1 | head -5

echo ""
echo "✅ 安装完成！"
echo ""
echo "使用方法:"
echo "  cd $OPENCLAW_SKILLS/okx-best-route"
echo "  python3 best_route.py 8453 0xE... 0x8335... 10000000000000000"
echo ""
echo "或在OpenClaw中直接使用:"
echo "  python3 ~/.openclaw/workspace/skills/okx-best-route/best_route.py <参数>"
