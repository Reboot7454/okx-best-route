#!/usr/bin/env python3
"""
OKX BEST ROUTE - 多DEX最优路径查找器 (独立版)
基于OKX DEX API，无需外部依赖，一键找到最便宜的swap路径
"""

import os
import sys
import json
import base64
import hmac
import hashlib
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

# ============ OKX DEX API Client (内嵌) ============

OKX_BASE_URL = "https://www.okx.com/api/v6/dex"
OKX_AGGREGATOR_URL = f"{OKX_BASE_URL}/aggregator"

# API凭证 (从环境变量或文件加载)
OKX_API_KEY = os.environ.get('OKX_API_KEY', '')
OKX_API_SECRET = os.environ.get('OKX_API_SECRET', '')
OKX_PASSPHRASE = os.environ.get('OKX_PASSPHRASE', '')

# 链名称映射
CHAIN_NAMES = {
    "1": "Ethereum",
    "2": "BSC", 
    "3": "Polygon",
    "4": "Arbitrum",
    "5": "Optimism",
    "6": "Base",
    "7": "zkSync Era",
    "8": "Linea",
    "9": "Mantle",
    "10": "Avalanche C",
    "8453": "Base",
    "56": "BSC",
    "137": "Polygon",
    "42161": "Arbitrum",
    "10": "Optimism",
    "324": "zkSync Era",
    "59144": "Linea",
    "5000": "Mantle",
    "43114": "Avalanche C",
}


