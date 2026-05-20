# ── Disaster Rescue MAS — Symbolic FOL Edition ─────────────────────────────────
# ── Simulation settings ───────────────────────────────────────────────────────
GRID_SIZE: int = 20          # NxN disaster grid

# Robot depot / start position for Cost(r,t) = Distance(r,t) / Speed(r)
ROBOT_START_X: int = 0
ROBOT_START_Y: int = 0
NUM_TASKS: int = 10          # number of tasks to generate
RANDOM_SEED: int = 42        # reproducibility seed (None = fully random)

# ── Priority levels (lower number = higher urgency) ───────────────────────────
PRIORITY_ORDER = {"high": 1, "medium": 2, "low": 3}

# ── Task catalogue  ──────────────────────────────────────────────────────────
#   Each entry: (task_type, priority, required_capability)
TASK_CATALOGUE = [
    ("rescue victim",    "high",   "medical support"),
    ("rescue victim",    "high",   "search and mapping"),
    ("clear debris",     "medium", "heavy debris removal"),
    ("map building",     "low",    "search and mapping"),
    ("deliver medicine", "medium", "medical support"),
]

# ── Robot definitions ─────────────────────────────────────────────────────────
#   Each entry: (robot_id, name, capability, speed)
ROBOT_DEFINITIONS = [
    ("R1", "Search and Mapping Robot",   "search and mapping",   "fast"),
    ("R2", "Medical Support Robot",      "medical support",      "medium"),
    ("R3", "Heavy Debris Removal Robot", "heavy debris removal", "slow"),
]

# ── Speed → simulated seconds per task (used by robot_agents.py) ─────────────
SPEED_DELAY = {"fast": 1, "medium": 2, "slow": 3}

# ── Speed → numeric values for FOL cost formula: Cost(r,t) = Distance(r,t) / Speed(r)
SPEED_VALUES = {"fast": 2.0, "medium": 1.0, "slow": 0.5}
