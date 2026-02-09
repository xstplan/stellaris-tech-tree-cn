#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import re
import sys
from pathlib import Path


def _eprint(*args: object) -> None:
    print(*args, file=sys.stderr)


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig", errors="replace")


_VDF_PATH_RE = re.compile(r'"path"\s*"([^"]+)"')


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
    # Some installs have localisation under a game subfolder; do a shallow search.
    for p in stellaris_dir.glob("**/localisation"):
        if p.is_dir():
            return p
    for p in stellaris_dir.glob("**/localization"):
        if p.is_dir():
            return p
    return None


_LOC_LINE_RE = re.compile(
    r'^\s*([A-Za-z0-9_.\-]+)\s*:\s*(?:\d+\s*)?"((?:[^"\\]|\\.)*)"\s*(?:#.*)?$'
)

_REF_RE = re.compile(r"\$([A-Za-z0-9_.\-]+)(?:\|[^$]+)?\$")


def _make_resolver(loc: dict[str, str]):
    resolved: dict[str, str] = {}
    resolving: set[str] = set()

    def resolve_text(text: str) -> str:
        def repl(m: re.Match[str]) -> str:
            k = m.group(1)
            v = resolve_key(k)
            return v if v is not None else m.group(0)

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
        v = loc.get(key)
        if v is None:
            return None
        resolving.add(key)
        out = resolve_text(v)
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


def _walk_tree(node: dict, fn) -> None:
    fn(node)
    children = node.get("children")
    if isinstance(children, list):
        for child in children:
            if isinstance(child, dict):
                _walk_tree(child, fn)


def _load_json(path: Path):
    return json.loads(_read_text(path))


def _collect_phoenix_nodes(phoenix_dir: Path) -> list[dict]:
    nodes: list[dict] = []

    def push(n: dict) -> None:
        if "key" in n:
            nodes.append(n)

    for filename in ("physics.json", "society.json", "engineering.json"):
        obj = _load_json(phoenix_dir / filename)
        root = obj.get("children", [{}])[0]
        if isinstance(root, dict):
            _walk_tree(root, push)

    anomalies = _load_json(phoenix_dir / "anomalies.json")
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


def _build_reverse_value_map(en: dict[str, str]) -> dict[str, str]:
    rev: dict[str, str] = {}
    for k, v in en.items():
        if v not in rev:
            rev[v] = k
    return rev


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(
        description="Generate phoenix-4.0.10 Chinese i18n map from official Stellaris localisation."
    )
    ap.add_argument(
        "--stellaris-dir",
        type=Path,
        default=None,
        help="Path to Stellaris install directory (defaults to auto-detect Steam install).",
    )
    ap.add_argument(
        "--phoenix-dir",
        type=Path,
        default=Path("phoenix-4.0.10"),
        help="Phoenix data directory (default: phoenix-4.0.10).",
    )
    ap.add_argument(
        "--out",
        type=Path,
        default=Path("phoenix-4.0.10") / "i18n.zh-hans.json",
        help="Output file (default: phoenix-4.0.10/i18n.zh-hans.json).",
    )
    args = ap.parse_args(argv)

    repo_root = Path(__file__).resolve().parents[1]
    phoenix_dir = (repo_root / args.phoenix_dir).resolve()
    out_path = (repo_root / args.out).resolve()

    stellaris_dir = args.stellaris_dir
    if stellaris_dir is None:
        stellaris_dir = _try_find_stellaris_dir()
    if stellaris_dir is None:
        _eprint("ERROR: 无法自动定位 Stellaris 安装目录。")
        _eprint("请传入 --stellaris-dir，例如：")
        _eprint(r'  python scripts/build_phoenix_i18n.py --stellaris-dir "D:\SteamLibrary\steamapps\common\Stellaris"')
        return 2

    stellaris_dir = stellaris_dir.resolve()
    loc_root = _find_localisation_root(stellaris_dir)
    if not loc_root:
        _eprint(f"ERROR: 在 {stellaris_dir} 下找不到 localisation/localization 目录。")
        _eprint("请确认游戏已下载完成，或手动指定正确的 --stellaris-dir。")
        return 2

    en_dir = loc_root / "english"
    zh_dir = loc_root / "simp_chinese"

    if not en_dir.exists() or not zh_dir.exists():
        _eprint(f"ERROR: 找不到语言目录：{en_dir} 或 {zh_dir}")
        _eprint("请确认游戏语言文件存在（Steam 下载完成后通常会有）。")
        return 2

    if not phoenix_dir.exists():
        _eprint(f"ERROR: Phoenix 目录不存在：{phoenix_dir}")
        return 2

    nodes = _collect_phoenix_nodes(phoenix_dir)
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

    line_map: dict[str, str] = {}
    type_map = {
        "Building": "建筑",
        "Component": "组件",
        "Edict": "法令",
        "Ship": "舰船",
        "Starbase Building": "恒星基地建筑",
        "Army": "陆军",
        "Policy": "政策",
        "Planetary Feature": "行星特征",
        "Tradition": "传统",
        "Ascension Perk": "飞升天赋",
        "Decision": "决议",
        "Situation": "局势",
    }

    unlock_re = re.compile(r"^\s*<b>([^<]+)</b>\s*:\s*(.+?)\s*$")

    def translate_value(en_text: str) -> str | None:
        lk = rev_en.get(en_text)
        if lk and lk in zh:
            return resolve_zh_text(zh[lk])
        return None

    def translate_line(line: str) -> str | None:
        m = unlock_re.match(line)
        if m:
            t = m.group(1).strip()
            item = m.group(2).strip()
            t_zh = type_map.get(t, t)
            item_zh = translate_value(item)
            if item_zh:
                return f"<b>{t_zh}</b>：{item_zh}"
            if t_zh != t:
                return f"<b>{t_zh}</b>：{item}"
            return None

        whole = translate_value(line)
        if whole and whole != line:
            return whole
        return None

    for n in nodes:
        for field in ("feature_unlocks", "potential", "weight_modifiers"):
            arr = n.get(field)
            if not isinstance(arr, list):
                continue
            for item in arr:
                if not isinstance(item, str) or not item:
                    continue
                translated = translate_line(item)
                if translated and translated != item:
                    line_map[item] = translated

    payload = {
        "version": "phoenix-4.0.10",
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
    print(f"Extra lines translated: {len(line_map)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
