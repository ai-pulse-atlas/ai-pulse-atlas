# 更新日志

本文件记录数据集、schema 与代码的重要变更。

- 数据集按月打 tag（如 `data-2026.10`）。
- 事件 schema 版本采用 SchemaVer（`MODEL-REVISION-ADDITION`）：只新增可选字段时升 ADDITION；可能使部分历史数据失效时升 REVISION；破坏性变更升 MODEL，并附迁移脚本、在此说明。

## [未发布]

### 新增

- 独立技术模块 `/tech/`：分类、等级、月份筛选和中文空状态；不与 AI 首页混排。
- 技术目录 `data/tech/YYYY-MM.jsonl` 与必填 `tech_category` schema；复用严格北京时间校验，技术来源仅支持 HTTPS，两条数据线隔离校验。
- 构建技术 JSON 与包含计数、月份的 manifest 技术段；空数据导出 `[]`，AI events.json 保持不变。
- 技术分级、Issue 投稿说明与样例单元测试；本次不含种子数据和采集器。

- 首发数据：回填 2026-09-26 至 2026-10-26 共 78 条事件（S 1 / A 19 / B 54 / C 4，已通过 strict 校验和 S/A 级人工抽查）。
- 分类体系 `data/taxonomy.yaml`（version 1，7 大类）、实体表 `data/entities.yaml`、分级规则 `docs/grading.md`。
- 事件 JSON Schema `schema/event.schema.json`（JSON Schema 2020-12）。初始版本 `1-0-0`。
- 校验与构建脚本 `scripts/validate.py`、`scripts/build.py`、防泄漏检查 `scripts/export_check.py`。
- 社区文件：README、CONTRIBUTING、CODE_OF_CONDUCT、SECURITY、LICENSE（MIT）、LICENSE-DATA（CC BY 4.0）、Issue 表单。
