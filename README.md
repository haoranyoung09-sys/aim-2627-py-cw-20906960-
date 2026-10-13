# AIM 2627 Python Coursework —— 哨兵 Sentry 控制模块

> **全部题目、规范、评分、提交见 [题面.pdf](题面.pdf)。** 本 README 只讲怎么把环境跑起来；没在这里出现的规格细节，一律以题面为准。

## 1. 环境要求

- Python 3.8+，仅标准库（不允许第三方运行时依赖）；
- 开发工具只需 `pytest`（测试）与 `autopep8`（风格，CI 会检查）；
- VS Code 打开仓库会推荐安装 `ms-python.autopep8` 插件（`.vscode/extensions.json`），保存即格式化即可过风格检查。

## 2. 快速开始

```bash
# 1. 用 GitHub 的 Use this template 创建你自己的仓库，然后 clone
git clone https://github.com/<你的用户名>/<你的仓库>.git
cd <你的仓库>   # 直接在 main 分支上开发

# 创建虚拟环境

python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

# 2. 装依赖
python -m pip install pytest autopep8

# 3. 启用 AI 会话归档钩子（课程要求，见下方第 3 节）
python -m pip install 'agent-session-commit[pre-commit]==0.1.3' -i https://pypi.org/simple
agent-session-commit install --pre-commit   # 交互选择你的 AI 助手与会话目录

# 4. 跑测试（刚到手：全部 skip，CI 是绿的）
python -m pytest

# 5. 看演示
python main.py

# 6. 打开 题面.pdf 读题，开始实现 src/main/__init__.py 里的 TODO
```

## 3. AI 会话归档（pre-commit）

