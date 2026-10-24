# 维护 Skills

[English](maintaining.md) · [仓库 README](../README.zh-CN.md)

## 权威来源

本机已安装的 Skill 副本是执行行为的权威来源。将本地安装内容同步到仓库时，除非同时有意更新本地来源，否则应保持 Skill 文件逐字节一致。英文和简体中文文档应描述相同的行为。

仓库目录如下：

```text
skills/  Skill 实现
docs/    双语用户指南和维护指南
scripts/ 验证入口
```

## 验证

在仓库根目录创建开发环境并运行仓库验证器：

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-dev.txt
python scripts/validate-skills.py
```

验证器会检查 Skill 元数据、本地 Markdown 链接和锚点、YAML 与 JSON 语法，以及 Python 与 Bash 语法。CI 会在 Pull Request 和推送到 `main` 时运行相同的验证。
