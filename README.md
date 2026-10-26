# AI 动态汇总（ai-pulse-atlas）

按影响力分级、可追溯官方来源的 AI 行业事件开放数据集与可视化。

- 在线站点：<https://pulse.daowuu.work>（计划于 M1 上线，TODO：上线后确认）
- 仓库：<https://github.com/ai-pulse-atlas/ai-pulse-atlas>
- 分级规则：[docs/grading.md](docs/grading.md)
- 贡献方式：[CONTRIBUTING.md](CONTRIBUTING.md)（首发阶段只接受 Issue，暂不接受外部 PR）

## 收录什么

每条事件是一条结构化记录：发生日期、机构、自写的中文标题和一句话摘要、分类、影响力等级及理由、来源链接。
- 每条事件至少有 1 个官方来源链接；没有官方原文的事件标为 `verified: confirmed` 或 `rumor`，最高只能定 B 级。
- 标题和摘要都是本项目自写的文字，**不收录**第三方正文、图片或付费墙内容。

## 目录结构

```
data/events/YYYY-MM.jsonl   # 事件库，按 event_date 所在月份分文件，每行一条 JSON
data/manifest.json          # 数据集元信息（schema_version 等）
data/taxonomy.yaml          # 分类（7 大类及子类）与各枚举
data/entities.yaml          # 机构和模型的标准名与别名
docs/grading.md             # S/A/B/C 判定标准、兜底打分、硬规则
schema/event.schema.json    # 事件 JSON Schema（2020-12）
scripts/                    # validate.py / build.py / export_check.py
site/                       # 展示站（Astro + ECharts）
```

## 分类（一级 7 类）

| 大类 | key | 子类 |
|---|---|---|
| 模型 | model | 旗舰与基础模型、开源权重、多模态、推理与Agent能力、评测与榜单 |
| 算力硬件 | compute | 芯片、数据中心与云算力、端侧设备、供应链与出口管制 |
| 产品应用 | product | 消费级产品、开发者工具与API、企业应用、Agent产品 |
| 研究 | research | 新方法与论文、安全与对齐研究 |
| 产业资本 | industry | 融资并购、人事变动、合作、财报 |
| 政策安全 | policy | 监管法规、诉讼与版权、安全事故 |
| 开源社区 | opensource | 爆火项目、框架与基础设施 |

事件中的 `category` / `subcategory` 直接写上表中文名，以 `data/taxonomy.yaml` 为准。

## 影响力分级

| 等级 | 典型事件 | 指数权重 |
|---|---|---|
| **S** | 头部厂商新一代旗舰；明确登顶主要榜单；≥100 亿美元的融资/并购；全行业级监管或出口管制生效 | 8 |
| **A** | 头部厂商重要小版本；二线厂商旗舰；开源 SOTA；新一代芯片；≥10 亿美元融资；主流产品重大功能；重大诉讼判决 | 4 |
| **B** | 常规更新；1 亿–10 亿美元融资；有代表性的开源项目/论文 | 2 |
| **C** | 其余 | 1 |

硬规则：非官方确认（`verified` 不是 `official`）的事件最高 B；拿不准就降一级；每条必须写 `impact_reason`。完整规则见 [docs/grading.md](docs/grading.md)。

## 数据字段

必填：
- `id`：`YYYY-MM-DD-slug`，日期须等于 `event_date`
- `event_date`：北京时间日期
- `title`、`summary`：自写中文，摘要不超过 150 字
- `category`、`subcategory`：见上方分类
- `impact`（S/A/B/C）、`impact_reason`
- `orgs`：机构标准名（见 `data/entities.yaml`）
- `sources`：`[{url, publisher, type}]`，`type` 取 `official` / `media` / `community`
- `verified`：`official` / `confirmed` / `rumor`
- `created_at`、`updated_at`：`YYYY-MM-DDTHH:MM+08:00`

可选：`models`、`product`、`region`（US/CN/EU/Global）、`tags`、`metrics`、`related_ids`、`status`、`impact_history`、`date_basis`、`note`。

`date_basis` 取值：`official_bj`（官方原文有精确时间，换算为北京时间）、`official_local`（官方只写日期，直接用原文日期）、`hn_bj`（官方无日期，取 Hacker News 首次出现时间）、`media_bj`（媒体发布时间换算为北京时间）。

示例：

```json
{"id": "2026-10-01-cloudflare-clef", "event_date": "2026-10-01", "title": "Cloudflare 开源决策模型 Clef 和 Clef-flash", "summary": "开源决策类模型，并提供强化学习微调平台。", "category": "模型", "subcategory": "开源权重", "impact": "B", "impact_reason": "有代表性的开源模型", "orgs": ["Cloudflare"], "sources": [{"url": "https://blog.cloudflare.com/clef-decision-models/", "publisher": "Cloudflare", "type": "official"}], "verified": "official", "created_at": "2026-10-26T12:30:00+08:00", "updated_at": "2026-10-26T12:30:00+08:00", "region": "US", "date_basis": "official_bj"}
```

## 本地校验与构建

环境：Python 3.12、Node.js 22（与 CI 一致）。在仓库根目录执行：

```bash
python3 -m pip install -r requirements.txt   # PyYAML、jsonschema
python3 scripts/export_check.py --self-test  # 防泄漏规则自检
python3 scripts/export_check.py              # 全仓防泄漏扫描，必须零命中
python3 scripts/validate.py --strict         # 必须零错误、零告警
python3 scripts/build.py                     # 生成 build/page-data.json；可加 --asof YYYY-MM-DD 指定截止日（默认北京时间今天）
cd site
npm ci
npm run build                                # 会先自动运行 ../scripts/build.py，再 astro build，产物在 site/dist/
```

## 数据版本

- 事件 schema 版本采用 SchemaVer（`MODEL-REVISION-ADDITION`），写在 `data/manifest.json`。
- 数据集计划每月打一个 tag（如 `data-2026.10`），便于引用固定版本。变更见 [CHANGELOG.md](CHANGELOG.md)。

## 引用

TODO：补充 `CITATION.cff` 后在此给出引用格式。

## 许可证

- 代码：`scripts/`、`site/`、`schema/`（含 `schema/event.schema.json`）及其他代码文件，采用 [MIT](LICENSE)。
- 数据：`data/` 目录（事件记录、`taxonomy.yaml`、`entities.yaml`、`manifest.json`，含自写的 title / summary）以及 `docs/grading.md`，采用 [CC BY 4.0](LICENSE-DATA.md)。
- `sources` 链接指向的第三方页面不在本项目许可范围内。

## 安全与下架

安全问题、权利人下架请求和行为准则举报，一律通过 GitHub 私密漏洞报告提交：<https://github.com/ai-pulse-atlas/ai-pulse-atlas/security>（Security → Report a vulnerability），详见 [SECURITY.md](SECURITY.md)。请勿公开提交 Issue。
