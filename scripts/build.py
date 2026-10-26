#!/usr/bin/env python3
"""生成 build/page-data.json：最近 12 个月事件明细 + 分类×等级×周聚合 + 影响力指数。
影响力指数权重：S=8, A=4, B=2, C=1。周以北京时间周一为起点。
用法：python3 scripts/build.py [--asof YYYY-MM-DD]
"""
import json, sys, datetime as dt
from collections import Counter, defaultdict
from common import ROOT, load_taxonomy, load_entities, iter_events

W = {"S": 8, "A": 4, "B": 2, "C": 1}


def week_start(d):
    return d - dt.timedelta(days=d.weekday())


def main():
    asof = dt.datetime.now(dt.timezone(dt.timedelta(hours=8))).date()
    if "--asof" in sys.argv:
        asof = dt.date.fromisoformat(sys.argv[sys.argv.index("--asof") + 1])
    start = (asof.replace(day=1) - dt.timedelta(days=335)).replace(day=1)  # 约 12 个月
    tax = load_taxonomy(); ent = load_entities()
    evs = []
    for f, ln, ev, exc in iter_events():
        if exc:
            sys.exit(f"{f.name}:{ln} 解析失败，请先运行 validate.py")
        d = dt.date.fromisoformat(ev["event_date"][:10])
        if start <= d <= asof:
            evs.append(ev)
    evs.sort(key=lambda e: (e["event_date"], {"S": 0, "A": 1, "B": 2, "C": 3}[e["impact"]]))

    weeks = sorted({week_start(dt.date.fromisoformat(e["event_date"][:10])).isoformat() for e in evs})
    if evs:  # 补齐空周
        w0 = dt.date.fromisoformat(weeks[0]); w1 = week_start(asof)
        weeks = []
        while w0 <= w1:
            weeks.append(w0.isoformat()); w0 += dt.timedelta(days=7)

    cat_lvl_week = defaultdict(lambda: defaultdict(Counter))  # cat -> week -> impact -> n
    sub_week_idx = defaultdict(Counter)                       # "cat/sub" -> week -> index
    cat_week_idx = defaultdict(Counter)
    cat_cnt, lvl_cnt, org_cnt = Counter(), Counter(), Counter()
    for e in evs:
        wk = week_start(dt.date.fromisoformat(e["event_date"][:10])).isoformat()
        cat_lvl_week[e["category"]][wk][e["impact"]] += 1
        sub_week_idx[f'{e["category"]}/{e["subcategory"]}'][wk] += W[e["impact"]]
        cat_week_idx[e["category"]][wk] += W[e["impact"]]
        cat_cnt[e["category"]] += 1; lvl_cnt[e["impact"]] += 1
        for o in e["orgs"]:
            org_cnt[o] += 1

    cats = [c["name"] for c in tax["categories"]]
    cat_index_total = {c: sum(cat_week_idx[c].values()) for c in cats}
    hottest = max(cats, key=lambda c: (cat_index_total[c], cat_cnt[c])) if evs else None
    out = {
        "generated_at": dt.datetime.now(dt.timezone(dt.timedelta(hours=8))).isoformat(timespec="seconds"),
        "asof": asof.isoformat(),
        "window": {"start": start.isoformat(), "end": asof.isoformat()},
        "weights": W,
        "taxonomy": [{"name": c["name"], "key": c["key"], "subcategories": c["subcategories"]} for c in tax["categories"]],
        "weeks": weeks,
        "metrics": {
            "total": len(evs),
            "by_impact": {k: lvl_cnt.get(k, 0) for k in "SABC"},
            "by_category": {c: cat_cnt.get(c, 0) for c in cats},
            "index_by_category": cat_index_total,
            "hottest_category": hottest,
            "top_orgs": org_cnt.most_common(12),
        },
        "agg": {
            "category_impact_week": {c: {w: dict(cat_lvl_week[c][w]) for w in weeks if cat_lvl_week[c][w]} for c in cats},
            "category_week_index": {c: [cat_week_idx[c].get(w, 0) for w in weeks] for c in cats},
            "subcategory_week_index": {f"{c['name']}/{s}": [sub_week_idx[f"{c['name']}/{s}"].get(w, 0) for w in weeks]
                                        for c in tax["categories"] for s in c["subcategories"]},
        },
        "events": [{k: e.get(k) for k in ("id", "event_date", "title", "summary", "category", "subcategory", "impact",
                                         "impact_reason", "orgs", "models", "region", "sources", "verified", "status",
                                         "related_ids", "impact_history", "tags") if e.get(k) not in (None, [], "")}
                   for e in evs],
    }
    (ROOT / "build").mkdir(exist_ok=True)
    p = ROOT / "build" / "page-data.json"
    p.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"写入 {p}：{len(evs)} 条事件，{len(weeks)} 周；等级 {dict(lvl_cnt)}；最热分类 {hottest}")


if __name__ == "__main__":
    main()
