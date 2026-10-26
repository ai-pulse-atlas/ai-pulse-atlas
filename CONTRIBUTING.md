# 贡献指南

感谢关注 AI 动态汇总。请先阅读 [README.md](README.md) 和 [docs/grading.md](docs/grading.md)。

## 当前阶段：只接受 Issue

- **首发阶段只开放 Issue**，请通过 Issue 表单提交新事件、定级争议、更正和分类建议。
- **外部 Pull Request 计划在 M2 阶段开放**，在此之前提交的外部 PR 可能被关闭，内容会由维护者转为 Issue 处理。M2 开放时会更新本文。
- 所有参与者须遵守 [行为准则](CODE_OF_CONDUCT.md)。
- 安全问题、权利人下架请求和行为准则举报**不要**公开提交 Issue，请通过 GitHub 私密漏洞报告提交：<https://github.com/ai-pulse-atlas/ai-pulse-atlas/security>（见 [SECURITY.md](SECURITY.md)）。

## Issue 类型

| 表单 | 用途 |
|---|---|
| 新事件 | 提交一条尚未收录的事件：日期、机构、标题、一句话摘要、官方链接（必填）、建议分级与理由 |
| 定级争议 | 对已有事件的等级提出异议：事件 id、当前分级、主张的分级，并引用 grading.md 条款与证据链接 |
| 更正/撤回 | 事实错误、链接失效、重复条目 |
| 分类/实体建议 | 新增机构别名或子类 |

## 收录与写作规范

1. **title 和 summary 必须自写**，不复制原文句子；摘要不超过 150 字。
2. 可以引用官方产品名、模型名和数字指标。
3. 不收录正文、图片、付费墙内容。
4. 每条事件至少有 1 个官方链接；否则须标为 `verified: confirmed` 或 `rumor`，最高定 B 级。
5. 媒体来源只放链接，并注明 `publisher`。
6. `orgs` 使用 `data/entities.yaml` 中的标准名；新机构请先提「分类/实体建议」。
7. 拿不准等级时降一级，并写清 `impact_reason`。

## 修改已有事件

- 只改原记录，不新增重复事件；同时更新 `updated_at`。
- 改等级时在 `impact_history` 中追加一条记录，不删旧值。格式：必填 `from`、`to`、`at`（调整决定时间，`+08:00` 格式）、`reason`；可选 `ref`（依据链接，如争议 Issue）、`by`（`maintainer`/`bot`/`community`）。记录按 `at` 升序且首尾相接，最后一条的 `to` 等于当前 `impact`。
- 同一事件的后续进展（如预览后正式上线）另记一条，用 `related_ids` 双向关联。

## 定级争议流程

1. 使用「定级争议」表单提出 Issue。
2. 维护者在 7 天内依据 grading.md 裁决；规则覆盖不到时，用四维兜底打分。
3. 改级通过提交完成，并在 `impact_history` 留痕。
4. S 级的升降必须由人类维护者批准，自动化账号不能自行合并。
5. 同一事件 30 天内不再受理重复争议。

## 提交 PR 时（M2 起）

- 只改 `data/events/` 下一个月份文件。
- 本地运行 `python3 scripts/validate.py --strict`，零错误、零告警。
- 来源为官方，或已注明 `verified` 与 `publisher`。
- CI 会检查：`validate.py --strict` 与 JSON Schema 校验、id 唯一、URL 归一化去重、±3 天疑似重复（WARN，由维护者确认）、新增链接可达性（只告警不阻断）、文本长度、防泄漏检查。
- 外部 PR 至少需要 1 个审批且 CI 通过才能合并。

## 维护

- 数据目录 `data/` 与 `docs/grading.md` 由 CODEOWNERS 指定的 Owner 最终裁决。Owner 为 @Daowuu。
- 每日数据由自动化账号提交到 main，提交信息带 `[bot]` 前缀；它可以分诊 Issue、给出建议分级，但不合并外部 PR。
