# Daily Express — 每日速递

> 三站日报，每日精选。游戏、健康、世界，5 分钟跟上步伐。

**总站**：https://nope-gao.github.io/ai-daily-express/

| 分站 | 覆盖范围 |
|------|----------|
| 游戏 & AI & 网安 | 引擎更新、游戏圈、AI 突破、网络安全 |
| 生物 & 永生 & 健康 | 抗衰老、基因治疗、生物技术、健康科普 |
| 世界 & 政治 & 经济 | 国际局势、政治动态、经济趋势、商业 |

## 技术栈

- **内容生成**：Hermes Agent + AI 模型
- **页面**：纯静态 HTML + CSS，极简工作室风格
- **部署**：GitHub Pages（三站共用域名，子目录路由）
- **自动化**：Hermes Cron Job + 微信推送

## 项目结构

```
├── index.html          ← 总站 Hub（三个按钮 → 分站）
├── assets/
│   ├── style.css       ← 总站样式
│   └── images/         ← 共享表情包
├── game/               ← 分站 A
│   ├── index.html
│   ├── template.html
│   ├── assets/style.css
│   └── daily/
├── bio/                ← 分站 B
│   ├── index.html
│   ├── template.html
│   ├── assets/style.css
│   └── daily/
├── world/              ← 分站 C
│   ├── index.html
│   ├── template.html
│   ├── assets/style.css
│   └── daily/
└── deploy.sh           ← 三站遍历部署脚本
```
