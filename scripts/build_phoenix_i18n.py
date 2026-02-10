#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as _dt
import json
import re
import sys
from pathlib import Path


def _eprint(*args: object) -> None:
    print(*args, file=sys.stderr)


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig", errors="replace")


_VDF_PATH_RE = re.compile(r'"path"\s*"([^"]+)"')
_LOC_LINE_RE = re.compile(
    r'^\s*([A-Za-z0-9_.\-]+)\s*:\s*(?:\d+\s*)?"((?:[^"\\]|\\.)*)"\s*(?:#.*)?$'
)
_REF_RE = re.compile(r"\$([A-Za-z0-9_.\-]+)(?:\|[^$]+)?\$")


def _try_find_steam_root() -> Path | None:
    try:
        import winreg  # type: ignore
    except Exception:
        return None

    keys = [
        (winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam", "SteamPath"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Valve\Steam", "InstallPath"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Valve\Steam", "InstallPath"),
    ]
    for hive, subkey, value_name in keys:
        try:
            with winreg.OpenKey(hive, subkey) as key:
                value, _ = winreg.QueryValueEx(key, value_name)
                if value and isinstance(value, str):
                    p = Path(value)
                    if p.exists():
                        return p
        except Exception:
            continue
    return None


def _iter_steam_library_roots(steam_root: Path) -> list[Path]:
    roots = [steam_root]
    vdf = steam_root / "steamapps" / "libraryfolders.vdf"
    if not vdf.exists():
        return roots

    txt = _read_text(vdf)
    for m in _VDF_PATH_RE.finditer(txt):
        p = Path(m.group(1).replace("\\\\", "\\"))
        if p.exists():
            roots.append(p)

    seen: set[Path] = set()
    uniq: list[Path] = []
    for r in roots:
        rr = r.resolve()
        if rr not in seen:
            seen.add(rr)
            uniq.append(r)
    return uniq


def _try_find_stellaris_dir() -> Path | None:
    steam_root = _try_find_steam_root()
    if not steam_root:
        return None

    for lib in _iter_steam_library_roots(steam_root):
        candidate = lib / "steamapps" / "common" / "Stellaris"
        if candidate.exists():
            return candidate
    return None


def _find_localisation_root(stellaris_dir: Path) -> Path | None:
    for name in ("localisation", "localization"):
        p = stellaris_dir / name
        if p.exists():
            return p
    for p in stellaris_dir.glob("**/localisation"):
        if p.is_dir():
            return p
    for p in stellaris_dir.glob("**/localization"):
        if p.is_dir():
            return p
    return None


def _make_resolver(loc: dict[str, str]):
    resolved: dict[str, str] = {}
    resolving: set[str] = set()

    def resolve_text(text: str) -> str:
        def repl(m: re.Match[str]) -> str:
            key = m.group(1)
            value = resolve_key(key)
            return value if value is not None else m.group(0)

        prev = None
        cur = text
        for _ in range(20):
            if prev == cur:
                break
            prev = cur
            cur = _REF_RE.sub(repl, cur)
        return cur

    def resolve_key(key: str) -> str | None:
        if key in resolved:
            return resolved[key]
        if key in resolving:
            return None
        value = loc.get(key)
        if value is None:
            return None
        resolving.add(key)
        out = resolve_text(value)
        resolving.remove(key)
        resolved[key] = out
        return out

    return resolve_key, resolve_text


def _parse_localisation_dir(lang_dir: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    if not lang_dir.exists():
        return out

    for yml in sorted(lang_dir.rglob("*.yml")):
        txt = _read_text(yml)
        for line in txt.splitlines():
            m = _LOC_LINE_RE.match(line)
            if not m:
                continue
            key = m.group(1)
            raw = m.group(2)
            raw = raw.replace(r"\\", "\\")
            raw = raw.replace(r"\"", '"')
            raw = raw.replace(r"\n", "\n")
            out[key] = raw
    return out


def _load_json(path: Path):
    return json.loads(_read_text(path))


def _walk_tree(node: dict, fn) -> None:
    fn(node)
    children = node.get("children")
    if isinstance(children, list):
        for child in children:
            if isinstance(child, dict):
                _walk_tree(child, fn)


def _collect_nodes(version_dir: Path) -> list[dict]:
    nodes: list[dict] = []

    def push(n: dict) -> None:
        if "key" in n:
            nodes.append(n)

    for filename in ("physics.json", "society.json", "engineering.json"):
        obj = _load_json(version_dir / filename)
        root = obj.get("children", [{}])[0]
        if isinstance(root, dict):
            _walk_tree(root, push)

    anomalies = _load_json(version_dir / "anomalies.json")
    if isinstance(anomalies, list):
        for item in anomalies:
            if isinstance(item, dict) and "key" in item:
                nodes.append(item)
    return nodes


def _desc_keys(key: str) -> list[str]:
    return [
        f"{key}_desc",
        f"{key}_DESC",
        f"{key}_description",
        f"{key}_DESCRIPTION",
    ]


def _build_reverse_value_map(source: dict[str, str]) -> dict[str, str]:
    out: dict[str, str] = {}
    for key, value in source.items():
        if value not in out:
            out[value] = key
    return out


def _safe_phrase(en_text: str, zh_text: str) -> bool:
    source = en_text.strip()
    target = zh_text.strip()
    if not source or not target or source == target:
        return False
    if "$" in source or "$" in target:
        return False
    if "\n" in source or "\n" in target:
        return False
    if len(source) < 4 or len(source) > 120:
        return False
    if not re.search(r"[A-Za-z]", source):
        return False
    if source.lower() in {
        "has", "is", "are", "the", "and", "or", "not",
        "yes", "no", "all", "any", "one", "none", "true", "false",
    }:
        return False
    if re.fullmatch(r"[A-Za-z]{1,4}", source):
        return False
    return True


def _apply_official_phrases(
    line: str,
    phrase_pairs: list[tuple[str, str]],
    type_map: dict[str, str],
) -> str:
    out = line

    out = re.sub(
        r"<b>([^<]+)</b>\s*:",
        lambda m: f"<b>{type_map.get(m.group(1).strip(), m.group(1).strip())}</b>：",
        out,
    )

    for src, dst in phrase_pairs:
        if src in out:
            out = out.replace(src, dst)

    return out


def _apply_dsl_keywords(line: str) -> str:
    out = line
    replacements: list[tuple[str, str]] = [
        (r"\bOne\s+must\s+be\s+true\b", "以下条件至少一个满足"),
        (r"\bAll\s+must\s+be\s+true\b", "以下条件全部满足"),
        (r"\bAll\s+must\s+be\s+false\b", "以下条件全部为否"),
        (r"\bAny\s+Leader\s+in\s+council\b", "内阁中的任意领袖"),
        (r"\bAny\s+owned\s+Leader\b", "任意已拥有领袖"),
        (r"\bAny\s+owned\s+Species\b", "任意已拥有物种"),
        (r"\bAny\s+owned\s+Population\s+Group\b", "任意已拥有人口群体"),
        (r"\bAny\s+Owned\s+Planet\b", "任意已拥有行星"),
        (r"\bAny\s+Neighbor\s+Country\b", "任意邻国"),
        (r"\bAny\s+System\s+within\s+borders\b", "任意境内恒星系"),
        (r"\bFounder\s+Species\b", "创始物种"),
        (r"\bNumber\s+of\s+years\s+since\s+game\s+start\b", "开局后年数"),
        (r"\bNumber\s+of\s+owned\s+planets\s+is\s+greater\s+than\b", "已拥有行星数量大于"),
        (r"\bNumber\s+of\s+owned\s+planets\s+is\s+lower\s+than\b", "已拥有行星数量小于"),
        (r"\bNumber\s+of\s+communications\s+is\s+greater\s+than\b", "已建立通讯数量大于"),
        (r"\bNumber\s+of\s+communications\s+is\s+lower\s+than\b", "已建立通讯数量小于"),
        (r"\bNumber\s+of\s+conditions\s+true\s+greater\s+than\s+or\s+equal\s+to\b", "为真的条件数量大于等于"),
        (r"\bPop\s+count\s+is\s+greater\s+than\s+or\s+equal\s+to\b", "人口数量大于等于"),
        (r"\bPop\s+count\s+is\s+greater\s+than\b", "人口数量大于"),
        (r"\bIs\s+of\s+country\s+type\b", "国家类型为"),
        (r"\bCountry\s+does\s+NOT\s+use\s+biological\s+ships\b", "国家不使用生物舰船"),
        (r"\bCountry\s+uses\s+biological\s+ships\b", "国家使用生物舰船"),
        (r"\bHas\s+Technology\b", "已拥有科技"),
        (r"\bHas\s+policy\b", "已启用政策"),
        (r"\bHas\s+civic\b", "拥有国民理念"),
        (r"\bHas\s+tradition\b", "拥有传统"),
        (r"\bHas\s+ascension\s+perk\b", "拥有飞升天赋"),
        (r"\bDoes\s+NOT\s+have\b", "没有"),
        (r"\bhas\s+trait\b", "拥有特质"),
        (r"\bHas\s+trait\b", "拥有特质"),
        (r"\bin\s+council\b", "在内阁中"),
        (r"\bowned\b", "已拥有"),
        (r"\bmodifier\b", "修正"),
        (r"\bat\s+level\b", "在等级"),
        (r"\bcountry\s+flag\b", "国家标识"),
        (r"\bglobal\s+flag\b", "全局标识"),
        (r"\bHas\s+the\b", "拥有"),
        (r"\bHas\b", "拥有"),
        (r"\bNOT\b", "不"),
        (r"\bIs\s+NOT\b", "不是"),
        (r"\bIs\b", "是"),
        (r"\bAny\b", "任意"),
        (r"\bNo\b", "无"),
    ]

    for pattern, target in replacements:
        out = re.sub(pattern, target, out, flags=re.IGNORECASE)
    return out


def _normalize_mixed_line(line: str) -> str:
    out = line

    dynamic_token_map = {
        "[GetTechnicianSwapPluralWithIcon]": "£job_technician£技工岗位",
        "[GetFarmerSwapPluralWithIcon]": "£job_farmer£农夫岗位",
        "[GetMinerSwapPluralWithIcon]": "£job_miner£矿工岗位",
        "[GetResearcherPluralWithIcon]": "£job_researcher£研究人员岗位",
        "[GetFoundrySwapPluralWithIcon]": "£job_foundry£铸造岗位",
        "[GetFactorySwapPluralWithIcon]": "£job_artisan£工匠岗位",
        "[technician.GetIcon]": "£job_technician£",
        "[farmer.GetIcon]": "£job_farmer£",
        "[miner.GetIcon]": "£job_miner£",
        "[foundry.GetIcon]": "£job_foundry£",
        "[GetArtisanIcon]": "£job_artisan£",
        "[GetArtisan]": "工匠",
        "[GetSpecialist]": "专家",
        "[GetWorker]": "劳工",
        "[GetCrimeDeviancy]": "犯罪度/反常度",
        "[GetTechnicianPlural]": "技工岗位",
        "[GetFarmerPlural]": "农夫岗位",
        "[GetMinerPlural]": "矿工岗位",
        "[GetAlloyProducer]": "铸造工岗位",
        "[GetAlloyProducerPlural]": "铸造工岗位",
        "[Get技工复数形式]": "技工岗位",
        "[Get农夫复数形式]": "农夫岗位",
        "[Get矿工复数形式]": "矿工岗位",
        "[Get合金Producer]": "铸造工岗位",
        "[Get合金Producer复数形式]": "铸造工岗位",
        "[Get技工Swap复数形式WithIcon]": "£job_technician£技工岗位",
        "[Get农夫Swap复数形式WithIcon]": "£job_farmer£农夫岗位",
        "[Get矿工Swap复数形式WithIcon]": "£job_miner£矿工岗位",
        "[Get研究人员复数形式WithIcon]": "£job_researcher£研究人员岗位",
        "[Get铸造者Swap复数形式WithIcon]": "£job_foundry£铸造岗位",
        "[Get工厂Swap复数形式WithIcon]": "£job_artisan£工匠岗位",
    }
    for source, target in dynamic_token_map.items():
        out = out.replace(source, target)
    out = re.sub(r"\[Get([^\]]+?)Icon\]\s*", "", out)
    out = re.sub(r"\[Get([^\]]+?)\]", r"\1", out)
    out = re.sub(r"\[Get([^\]]+?)Swap复数形式WithIcon\]", r"\1岗位", out)
    out = re.sub(r"\[Get([^\]]+?)复数形式WithIcon\]", r"\1岗位", out)
    out = re.sub(r"\[Get([^\]]+?)SwapPluralWithIcon\]", r"\1岗位", out)
    out = re.sub(r"\[Get([^\]]+?)PluralWithIcon\]", r"\1岗位", out)
    out = re.sub(r"\[Get([^\]]+?)复数形式\]", r"\1岗位", out)
    out = re.sub(r"\[Get([^\]]+?)Plural\]", r"\1岗位", out)
    out = re.sub(r"\[Get[^\]]+WithIcon\]", "岗位", out)

    resource_token_map = {
        "£能量币£": "£energy£",
        "£矿物£": "£minerals£",
        "£合金£": "£alloys£",
    }
    for source, target in resource_token_map.items():
        out = out.replace(source, target)

    phrase_replacements = [
        (r"\bBuild\s+Cost\b", "建造花费"),
        (r"\bThe\s+Empire\s+Size\s+Effect\s+is\s+modified\s+by\b", "帝国规模效应修正为"),
        (r"\bCan\s+research\s+technology\b", "可研究科技"),
        (r"\bAI\s+Personality\b", "AI性格"),
        (r"\bCrisis\s+level\b", "危机等级"),
        (
            r"\bIs\s+a\s+Member\s+of\s+a\s+spiritualist\s+Federation\s+with\s+perk\s+'A\s+Union\s+of\s+Faith'\b",
            "是拥有“信仰同盟”特典的唯心主义联邦成员",
        ),
        (r"\bASTRAL_RIFT\b", "星界裂隙"),
        (r"\bastral\s+scar\b", "星界裂痕"),
        (r"\bSpecies\s+Leader\s+Exp\s+Gain\b", "物种领袖经验获取"),
        (r"\bEmpire\s+Size\s+from\s+Pops\b", "人口导致的帝国规模"),
        (r"\bUrban\s+District\s+Housing\b", "都市区划住房"),
        (r"\bPop\s+Resource\s+Output\b", "人口资源产出"),
        (r"\bJob\s+Efficiency\b", "岗位效率"),
        (r"\bMajor\s+Capital\s+Buildings\b", "主都建筑"),
        (r"\bUpgraded\s+Capital\s+Buildings\b", "升级首都建筑"),
        (r"\bCapital\s+Buildings\b", "首都建筑"),
        (r"\bMind\s+over\s+Matter\b", "超凡入圣"),
        (r"\bTeachers\s+of\s+the\s+Shroud\b", "虚境导师"),
        (r"\bGenome\s+Mapping\b", "基因测绘"),
        (r"\bHas\s+DLC\s+Astral\s+Planes\b", "拥有 DLC 星界位面"),
        (r"\bHas\s+DLC\s+Biogenesis\b", "拥有 DLC 生体进化"),
        (r"\bHas\s+DLC\s+Megacorp\b", "拥有 DLC 巨型企业"),
        (r"\bHas\s+encountered\s+a\s+", "\u906d\u9047\u8fc7"),
        (r"\bHas\s+encountered\b", "\u906d\u9047\u8fc7"),
        (r"\u62e5\u6709\s+encountered\s+a\s+", "\u906d\u9047\u8fc7"),
        (r"\u62e5\u6709\s+encountered\b", "\u906d\u9047\u8fc7"),
        (r"\bAny\s+Country\s+Relation\b", "\u4efb\u610f\u5e1d\u56fd\u5173\u7cfb"),
        (r"\bHas\s+communication\s+with\s+our\s+Empire\b", "\u5df2\u4e0e\u6211\u56fd\u5efa\u7acb\u901a\u8baf"),
        (r"\bHas\s+communication\s+with\s+our\s+\u5e1d\u56fd\b", "\u5df2\u4e0e\u6211\u56fd\u5efa\u7acb\u901a\u8baf"),
        (r"\bHas\s+communication\s+\u4e0e\u6211\u56fd\b", "\u5df2\u4e0e\u6211\u56fd\u5efa\u7acb\u901a\u8baf"),
        (r"\bHas\s+\u4e0e\u6211\u56fd\u5efa\u7acb\u901a\u8baf\b", "\u5df2\u4e0e\u6211\u56fd\u5efa\u7acb\u901a\u8baf"),
        (r"\bcommunication\s+with\s+our\s+Empire\b", "\u4e0e\u6211\u56fd\u5efa\u7acb\u901a\u8baf"),
        (r"\bcommunication\s+with\s+our\s+\u5e1d\u56fd\b", "\u4e0e\u6211\u56fd\u5efa\u7acb\u901a\u8baf"),
        (r"\bcommunication\s+\u4e0e\u6211\u56fd\b", "\u4e0e\u6211\u56fd\u5efa\u7acb\u901a\u8baf"),
        (r"\u62e5\u6709\s+communication\s+with\s+our\s+Empire", "\u5df2\u4e0e\u6211\u56fd\u5efa\u7acb\u901a\u8baf"),
        (r"\u62e5\u6709\s+communication\s+\u4e0e\u6211\u56fd", "\u5df2\u4e0e\u6211\u56fd\u5efa\u7acb\u901a\u8baf"),
        (r"\u62e5\u6709\s+\u4e0e\u6211\u56fd\u5efa\u7acb\u901a\u8baf", "\u5df2\u4e0e\u6211\u56fd\u5efa\u7acb\u901a\u8baf"),
        (r"\bcommunication\s+\u4e0e\u6211\u56fd\b", "\u4e0e\u6211\u56fd\u5efa\u7acb\u901a\u8baf"),
        (r"\bControls\s+a\s+system\s+with\s+a\s+Gateway\b", "\u63a7\u5236\u6709\u661f\u95e8\u7684\u661f\u7cfb"),
        (r"\bControls\s+a\s+system\s+with\s+a\s+bypass_lgate\b", "\u63a7\u5236\u6709L-\u661f\u95e8\u7684\u661f\u7cfb"),
        (r"\bControls\s+a\s+system\s+with\s+a\s+Natural\s+Wormhole\b", "\u63a7\u5236\u6709\u5929\u7136\u866b\u6d1e\u7684\u661f\u7cfb"),
        (r"\u63a7\u5236\s+a\s+system\s+with\s+a\s+Gateway", "\u63a7\u5236\u6709\u661f\u95e8\u7684\u661f\u7cfb"),
        (r"\u63a7\u5236\s+a\s+system\s+with\s+a\s+\u661f\u95e8", "\u63a7\u5236\u6709\u661f\u95e8\u7684\u661f\u7cfb"),
        (r"\u63a7\u5236\s+a\s+system\s+with\s+a\s+bypass_lgate", "\u63a7\u5236\u6709L-\u661f\u95e8\u7684\u661f\u7cfb"),
        (r"\u63a7\u5236\s+a\s+system\s+with\s+a\s+Natural\s+Wormhole", "\u63a7\u5236\u6709\u5929\u7136\u866b\u6d1e\u7684\u661f\u7cfb"),
        (r"\u63a7\u5236\s+a\s+system\s+with\s+a\s+\u5929\u7136\u866b\u6d1e", "\u63a7\u5236\u6709\u5929\u7136\u866b\u6d1e\u7684\u661f\u7cfb"),
        (r"\bencountered\s+is\s+lower\s+than\b", "\u906d\u9047\u6b21\u6570\u5c0f\u4e8e"),
        (r"\bencountered\s+is\s+greater\s+than\b", "\u906d\u9047\u6b21\u6570\u5927\u4e8e"),
        (r"\bNumber\s+of\s+years\s+since\s+game\s+start\b", "\u5f00\u5c40\u540e\u5e74\u6570"),
        (r"\byears\s+since\s+game\s+start\b", "\u5f00\u5c40\u540e\u5e74\u6570"),
        (r"\u6570\u91cf\s+years\s+since\s+game\s+start\b", "\u5f00\u5c40\u540e\u5e74\u6570"),
        (r"\bNumber\s+of\b", "\u6570\u91cf"),
        (r"\bPop\s+count\b", "\u4eba\u53e3\u6570\u91cf"),
        (r"\blevel\b", "\u7b49\u7ea7"),
        (r"\bin\s+nebula\b", "\u4f4d\u4e8e\u661f\u4e91\u4e2d"),
        (r"\barchetype\b", "\u539f\u578b"),
        (r"\bcommunications\b", "\u901a\u8baf"),
        (r"\ba\s+number\s+of\s+pop\b", "\u4eba\u53e3\u6570\u91cf"),
        (r"\bexists\b", "\u5b58\u5728"),
        (r"\bsubject\b", "\u9644\u5c5e\u56fd"),
        (r"\bwithin\s+borders\b", "\u5883\u5185"),
        (r"\bin\s+construction\b", "\u5728\u5efa\u9020\u4e2d"),
        (r"\bdisabled\b", "\u5df2\u7981\u7528"),
        (r"\bopen\s+ascension\s+perk\s+slots\b", "\u53ef\u7528\u98de\u5347\u5929\u8d4b\u69fd\u4f4d"),
        (r"\bCountry\s+does\s+NOT\s+use\s+biological\s+ships\b", "\u56fd\u5bb6\u4e0d\u4f7f\u7528\u751f\u7269\u8230\u8239"),
        (r"\bCountry\s+uses\s+biological\s+ships\b", "\u56fd\u5bb6\u4f7f\u7528\u751f\u7269\u8230\u8239"),
        (r"\ba\s+bulwark\s+\(specialised\s+subject\)", "\u5821\u5792\u5b50\u56fd"),
        (r"\ba\s+prospectorium\s+\(specialised\s+subject\)", "\u52d8\u63a2\u5b50\u56fd"),
        (r"\ba\s+scholarium\s+\(specialised\s+subject\)", "\u5b66\u8005\u5b50\u56fd"),
        (r"\bLaw\s+None\b", "\u6cd5\u5f8b\uff1a\u65e0"),
        (r"\bLarge\b", "\u5927\u578b"),
        (r"\bMedium\b", "\u4e2d\u578b"),
        (r"\bSmall\b", "\u5c0f\u578b"),
        (r"\bis\s+greater\s+than\s+or\s+equal\s+to\b", "\u5927\u4e8e\u7b49\u4e8e"),
        (r"\bis\s+lower\s+than\s+or\s+equal\s+to\b", "\u5c0f\u4e8e\u7b49\u4e8e"),
        (r"\bis\s+greater\s+than\b", "\u5927\u4e8e"),
        (r"\bis\s+lower\s+than\b", "\u5c0f\u4e8e"),
        (r"\bis\s+equal\s+to\b", "\u7b49\u4e8e"),
        (r"\bis\s+not\s+equal\s+to\b", "\u4e0d\u7b49\u4e8e"),
    ]
    for pattern, target in phrase_replacements:
        out = re.sub(pattern, target, out, flags=re.IGNORECASE)

    token_replacements = [
        ("Blue Eye Beam", "蓝色眼光束"),
        ("Gamma Eye Beam", "伽马眼光束"),
        ("UV Eye Beam", "紫外眼光束"),
        ("X-Ray Eye Beam", "X射线眼光束"),
        ("Orbital Growth Chamber", "轨道生长舱"),
        ("Calamity", "灾厄"),
        ("Danger", "危险"),
        ("Existential Threat", "生存威胁"),
        ("Risk", "风险"),
        ("Cuthuloids", "克苏鲁体"),
        ("Arc Furnace", "电弧熔炉"),
        ("Borehole Pumps", "钻孔泵"),
        ("Equatorial Band", "赤道带"),
        ("Mohole Extractors", "莫霍开采机"),
        ("Dyson Swarm: Constellation", "戴森蜂群：星群"),
        ("Dyson Swarm: Array", "戴森蜂群：阵列"),
        ("Mega Shipyard Core", "巨型船坞核心"),
        ("Mega Shipyard Framework", "巨型船坞框架"),
        ("Mega Shipyard Site", "巨型船坞工地"),
        ("Quantum Catapult Single Array", "量子弹弓单阵列"),
        ("Quantum Catapult Twin Arrays", "量子弹弓双阵列"),
        ("Quantum Catapult Site", "量子弹弓工地"),
        ("Strategic Coordination Center Site", "战略协调中心工地"),
        ("Matter Decompressor Site", "物质解压器工地"),
        ("Grand Archive", "博物天枢"),
        ("Megastructure", "巨型结构"),
        ("Single", "单"),
        ("Twin", "双"),
        ("Ruined", "损毁"),
        ("Accelerated Juvenile Growth Gland", "加速幼体生长腺体"),
        ("Juvenile Growth Gland", "幼体生长腺体"),
        ("Mature Growth Gland", "成熟生长腺体"),
        ("Ancient Energised Carapace", "远古充能甲壳"),
        ("Autonomous Ship Intellect", "自主舰船智能"),
        ("Bio-Swarmer Missiles", "生物蜂群导弹"),
        ("Bio-Whirlwind Missiles", "生物旋风导弹"),
        ("Improved Rangefinder Cluster", "改良测距集群"),
        ("Rapid Incubation Matrix", "快速孵化矩阵"),
        ("Large Nanite Quill Battery", "大型纳米棘刺炮组"),
        ("Medium Nanite Quill Battery", "中型纳米棘刺炮组"),
        ("Small Nanite Quill Battery", "小型纳米棘刺炮组"),
        ("Large Ripper Quill Battery", "大型撕裂棘刺炮组"),
        ("Medium Ripper Quill Battery", "中型撕裂棘刺炮组"),
        ("Small Ripper Quill Battery", "小型撕裂棘刺炮组"),
        ("Large Stormfire Quill Battery", "大型风暴火棘刺炮组"),
        ("Medium Stormfire Quill Battery", "中型风暴火棘刺炮组"),
        ("Small Stormfire Quill Battery", "小型风暴火棘刺炮组"),
        ("Advanced Combat Computer", "先进作战电脑"),
        ("Sapient Combat Computer", "智慧型作战电脑"),
        ("Combat Computer", "作战电脑"),
        ("Bio-Hyperlane Field III", "生物超空间航道场 III"),
        ("Hyper Drive III", "超空间引擎 III"),
        ("NEUROCHIPS", "神经芯片"),
        ("Large UV Beam Projector", "大型紫外光束投射器"),
        ("Medium UV Beam Projector", "中型紫外光束投射器"),
        ("Small UV Beam Projector", "小型紫外光束投射器"),
        ("Starbase", "恒星基地"),
        ("Module", "模块"),
        ("Upgrade", "升级"),
        ("Country", "国家"),
        ("Perk", "特典"),
        ("Array", "阵列"),
        ("Arrays", "阵列"),
        ("Site", "站点"),
        ("Battery", "电池"),
        ("Capacity", "容量"),
        ("Offspring", "后代"),
        ("Quill", "棘刺"),
        ("Sapient", "智慧"),
        ("Nanite", "纳米"),
        ("Ripper", "撕裂"),
        ("Stormfire", "风暴火"),
        ("bypass_lgate", "L-\u661f\u95e8"),
        ("bypass_relay_bypass", "\u4e2d\u7ee7\u5668\u901a\u9053"),
        ("default", "\u5e38\u89c4\u5e1d\u56fd"),
        ("with our \u5e1d\u56fd", "\u4e0e\u6211\u56fd"),
        ("our Empire", "\u6211\u56fd"),
        ("Empire", "\u5e1d\u56fd"),
    ]
    for source, target in token_replacements:
        out = out.replace(source, target)

    out = re.sub(r"\bEnergy\s+Credits\s+from\b", "能量币产自", out, flags=re.IGNORECASE)
    out = re.sub(r"\bMinerals\s+from\b", "矿物产自", out, flags=re.IGNORECASE)
    out = re.sub(r"\bFood\s+from\b", "食物产自", out, flags=re.IGNORECASE)
    out = re.sub(r"\bTrade\s+from\b", "贸易产自", out, flags=re.IGNORECASE)
    out = re.sub(r"\bResources\s+from\b", "资源产自", out, flags=re.IGNORECASE)
    out = re.sub(r"\bfrom\s+£job£\s*Jobs\b", "来自£job£岗位", out, flags=re.IGNORECASE)
    out = out.replace("能量币 from", "能量币产自")
    out = out.replace("矿物 from", "矿物产自")
    out = out.replace("食物 from", "食物产自")
    out = out.replace("贸易 from", "贸易产自")
    out = out.replace("产自 £job£ Jobs", "来自£job£岗位")
    out = out.replace("来自£job£ Jobs", "来自£job£岗位")
    out = re.sub(r"([\u4e00-\u9fff])s\b", r"\1", out)
    out = out.replace("数量 of ", "数量")
    out = out.replace("国家 uses ", "国家使用")
    out = out.replace("生物 ships", "生物舰船")
    out = out.replace("playable 帝国 met", "可游玩帝国已接触数量")
    out = out.replace("Percentage of ", "")
    out = out.replace("the completed_", "已完成_")
    out = out.replace(" completed ", " 已完成 ")
    out = out.replace("Mind over 物质", "超凡入圣")
    out = out.replace("Feature: ", "特性：")
    out = out.replace("Output ", "产出 ")
    out = out.replace("蓝眼光线", "蓝色眼光束")
    out = out.replace("伽马眼光线", "伽马眼光束")
    out = out.replace("紫外眼光线", "紫外眼光束")
    out = out.replace("X射线眼光线", "X射线眼光束")
    out = out.replace("帝国规模 from Pops", "人口导致的帝国规模")
    out = out.replace("Urban 区划 住房", "都市区划住房")
    out = out.replace("物种 领袖 Exp Gain", "物种领袖经验获取")
    out = out.replace("犯罪度反常度", "犯罪度/反常度")
    out = out.replace("工虫人口资源产出", "劳工人口资源产出")
    out = out.replace("阿斯特拉l Planes", "星界位面")
    out = out.replace("DLC 远古 遗珍 Story Pack", "DLC 远古遗物故事包")
    out = out.replace("£轻度_artifacts£", "£minor_artifacts£")
    out = out.replace("Major 首都 建筑", "主都建筑")
    out = out.replace("国家 does 不 use 生物舰船", "国家不使用生物舰船")
    out = out.replace("建造 Cost", "建造花费")
    out = out.replace("建造 花费：", "建造花费：")
    out = out.replace("建造 速度", "建造速度")
    out = re.sub(r"The\s+帝国规模\s+效果\s+是\s+改造的\s+by", "帝国规模效应修正为", out)
    out = re.sub(r"不\s+AI性格\s+是\s+排外孤立主义", "AI性格不是排外孤立主义", out)
    out = out.replace(" 单 阵列", "单阵列")
    out = out.replace(" 双 阵列", "双阵列")
    out = re.sub(r"a\s+bulwark\s+\([^)]*附属国\)", "堡垒子国", out, flags=re.IGNORECASE)
    out = re.sub(r"a\s+prospectorium\s+\([^)]*附属国\)", "勘探子国", out, flags=re.IGNORECASE)
    out = re.sub(r"a\s+scholarium\s+\([^)]*附属国\)", "学者子国", out, flags=re.IGNORECASE)
    out = re.sub(
        r"a\s+bulwark\s+\(specialised\s+附属国\)",
        "堡垒子国",
        out,
        flags=re.IGNORECASE,
    )
    out = re.sub(
        r"a\s+prospectorium\s+\(specialised\s+附属国\)",
        "勘探子国",
        out,
        flags=re.IGNORECASE,
    )
    out = re.sub(
        r"a\s+scholarium\s+\(specialised\s+附属国\)",
        "学者子国",
        out,
        flags=re.IGNORECASE,
    )

    return out


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Generate version i18n.zh-hans.json from official Stellaris localisation."
    )
    parser.add_argument(
        "--stellaris-dir",
        type=Path,
        default=None,
        help="Path to Stellaris install directory (default: auto-detect Steam install).",
    )
    parser.add_argument(
        "--phoenix-dir",
        type=Path,
        default=Path("phoenix-4.0.10"),
        help="Version data directory (default: phoenix-4.0.10).",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("phoenix-4.0.10") / "i18n.zh-hans.json",
        help="Output file (default: phoenix-4.0.10/i18n.zh-hans.json).",
    )
    args = parser.parse_args(argv)

    repo_root = Path(__file__).resolve().parents[1]
    version_dir = (repo_root / args.phoenix_dir).resolve()
    out_path = (repo_root / args.out).resolve()

    stellaris_dir = args.stellaris_dir or _try_find_stellaris_dir()
    if stellaris_dir is None:
        _eprint("ERROR: 无法自动定位 Stellaris 安装目录。")
        _eprint("请传入 --stellaris-dir，例如：")
        _eprint(r'  python scripts/build_phoenix_i18n.py --stellaris-dir "D:\SteamLibrary\steamapps\common\Stellaris"')
        return 2
    stellaris_dir = stellaris_dir.resolve()

    loc_root = _find_localisation_root(stellaris_dir)
    if not loc_root:
        _eprint(f"ERROR: 在 {stellaris_dir} 下找不到 localisation/localization 目录。")
        return 2

    en_dir = loc_root / "english"
    zh_dir = loc_root / "simp_chinese"
    if not en_dir.exists() or not zh_dir.exists():
        _eprint(f"ERROR: 找不到语言目录：{en_dir} 或 {zh_dir}")
        return 2

    if not version_dir.exists():
        _eprint(f"ERROR: 版本目录不存在：{version_dir}")
        return 2

    nodes = _collect_nodes(version_dir)
    tech_keys = sorted({n.get("key") for n in nodes if isinstance(n.get("key"), str)})

    en = _parse_localisation_dir(en_dir)
    zh = _parse_localisation_dir(zh_dir)
    rev_en = _build_reverse_value_map(en)
    _, resolve_zh_text = _make_resolver(zh)

    tech_map: dict[str, dict[str, str]] = {}
    missing_name = 0
    missing_desc = 0
    for key in tech_keys:
        if not isinstance(key, str):
            continue
        name = zh.get(key)
        desc = None
        for dk in _desc_keys(key):
            if dk in zh:
                desc = zh[dk]
                break

        if not name:
            missing_name += 1
        if not desc:
            missing_desc += 1

        entry: dict[str, str] = {}
        if name:
            entry["name"] = resolve_zh_text(name)
        if desc:
            entry["description"] = resolve_zh_text(desc)
        if entry:
            tech_map[key] = entry

    categories: set[str] = set()
    for n in nodes:
        c = n.get("category")
        if isinstance(c, str) and c:
            categories.add(c)

    category_map: dict[str, str] = {}
    for c in sorted(categories):
        lk = rev_en.get(c)
        if lk and lk in zh:
            category_map[c] = resolve_zh_text(zh[lk])

    phrase_map: dict[str, str] = {}
    for key, en_text in en.items():
        zh_raw = zh.get(key)
        if not zh_raw:
            continue
        zh_text = resolve_zh_text(zh_raw)
        if _safe_phrase(en_text, zh_text):
            phrase_map.setdefault(en_text, zh_text)

    for n in nodes:
        node_key = n.get("key")
        node_name = n.get("name")
        if (
            isinstance(node_key, str)
            and isinstance(node_name, str)
            and node_key in tech_map
            and "name" in tech_map[node_key]
        ):
            phrase_map.setdefault(node_name, tech_map[node_key]["name"])

    for en_cat, zh_cat in category_map.items():
        phrase_map.setdefault(en_cat, zh_cat)

    phrase_pairs = sorted(phrase_map.items(), key=lambda kv: len(kv[0]), reverse=True)

    type_map = {
        "Building": "建筑",
        "Component": "组件",
        "Edict": "法令",
        "Feature": "特性",
        "Ship": "舰船",
        "Ship Size": "舰船尺寸",
        "Starbase Building": "恒星基地建筑",
        "Starbase Module": "恒星基地模块",
        "Starbase Upgrade": "恒星基地升级",
        "Army": "陆军",
        "Policy": "政策",
        "Planetary Feature": "行星特征",
        "Tradition": "传统",
        "Ascension Perk": "飞升天赋",
        "Decision": "决议",
        "Situation": "局势",
        "Mega-Structure": "巨型结构",
        "Reveals Ressource": "揭示资源",
        "Reveals Resource": "揭示资源",
    }

    unlock_re = re.compile(r"^\s*<b>([^<]+)</b>\s*:\s*(.+?)\s*$")

    def translate_value(en_text: str) -> str | None:
        lk = rev_en.get(en_text)
        if lk and lk in zh:
            return resolve_zh_text(zh[lk])
        return None

    def alias_unlock_items(item: str) -> list[str]:
        return [item]

    def translate_sized_item(item: str) -> str | None:
        sized = re.match(r"^(Small|Medium|Large)\s+(.+)$", item)
        if not sized:
            return None
        size_en = sized.group(1)
        base_en = sized.group(2)
        size_map = {
            "Small": "小型",
            "Medium": "中型",
            "Large": "大型",
        }
        size_zh = size_map.get(size_en)
        if not size_zh:
            return None

        if base_en.endswith("Beam Projector"):
            core_en = base_en[: -len("Beam Projector")].strip()
            core_zh = translate_value(f"{core_en} Laser") or translate_value(core_en)
            if core_zh:
                core_zh = re.sub(r"^(大型|中型|小型)", "", core_zh)
                core_zh = re.sub(r"激光器?$", "", core_zh)
                return f"{size_zh}{core_zh}光束投射器"

        base_candidates = [base_en]

        for base_candidate in base_candidates:
            base_zh = translate_value(base_candidate)
            if not base_zh:
                continue
            base_zh = re.sub(r"^(大型|中型|小型)", "", base_zh)
            return f"{size_zh}{base_zh}"
        return None

    def translate_line_exact(line: str) -> str | None:
        m = unlock_re.match(line)
        if m:
            line_type = m.group(1).strip()
            item = m.group(2).strip()
            line_type_zh = type_map.get(line_type, line_type)
            item_zh = translate_sized_item(item)
            if item_zh:
                return f"<b>{line_type_zh}</b>：{item_zh}"
            for candidate in alias_unlock_items(item):
                item_zh = translate_value(candidate)
                if item_zh:
                    return f"<b>{line_type_zh}</b>：{item_zh}"
            if line_type_zh != line_type:
                return f"<b>{line_type_zh}</b>：{item}"
            return None

        whole = translate_value(line)
        if whole and whole != line:
            return whole
        return None

    all_lines: set[str] = set()
    line_map: dict[str, str] = {}
    for n in nodes:
        for field in ("feature_unlocks", "potential", "weight_modifiers"):
            arr = n.get(field)
            if not isinstance(arr, list):
                continue
            for item in arr:
                if not isinstance(item, str) or not item:
                    continue
                all_lines.add(item)
                translated = translate_line_exact(item)
                if translated and translated != item:
                    line_map[item] = _apply_dsl_keywords(_normalize_mixed_line(translated))

    for raw_line in sorted(all_lines):
        if raw_line in line_map:
            continue
        translated = _apply_official_phrases(raw_line, phrase_pairs, type_map)
        translated = _apply_dsl_keywords(_normalize_mixed_line(translated))
        if translated != raw_line:
            line_map[raw_line] = translated

    manual_line_overrides = {
        "One must be true\n    •   Has Spiritualist Ethic\n    •   Has Fanatic Spiritualist Ethic\n    •   All must be true\n\t    •   Does NOT have Gestalt Consciousness Ethic\n\t    •   Is a Member of a spiritualist Federation with perk 'A Union of Faith'":
            "以下条件至少一个满足\n    •   拥有 唯心主义 思潮\n    •   拥有 极端唯心主义 思潮\n    •   以下条件全部满足\n\t    •   没有 格式塔意识 思潮\n\t    •   是拥有“信仰同盟”特典的唯心主义联邦成员",
        "(×<b style='color:red'>0.025</b>) Does NOT have Crisis level: Calamity":
            "(×<b style='color:red'>0.025</b>) 没有 危机等级: 灾厄",
        "(×<b style='color:red'>0.025</b>) Does NOT have Crisis level: Existential Threat":
            "(×<b style='color:red'>0.025</b>) 没有 危机等级: 生存威胁",
        "(×<b style='color:red'>0.0</b>) All must be false<br/>    •   Any Owned Planet<br/>\t    •   One must be true<br/>\t\t    •   Has deposit Isolated Valley<br/>\t\t    •   Has deposit Avian Reserve<br/>\t\t    •   Any owned Population Group:<br/>\t\t\t    •   One must be true<br/>\t\t\t\t    •   Pop is NOT Sapient<br/>\t\t\t\t    •   Is livestock<br/>\t\t\t\t    •   Is TODO":
            "(×<b style='color:red'>0.0</b>) 以下条件全部为否<br/>    •   任意所属行星<br/>\t    •   以下条件至少一个满足<br/>\t\t    •   拥有矿藏 偏僻山谷<br/>\t\t    •   拥有矿藏 鸟类保护区<br/>\t\t    •   任意 已拥有 人口 团体:<br/>\t\t\t    •   以下条件至少一个满足<br/>\t\t\t\t    •   人口 不是 智慧物种<br/>\t\t\t\t    •   是 牲畜<br/>\t\t\t\t    •   是 待定",
        "(×<b style='color:red'>0.0</b>) All must be false<br/>    •   Has Crisis level: Calamity<br/>    •   Has Enigmatic Engineering Ascension Perk":
            "(×<b style='color:red'>0.0</b>) 以下条件全部为否<br/>    •   拥有 危机等级: 灾厄<br/>    •   拥有 天机工程 飞升天赋",
        "(×<b style='color:red'>0.0</b>) All must be false<br/>    •   Has Crisis level: Existential Threat<br/>    •   Has Enigmatic Engineering Ascension Perk":
            "(×<b style='color:red'>0.0</b>) 以下条件全部为否<br/>    •   拥有 危机等级: 生存威胁<br/>    •   拥有 天机工程 飞升天赋",
        "(×<b style='color:red'>0.1</b>) Number of buildings lower than 1<br/>    •   Type is Faculty of Archaeostudies<br/>    •   Is NOT disabled<br/>    •   Is NOT in construction":
            "(×<b style='color:red'>0.1</b>) 建筑数量小于 1<br/>    •   类型是 远古学院<br/>    •   未禁用<br/>    •   不在建造中",
        "<b>Component</b>: Bio-Hyperlane Field III":
            "<b>组件</b>：生物超空间航道场 III",
        "<b>Component</b>: Hyper Drive III":
            "<b>组件</b>：超空间引擎 III",
        "One must be true\n    •   One must be true\n\t    •   Has encountered Tiyanki\n\t    •   Has encountered Space Amoeba\n\t    •   Has encountered Crystalline Entity\n\t    •   Has encountered Voidworms\n\t    •   Has encountered Cuthuloids\n    •   One must be true\n\t    •   Has Government Civic: Beastmasters\n\t    •   Has Government Civic: Wild Swarm\n\t    •   Has Government Civic: Biodrones\n\t    •   Has Government Civic: Space Ranchers":
            "以下条件至少一个满足\n    •   以下条件至少一个满足\n\t    •   遭遇过 缇扬奇\n\t    •   遭遇过 太空变形虫\n\t    •   遭遇过 晶态实体\n\t    •   遭遇过 虚空虫\n\t    •   遭遇过 克苏鲁体\n    •   以下条件至少一个满足\n\t    •   拥有 政府 国民理念: 万兽之王\n\t    •   拥有 政府 国民理念: 荒野蜂群\n\t    •   拥有 政府 国民理念: 生态无人机\n\t    •   拥有 政府 国民理念: 太空牧场",
    }
    line_map.update(manual_line_overrides)

    for raw_line, translated in list(line_map.items()):
        fixed = translated
        if "A Union of Faith" in raw_line:
            fixed = (
                "以下条件至少一个满足\n"
                "    •   拥有 唯心主义 思潮\n"
                "    •   拥有 极端唯心主义 思潮\n"
                "    •   以下条件全部满足\n"
                "\t    •   没有 格式塔意识 思潮\n"
                "\t    •   是拥有“信仰同盟”特典的唯心主义联邦成员"
            )
        if raw_line.startswith("(×<b style='color:red'>0.1</b>) Number of buildings lower than 1"):
            fixed = (
                "(×<b style='color:red'>0.1</b>) 建筑数量小于 1<br/>"
                "    •   类型是 远古学院<br/>"
                "    •   未禁用<br/>"
                "    •   不在建造中"
            )
        if raw_line == "<b>Component</b>: Bio-Hyperlane Field III":
            fixed = "<b>组件</b>：生物超空间航道场 III"
        if raw_line == "<b>Component</b>: Hyper Drive III":
            fixed = "<b>组件</b>：超空间引擎 III"
        if "Has encountered Cuthuloids" in raw_line:
            fixed = (
                "以下条件至少一个满足\n"
                "    •   以下条件至少一个满足\n"
                "\t    •   遭遇过 缇扬奇\n"
                "\t    •   遭遇过 太空变形虫\n"
                "\t    •   遭遇过 晶态实体\n"
                "\t    •   遭遇过 虚空虫\n"
                "\t    •   遭遇过 克苏鲁体\n"
                "    •   以下条件至少一个满足\n"
                "\t    •   拥有 政府 国民理念: 万兽之王\n"
                "\t    •   拥有 政府 国民理念: 荒野蜂群\n"
                "\t    •   拥有 政府 国民理念: 生态无人机\n"
                "\t    •   拥有 政府 国民理念: 太空牧场"
            )
        if "AI Personality is Xenophobic Isolationists" in raw_line:
            fixed = fixed.replace("不 AI性格 是 排外孤立主义", "AI性格不是排外孤立主义")
        if raw_line == "The Empire Size Effect is modified by: -5%":
            fixed = "帝国规模效应修正为: -5%"
        fixed = fixed.replace("天灾 等级", "危机等级")
        fixed = fixed.replace("卡拉姆ity", "灾厄")
        fixed = fixed.replace("Existential 威胁", "生存威胁")
        fixed = fixed.replace("Pop 不是 智慧", "人口 不是 智慧物种")
        fixed = fixed.replace("是 livestock", "是 牲畜")
        fixed = fixed.replace("是 TODO", "是 待定")
        fixed = fixed.replace(" 建造花费", "建造花费")
        fixed = fixed.replace(" 建造速度", "建造速度")
        line_map[raw_line] = fixed

    payload = {
        "version": str(args.phoenix_dir),
        "locale": "zh-Hans",
        "generatedAt": _dt.datetime.now(tz=_dt.timezone.utc).isoformat(),
        "tech": tech_map,
        "category": category_map,
        "line": line_map,
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print(f"Written: {out_path}")
    print(f"Tech keys: {len(tech_keys)}")
    print(f"Tech translated (name/desc any): {len(tech_map)}")
    print(f"Missing tech name: {missing_name}")
    print(f"Missing tech desc: {missing_desc}")
    print(f"Category translated: {len(category_map)} / {len(categories)}")
    print(f"Line translated: {len(line_map)} / {len(all_lines)}")
    print(f"Phrase pairs used: {len(phrase_pairs)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
