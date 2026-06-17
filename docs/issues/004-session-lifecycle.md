# Issue 4: Session Lifecycle & Stability

## What to build
Ensure the bot is robust and self-cleaning:
1. Implement automatic session expiration after 5 hours using `TTLCache`.
2. Add comprehensive error handling for blurry photos, network timeouts, and Gemini parsing failures.
3. Ensure temporary files (downloaded photos) are deleted immediately after processing.

## Acceptance criteria
- [x] Sessions are automatically removed from memory after 5 hours.
- [x] User receives a helpful error message if receipt processing fails.
- [x] Temporary image files do not persist in the filesystem.

## Blocked by
- [docs/issues/003-secure-finalization.md](003-secure-finalization.md)
