# Issue 3: Secure Finalization & Proportional Split

## What to build
Implement the final calculation and summary phase:
1. Provide a "✅ Finalize" button visible only to the Payer.
2. Restrict the "Finalize" action to the user ID that uploaded the receipt.
3. Calculate the total for each participant, including a proportional share of tax and service charges.
4. Output a clean, readable text summary listing everyone's total due to the Payer.

## Acceptance criteria
- [x] "Finalize" button only works for the Payer.
- [x] Proportional math correctly distributes tax/tip based on base consumption.
- [x] Final summary displays totals rounded to 2 decimal places.
- [x] The sum of participant totals matches the receipt total (within rounding error).

## Blocked by
- [docs/issues/002-interactive-participation.md](002-interactive-participation.md)
