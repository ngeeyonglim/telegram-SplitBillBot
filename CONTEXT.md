# Domain Glossary

## Core Concepts

### Payer
The user who uploads the receipt photo and is the primary creditor for the session.

### Participant
Any user included in the bill split. This includes the Payer, users @mentioned in the caption, and users who manually "Join" the session.

### Session
A temporary, 5-hour stateful object tied to a specific receipt upload. It tracks the bill data and the list of Participants.

### Unassigned Item
A line item extracted from the receipt that Gemini could not confidently map to a specific Participant based on the user's description.

### Shared Item
An item explicitly mentioned as shared (e.g., "shared the wings") without specific names. These are treated as Unassigned Items and split among all Participants.

### Final Split
The end state of a Session where the total amount is distributed among all Participants, including proportional allocation of tax and service charges.
