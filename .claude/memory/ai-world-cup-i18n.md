---
name: ai-world-cup-i18n
description: AI World Cup 项目 i18n 国际化重构方案和同步流程
metadata: 
  node_type: memory
  type: project
  originSessionId: 5b80534f-253e-4a73-9054-d60a77994879
---

## AI World Cup 项目

**仓库**: ileonspace/ai-world-cup (fork from jonaidshianifar/ai-world-cup)
**本地路径**: `/Users/leonli/Desktop/Leon项目/ai-world-cup`
**部署**: Cloudflare Pages

## 核心架构：i18n 国际化

代码与上游保持一致，所有汉化通过 i18n 层实现：
- `website/src/i18n/index.tsx` — I18nProvider + useT hook（React Context）
- `website/src/i18n/zh-CN.ts` — 120+ 条英文→中文翻译映射（UI文本）
- `website/src/lib/teams.tsx` — 队名中文映射 + TeamName组件 + flagFor
- `website/src/lib/venues.ts` — 场馆中文映射
- `website/src/data/reasoning-zh.json` — 1040 条推理中文翻译（运行时切换）
- `website/src/data/reasoningZh.ts` — 推理翻译查找函数

语言切换按钮在 Navbar 右上角，状态持久化到 localStorage (`aiwc-lang`)。

## 同步上游的方式

**方式一（推荐先试）**: GitHub 仓库主页 → "Sync fork" → "Update branch"
**方式二（最稳）**: Actions → "自动同步上游" → "Run workflow"（会跑merge-predictions.js）

工具文件：
- `.github/scripts/merge-predictions.js` — 合并上游数据时直接用上游版本
- `.github/workflows/sync-upstream.yml` — 手动触发（已禁用定时cron）
- `wrangler.toml` — Cloudflare Pages 部署配置

## 翻译策略

- UI文本：代码中用 t('English text') 包裹，翻译在 zh-CN.ts
- 队名：teamNameCN() 自动检查语言，英文模式返回原文
- 推理：英文存 predictions.json，中文存 reasoning-zh.json，运行时切换
- 数据文件：全部用上游原版，不修改

## 上游更新零冲突原因

只添加了 import 和 t()/teamNameCN() 包裹，代码结构与上游一致。
Git merge 时自动合并，不会像之前硬编码中文那样产生大量冲突。
