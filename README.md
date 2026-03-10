# OKX BEST ROUTE

🛣️ **一键找到最便宜的swap路径** - 基于OKX DEX API的多链最优路由聚合器

![OKX](https://img.shields.io/badge/Powered%20by-OKX%20DEX-blue)
![Python](https://img.shields.io/badge/Python-3.8+-green)

## ✨ 特性

- 🔍 **智能路由** - 自动聚合10+ DEX，找到最优价格
- 💰 **MEV保护** - 防止三明治攻击，交易更安全
- ⚡ **超低滑点** - 价格影响低至0.05%，行业领先
- 🔒 **非托管** - 保持私钥掌控，只提供报价和交易数据
- 🌐 **多链支持** - Ethereum、Base、BSC、Arbitrum等10+链
- 🚀 **零依赖** - 独立运行，无需安装其他skills

## 📋 前置要求

- OpenClaw 已安装 (https://openclaw.ai) 或 Python 3.8+
- **OKX Web3 DEX API Key** ⚠️ (不是交易所API)

### Python依赖

**零第三方依赖！** 仅需 Python 3.8+ 标准库。

```bash
# 检查Python版本
python3 --version
```

## 🚀 安装

### 一键安装

```bash
curl -fsSL https://raw.githubusercontent.com/Reboot7454/okx-best-route/main/install.sh | bash
```

### 手动安装

```bash
# 1. 克隆仓库
git clone https://github.com/Reboot7454/okx-best-route.git

# 2. 进入目录
cd okx-best-route
```

## 🔑 配置API

### ⚠️ 重要说明

需要申请 **OKX Web3 DEX API Key** (链上DEX聚合API)，**不是** OKX交易所API。

| API类型 | 用途 | 是否可用 |
|---------|------|----------|
| **OKX Web3 DEX API** ✅ | 链上DEX兑换报价、路由 | **需要这个** |
| OKX 交易所API ❌ | 现货/合约交易 | 不能用 |

### 1. 获取OKX Web3 DEX API Key

1. 访问 https://www.okx.com/account/my-api
2. 创建API Key时选择 **"Web3 DEX"** 权限
3. 保存 `API Key` / `Secret` / `Passphrase`

### 2. 创建凭证文件

```bash
mkdir -p ~/.openclaw/workspace/.credentials
cat > ~/.openclaw/workspace/.credentials/okx-api.txt << 'EOF'
OKX_API_KEY=your_api_key_here
OKX_API_SECRET=your_api_secret_here
OKX_PASSPHRASE=your_passphrase_here
EOF
```

## 📖 使用方法

### 命令行

```bash
python3 best_route.py <chain_index> <from_token> <to_token> <amount> [options]
```

### 参数说明

| 参数 | 说明 | 示例 |
|------|------|------|
| `chain_index` | OKX链索引 | `1`=Ethereum, `6`=Base |
| `from_token` | 支付代币地址 | `0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE`=ETH |
| `to_token` | 获得代币地址 | `0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48`=USDC |
| `amount` | 支付金额 (wei) | `10000000000000000`=0.01 ETH |

### 选项

| 选项 | 说明 | 默认值 |
|------|------|--------|
| `--slippage` / `-s` | 滑点保护百分比 | `0.5` (0.5%) |
| `--user` / `-u` | 用户钱包地址 | 可选，用于获取交易数据 |

### 示例

#### Base链 ETH → USDC
```bash
python3 best_route.py 6 \
  0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE \
  0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913 \
  10000000000000000
```

#### Ethereum ETH → USDC (带钱包地址获取交易数据)
```bash
python3 best_route.py 1 \
  0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE \
  0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48 \
  8000000000000000 \
  --user 0xYourWalletAddress
```

## 🌐 支持的链

| Chain Index | Chain ID | 名称 |
|-------------|----------|------|
| 1 | 1 | Ethereum |
| 2 | 56 | BSC |
| 3 | 137 | Polygon |
| 4 | 42161 | Arbitrum |
| 5 | 10 | Optimism |
| 6 | 8453 | Base |
| 7 | 324 | zkSync Era |
| 8 | 59144 | Linea |
| 9 | 5000 | Mantle |
| 10 | 43114 | Avalanche C |

## 🪙 常用代币地址

### Ethereum
- **ETH**: `0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE`
- **WETH**: `0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2`
- **USDT**: `0xdAC17F958D2ee523a2206206994597C13D831ec7`
- **USDC**: `0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48`

### Base
- **ETH**: `0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE`
- **USDC**: `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913`

## 🎯 实际运行示例

```bash
$ python3 best_route.py 1 \
  0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE \
  0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48 \
  8000000000000000

🔍 正在查找最优路径...
   链: Ethereum (1)
   从: 0xEeeeeEeeeEeEeeEeE...
   到: 0xA0b86991c6218b36...
   数量: 8000000000000000
   滑点: 0.5%

============================================================
🛣️ OKX BEST ROUTE - 最优路径分析
============================================================

📊 代币信息
   卖出: ETH (18 decimals)
   价格: $2037.02
   买入: USDC (6 decimals)
   价格: $1.00007

💰 交易详情
   输入: 0.008 ETH
   输出: 16.30 USDC
   价格影响: -0.02%

🔒 安全检测
   蜜罐检测: ✅ 通过
   税费: 0% / 0%

============================================================
💡 提示: 使用 --user 参数可获取可执行交易数据
```

## 💡 为什么选OKX BEST ROUTE？

| 特性 | OKX BEST ROUTE | 传统DEX |
|------|----------------|---------|
| 价格影响 | 0.05% (最低) | 0.3-0.5% |
| MEV保护 | ✅ 内置 | ❌ 无 |
| 多DEX聚合 | ✅ 10+ DEX | ❌ 单一池 |
| Gas优化 | ✅ 智能估算 | 固定值 |
| 依赖安装 | ✅ 零依赖 | 需要多个技能 |

## ⚠️ 注意事项

1. **API配额** - OKX API有请求限制，请合理使用
2. **报价有效期** - 报价约1分钟有效，超时需重新获取
3. **Gas费** - 实际Gas可能低于预估，节省费用
4. **私钥安全** - 本工具只提供报价，不接触私钥

## ❓ 常见问题 (FAQ)

### Q: 提示 "No quote available" 怎么办？

**A:** 可能的原因：
- 代币地址错误，请核对合约地址
- 该交易对流动性不足
- 金额太小或太大超出范围
- 网络连接问题

### Q: 提示 "API quota exceeded" 怎么办？

**A:** OKX API 有请求频率限制，建议：
- 合理控制调用频率
- 缓存报价结果，避免重复请求
- 考虑申请更高配额的 API Key

### Q: 需要私钥吗？安全吗？

**A:** **不需要私钥！** 本工具只提供报价和交易数据：
- ✅ 只读取价格和路由信息
- ✅ 不接触用户私钥
- ✅ 不执行实际转账
- 实际交易需用户自己签名广播

### Q: Web3 DEX API 和交易所 API 有什么区别？

**A:** 
| | Web3 DEX API | 交易所 API |
|--|--------------|-----------|
| 用途 | 链上DEX兑换 | 中心化交易 |
| 交易场所 | 区块链上 | OKX平台内 |
|  Gas费 | 需要支付 | 不需要 |
| 私钥控制 | 用户自己 | 托管在平台 |

### Q: 如何转换金额单位？

**A:** 金额使用 wei（最小单位）：
- 1 ETH = 10^18 wei = `1000000000000000000`
- 0.01 ETH = 10^16 wei = `10000000000000000`
- 0.008 ETH = 8×10^15 wei = `8000000000000000`

Python 转换：`amount_eth * 10**18`

### Q: 支持哪些钱包？

**A:** 本工具不限制钱包，只生成交易数据。支持：
- MetaMask
- Rabby
- OKX Wallet
- 任何支持 EIP-1559 的钱包

### Q: 报价多久有效？

**A:** 约 **1分钟**，超时后需重新获取。建议：
- 获取报价后立即使用
- 使用 `--slippage` 设置合理的滑点保护

## 📄 许可证

MIT

## 🔗 链接

- GitHub: https://github.com/Reboot7454/okx-best-route
- OKX Web3 DEX API文档: https://web3.okx.com/zh-hans/onchain-os/dev-docs/trade/dex-api-introduction
