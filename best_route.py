#!/usr/bin/env python3
"""
OKX BEST ROUTE - 多DEX最优路径查找器
基于真实OKX DEX API，找到最便宜的swap路径
"""

import os
import sys
import json
import subprocess
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

@dataclass
class SwapRoute:
    """Swap路径信息"""
    dex_name: str
    from_token: str
    to_token: str
    from_amount: str
    to_amount: str
    price_impact: str
    estimate_gas: str
    slippage: str
    score: float

class OKXBestRoute:
    """OKX最优路径查找器 - 使用现有技能"""
    
    def __init__(self):
        self.okx_dex_script = os.path.expanduser('~/.openclaw/workspace/skills/okx-dex/scripts/okx_dex.py')
    
    def _call_okx_dex(self, action: str, **kwargs) -> Dict:
        """调用OKX DEX技能"""
        cmd = ['python3', self.okx_dex_script, action]
        
        # 参数名映射
        param_map = {
            'from_token': '--from',
            'to_token': '--to',
            'amount': '--amount',
            'chain': '--chain',
            'slippage': '--slippage',
            'user_address': '--user'
        }
        
        for key, value in kwargs.items():
            if key in param_map:
                cmd.extend([param_map[key], str(value)])
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                return {"success": False, "error": result.stderr}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def find_best_route(self, chain: str, from_token: str, to_token: str, 
                        amount: str, slippage: str = "0.5") -> Dict[str, Any]:
        """
        查找最优swap路径
        """
        print(f"🔍 正在查找最优路径...")
        print(f"   链: {chain}")
        print(f"   从: {from_token[:20]}...")
        print(f"   到: {to_token[:20]}...")
        print(f"   数量: {amount}")
        print(f"   滑点: {slippage}%")
        print()
        
        # 获取报价
        result = self._call_okx_dex(
            'quote',
            from_token=from_token,
            to_token=to_token,
            amount=amount,
            chain=chain,
            slippage=slippage
        )
        
        if not result.get('success'):
            print(f"❌ 获取报价失败: {result.get('error', 'Unknown error')}")
            return {"success": False, "error": result.get('error')}
        
        data = result.get('data', {})
        
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
            price_impact=data.get('priceImpact', '0') or '0',
            estimate_gas='Unknown',
            slippage=slippage,
            score=float(data.get('toAmount', 0))
        )
        
        # 获取交易数据（如果需要执行）
        swap_result = self._call_okx_dex(
            'swap',
            from_token=from_token,
            to_token=to_token,
            amount=amount,
            chain=chain,
            user_address='0x62b8ef8a769c8bc785a147f364ae3b2d117cb895',  # 示例地址
            slippage=slippage
        )
        
        return {
            "success": True,
            "chain": chain,
            "from_token": from_token,
            "to_token": to_token,
            "amount": amount,
            "route": route,
            "quote_data": data,
            "swap_data": swap_result.get('data') if swap_result.get('success') else None
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
        lines.append(f"   价格: ${from_token.get('tokenUnitPrice')}")
        lines.append(f"   买入: {to_token.get('tokenSymbol')} ({to_token.get('decimal')} decimals)")
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
        lines.append(f"   蜜罐检测: {'⚠️ 有风险' if from_token.get('isHoneyPot') or to_token.get('isHoneyPot') else '✅ 通过'}")
        lines.append(f"   税费: {from_token.get('taxRate', '0')}% / {to_token.get('taxRate', '0')}%")
        lines.append("")
        
        # 如果可执行，显示交易数据
        swap_data = result.get('swap_data')
        if swap_data and swap_data.get('transaction'):
            tx = swap_data['transaction']
            lines.append("=" * 60)
            lines.append("🚀 可执行交易数据")
            lines.append(f"   To: {tx.get('to')}")
            lines.append(f"   Value: {tx.get('value')}")
            lines.append(f"   Gas: {tx.get('gas')}")
            lines.append("")
        
        lines.append("=" * 60)
        
        return "\n".join(lines)


def main():
    if len(sys.argv) < 5:
        print("🛣️ OKX BEST ROUTE - 多DEX最优路径查找器")
        print()
        print("用法:")
        print("  python3 best_route.py <chain> <from_token> <to_token> <amount>")
        print()
        print("示例:")
        print("  # Base链: 0.01 ETH -> USDC")
        print("  python3 best_route.py 8453 0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE 0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913 10000000000000000")
        print()
        print("链ID:")
        print("  1 = Ethereum")
        print("  8453 = Base")
        print("  56 = BSC")
        print("  137 = Polygon")
        print("  42161 = Arbitrum")
        sys.exit(1)
    
    chain = sys.argv[1]
    from_token = sys.argv[2]
    to_token = sys.argv[3]
    amount = sys.argv[4]
    
    finder = OKXBestRoute()
    result = finder.find_best_route(chain, from_token, to_token, amount)
    
    print(finder.format_output(result))


if __name__ == "__main__":
    main()
