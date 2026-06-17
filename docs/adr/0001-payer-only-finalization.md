# ADR 0001: Payer-Only Session Finalization

## Status
Accepted

## Context
In a group chat, multiple users can interact with the bot. If anyone could "Finalize" a session, it could lead to premature calculations before all participants have joined or been correctly assigned.

## Decision
We will restrict the `Finalize` action (triggered by the inline button) to the **Payer** (the user who originally uploaded the receipt).

## Consequences
- **Security:** Prevents accidental or malicious termination of a session by non-participants.
- **Accuracy:** Ensures the person most responsible for the bill's correctness has the final say.
- **UX:** Other users who try to finalize will see an alert explaining that only the Payer has this authority.
