# 群星科技树

项目是群星科技树汉化版本，
✨原仓库地址为：https://github.com/BloodStainedCrow/stellaris-tech-tree

## 快速启动
- 从仓库根目录启动本地 Web 服务器:
  - `python -m http.server 8000`
- 浏览器打开:
  - `http://localhost:8000/`

## 一键汉化
需要这一条命令：
- `python scripts/translate_cn.py`

这会自动为 `phoenix-4.0.10` 生成：
- `phoenix-4.0.10/i18n.zh-hans.json`

## 其他版本
指定版本目录名即可，不过还是需要另一个版本更新，这里进行一个同步比如assets的icons和img：
- `python scripts/translate_cn.py --version cetus-4.3.0`

## 自动定位失败时
如果脚本无法自动找到游戏目录，手动指定：
- `python scripts/translate_cn.py --stellaris-dir "X:\\SteamLibrary\\steamapps\\common\\Stellaris"`
- 或同时指定版本：
- `python scripts/translate_cn.py --version cetus-4.3.0 --stellaris-dir "X:\\SteamLibrary\\steamapps\\common\\Stellaris"`

## 说明注意
- `i18n.zh-hans.json` 默认在 `.gitignore` 中，不会被提交，需要自行生成，需要安装python。