def _load_credentials():
    """从多个位置加载OKX API凭证"""
    global OKX_API_KEY, OKX_API_SECRET, OKX_PASSPHRASE
    
    # 尝试加载路径列表
    paths = [
        os.path.expanduser('~/.openclaw/workspace/.credentials/okx-api.txt'),
        os.path.expanduser('~/.okx-api.txt'),
        './okx-api.txt',
    ]
    
    for cred_file in paths:
        if os.path.exists(cred_file):
            try:
                with open(cred_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith('#'):
                            continue
                        if line.startswith('OKX_API_KEY='):
                            OKX_API_KEY = line.split('=', 1)[1]
                        elif line.startswith('OKX_API_SECRET='):
                            OKX_API_SECRET = line.split('=', 1)[1]
                        elif line.startswith('OKX_PASSPHRASE='):
                            OKX_PASSPHRASE = line.split('=', 1)[1]
                if OKX_API_KEY:
                    return True
            except Exception:
                pass
    return bool(OKX_API_KEY)


# 启动时尝试加载凭证
_load_credentials()


def _get_iso_timestamp() -> str:
    """获取ISO 8601格式时间戳"""
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'


def _generate_signature(timestamp: str, method: str, request_path: str, body: str = "") -> str:
    """生成OKX API签名 (HMAC-SHA256)"""
    if not OKX_API_SECRET:
        return ""
    message = timestamp + method.upper() + request_path + body
    mac = hmac.new(
        OKX_API_SECRET.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    )
    return base64.b64encode(mac.digest()).decode('utf-8')


def _fetch_json(url: str, method: str = "GET", body: str = "") -> Dict:
    """发送HTTP请求并返回JSON"""
    parsed = urllib.parse.urlparse(url)
    request_path = parsed.path
    if parsed.query:
        request_path += "?" + parsed.query
    
    timestamp = _get_iso_timestamp()
    signature = _generate_signature(timestamp, method, request_path, body)
    
    headers = {
        "User-Agent": "OKX-Best-Route/1.0",
        "Accept": "application/json",
        "Content-Type": "application/json" if body else "application/x-www-form-urlencoded",
    }
    
    if OKX_API_KEY:
        headers["OK-ACCESS-KEY"] = OKX_API_KEY
        headers["OK-ACCESS-TIMESTAMP"] = timestamp
        headers["OK-ACCESS-PASSPHRASE"] = OKX_PASSPHRASE
        if signature:
            headers["OK-ACCESS-SIGN"] = signature
    
    req = urllib.request.Request(
        url,
        data=body.encode('utf-8') if body else None,
        headers=headers,
        method=method
    )
    
    import time
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < 2:
                time.sleep(2 * (attempt + 1))
                continue
            raise RuntimeError(f"HTTP {e.code}: {e.read().decode('utf-8')}")
        except Exception as e:
            if attempt < 2:
                time.sleep(2 * (attempt + 1))
                continue
            raise RuntimeError(f"Request failed: {e}")
    
    raise RuntimeError("Max retries exceeded")


def get_supported_chains() -> Dict:
    """获取支持的链列表"""
    url = f"{OKX_AGGREGATOR_URL}/supported/chain"
    response = _fetch_json(url)
    
    if response.get("code") == "0":
        data = response.get("data", [])
        result = []
        for chain in data:
            chain_id = str(chain.get("chainId", ""))
            chain_index = str(chain.get("chainIndex", chain_id))
            result.append({
                "chainId": chain_id,
                "chainIndex": chain_index,
                "name": chain.get("chainName", CHAIN_NAMES.get(chain_id, "Unknown")),
            })
        return {"chains": result}
    return {"chains": [], "raw": response}


def get_tokens(chain_index: str, limit: int = 100) -> Dict:
    """获取指定链支持的代币"""
    url = f"{OKX_AGGREGATOR_URL}/all-tokens?chainIndex={chain_index}&limit={limit}"
    response = _fetch_json(url)
    
    if response.get("code") == "0" and "data" in response:
        tokens = response["data"]
        result = []
        for token in tokens[:limit]:
            result.append({
                "symbol": token.get("tokenSymbol", ""),
                "name": token.get("tokenName", ""),
                "address": token.get("tokenContractAddress", ""),
                "decimals": token.get("decimals", 18),
            })
        return {"tokens": result}
    return {"tokens": [], "raw": response}


def get_swap_quote(
    from_token: str,
    to_token: str,
    amount: str,
    chain_index: str,
    slippage: str = "0.5"
) -> Dict:
    """获取swap报价"""
    params = urllib.parse.urlencode({
        "chainIndex": chain_index,
        "fromTokenAddress": from_token,
        "toTokenAddress": to_token,
        "amount": amount,
        "slippagePercent": slippage,
    })
    url = f"{OKX_AGGREGATOR_URL}/quote?{params}"
    response = _fetch_json(url)
    
    if response.get("code") == "0" and "data" in response:
        quotes = response["data"]
        if quotes and len(quotes) > 0:
            quote = quotes[0]
            return {
                "fromToken": quote.get("fromToken", {}),
                "toToken": quote.get("toToken", {}),
                "fromAmount": quote.get("fromTokenAmount", ""),
                "toAmount": quote.get("toTokenAmount", ""),
                "priceImpact": quote.get("priceImpactPercentage", ""),
                "dex": quote.get("dexName", ""),
            }
    return {"error": "No quote available", "raw": response}


def get_swap_transaction(
    from_token: str,
    to_token: str,
    amount: str,
    chain_index: str,
    user_address: str,
    slippage: str = "0.5"
) -> Dict:
    """获取swap交易数据"""
    params = urllib.parse.urlencode({
        "chainIndex": chain_index,
        "fromTokenAddress": from_token,
        "toTokenAddress": to_token,
        "amount": amount,
        "slippagePercent": slippage,
        "userWalletAddress": user_address,
    })
    url = f"{OKX_AGGREGATOR_URL}/swap?{params}"
    response = _fetch_json(url)
    
    if response.get("code") == "0" and "data" in response:
        data_list = response["data"]
        if data_list and len(data_list) > 0:
            data = data_list[0]
            tx = data.get("tx", {})
            router_result = data.get("routerResult", {})
            
            return {
                "transaction": {
                    "to": tx.get("to", ""),
                    "from": tx.get("from", ""),
                    "data": tx.get("data", ""),
                    "value": tx.get("value", ""),
                    "gas": tx.get("gas", ""),
                    "gasPrice": tx.get("gasPrice", ""),
                },
                "swapInfo": {
                    "fromToken": router_result.get("fromToken", {}),
                    "toToken": router_result.get("toToken", {}),
                    "fromAmount": router_result.get("fromTokenAmount", ""),
                    "toAmount": router_result.get("toTokenAmount", ""),
                    "minReceiveAmount": tx.get("minReceiveAmount", ""),
                    "priceImpact": router_result.get("priceImpactPercent", ""),
                    "slippagePercent": tx.get("slippagePercent", ""),
                }
            }
    return {"error": "Failed to get transaction", "raw": response}


# ============ Best Route Finder ============

@dataclass
class SwapRoute:
    """Swap路径信息"""
    dex_name: str
    from_token: str
    to_token: str
    from_amount: str
    to_amount: str
    price_impact: str
    slippage: str
    score: float


class OKXBestRoute:
    """OKX最优路径查找器 - 独立版"""
    
    def __init__(self):
        if not OKX_API_KEY:
            print("⚠️ 警告: 未找到OKX API配置")
            print("请设置环境变量或创建凭证文件:")
            print("  ~/.openclaw/workspace/.credentials/okx-api.txt")
            print("  ~/.okx-api.txt")
            print("  ./okx-api.txt")
    
    def find_best_route(self, chain: str, from_token: str, to_token: str, 
                        amount: str, slippage: str = "0.5", user_address: str = None) -> Dict[str, Any]:
        """
        查找最优swap路径
        """
        print(f"🔍 正在查找最优路径...")
        chain_name = CHAIN_NAMES.get(str(chain), f"Chain {chain}")
        print(f"   链: {chain_name} ({chain})")
        print(f"   从: {from_token[:20]}...")
        print(f"   到: {to_token[:20]}...")
        print(f"   数量: {amount}")
        print(f"   滑点: {slippage}%")
        print()
        
        # 获取报价
        try:
            data = get_swap_quote(from_token, to_token, amount, chain, slippage)
        except Exception as e:
            print(f"❌ 获取报价失败: {e}")
            return {"success": False, "error": str(e)}
        
        if data.get('error'):
            print(f"❌ 获取报价失败: {data.get('error')}")
            return {"success": False, "error": data.get('error')}
        
        if not data or not data.get('toAmount'):
            print("❌ 未找到可用路径")
            return {"success": False, "error": "No routes found"}
        
        # 构建单条路径结果
        route = SwapRoute(
            dex_name=data.get('dex', 'OKX DEX'),
            from_token=data.get('fromToken', {}).get('tokenSymbol', 'Unknown'),
            to_token=data.get('toToken', {}).get('tokenSymbol', 'Unknown'),
            from_amount=data.get('fromAmount', '0'),
            to_amount=data.get('toAmount', '0'),
            price_impact=data.get('priceImpact', '') or '0',
            slippage=slippage,
            score=float(data.get('toAmount', 0))
        )
        
        # 获取交易数据
        swap_data = None
        if user_address:
            try:
                swap_data = get_swap_transaction(
                    from_token, to_token, amount, chain, user_address, slippage
                )
            except Exception as e:
                print(f"⚠️ 获取交易数据失败: {e}")
        
        return {
            "success": True,
            "chain": chain,
            "from_token": from_token,
            "to_token": to_token,
            "amount": amount,
            "route": route,
            "quote_data": data,
            "swap_data": swap_data
        }
    
    def format_output(self, result: Dict) -> str:
        """格式化输出结果"""
        if not result.get("success"):
            return f"❌ 错误: {result.get('error', 'Unknown error')}"
        
        route = result.get("route")
        data = result.get("quote_data", {})
        
        lines = []
        lines.append("=" * 60)
        lines.append("🛣️ OKX BEST ROUTE - 最优路径分析")
        lines.append("=" * 60)
        lines.append("")
        
        # 代币信息
        from_token = data.get('fromToken', {})
        to_token = data.get('toToken', {})
        
        lines.append("📊 代币信息")
        lines.append(f"   卖出: {from_token.get('tokenSymbol')} ({from_token.get('decimal')} decimals)")
        if from_token.get('tokenUnitPrice'):
            lines.append(f"   价格: ${from_token.get('tokenUnitPrice')}")
        lines.append(f"   买入: {to_token.get('tokenSymbol')} ({to_token.get('decimal')} decimals)")
        if to_token.get('tokenUnitPrice'):
            lines.append(f"   价格: ${to_token.get('tokenUnitPrice')}")
        lines.append("")
        
        # 交易详情
        lines.append("💰 交易详情")
        lines.append(f"   输入: {route.from_amount} {route.from_token}")
        lines.append(f"   输出: {route.to_amount} {route.to_token}")
        lines.append(f"   价格影响: {route.price_impact or 'N/A'}%")
        lines.append("")
        
        # 安全检测
        lines.append("🔒 安全检测")
        is_honeypot = from_token.get('isHoneyPot') or to_token.get('isHoneyPot')
        lines.append(f"   蜜罐检测: {'⚠️ 有风险' if is_honeypot else '✅ 通过'}")
        lines.append(f"   税费: {from_token.get('taxRate', '0')}% / {to_token.get('taxRate', '0')}%")
        lines.append("")
        
        # 如果可执行，显示交易数据
        if result.get('swap_data') and result['swap_data'].get('transaction'):
            tx = result['swap_data']['transaction']
            swap_info = result['swap_data'].get('swapInfo', {})
            lines.append("=" * 60)
            lines.append("🚀 可执行交易数据")
            lines.append(f"   To: {tx.get('to')}")
            lines.append(f"   From: {tx.get('from')}")
            lines.append(f"   Value: {tx.get('value')}")
            lines.append(f"   Gas: {tx.get('gas')}")
            lines.append(f"   Gas Price: {tx.get('gasPrice')}")
            if swap_info.get('minReceiveAmount'):
                lines.append(f"   最少获得: {swap_info.get('minReceiveAmount')}")
            lines.append("")
            lines.append("💡 提示: 使用以上交易数据可通过Web3广播执行兑换")
        
        lines.append("=" * 60)
        
        return "\n".join(lines)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="🛣️ OKX BEST ROUTE - 一键找到最便宜的swap路径",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # Base链: 0.01 ETH -> USDC
  python3 best_route.py 8453 0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE 0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913 10000000000000000

  # Ethereum: 0.008 ETH -> USDC (指定钱包地址获取交易数据)
  python3 best_route.py 1 0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE 0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48 8000000000000000 --user 0xYourAddress

链索引 (Chain Index):
  1  = Ethereum    6  = Base
  2  = BSC         7  = zkSync Era
  3  = Polygon     8  = Linea
  4  = Arbitrum    9  = Mantle
  5  = Optimism    10 = Avalanche C
        """
    )
    
    parser.add_argument("chain", help="链索引 (如: 1=Ethereum, 6=Base, 8453=Base)")
    parser.add_argument("from_token", help="支付代币地址 (如: ETH=0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE)")
    parser.add_argument("to_token", help="获得代币地址")
    parser.add_argument("amount", help="支付金额 (wei/最小单位)")
    parser.add_argument("--slippage", "-s", default="0.5", help="滑点保护百分比 (默认: 0.5%%)")
    parser.add_argument("--user", "-u", dest="user_address", help="用户钱包地址 (用于获取可执行交易数据)")
    
    args = parser.parse_args()
    
    finder = OKXBestRoute()
    result = finder.find_best_route(
        args.chain, 
        args.from_token, 
        args.to_token, 
        args.amount,
        args.slippage,
        args.user_address
    )
    
    print(finder.format_output(result))


if __name__ == "__main__":
    main()
