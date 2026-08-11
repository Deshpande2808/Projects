# Enhanced Multi-Agent Stock Analyzer (Your Project)

**Layer**: Harness Engineering (2026)

## Current State
LangGraph agent integrated with Zerodha Kite API.

## Harness Improvements

### Tool Orchestration
- Rate limiting (don't exceed Kite API quotas)
- Order validation (never place order if data is stale > 5 min)
- Position limits (max 10 concurrent positions, max 20% portfolio in one stock)
- Slippage checks (don't buy if asking price > signal price + threshold)

### Guardrails
- Position size: Never trade > 5% of portfolio per signal
- Confidence threshold: Only execute if confidence > 75%
- Manual approval: For large trades (> 10% portfolio value), require human sign-off
- Stop loss enforcement: Always set stop loss before buying

### Verification Loop
- Observe: Market data, technical signals
- Decide: Buy/sell/hold. Size the trade.
- Act: Place order (if manual approval passed)
- Verify: Order filled correctly? Position size in range? Stop loss hit?
- If error: Cancel and escalate

### Memory
- Portfolio state (current positions, avg entry price, % gains)
- Trade history (recent trades, success rate)
- Performance metrics (win rate, average return, max drawdown)
- Learned preferences (this user doesn't like volatile stocks)

### Observability
- Trade journal: Every decision, data, rationale
- Performance dashboard: Returns, Sharpe ratio, drawdown
- Audit: All trades (what algorithm made this? What were the inputs?)
- Alerts: If performance degrades or portfolio drifts from strategy

## Success Criteria
- Never execute without passing all guardrails
- Human can audit any trade decision via trace
- Risk limits always enforced
- Recovers gracefully from Kite API errors

## When to Use This Layer
- Multi-hour or multi-day agent runs
- Autonomous execution (agent runs while you sleep)
- Production systems (must be reliable)
- Safety-critical decisions (trading, infrastructure, customer data)
- Compliance requirements (audit trails, approval gates)

## Build Plan

**MVP**: Existing Zerodha/LangGraph analyzer hardened with guardrails, traces, and risk limits — trustworthy enough for paper/autonomous overnight runs.

| Milestone | Deliverable |
|-----------|-------------|
| 1. Observability | Decision journal + traces for every signal/order |
| 2. Guardrails | Position size, confidence threshold, stale-data block, large-trade approval |
| 3. Verification | Fill/size/stop-loss checks; cancel + escalate on failure |
| 4. Soak test | Multi-day paper run; metrics + incident log |

**Done when**: No order bypasses guardrails; every trade is auditable; Kite errors recover without silent bad state.
**Estimate**: 2 weeks · **Target finish**: Nov 1, 2026

## Implementation Progression (from source doc)

### Phase 1: Strengthen Harness (Month 1-2)
- Add guardrails: position limits, confidence thresholds, manual approval gates
- Add observability: trade journal, performance dashboard, audit logs
- Goal: Make it production-ready, trustworthy enough to run autonomous overnight

### Quick Wins
- Week 1: Document + trace every decision, setup observability dashboard
- Week 2: Add guardrails (position limits, confidence thresholds, manual approval for large trades)
- Week 3: First verification loop (e.g. code review agent pattern)
- Week 4: Multi-day run — set loose for 1 week, collect metrics, debug issues found
