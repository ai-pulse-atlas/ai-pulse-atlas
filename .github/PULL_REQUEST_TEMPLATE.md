<!--
首发阶段暂不接受外部 PR（计划 M2 开放）。如果你不是维护者，请改为提交 Issue。
-->

## 变更说明

<!-- 简述改了什么；关联 Issue 请写 Closes #编号 -->

## 检查清单

- [ ] 只改了 `data/events/` 下的一个月份文件
- [ ] 已在本地运行 `python3 scripts/validate.py --strict`，零错误、零告警
- [ ] 来源为官方，或已注明 `verified` 与 `publisher`（非官方事件最高 B）
- [ ] 摘要为自写且不超过 150 字
- [ ] 未复制原文句子、正文、图片或付费墙内容
- [ ] 修改已有事件时更新了 `updated_at`；改等级时在 `impact_history` 中追加了记录
