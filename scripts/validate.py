#!/usr/bin/env python3
"""事件校验：必填字段、枚举、分类、日期、id 唯一、URL 去重、等级规则；
同厂商+同产品 ±3 天内的疑似重复只告警（WARN），不算错误。
用法：python3 scripts/validate.py [--strict]   (--strict 时告警也算失败)
"""
import re, sys, json, datetime as dt
from jsonschema import Draft202012Validator, FormatChecker
from common import ROOT
from collections import defaultdict
from common import load_taxonomy, load_entities, org_alias_map, model_alias_map, iter_events

REQUIRED = ["id", "event_date", "title", "summary", "category", "subcategory", "impact",
            "impact_reason", "orgs", "sources", "verified", "created_at", "updated_at"]
OPTIONAL = {"models", "region", "tags", "metrics", "related_ids", "status", "impact_history",
            "product", "date_basis", "note", "submitted_by"}
ID_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})-[a-z0-9]+(?:-[a-z0-9]+)*$")
TS_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(:\d{2})?\+08:00$")
URL_RE = re.compile(r"^https?://[^\s]+$")


def norm_url(u):
    u = u.strip()
    u = re.sub(r"^http://", "https://", u)
    u = re.sub(r"#.*$", "", u)
    return u.rstrip("/").lower()


