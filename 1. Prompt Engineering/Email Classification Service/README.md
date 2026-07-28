# Email Classification Service

**Layer**: Prompt Engineering (2022–2024)

## Goal
Automatically categorize customer emails into [Support/Sales/Billing/Other]

## Approach
```
System: You are an email classifier. Analyze emails and categorize them strictly.
Examples:
- Email: "My login stopped working" → Category: Support
- Email: "How much is the Pro plan?" → Category: Sales

Email to classify: [USER_EMAIL]
Response: {"category": "...", "confidence": 0.95, "reason": "..."}
```

## Limitations
Adding new categories requires prompt rewriting. No learning from misclassifications. If email volume spikes, you're paying for repeated inference, not building infrastructure.

## When to Use This Layer
- Demos and prototypes
- One-off analysis
- Interactive experiences where *you* are still in the loop between steps
- Tasks with no state or iteration
