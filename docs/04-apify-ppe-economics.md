# 04 — Apify PPE Economics (post-April 1 2025)

## The free-tier reality

Every Apify user account receives $5/month in free platform credits. At $0.02 per tool call, that is 250 free runs per user per month before the first paid dollar flows.

This has three implications for pricing your Actor:

1. **Hobbyists and solo devs may never pay.** Design for this. They are the distribution channel (GitHub stars, forum posts, word of mouth), not the revenue source.
2. **Price for teams and pro users.** A team running 100 audits/day at $0.02 = $60/month. That is the TAM.
3. **The free tier is a feature, not a bug.** The "zero recurring cost for light users" framing is your marketing advantage over always-on VPS MCPs.

## pay_per_event.json structure

```json
{
  "light-read": {
    "eventTitle": "List / lookup call",
    "eventDescription": "Charged for catalog and lookup calls.",
    "eventPriceUsd": 0.005
  },
  "heavy-call": {
    "eventTitle": "Analysis call",
    "eventDescription": "Charged per primary analysis tool call.",
    "eventPriceUsd": 0.02
  }
}
```

Keep the ratio 4:1 (light:heavy). Discovery calls should be cheap so users explore the catalog; execution calls carry the revenue.

## Charging in your tool

```python
@server.tool(annotations=_ANNOTATIONS)
async def my_tool(input: str) -> dict:
    await Actor.charge("heavy-call")  # charge BEFORE doing work
    # ... your logic ...
    return {"type": "text", "text": result}
```

Call `Actor.charge()` at the start of the tool, before any computation. If the tool fails after charging, the user is still charged — this is expected behaviour (the Actor consumed compute). Do not swallow exceptions to avoid charging.

## The startedAt gotcha

When setting PPE pricing via the Apify API, the `startedAt` field must be at least 14 days in the future from the push date. Setting it closer returns:

```
403 cannot-modify-actor-pricing-with-immediate-effect
```

Set it 15-20 days out to be safe. This catches every first-time Actor publisher.

Example (Python):

```python
from datetime import datetime, timedelta, timezone
started_at = (datetime.now(timezone.utc) + timedelta(days=16)).strftime("%Y-%m-%dT%H:%M:%S.000Z")
```

## Docs

- [Apify PPE documentation](https://docs.apify.com/platform/actors/running/pay-per-event)
- [Apify pricing calculator](https://apify.com/pricing)