def main():
    strict = "--strict" in sys.argv
    checker = FormatChecker()
    @checker.checks("beijing-time", raises=ValueError)
    def beijing_time(value):
        if not isinstance(value, str):
            return True
        return dt.datetime.fromisoformat(value).utcoffset() == dt.timedelta(hours=8)
    schema = json.loads((ROOT / "schema/event.schema.json").read_text())
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=checker)
    tax = load_taxonomy(); ent = load_entities()
    cats = {c["name"]: set(c["subcategories"]) for c in tax["categories"]}
    en = tax["enums"]
    orgmap = org_alias_map(ent); modmap = model_alias_map(ent)
    shared = {norm_url(u) for u in tax.get("shared_sources", []) or []}
    errors, warns = [], []
    ids, urls = {}, {}
    events = []

    for f, ln, ev, exc in iter_events():
        where = f"{f.name}:{ln}"
        if exc:
            errors.append(f"{where} JSON 解析失败：{exc}"); continue
        schema_errors = list(validator.iter_errors(ev))
        if schema_errors:
            for error in schema_errors:
                field = ".".join(map(str, error.absolute_path)) or "$"
                errors.append(f"{where} schema {field}: {error.message}")
            continue
        eid = ev.get("id", "?")
        tag = f"{where} [{eid}]"
        for k in REQUIRED:
            if k not in ev or ev[k] in (None, "", []):
                errors.append(f"{tag} 缺少必填字段 {k}")
        for k in ev:
            if k not in REQUIRED and k not in OPTIONAL:
                errors.append(f"{tag} 未知字段 {k}")
        m = ID_RE.match(str(ev.get("id", "")))
        if not m:
            errors.append(f"{tag} id 格式应为 YYYY-MM-DD-slug（小写字母数字与连字符）")
        ed = str(ev.get("event_date", ""))
        try:
            d = dt.date.fromisoformat(ed[:10])
            if m and m.group(1) != ed[:10]:
                errors.append(f"{tag} id 日期与 event_date 不一致")
            if f.stem != ed[:7]:
                errors.append(f"{tag} 应存放在 data/events/{ed[:7]}.jsonl")
        except ValueError:
            errors.append(f"{tag} event_date 不是 YYYY-MM-DD（北京时间）"); d = None
        if len(ed) > 10 and not TS_RE.match(ed):
            errors.append(f"{tag} event_date 带时间时必须是 +08:00")
        for k in ("created_at", "updated_at"):
            if k in ev and not TS_RE.match(str(ev[k])):
                errors.append(f"{tag} {k} 必须是 ISO 时间且时区 +08:00")
        cat, sub = ev.get("category"), ev.get("subcategory")
        if cat not in cats:
            errors.append(f"{tag} category 非法：{cat}")
        elif sub not in cats[cat]:
            errors.append(f"{tag} subcategory「{sub}」不属于「{cat}」")
        if ev.get("impact") not in en["impact"]:
            errors.append(f"{tag} impact 非法：{ev.get('impact')}")
        if ev.get("verified") not in en["verified"]:
            errors.append(f"{tag} verified 非法：{ev.get('verified')}")
        if ev.get("verified") != "official" and ev.get("impact") in ("S", "A"):
            errors.append(f"{tag} 非官方确认事件最高 B（当前 {ev.get('impact')}）")
        if "region" in ev and ev["region"] not in en["region"]:
            errors.append(f"{tag} region 非法：{ev['region']}")
        if "status" in ev and ev["status"] not in en["status"]:
            errors.append(f"{tag} status 非法：{ev['status']}")
        if "date_basis" in ev and ev["date_basis"] not in en["date_basis"]:
            errors.append(f"{tag} date_basis 非法：{ev['date_basis']}")
        if not isinstance(ev.get("orgs", []), list):
            errors.append(f"{tag} orgs 必须是数组")
        else:
            for o in ev.get("orgs", []):
                if str(o).lower() not in orgmap:
                    warns.append(f"{tag} 厂商「{o}」不在 entities.yaml，建议补别名")
                elif orgmap[str(o).lower()] != o:
                    errors.append(f"{tag} 厂商「{o}」应写规范名「{orgmap[str(o).lower()]}」")
        srcs = ev.get("sources", [])
        if not isinstance(srcs, list):
            errors.append(f"{tag} sources 必须是数组"); srcs = []
        has_official_src = False
        for s in srcs:
            if not isinstance(s, dict) or not s.get("url") or not s.get("publisher") or s.get("type") not in en["source_type"]:
                errors.append(f"{tag} 来源格式错误：{s}"); continue
            if not URL_RE.match(s["url"]):
                errors.append(f"{tag} URL 非法：{s['url']}")
            if s["type"] == "official":
                has_official_src = True
            nu = norm_url(s["url"])
            if nu in shared:
                continue
            if nu in urls and urls[nu] != eid:
                errors.append(f"{tag} URL 重复（已用于 {urls[nu]}）：{s['url']}")
            urls.setdefault(nu, eid)
        if ev.get("verified") == "official" and not has_official_src:
            errors.append(f"{tag} verified=official 但没有 type=official 的来源")
        for h in ev.get("impact_history", []) or []:
            if not isinstance(h, dict) or h.get("from") not in en["impact"] or h.get("to") not in en["impact"] or not h.get("reason"):
                errors.append(f"{tag} impact_history 条目需含 from/to/at/reason：{h}")
        if eid in ids:
            errors.append(f"{tag} id 重复（首次出现于 {ids[eid]}）")
        ids[eid] = where
        events.append((ev, d, tag))

    allids = set(ids)
    for ev, d, tag in events:
        for r in ev.get("related_ids", []) or []:
            if r not in allids:
                errors.append(f"{tag} related_ids 指向不存在的事件 {r}")

    # 同厂商 + 同产品 ±3 天
    bykey = defaultdict(list)
    for ev, d, tag in events:
        if not d:
            continue
        prods = set()
        for mname in ev.get("models", []) or []:
            prods.add(modmap.get(str(mname).lower(), str(mname)))
        if ev.get("product"):
            prods.add(modmap.get(ev["product"].lower(), ev["product"]))
        for o in ev.get("orgs", [])[:1]:  # 第一个 org 视为主体
            for p in prods:
                bykey[(o, p)].append((d, ev, tag))
    for (o, p), lst in bykey.items():
        lst.sort(key=lambda x: x[0])
        for i in range(len(lst)):
            for j in range(i + 1, len(lst)):
                d1, e1, _ = lst[i]; d2, e2, t2 = lst[j]
                if (d2 - d1).days > 3:
                    break
                linked = e2["id"] in (e1.get("related_ids") or []) or e1["id"] in (e2.get("related_ids") or [])
                if not linked:
                    warns.append(f"{t2} 疑似重复：与 {e1['id']} 同为 {o}/{p}，相差 {(d2-d1).days} 天（若确为不同事件，请互相写入 related_ids）")

    for w in warns:
        print("WARN ", w)
    for e in errors:
        print("ERROR", e)
    print(f"\n共 {len(events)} 条事件；错误 {len(errors)}；告警 {len(warns)}")
    sys.exit(1 if errors or (strict and warns) else 0)


if __name__ == "__main__":
    main()
