# Task 14: 自动更新与分发

## Feature
实现自动更新、打包分发、安装程序。

## 优先级
P3 - 上线前必须

## 验收标准
- [ ] tauri-plugin-updater 集成
- [ ] 签名密钥管理: `tauri signer generate`
- [ ] 更新检查: 定时/启动时检查新版本
- [ ] 更新通知: UI 提示用户更新
- [ ] 后台下载 + 安装 + 重启
- [ ] 多渠道: stable/beta
- [ ] GitHub Releases 托管更新 manifest
- [ ] macOS: 代码签名 + 公证 (notarization)
- [ ] Windows: NSIS 安装包 + Authenticode 签名
- [ ] Linux: AppImage + .deb + .rpm
- [ ] CI/CD: GitHub Actions 自动构建 + 发布

## 分发格式

| 平台 | 格式 | 签名要求 |
|------|------|----------|
| macOS | .dmg | Apple Developer ID + 公证 |
| Windows | .exe (NSIS) | Authenticode 证书 |
| Linux | .AppImage / .deb | 无 |

## 参考代码
- GitButler: `but-update` crate — 完整的自动更新实现

## 依赖
Task 01 (项目脚手架)

## 预估复杂度
中 — 官方插件成熟，主要是 CI/CD 配置
