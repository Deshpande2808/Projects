# Autonomous Trading Hedge Fund (Multi-Agent)

**Layer**: Graph Engineering (July 2026)

## Goal
A fund that trades autonomously, with specialized agents handling analysis, strategy, risk, execution, and compliance.

## Graph Structure
```
NODES (Agents):
  1. DataAgent: Fetches market data, runs technical analysis
  2. StrategyAgent: Backtests strategies, selects trades
  3. RiskAgent: Validates position sizing, checks portfolio constraints
  4. ExecutionAgent: Places trades, monitors fills
  5. ComplianceAgent: Audits all decisions against policies
  6. MonitoringAgent: Watches live performance, flags anomalies
  7. Human: Approves trades > $X value

EDGES (Handoffs & Checks):
  Market Data → DataAgent (observe-decide-act-verify loop)
                ↓
              StrategyAgent (run backtest loop, select top trades)
                ↓
              RiskAgent (validate each trade)
                ├─→ APPROVED → ExecutionAgent
                └─→ REJECTED → back to StrategyAgent (try different strategy)
                ↓
          ComplianceAgent (parallel check: are trades legal/ethical?)
                ├─→ OK → Execute
                └─→ VIOLATION → Escalate to Human
                ↓
          ExecutionAgent (place orders, verify fills)
                ↓
          MonitoringAgent (watch open positions, alert on anomalies)
                ├─→ Normal → Continue
                └─→ RISK DETECTED → Alert Human
```

## Each Agent's Loop

**DataAgent**
- Observe: Market conditions
- Decide: What indicators to compute? Technical, sentiment, macro?
- Act: Fetch data, compute indicators
- Verify: Are calculations correct? Is data fresh (<1 min old)?

**StrategyAgent**
- Observe: Indicators from DataAgent
- Decide: Which strategies apply today? (momentum, mean-reversion, etc)
- Act: Backtest each strategy on recent data
- Verify: Does backtest result beat benchmark? Is it robust to parameter changes?
- Loop: If strategy doesn't beat benchmark, skip it. Only pass winning strategies.

**RiskAgent**
- Observe: Proposed trades from StrategyAgent
- Decide: What's the portfolio impact? What's current exposure to this sector?
- Act: Calculate position size (never > 5% per trade, never > 20% in one stock)
- Verify: Does trade fit within portfolio constraints? Max correlation check?
- If trade too large: Reject, suggest smaller position. StrategyAgent tries different trade.

**ExecutionAgent**
- Observe: Approved trades from RiskAgent
- Decide: Best execution price? Market or limit order?
- Act: Place order
- Verify: Did order fill? At expected price? Within slippage budget?
- If problem: Cancel, retry, or escalate.

**ComplianceAgent**
- Observe: Every trade from ExecutionAgent
- Decide: Is this legal? Does it violate client restrictions? Is insider info involved?
- Act: Audit trade decision + rationale
- Verify: Pass/fail compliance check
- If fail: Escalate immediately, halt trading.

**MonitoringAgent**
- Observe: Open positions, market conditions
- Decide: Are any positions in danger? Is portfolio drifting from strategy?
- Act: Check stop-loss levels, rebalancing needs
- Verify: All positions still within policy?
- If anomaly: Alert human (don't force-close).

## State Across Edges
- Market data (DataAgent → StrategyAgent → RiskAgent)
- Indicators (DataAgent → StrategyAgent)
- Trade proposals (StrategyAgent → RiskAgent → ExecutionAgent)
- Portfolio state (RiskAgent, ExecutionAgent, MonitoringAgent)
- Audit trail (ComplianceAgent watches all)

## When to Use This Layer
- Multiple agents with different expertise
- Workflow requires handoffs (agent A → agent B → agent C)
- Verification chains (each agent checks previous agent's work)
- Multi-step pipelines (data → analysis → decision → action)
- Enterprise-scale (needs audit trails, compliance, observability)

## Build Plan

**MVP**: Multi-agent paper-trading fund: Data → Strategy → Risk → Compliance → Execution → Monitoring, with human gate for large notional.

| Milestone | Deliverable |
|-----------|-------------|
| 1. Agent roles | Clear contracts; Risk/Compliance as hard gates |
| 2. Rejection loops | Risk reject → Strategy replans |
| 3. Paper execution | Simulated fills + portfolio state |
| 4. Compliance audit | Every trade decision logged for review |

**Done when**: No trade executes without Risk+Compliance OK; large trades require human; monitoring alerts on anomalies.
**Estimate**: 4 weeks · **Target finish**: May 21, 2027
