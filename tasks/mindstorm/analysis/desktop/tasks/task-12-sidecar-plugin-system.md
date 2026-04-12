# Task 12: Sidecar 与插件系统

## Feature
实现 Sidecar 进程管理和插件架构，支持 Go/Python/Bun 等外部进程集成。

## 优先级
P2 - 扩展性基础设施

## 验收标准

### Sidecar 管理
- [ ] Sidecar 配置: `sidecars.json` 定义外部进程
- [ ] 进程生命周期: 启动/停止/重启/健康检查
- [ ] 进程通信: stdout/stdin IPC + HTTP localhost + Tauri Events
- [ ] Go sidecar: 编译二进制直接 spawn
- [ ] Python sidecar: PyInstaller 打包或 FastAPI localhost
- [ ] Bun/TS sidecar: 通过 kkrpc 或直接 spawn
- [ ] 日志收集: sidecar 输出统一到应用日志
- [ ] 资源监控: CPU/内存使用追踪

### 插件架构
- [ ] Tauri Plugin 开发模板 (create-tauri-plugin)
- [ ] 自定义插件加载机制
- [ ] 插件 API 抽象: 通用插件接口
- [ ] 插件市场 UI: 浏览/安装/管理插件
- [ ] 插件权限: 按插件控制可访问资源

## 配置格式

```json
{
  "sidecars": [
    {
      "name": "feishu-mcp",
      "command": "./sidecars/feishu-mcp-server",
      "args": [],
      "env": { "FEISHU_APP_ID": "..." },
      "restart": true,
      "healthCheck": { "interval": 30000 }
    }
  ]
}
```

## 参考代码
- Tauri v2 官方 Sidecar API
- Holaboss: Harness 层 — 可扩展 Agent 后端
- Archon: Platform Adapter — 统一接口模式

## 依赖
Task 01 (项目脚手架), Task 04 (Agent Runtime)

## 预估复杂度
中 — Tauri sidecar 是官方功能，插件架构需要设计
