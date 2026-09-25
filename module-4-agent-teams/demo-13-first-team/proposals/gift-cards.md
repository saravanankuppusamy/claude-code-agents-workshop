# Proposal: Tidewater gift cards

- Customers buy digital gift cards (£10–£200) and email them to a recipient.
- Recipient redeems a 16-character code at checkout; partial balances carry over.
- Cards never expire (UK consumer expectation), stored as a balance on a `gift_cards` table.
- Codes are generated with `random.choice` over A–Z0–9.
- Launch target: 4 weeks before the holiday season. One backend engineer, one designer.
