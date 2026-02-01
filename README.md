# 🤖 AI Daily - 每日AI新闻简报

自动化的AI新闻日报生成与部署系统。

## 📋 功能

- 🤖 自动获取AI新闻摘要
- 📅 每天自动生成日报
- 🚀 自动部署到GitHub Pages
- 📖 访问: https://你的用户名.github.io/ai-daily/

## 📁 目录结构

```
ai-daily/
├── .github/workflows/deploy.yml  # GitHub Actions部署配置
├── reports/                       # 日报文件 (Markdown)
│   └── ai-daily-YYYY-MM-DD.md
├── scripts/
│   └── generate_report.py         # 日报生成脚本
├── docs/                          # GitHub Pages静态文件
└── README.md
```

## 🚀 快速开始

### 1. Fork此仓库

### 2. 启用GitHub Pages

1. 进入仓库 **Settings** → **Pages**
2. Source 选择 **GitHub Actions**
3. 保存

### 3. 启用Actions

首次需要手动运行一次：
- 进入 **Actions** 标签
- 点击 **AI Daily Deploy** → **Run workflow**

### 4. 自定义配置

修改 `scripts/generate_report.py` 自定义日报格式。

## ⏰ 自动执行时间

- 每天 **北京时间 00:00** (UTC 16:00)
- 手动触发: 点击 **Actions** → **Run workflow**

## 📝 添加自定义内容

修改 `scripts/generate_report.py` 中的 `TEMPLATE` 变量即可自定义日报模板。

## 🛠️ 技术栈

- Python 3.11+
- GitHub Actions
- GitHub Pages

## 📄 许可证

MIT
