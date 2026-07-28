# Code Review Chatbot

**Layer**: Prompt Engineering (2022–2024)

## Goal
Paste code, get feedback on bugs, style, security

## Approach
```
System: You are an expert code reviewer. Analyze code for:
1. Logic errors
2. Security issues
3. Performance problems
4. Style violations

Format response as JSON with severity levels.
```

## What Works
Good for quick feedback on small snippets

## What Breaks
Context—the reviewer doesn't understand your codebase style. Doesn't run tests. Can't learn from your actual code patterns.

## When to Use This Layer
- Demos and prototypes
- One-off analysis
- Interactive experiences where *you* are still in the loop between steps
- Tasks with no state or iteration
