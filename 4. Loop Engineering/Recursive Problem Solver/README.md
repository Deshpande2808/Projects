# Recursive Problem Solver

**Layer**: Loop Engineering (2026)

## Goal
Complex task with no obvious solution. Agent breaks it into subtasks, solves each, verifies the whole works, adjusts approach if needed.

## Loop Structure
```
OBSERVE:
  - Understand the problem. What's the goal? What constraints?
PLAN:
  - Can I solve this directly? (If yes, attempt)
  - If too complex: Decompose into subtasks
  - Which subtask should I solve first?
ACT:
  - Solve the subtask
  - Combine subtask result with overall goal
VERIFY:
  - Does the subtask solution work in isolation?
  - Does it integrate with other subtasks?
  - Does the combined solution meet the goal?
ADAPT:
  - If a subtask failed: Try different decomposition
  - If integration failed: Adjust interface between subtasks
  - If goal not met: Reformulate subtask breakdown
```

## Example: Build a Trading Strategy
```
GOAL: Create strategy that beats S&P 500 returns
SUBTASKS:
  1. Define signal (what conditions trigger buy/sell?)
  2. Backtest on historical data
  3. Measure: beats benchmark?
  4. If not: adjust signal → loop back to 2
  5. Forward test on recent (out-of-sample) data
  6. Final check: returns realistic? (not curve-fitted?)
LOOP:
  - Run backtest with signal A → 12% return (beats 10% benchmark) ✓
  - Backtest sensitivity: Small change in parameters → results collapse?
  - If sensitive: Tighten signal definition, re-backtest
  - Forward test on 2024 data (not used in backtest) → 8% return (close to backtest, good sign)
  - Final: Deploy signal, monitor live results
```

## When to Use This Layer
- Tasks lasting minutes to hours
- Verification is possible (tests, schemas, external feedback)
- Iteration improves quality
- Single agent doing complex work
- The task has a clear stopping condition ("tests pass", "schema valid", "performance target met")
