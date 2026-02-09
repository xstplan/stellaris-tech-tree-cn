# Stellaris Tech Tree
This is the source code for the current updated version (as of Stellaris 4.0.10) of the stellaris tech tree available [here](https://bloodstainedcrow.github.io/stellaris-tech-tree/).

If you are looking for the script for extracting the necessary information from the game files, it is available [here](https://github.com/BloodStainedCrow/stellaris-technology).

## 汉化（Phoenix 4.0.10）
这个仓库是纯静态页面（`index.html` + `assets/`），各版本目录（如 `phoenix-4.0.10/`）包含对应版本导出的 JSON 数据。

为保证“与游戏内一致、不是机翻”的效果，本项目的科技名/描述等文本建议从你本机 Stellaris 的**官方本地化文件**生成，并在页面渲染时覆盖 JSON 里的英文文本。

### 1) 先启动本地静态服务器
浏览器直接打开本地文件时，`$.getJSON()` 可能被拦截。建议在仓库根目录启动一个静态服务器，例如：
- `python -m http.server 8000`

然后访问：`http://localhost:8000/`

### 2) 生成 Phoenix 4.0.10 的中文 i18n 文件
脚本会读取 Phoenix 目录里的科技 `key`，并从官方 `english` 与 `simp_chinese` 本地化中提取对应的中文字符串，生成：`phoenix-4.0.10/i18n.zh-hans.json`。

运行：
- 自动定位（Steam 安装）：`python scripts/build_phoenix_i18n.py`
- 手动指定安装目录：`python scripts/build_phoenix_i18n.py --stellaris-dir "X:\\SteamLibrary\\steamapps\\common\\Stellaris"`

说明：生成的 `i18n.zh-hans.json` 默认已加入 `.gitignore`，避免将游戏文本误提交到仓库。


