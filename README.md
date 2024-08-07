<!-- markdownlint-disable MD031 MD033 MD036 MD041 -->

<div align="center">

<a href="https://v2.nonebot.dev/store">
  <img src="https://raw.githubusercontent.com/lgc-NB2Dev/readme/main/clash/clash.png" width="180" height="180" alt="NoneBotPluginLogo">
</a>

<p>
  <img src="https://raw.githubusercontent.com/lgc-NB2Dev/readme/main/template/plugin.svg" alt="NoneBotPluginText">
</p>

# NoneBot-Plugin-Clash

_✨ 在 NoneBot2 中管理 Clash ✨_

<img src="https://img.shields.io/badge/python-3.9+-blue.svg" alt="python">
<a href="https://pdm.fming.dev">
  <img src="https://img.shields.io/badge/pdm-managed-blueviolet" alt="pdm-managed">
</a>
<a href="https://wakatime.com/badge/user/b61b0f9a-f40b-4c82-bc51-0a75c67bfccf/project/018c485d-8163-4802-9e3d-579cab2715aa">
  <img src="https://wakatime.com/badge/user/b61b0f9a-f40b-4c82-bc51-0a75c67bfccf/project/018c485d-8163-4802-9e3d-579cab2715aa.svg" alt="wakatime">
</a>

<br />

<a href="https://pydantic.dev">
  <img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/lgc-NB2Dev/readme/main/template/pyd-v1-or-v2.json" alt="Pydantic Version 1 Or 2" >
</a>
<a href="./LICENSE">
  <img src="https://img.shields.io/github/license/lgc-NB2Dev/nonebot-plugin-clash.svg" alt="license">
</a>
<a href="https://pypi.python.org/pypi/nonebot-plugin-clash">
  <img src="https://img.shields.io/pypi/v/nonebot-plugin-clash.svg" alt="pypi">
</a>
<a href="https://pypi.python.org/pypi/nonebot-plugin-clash">
  <img src="https://img.shields.io/pypi/dm/nonebot-plugin-clash" alt="pypi download">
</a>

<br />

<a href="https://registry.nonebot.dev/plugin/nonebot-plugin-clash:nonebot_plugin_clash">
  <img src="https://img.shields.io/endpoint?url=https%3A%2F%2Fnbbdg.lgc2333.top%2Fplugin%2Fnonebot-plugin-clash" alt="NoneBot Registry">
</a>
<a href="https://registry.nonebot.dev/plugin/nonebot-plugin-clash:nonebot_plugin_clash">
  <img src="https://img.shields.io/endpoint?url=https%3A%2F%2Fnbbdg.lgc2333.top%2Fplugin-adapters%2Fnonebot-plugin-clash" alt="Supported Adapters">
</a>

</div>

<!-- ## 📖 介绍

这里是插件的详细介绍部分 -->

## 💿 安装

以下提到的方法 任选**其一** 即可

<details open>
<summary>[推荐] 使用 nb-cli 安装</summary>
在 nonebot2 项目的根目录下打开命令行, 输入以下指令即可安装

```bash
nb plugin install nonebot-plugin-clash
```

</details>

<details>
<summary>使用包管理器安装</summary>
在 nonebot2 项目的插件目录下, 打开命令行, 根据你使用的包管理器, 输入相应的安装命令

<details>
<summary>pip</summary>

```bash
pip install nonebot-plugin-clash
```

</details>
<details>
<summary>pdm</summary>

```bash
pdm add nonebot-plugin-clash
```

</details>
<details>
<summary>poetry</summary>

```bash
poetry add nonebot-plugin-clash
```

</details>
<details>
<summary>conda</summary>

```bash
conda install nonebot-plugin-clash
```

</details>

打开 nonebot2 项目根目录下的 `pyproject.toml` 文件, 在 `[tool.nonebot]` 部分的 `plugins` 项里追加写入

```toml
[tool.nonebot]
plugins = [
    # ...
    "nonebot_plugin_clash"
]
```

</details>

## ⚙️ 配置

在 NoneBot2 项目的`.env`文件中添加下表中的必填配置

|         配置项         |             必填             | 默认值 |                          说明                           |
| :--------------------: | :--------------------------: | :----: | :-----------------------------------------------------: |
| `CLASH_CONTROLLER_URL` | $${\textsf{\color{red}是}}$$ |   无   | Clash 的 `external-controller` 地址，需要带上 `http://` |
|     `CLASH_SECRET`     |              否              |   无   |     Clash 的 `external-controller` 使用的 `secret`      |
| `CLASH_NEED_SUPERUSER` |              否              | `True` |          是否只有 `SUPERUSER` 可以触发插件指令          |
|  `CLASH_CHART_WIDTH`   |              否              | `150`  |                概览中图标的 X 轴最大点数                |
|   `CLASH_LOG_LEVEL`    |              否              | `info` |                     监控的日志等级                      |
|   `CLASH_LOG_COUNT`    |              否              |  `50`  |                     保留的日志条数                      |
|  `CLASH_IMAGE_WIDTH`   |              否              | `600`  | 生成的图片宽度，单位像素（实际结果可能会为此值的两倍）  |

## 🎉 使用

### 指令

#### `clash概览`

获取当前 Clash 的运行状态概览

<details>
<summary>示例（点击展开）</summary>

![概览](https://raw.githubusercontent.com/lgc-NB2Dev/readme/main/clash/summary.jpg)

</details>

#### `clash日志`

获取已记录的 Clash 日志

<details>
<summary>示例（点击展开）</summary>

![概览](https://raw.githubusercontent.com/lgc-NB2Dev/readme/main/clash/logs.jpg)

</details>

#### `clash清空日志`

清空 Clash 日志记录

## 📞 联系

QQ：3076823485  
Telegram：[@lgc2333](https://t.me/lgc2333)  
吹水群：[1105946125](https://jq.qq.com/?_wv=1027&k=Z3n1MpEp)  
邮箱：<lgc2333@126.com>

## 💡 鸣谢

### [haishanh/yacd](https://github.com/haishanh/yacd)

- 样式借鉴

## 💰 赞助

**[赞助我](https://blog.lgc2333.top/donate)**

感谢大家的赞助！你们的赞助将是我继续创作的动力！

## 📝 更新日志

芝士刚刚发布的插件，还没有更新日志的说 qwq~
