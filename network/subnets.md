# VLSM subnet allocation

Parent block: `10.20.0.0/16`. Allocate largest to smallest, contiguously.

| Subnet | Required hosts | Smallest prefix | Network | Usable range | Broadcast | Usable hosts |
|---|---:|---:|---|---|---|---:|
| app | 1,000 | /22 | 10.20.0.0 | 10.20.0.1–10.20.3.254 | 10.20.3.255 | 1,022 |
| public | 250 | /24 | 10.20.4.0 | 10.20.4.1–10.20.4.254 | 10.20.4.255 | 254 |
| data | 100 | /25 | 10.20.5.0 | 10.20.5.1–10.20.5.126 | 10.20.5.127 | 126 |
| management | 20 | /27 | 10.20.5.128 | 10.20.5.129–10.20.5.158 | 10.20.5.159 | 30 |

Calculations:
- 1,000 hosts: 2^10 - 2 = 1,022, therefore /22.
- 250 hosts: 2^8 - 2 = 254, therefore /24.
- 100 hosts: 2^7 - 2 = 126, therefore /25.
- 20 hosts: 2^5 - 2 = 30, therefore /27.

The next subnet starts at the first correctly aligned network boundary after the previous subnet.
