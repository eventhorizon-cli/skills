# 基准测试图表

[English](render-benchmark-charts.md) · [仓库 README](../README.zh-CN.md) · [Skill 说明](../skills/render-benchmark-charts/SKILL.md)

使用 `render-benchmark-charts` 将实测 CSV 数据绘制为 SVG 图表，拆分比较场景，并在放入 README 或报告前检查渲染效果。

## 需要提供的信息

- 包含数值列的实测 CSV，统一计量单位，并保留已有的不确定性数据。
- 各项测量对应的 API、计时操作、提交模式、并发度和容量配置。
- 要展示的比较、输出目录、语言和预期显示尺寸。

Skill 会保留完整测量数据，将筛选条件、标签、坐标轴比例和场景放入临时 JSON 配置。[配置参考](../skills/render-benchmark-charts/references/chart-config.md)提供格式和示例。渲染器支持曲线、固定基线和分组柱状图；柱状图需单独绘制，并使用从零开始的线性纵轴。

## 产物与依赖

内置渲染器生成 SVG 文件。原始 CSV 和可复现配置应与测试详情一起保留，README 只展示简要说明和相关图表。

在临时 Python 环境中安装 `matplotlib`。视觉检查还需要 SVG 栅格化工具，例如 `resvg-py`，以及图片查看工具。绘图依赖应放在目标项目的运行时和构建依赖之外。字体使用本机字体，需核对实际字形来源，包含中文字符；外部提供的字体应保留其许可证。

```bash
python <skill-dir>/scripts/render_benchmark_charts.py \
  --csv /path/results.csv \
  --config /tmp/chart-config.json \
  --output /path/charts
```

## 使用示例

```text
使用 $render-benchmark-charts 将 benchmark/results.csv 绘制为 SVG 图表。
在相同负载配置下比较异步 API，单独展示同步参考。
保留原始测量数据，使用记录的单位和不确定性，并逐张检查视觉效果。
渲染脚本和环境配置放在目标项目之外。
```

## 检查与失败处理

测量缺失或筛选结果有歧义时，渲染器会报错。固定基线使用 `baseline_x` 选中的测量值，曲线及不确定性区间均保持水平。合并近似曲线时，需配置 `equivalent_filters` 和明确的相对容差；出现重叠警告后，应按预期显示尺寸检查图表。

每张交付的 SVG 都要栅格化并查看，检查标签、图例、单位、坐标轴比例、裁切和数据一致性。保存成功或 XML 检查只完成部分验证。渲染或视觉检查不可用时，应说明未完成的检查。使用已有实测数据，微基准测试结论应限定在实际测量的负载范围内。
