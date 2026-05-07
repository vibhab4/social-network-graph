import pandas as pd

edges = []
with open("facebook_combined.txt") as f:
    for line in f:
        if line.startswith("#") or not line.strip():
            continue
        a, b = line.strip().split()
        edges.append((int(a), int(b)))

df = pd.DataFrame(edges, columns=["user1", "user2"])
df.to_csv("facebook_edges.csv", index=False)
print(f"Done! {len(df)} edges saved to facebook_edges.csv")