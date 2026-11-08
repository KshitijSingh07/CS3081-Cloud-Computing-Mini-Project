# Public-subnet stateless NACL design

Subnets:
- app: `10.20.0.0/22`
- public: `10.20.4.0/24`
- data: `10.20.5.0/25`
- management: `10.20.5.128/27`
- blocked source: `198.51.100.0/24`

## Required rule logic

Inbound, lowest rule number first:
1. DENY all protocols/ports from `198.51.100.0/24` (must precede web allows).
2. ALLOW TCP destination port 80 from `0.0.0.0/0`.
3. ALLOW TCP destination port 443 from `0.0.0.0/0`.
4. ALLOW TCP destination port 22 only from `10.20.5.128/27`.
5. ALLOW reply traffic from app subnet `10.20.0.0/22` with destination ephemeral ports 1024–65535.
6. DENY everything else.

Outbound:
1. ALLOW TCP destination port 8000 to app subnet `10.20.0.0/22`.
2. ALLOW TCP destination ephemeral ports 1024–65535 to `0.0.0.0/0` for replies to clients.
3. DENY everything else.

A network ACL is stateless: it does not track established connections. Therefore, return packets need explicit rules in the opposite direction. Rule ordering is important because first-match evaluation means a broad allow placed before the abusive-range deny would accidentally permit blocked traffic.

The matching simulator schema is implemented in `network/nacl.json`. Validate it with:

```bash
python tools/nacl_sim.py network/nacl.json network/packets_sample.jsonl --check
```

The sample packet set is a smoke test only; the assessment uses additional hidden packets.
