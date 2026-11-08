import argparse
def main():
    p=argparse.ArgumentParser(description="Estimate cost per 1,000 requests using the assignment's rate card.")
    p.add_argument("--hourly-replica-cost", type=float, required=True)
    p.add_argument("--replicas", type=int, required=True)
    p.add_argument("--requests-per-second", type=float, required=True)
    a=p.parse_args()
    if min(a.hourly_replica_cost, a.replicas, a.requests_per_second) <= 0:
        p.error("all values must be positive")
    served_per_hour=a.requests_per_second*3600
    cost_1000=(a.hourly_replica_cost*a.replicas/served_per_hour)*1000
    print(f"hourly_cost_all_replicas={a.hourly_replica_cost*a.replicas:.6f}")
    print(f"requests_per_hour={served_per_hour:.2f}")
    print(f"estimated_cost_per_1000_requests={cost_1000:.6f}")
if __name__=="__main__": main()
