# 测试用例生成 - 示例集

> 本文件配套 `testcasegen.md`，集中放置「步间引导示例」与「命令调用示例」。
>
> Agent 使用方式：仅在需要给用户演示输出格式或回顾用法时按需 Read；执行决策不依赖本文件，主文档已含全部判定规则。

---

## 步间引导示例（Phase 2 暂停/继续输出）

### 暂停场景（Step 3 有风险点）

> 需求解析完成，产出 `output/prd_analysis/V4.5_需求解析报告.md`（R0–R11，风险点 8 条）。
>
> `input/knowledge/` 当前含 baseline_cases 7 个、business 5 个、codedesign 4 个，Step 4 将通过索引自动引用。
>
> ✅ **说「继续」即可进入 Step 4（测试概要）。**

### 全自动场景（小文档无阻断项，Step 3→4→5→6 一口气跑完）

> ✅ Step 3 完成（全量，无风险点）→ 自动进入 Step 4。
>
> ✅ Step 4 完成（全量，无冲突）→ 自动进入 Step 5。
>
> ✅ Step 5 完成 → 自动进入 Step 6。
>
> Step 6 完成，已导出 `output/xmind/V2.0_测试用例.xmind`。

### 预算暂停场景（大文档模块循环模式，单步骤内触顶）

> ✅ Step 3 模块循环：已完成模块 01-04/19 的需求解析。
>
> ⏸️ 上下文预算检查：当前项目共 19 个模块，命中 `>12 模块` 档位，本步骤连续处理上限为 4。
> 请新开会话执行 `/testcasegen loc V1.0` 即可自动从模块 05 恢复。

### 预算暂停后恢复场景（新会话自动接续）

> 📋 进度检测：模块循环模式，Step 3 已完成 04/19 个模块，从模块 05 继续。
>
> （模块 05-08 自动处理...）
>
> ⏸️ 上下文预算检查：本步骤已连续处理 4/19 个模块（当前档位上限 = 4），建议新开会话继续。

### 引导禁止事项

- 不得在引导中展示规则路径、`.mdc` 文件名或让用户 @ 规则。

---

## 命令调用示例

```
/testcasegen acflow V4.5                 — 项目=acflow, 迭代=V4.5, 全流程
/testcasegen acflow V4.5 需求解析        — 只做 Step 3
/testcasegen acflow V4.5 --from 4        — 从测试概要开始
/testcasegen acflow                      — 未指定迭代，Agent 自动检测或询问
/testcasegen acflow --only 2.5           — 只刷新知识库索引
/testcasegen acflow 文档转换             — 只做 Step 2（纯格式转换工具）
/testcasegen @input/prd/V4.5/ 需求解析   — 从路径推断项目和迭代，执行 Step 3
```
