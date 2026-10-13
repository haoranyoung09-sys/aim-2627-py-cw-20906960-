# -*- coding: utf-8 -*-
"""旧版巡逻统计模块（2526 赛季遗留）—— Q7：昨天还能跑。

背景：本模块从上一届的巡逻系统原样迁移，上周还"能跑"。
最近的两次提交（见 git log）之后 CI 依旧全绿，但验收脚本报出的
数字不对，有的调用甚至卡死。上级只留了一句：昨天还能跑。

任务（题面 Q7·修复任务与提交物）：
1. 本模块共埋有 6 处 bug，其中两对互相遮蔽——修好 A 才会暴露 B；
2. 修复全部 6 处（验收以各函数 docstring 的契约为准，隐藏测试逐条核对）；
3. 在你的 README 里逐条写明：错在哪、你是怎么定位到的。

提示：不要迷信 git log 里的"修复"——有一件事被越修越错了。
"""

# ---------------------------------------------------------------------------
# 路线统计
# ---------------------------------------------------------------------------


def segment_length_cm(p1, p2):
    """两个检查点 (x, y) 之间的路线长度，单位：厘米。
    检查点坐标单位为格，1 格 = 1 米 = 100 厘米，路线按曼哈顿距离计算。"""
    return (abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])) * 100


def total_route_meters(points):
    """Return the Manhattan route length in meters, not centimeters."""
    distance_in_cm = 0
    for i in range(len(points) - 1):
        distance_in_cm += segment_length_cm(points[i], points[i + 1])
    return distance_in_cm / 100


# ---------------------------------------------------------------------------
# 事件日志
# ---------------------------------------------------------------------------
def parse_event(line):
    """Parse MOVE/SCAN/IDLE with a nonnegative count; reject dirty input."""
    if not isinstance(line, str):
        return None
    parts = line.strip().split(",")
    if len(parts) != 2 or parts[0] not in ("MOVE", "SCAN", "IDLE"):
        return None
    if not parts[1].isascii() or not parts[1].isdigit():
        return None
    try:
        count = int(parts[1])
    except ValueError:
        return None
    return {"type": parts[0], "count": count}


def first_positive(samples):
    """返回样本序列中第一个正数；若没有正数，返回 None（上游约定）。"""
    for s in samples:
        if s > 0:
            return s
    return None


def calibrate(samples):
    """Sum drift from the first positive sample; absent baselines yield zero."""
    baseline = first_positive(samples)
    if baseline is None:
        return 0
    return sum(sample - baseline for sample in samples)


def summarize_events(events, max_id):
    """统计 id 不超过 max_id 的事件。

    events: [{"id": int, "move": int, "samples": [int, ...]}, ...]
    每个事件的步数贡献 = move + calibrate(samples)。
    返回 {"events": 统计到的事件数, "steps": 步数总和}。
    """
    used = 0
    steps = 0
    for e in events:
        if e["id"] <= max_id:
            used += 1
            steps += e["move"] + calibrate(e["samples"])
    return {"events": used, "steps": steps}


def log(message, history=None):
    """Append to explicit history or create a new list for each call."""
    if history is None:
        history = []
    history.append(message)
    return history


# ---------------------------------------------------------------------------
# 旧版巡逻模拟
# ---------------------------------------------------------------------------
def run_legacy_sim(rounds, stamina_start=100):
    """Execute numbered rounds, stopping after stamina reaches 20 or less."""
    stamina = stamina_start
    trace = []
    for round_ in range(rounds):
        stamina -= 8
        if round_ >= 3:
            stamina -= 5
        trace.append((round_, stamina))
        if stamina <= 20:
            break
    return {"rounds": len(trace), "stamina": stamina, "trace": trace}
