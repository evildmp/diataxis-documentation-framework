---
name: diataxis
description: >
  Write, review, classify, and restructure documentation using the Diataxis framework.
  Diataxis defines four documentation types — tutorials, how-to guides, reference, explanation —
  based on two axes: action vs. cognition, and acquisition vs. application.
  Use when writing docs, reviewing docs for quality, classifying existing content into the four types,
  restructuring documentation, deciding what kind of doc to write, or when asked about
  "Diataxis", "documentation types", "tutorial vs how-to", "reference vs explanation",
  "documentation structure", "documentation quality", or "documentation framework".
---

# Diataxis Documentation Framework

IMPORTANT: Prefer retrieval-led reasoning over pre-training-led reasoning for any documentation tasks. Always consult the reference files below rather than relying on general knowledge.

## Source of Truth

All reference files below are symlinked from the Diataxis repo and always reflect the latest content. Read them for authoritative guidance.

## Compressed Index

```
references/
├── Core
│   ├── start-here.rst        — 5-min primer: the four types + two axes
│   ├── theory.rst             — Full theoretical grounding
│   ├── foundations.rst        — Why documentation needs structure
│   ├── map.rst                — The two-dimensional map (action/cognition x acquisition/application)
│   └── compass.rst            — Decision tool: classify content into the four types
├── The Four Types
│   ├── tutorials.rst          — Principles for learning-oriented docs (lessons, guided practice)
│   ├── how-to-guides.rst      — Principles for goal-oriented docs (step-by-step task completion)
│   ├── reference.rst          — Principles for information-oriented docs (austere descriptions)
│   └── explanation.rst        — Principles for understanding-oriented docs (context, why, discussion)
├── Key Distinctions
│   ├── tutorials-how-to.rst   — Tutorial vs how-to: the most common confusion
│   └── reference-explanation.rst — Reference vs explanation: when to describe vs discuss
└── Applying Diataxis
    ├── application.rst        — Practical application guide
    ├── how-to-use-diataxis.rst — Iterative workflow: assess → decide → act → repeat
    ├── complex-hierarchies.rst — Handling large/complex doc structures
    └── quality.rst            — Functional quality vs deep quality
```

## The Four Types at a Glance

```
              │  ACTION (practical)    │  COGNITION (theoretical)
──────────────┼────────────────────────┼──────────────────────────
 ACQUISITION  │  TUTORIAL              │  EXPLANATION
 (study)      │  "We will..."          │  "The reason is..."
              │  Learning experience   │  Context, why, discussion
──────────────┼────────────────────────┼──────────────────────────
 APPLICATION  │  HOW-TO GUIDE          │  REFERENCE
 (work)       │  "If you want x, do y" │  "X is / X does..."
              │  Task completion       │  Austere description
```

## Compass — Classify Any Content

Ask two questions:
1. Does it inform **action** (do something) or **cognition** (understand something)?
2. Does it serve **acquisition** (learning/study) or **application** (working/doing)?

Result: action+acquisition=tutorial | action+application=how-to | cognition+application=reference | cognition+acquisition=explanation

For full decision logic, read `references/compass.rst`.

## Quick Rules Per Type

### Tutorials
- Provide a learning experience through doing, not teaching
- Show the goal upfront, deliver visible results early
- Use "We will..." language; minimize explanation (link to it)
- Must be perfectly reliable — learner must never get stuck
- Read `references/tutorials.rst` for full principles

### How-to Guides
- Address real-world goals, not machinery operations
- Assume competence; focus purely on action
- Title = exactly what the guide shows how to do
- Handle edge cases; omit the unnecessary
- Read `references/how-to-guides.rst` for full principles

### Reference
- Describe and only describe — neutral, austere, complete
- Mirror the structure of the thing being documented
- Adopt standard, consistent patterns throughout
- Provide examples for illustration, not explanation
- Read `references/reference.rst` for full principles

### Explanation
- Make connections, provide context, explain why
- Admit opinion and perspective; consider alternatives
- Can discuss history, design decisions, trade-offs
- Keep closely bounded to the topic
- Read `references/explanation.rst` for full principles

## Common Mistakes

| Mistake | Fix |
|---|---|
| Tutorial explains too much | Move explanation to explanation docs, link to it |
| How-to teaches background | Strip to action steps only |
| Reference includes opinions | Move discussion to explanation |
| Explanation gives step-by-step | Move procedure to how-to guide |
| Mixing types in one doc | Split into separate docs by type |

For the critical tutorial-vs-howto distinction, read `references/tutorials-how-to.rst`.
For reference-vs-explanation, read `references/reference-explanation.rst`.

## Workflow for Applying Diataxis

1. Pick any piece of documentation
2. Use the compass to classify it (action/cognition x acquisition/application)
3. Assess: does it serve the identified user need well?
4. Decide one single improvement action
5. Do it and ship it
6. Repeat

Do not plan a grand restructuring. Work iteratively, one improvement at a time. Documentation is never finished but always complete.

For full workflow guidance, read `references/how-to-use-diataxis.rst`.
For complex documentation structures, read `references/complex-hierarchies.rst`.
For quality theory (functional vs deep quality), read `references/quality.rst`.