本课程允许使用 AI，提交的 commit 需要携带 AI 会话归档作为透明化记录：每次 `git commit` 后，钩子会把新增会话自动 amend 进同一个提交（`.agent-sessions/bundles/`），不产生额外的归档提交。支持 Claude Code、OpenAI Codex CLI、GitHub Copilot CLI、Qoder、ZCode、Trae、Tencent CodeBuddy 等（完整名单见 [AgentLedger](https://github.com/Gentle-Lijie/AgentLedger)）。

- 配置是仓库本地的：每个 clone 运行一次 `agent-session-commit install --pre-commit`，方向键选择 agent、确认其会话目录即可；
- 不想用 TUI 可手动配置：`git config --local agent-session.agent claude`、`git config --local agent-session.source "<会话目录>"`，然后 `python -m pip install 'pre-commit>=3.2.0' && pre-commit install`；
- 归档是普通 Git 内容且会推送到公开仓库——不要在 AI 会话里粘贴令牌等敏感信息；
- 换了 agent 或目录就重跑一次安装命令；卸载：从 `.pre-commit-config.yaml` 移除该条目后重跑 `pre-commit install`。

## 4. 本地开发循环

- **写代码**：全部作业在 `src/main/__init__.py`，按题面各题规范补全每个标有 TODO 的函数；注释里标注了对应的题面主题，推荐顺序 Q1 → Q6。
- **跑测试**：`python -m pytest` —— 可见测试是规格书的一部分，未实现的函数自动 skip，实现一个、对应测试亮一个。本地全绿 ≠ 满分（见题面）。
- **看演示**：`python main.py`（等价于 `PYTHONPATH=src python -m main`），随实现进度逐段点亮，不进测试。
- **Q6 自测**：`python tools/run_seeds.py --q6`（200 张固定地图统计），单 seed 渲染 `python tools/run_seeds.py --q6 --seed <N> --render`，Bonus 模式 `python tools/run_seeds.py --bonus`。

## 5. 仓库结构（哪些能改）

| 路径 | 说明 | 能否修改 |
|---|---|---|
| `src/main/__init__.py` | 你的全部作业（TODO 所在） | ✅ |
| `README.md` | 仅末尾两个"你来写"小节 | ✅ |
| `题面.pdf` | 题面（唯一规格说明） | ❌ 勿改 |
| `src/main/legacy_patrol.py` | Q7 模块（与主体同步发布，修复其缺陷） | Q7 时 ✅ |
| `.pre-commit-config.yaml` | AI 会话归档钩子配置 | ❌ 勿改 |
| `src/tests/`、`tools/`、`.github/`、`conftest.py`、`pytest.ini`、`main.py` | 测试与基础设施 | ❌ 勿改 |

CI 只允许修改 `src/main/**`、`README.md` 与 `.agent-sessions/**`（AI 会话归档）——其余文件改了直接红；autopep8 `--diff` 非空即败。提交方式（push、问卷、commit 粒度）见题面"提交与验收"一节。


## 6. 设计说明（你来写）

本实现完成哨兵自检、日志统计、载体运动、贪心导航、决策机和巡逻任务。保留题目提供的接口与基础设施，仅使用 Python 标准库。

### 读题与实现顺序

按 Q1 → Q6 → Bonus → Q7 实现，每一步先复现测试，再补全功能并检查边界。Q5 按 R1–R7 首条命中返回，热量不改变题目给定的优先级。Q6 先调用 Q4 贪心策略，失速时使用地图边界内的最短路脱困。

题面未公开部分边界。实现采用以下可复现约定：电量以 50、20 为分界；撤退恢复阈值为 60%；连续三个假帧视为持续丢失；坐标转整数后夹回地图范围，再拒绝障碍格。这些约定会随边界检查记录，不能据此承诺隐藏测试分数。

### AI 使用与归档

本作业使用 Codex 辅助实现。安装 Vercel agent-skills，并将其中 writing-guidelines 的明确标题、主动语态和可核验结果要求用于本文档；React 与 Vercel 部署技能不适用于本作业。

本聊天从独立工作目录启动。AgentLedger 的 Codex 适配器按启动目录过滤，无法直接匹配作业仓库。因此使用官方 custom 导出方式：增加说明导出归属的头记录，随后逐字节保留本聊天的原始 JSONL，包括原始 session_meta。每次 commit 前刷新导出，post-commit 钩子将新增归档并入该次提交，不改写原始会话记录。

## 7. 调试分析与验证（你来写）

旧模块的六处缺陷通过函数契约和独立输入复现定位，修复记录如下：

| 缺陷 | 定位证据 | 修复 |
| --- | --- | --- |
| 路线单位错误 | `(0,0) → (3,0) → (3,4)` 应为 7 米，原结果为 700 | 累加厘米后除以 100 |
| 缺少正样本时仍计算漂移 | `calibrate([-1, -2])` 将整数减去 `None`，抛出异常 | 没有基线时返回 0 |
| ID 上界遗漏 | 最大 ID 为 2 时，ID 等于 2 的事件未计入 | 将 `< max_id` 改为 `<= max_id` |
| 默认日志历史共享 | 连续调用 `log("a")` 和 `log("b")`，第二次返回两条日志 | 默认参数用 `None`，每次创建新列表 |
| 终止条件反向 | 体力充足时第一轮就终止 | 每轮结束后体力 `<= 20` 才停止 |
| 轮次不推进 | `round_` 始终为 0，后续轮次和额外消耗无法发生 | 用 `range(rounds)` 推进轮次 |

最后两处缺陷互相遮蔽：提前退出掩盖轮次不推进，修正退出条件后仍需修复轮次。此外，事件解析补充类型与数值转换校验，`None`、非字符串和无法转换的数字表示均返回 `None`。

### 边界处理与导航设计

`hp_ratio` 先规范化为整数，再用整数除法向下取整并夹到 0–100，避免超大整数经过浮点转换时溢出。非正满血量返回 0。报告中的电量读数也夹到 0–100。

日志解析先校验整行，再写入统计桶。每个传感器段独立计为一个事件；JSON 伤害仅接受严格正整数，拒绝布尔值和小数。ID 接受整数或字符串，重复有效 ID 只保留第一次；统计平均值按有效事件数计算。总伤害并列时按 front、left、right 的顺序选择。超过浮点表示范围的平均值返回 `float("inf")`，伤害总和与各桶仍保留精确整数。过深 JSON 按脏行跳过，后续有效行继续统计。

决策输入缺少字段、状态非法或帧历史长度非法时抛出 `ValueError`。未知机型归为步兵；敌距取值为 `None` 或非法值时按无限远处理。血量、撤退保持、单帧返航、交火和敌情确认依次判定，热量不会覆盖规则表。

巡逻在每轮读取当前位置并调用贪心策略。贪心不再减小曼哈顿距离时，在地图边界内执行一次广度优先搜索（Breadth-first search，BFS），缓存剩余路径，再通过公开转向和前进接口执行。已知目标不可达时提前结束，避免空耗电量。`steps` 统计前进尝试；`collisions` 统计本次任务新增碰撞；`visited_count` 包含起点和实际抵达的位置。

### 本地验证结果

本地验证覆盖题目可见测试、独立边界案例和两组地图，结果如下：

| 检查 | 结果 |
| --- | --- |
| 完整 `python -m pytest -ra` | 35 passed，无 skipped |
| 独立边界检查 | 24 项通过 |
| `autopep8 --diff --recursive src/main` | 输出为空 |
| Q6 官方 seed 1–200 | 成功率 100%，平均碰撞 0，平均步数/BFS 比 1.03 |
| Q6 额外 seed 1001–1200 | 成功率 100%，平均碰撞 0，平均步数/BFS 比 1.04 |
| Bonus 官方 200 seed | 成功率 100%，平均 29.5 步，平均碰撞 0 |
| `python main.py` | 演示正常完成，巡逻 15 步、零碰撞 |

修改范围仅包含 `src/main/**`、README 学生小节和 `.agent-sessions/**`。真实归档按完整包加后续增量包保存，manifest 记录偏移、文件大小和 SHA-256；校验时依序重建并与原始导出比对。

本地结果不能替代隐藏测试和人工评审。尚未推送，也未运行远程 Actions 或填写问卷。

归档安装说明：pre-commit 框架初始化因 GitHub 下载阻塞未完成，改用同版本 AgentLedger 官方原生 Git 钩子。pre-commit 钩子刷新原始导出，post-commit 钩子打包并 amend；题目配置文件保持原样。
