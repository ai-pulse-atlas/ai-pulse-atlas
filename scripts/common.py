"""共用：读取分类、实体、事件。"""
import json, pathlib, yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent


def load_taxonomy():
    return yaml.safe_load((ROOT / "data" / "taxonomy.yaml").read_text(encoding="utf-8"))


def load_entities():
    return yaml.safe_load((ROOT / "data" / "entities.yaml").read_text(encoding="utf-8"))


def org_alias_map(ent):
    m = {}
    for name, info in (ent.get("orgs") or {}).items():
        m[name.lower()] = name
        for a in (info or {}).get("aliases", []) or []:
            m[str(a).lower()] = name
    return m


def model_alias_map(ent):
    m = {}
    for fam, aliases in (ent.get("models") or {}).items():
        m[fam.lower()] = fam
        for a in aliases or []:
            m[str(a).lower()] = fam
    return m


def iter_events(track="events"):
    """逐行产出 (文件路径, 行号, 解析结果, 异常)；缺失目录视为空。"""
    if track not in ("events", "tech"):
        raise ValueError(f"未知数据线：{track}")
    for f in sorted((ROOT / "data" / track).glob("*.jsonl")):
        for i, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            try:
                yield f, i, json.loads(line), None
            except Exception as e:  # noqa
                yield f, i, None, e
