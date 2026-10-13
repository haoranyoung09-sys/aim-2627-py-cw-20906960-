# -*- coding: utf-8 -*-
"""AIM 2627 Python Coursework —— 哨兵 Sentry 控制模块（学生骨架）。

你的全部作业都在本文件里：按题面（题面.pdf）各题的规范补全每个标有 TODO 的函数。
- 骨架已提供：Facing / SentryState 枚举、SentryGrid 的构造与只读属性、
  渲染函数 render_frame（demo 用，不进测试）。
- 你要实现：Q1-Q6 与 Bonus 的全部 TODO，以及 SentryGrid 的
  四个方法（current_pos 的 setter、move_forward、turn_left、turn_right）。
- 未实现的函数 raise NotImplementedError：可见测试会自动 skip，
  CI 一开始就是绿的；实现一个，对应测试亮一个。
- `python main.py`（或 PYTHONPATH=src python -m main）可看 ASCII 演示。
"""
import json
from collections import deque
from enum import Enum


# ---------------------------------------------------------------------------
# 仿真世界基础（已提供，勿改）
# ---------------------------------------------------------------------------
class Facing(Enum):
    """朝向枚举。世界坐标 (x, y)：x 向右增长，y 向上增长（数学系）。"""

    UP = (0, 1)
    DOWN = (0, -1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

    @property
    def delta(self):
        """该朝向的单位位移向量 (dx, dy)。"""
        return self.value[0], self.value[1]


# ---------------------------------------------------------------------------
# Q1 机器人自检（题面 Q1·自检状态计算与报告生成）
# ---------------------------------------------------------------------------
def hp_ratio(hp, max_hp):
    """Return a clamped percentage using exact integer arithmetic."""
    try:
        hp, max_hp = int(hp), int(max_hp)
    except (TypeError, ValueError, OverflowError):
        return 0
    if max_hp <= 0:
        return 0
    return max(0, min(100, hp * 100 // max_hp))


def status_report(name, robot_type, hp, max_hp, battery):
    """Format the self-check report with battery tiers at 20 and 50."""
    try:
        battery = max(0, min(100, int(battery)))
    except (TypeError, ValueError, OverflowError):
        battery = 0
    tier = "OK" if battery >= 50 else "WARNING" if battery >= 20 else "LOW"
    return (f"{name:<10}|{robot_type:^10}|HP {hp_ratio(hp, max_hp):>3}%"
            f"|BAT {battery:>3}%|{tier}")


# ---------------------------------------------------------------------------
# Q2 战斗日志分析（题面 Q2·多源日志解析与统计）
# ---------------------------------------------------------------------------
def analyze_damage_log(lines):
    """Aggregate valid damage events; discard malformed lines atomically."""
    by_armor = dict.fromkeys(("front", "left", "right"), 0)
    labels = {"F": "front", "L": "left", "R": "right"}
    seen_ids = set()
    count = 0
    try:
        iterator = iter(lines)
    except TypeError:
        iterator = iter(())
    for line in iterator:
        if not isinstance(line, str):
            continue
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        try:
            if line.startswith("{"):
                event = json.loads(line)
                armor, damage = event["armor"], event["damage"]
                if (not isinstance(armor, str) or armor not in by_armor
                        or type(damage) is not int or damage <= 0):
                    continue
                if "id" in event:
                    event_id = event["id"]
                    if type(event_id) not in (int, str):
                        continue
                    if event_id in seen_ids:
                        continue
                    seen_ids.add(event_id)
                events = [(armor, damage)]
            else:
                events = []
                for segment in line.split(","):
                    label, value = segment.split(":")
                    value = value.strip()
                    if not value.isascii() or not value.isdigit():
                        raise ValueError("Invalid integer damage")
                    damage = int(value)
                    if damage <= 0:
                        raise ValueError("Damage must be positive")
                    events.append((labels[label.strip()], damage))
        except (ValueError, TypeError, KeyError):
            continue
        for armor, damage in events:
            by_armor[armor] += damage
            count += 1
    total = sum(by_armor.values())
    return {"total": total, "by_armor": by_armor,
            "most_hit": max(by_armor, key=by_armor.get) if count else None,
            "avg": round(total / count, 2) if count else 0.0}


# ---------------------------------------------------------------------------
# Q3 SentryGrid（题面 Q3·载体物理规则）
# ---------------------------------------------------------------------------
class SentryGrid:
    """哨兵仿真载体（构造与只读属性已提供；四个 TODO 方法由你实现）。"""

    def __init__(self, width, height, obstacles, enemy_pos,
                 start_pos=(0, 0), facing=Facing.UP, fuel=100):
        self._width = int(width)
        self._height = int(height)
        if self._width <= 0 or self._height <= 0:
            raise ValueError("地图尺寸必须为正")
        # 障碍坐标存入 set，查询 O(1)——已有实现，勿改。
        self._obstacles = set()
        for ob in obstacles:
            x, y = ob
            self._obstacles.add((int(x), int(y)))
        if not isinstance(enemy_pos, (tuple, list)) or len(enemy_pos) != 2:
            raise TypeError("enemy_pos 需要长度为 2 的 tuple/list")
        self._enemy_pos = self._clamp_cell(enemy_pos)
        if self._enemy_pos in self._obstacles:
            raise ValueError("enemy_pos 不能位于障碍物上")
        if not isinstance(facing, Facing):
            facing = Facing.UP
        self._facing = facing
        self._fuel = int(fuel)
        self._collision_count = 0
        self._pos = self._clamp_cell(start_pos)
        if self._pos in self._obstacles:
            raise ValueError("start_pos 不能位于障碍物上")

    def _clamp_cell(self, cell):
        """已提供：元素转 int 并夹回地图范围（供 __init__ 使用）。"""
        x = int(cell[0])
        y = int(cell[1])
        x = max(0, min(self._width - 1, x))
        y = max(0, min(self._height - 1, y))
        return (x, y)

    # -- 只读属性（已提供，勿改） ------------------------------------------
    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    @property
    def enemy_pos(self):
        return self._enemy_pos

    @property
    def facing(self):
        return self._facing

    @property
    def fuel(self):
        return self._fuel

    @property
    def collision_count(self):
        return self._collision_count

    @property
    def obstacles(self):
        """障碍集合的只读视图（内部 set 引用，不要修改它）。"""
        return self._obstacles

    @property
    def found_enemy(self):
        return self._pos == self._enemy_pos

    def is_blocked(self, x, y):
        """已提供：坐标是否为障碍或越界（O(1)）。"""
        return ((x, y) in self._obstacles
                or not (0 <= x < self._width and 0 <= y < self._height))

    # -- 你要实现的部分 ------------------------------------------------------
    @property
    def current_pos(self):
        """当前位置 (x, y) 的 tuple。"""
        return self._pos

    @current_pos.setter
    def current_pos(self, value):
        """Normalize and clamp a pair; reject obstacles without changing position."""
        if not isinstance(value, (tuple, list)) or len(value) != 2:
            raise TypeError("Position must be a tuple or list of length two")
        position = self._clamp_cell(value)
        if position in self._obstacles:
            raise ValueError("Position cannot be an obstacle")
        self._pos = position

    def move_forward(self):
        """Attempt one move, consuming fuel even when blocked."""
        if self._fuel <= 0:
            return self._pos
        self._fuel -= 1
        dx, dy = self._facing.delta
        position = (self._pos[0] + dx, self._pos[1] + dy)
        if self.is_blocked(*position):
            self._collision_count += 1
        else:
            self._pos = position
        return self._pos

    def turn_left(self):
        """Rotate counterclockwise without consuming fuel."""
        order = (Facing.UP, Facing.LEFT, Facing.DOWN, Facing.RIGHT)
        self._facing = order[(order.index(self._facing) + 1) % 4]
        return self._facing

    def turn_right(self):
        """Rotate clockwise without consuming fuel."""
        order = (Facing.UP, Facing.RIGHT, Facing.DOWN, Facing.LEFT)
        self._facing = order[(order.index(self._facing) + 1) % 4]
        return self._facing


# ---------------------------------------------------------------------------
# Q4 贪心导航（题面 Q4·单步贪心导航策略）
# ---------------------------------------------------------------------------
def next_step_toward(pos, target, obstacles, current_facing=Facing.UP):
    """Prefer the larger-distance axis; use the x axis to break ties."""
    dx, dy = target[0] - pos[0], target[1] - pos[1]
    horizontal = Facing.RIGHT if dx > 0 else Facing.LEFT
    vertical = Facing.UP if dy > 0 else Facing.DOWN
    order = (horizontal, vertical) if abs(dx) >= abs(dy) else (
        vertical, horizontal)
    distance = abs(dx) + abs(dy)
    for direction in order:
        sx, sy = direction.delta
        nxt = (pos[0] + sx, pos[1] + sy)
        remaining = abs(nxt[0] - target[0]) + abs(nxt[1] - target[1])
        if nxt not in obstacles and remaining < distance:
            return direction
    return current_facing


# ---------------------------------------------------------------------------
# Q5 哨兵决策机（题面 Q5·裁判系统决策规则表）
# ---------------------------------------------------------------------------
class SentryState(Enum):
    """哨兵状态机（已提供，勿改）。"""

    PATROL = "PATROL"
    SUSPECT = "SUSPECT"
    ENGAGE = "ENGAGE"
    RETREAT = "RETREAT"
    RETURN = "RETURN"


def decide(sensor, state, hp, heat):
    """Apply R1 through R7 in order; heat does not override those rules."""
    required = {"enemy_frames", "enemy_dist", "robot_type", "max_hp"}
    if not isinstance(state, SentryState):
        raise ValueError("Unknown sentry state")
    if not isinstance(sensor, dict) or not required.issubset(sensor):
        raise ValueError("Missing sensor fields")
    frames = sensor["enemy_frames"]
    if not isinstance(frames, (tuple, list)) or not 1 <= len(frames) <= 6:
        raise ValueError("Enemy history must contain one to six frames")
    visible = bool(frames[-1])
    distance = sensor["enemy_dist"]
    if type(distance) is not int or distance < 0:
        distance = float("inf")
    robot_type = sensor["robot_type"]
    if robot_type != "HERO":
        robot_type = "INFANTRY"
    hp_pct = hp_ratio(hp, sensor["max_hp"])
    if hp_pct <= 30:
        return "RETREAT", SentryState.RETREAT
    if state is SentryState.RETREAT:
        if hp_pct >= 60:
            return "RETURN", SentryState.RETURN
        return "RETREAT", SentryState.RETREAT
    if state is SentryState.RETURN:
        return "MOVE_BASE", SentryState.PATROL
    if state is SentryState.ENGAGE and not visible:
        if len(frames) >= 3 and not any(frames[-3:]):
            return "SCAN", SentryState.SUSPECT
        return "HOLD_FIRE", SentryState.ENGAGE
    if visible:
        confirmed = len(frames) >= 2 and bool(frames[-2])
        if state is SentryState.ENGAGE or confirmed:
            if distance <= 3:
                return "SHOOT", SentryState.ENGAGE
            action = "MOVE_RIGHT" if robot_type == "HERO" else "MOVE_LEFT"
            return action, SentryState.ENGAGE
        return "SCAN", SentryState.SUSPECT
    if state is SentryState.PATROL:
        return "PATROL_MOVE", SentryState.PATROL
    return "SCAN", SentryState.SUSPECT


# ---------------------------------------------------------------------------
# Q6 巡逻任务（题面 Q6·巡逻契约与验收阈值）
# ---------------------------------------------------------------------------
def _escape_route(grid):
    """Find a bounded shortest escape route without changing the grid."""
    start, target = grid.current_pos, grid.enemy_pos
    queue = deque([start])
    parents = {start: None}
    while queue:
        pos = queue.popleft()
        if pos == target:
            route = deque()
            while parents[pos] is not None:
                previous, direction = parents[pos]
                route.appendleft(direction)
                pos = previous
            return route
        for direction in (Facing.RIGHT, Facing.UP, Facing.LEFT, Facing.DOWN):
            dx, dy = direction.delta
            nxt = (pos[0] + dx, pos[1] + dy)
            if nxt not in parents and not grid.is_blocked(*nxt):
                parents[nxt] = (pos, direction)
                queue.append(nxt)
    return deque()


def run_patrol(grid, max_steps=500):
    """Use greedy steps, switching to a bounded escape route when stalled."""
    steps = 0
    initial_collisions = grid.collision_count
    visited = {grid.current_pos}
    escape = deque()
    while steps < max_steps and grid.fuel > 0 and not grid.found_enemy:
        pos, target = grid.current_pos, grid.enemy_pos
        direction = next_step_toward(pos, target, grid.obstacles, grid.facing)
        if escape:
            direction = escape.popleft()
        else:
            dx, dy = direction.delta
            nxt = (pos[0] + dx, pos[1] + dy)
            distance = abs(pos[0] - target[0]) + abs(pos[1] - target[1])
            remaining = abs(nxt[0] - target[0]) + abs(nxt[1] - target[1])
            if grid.is_blocked(*nxt) or remaining >= distance:
                escape = _escape_route(grid)
                if not escape:
                    break
                direction = escape.popleft()
        order = (Facing.UP, Facing.RIGHT, Facing.DOWN, Facing.LEFT)
        turns = (order.index(direction) - order.index(grid.facing)) % 4
        if turns == 3:
            grid.turn_left()
        else:
            for _ in range(turns):
                grid.turn_right()
        grid.move_forward()
        steps += 1
        visited.add(grid.current_pos)
    return {"steps": steps,
            "collisions": grid.collision_count - initial_collisions,
            "visited_count": len(visited),
            "found_enemy": bool(grid.found_enemy),
            "success": bool(grid.found_enemy)}


def report_to_json(stats):
    """TODO(Q6)：把 stats 序列化为确定性的 JSON 字符串，见题面 Q6 规范。"""
    raise NotImplementedError("Q6 report_to_json：题面 Q6·报告序列化")


# ---------------------------------------------------------------------------
# Bonus：BFS 全局最短路（题面 Bonus·BFS 语义与排行榜）
# ---------------------------------------------------------------------------
def bfs_path_length(start, target, obstacles):
    """TODO(Bonus)：BFS 全局最短路步数；返回语义与边界职责见题面 Bonus 规范。"""
    raise NotImplementedError("Bonus bfs_path_length")


# ---------------------------------------------------------------------------
# 渲染（已提供，demo 专用，不进测试）
# ---------------------------------------------------------------------------
def render_frame(grid, trail=()):
    """ASCII 渲染一帧战场；trail 为走过的格子集合。返回 list[str]。"""
    trail = set(trail)
    rows = []
    for y in range(grid.height - 1, -1, -1):
        row = []
        for x in range(grid.width):
            if (x, y) == grid.current_pos:
                row.append("◉")
            elif (x, y) == grid.enemy_pos:
                row.append("▲")
            elif (x, y) in grid.obstacles:
                row.append("█")
            elif (x, y) in trail:
                row.append("·")
            else:
                row.append(".")
        rows.append("".join(row))
    return rows
