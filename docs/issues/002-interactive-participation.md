# Issue 2: Interactive Participation

## What to build
Enhance the session flow to handle unassigned or shared items through user interaction.
1. The bot should display a list of "Unassigned Items" (items not mapped by Gemini).
2. Provide a "🙋 Join Split" inline button.
3. Maintain a set of "Joined Users" in the session state.
4. Update the session list as users interact with the button.

## Acceptance criteria
- [x] Inline keyboard with "Join Split" appears after receipt processing.
- [x] Clicking "Join Split" adds the user to the session's participant list.
- [x] The bot provides feedback (callback query answer) upon joining.
- [x] Unassigned items are correctly earmarked for the group of joined users.

## Blocked by
- [docs/issues/001-basic-receipt-mapping.md](001-basic-receipt-mapping.md)
