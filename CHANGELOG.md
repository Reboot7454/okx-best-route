# Changelog

所有 notable changes 都将记录在此文件。

格式基于 [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)，
版本号遵循 [Semantic Versioning](https://semver.org/lang/zh-CN/)。

## [Unreleased]

### Planned
- [ ] 支持更多链（添加自定义RPC）
- [ ] 批量报价功能
- [ ] 价格监控提醒

## [1.0.0] - 2025-03-10

### Added
- ✅ 独立版本发布，零依赖设计
- ✅ 内嵌 OKX DEX API 客户端
- ✅ 支持 10+ 链（Ethereum, Base, BSC, Arbitrum等）
- ✅ 智能路由聚合 10+ DEX
- ✅ MEV 保护检测
- ✅ 安全检测（蜜罐、税费）
- ✅ 完整的命令行接口
- ✅ 详细的 README 文档
- ✅ 一键安装脚本

### Changed
- 从依赖 `okx-dex` skill 改为完全独立运行
- 优化 Gas 估算逻辑

### Fixed
- 修复 install.sh 中的 clone 地址错误
- 澄清 API 类型说明（Web3 DEX vs 交易所 API）

## [0.1.0] - 2025-03-09

### Added
- 初始版本发布
- 基础报价功能
- 支持 Ethereum 和 Base 链

