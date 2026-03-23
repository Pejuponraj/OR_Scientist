import pandas as pd
import numpy as np
import gurobipy as gp
from gurobipy import GRB
import matplotlib.pyplot as plt

# Load data
mean_returns = pd.read_csv("mean_returns.csv", index_col=0)
cov_matrix = pd.read_csv("cov_matrix.csv", index_col=0)

r = mean_returns.values.flatten()
Sigma = cov_matrix.values
asset_names = list(mean_returns.index)

n = len(r)

print("Mean returns:", r)
print("Asset names:", asset_names)

# Target return range
r_min = min(r)
r_max = max(r)

target_returns = np.linspace(r_min, r_max, 20)

risks = []
realized_returns = []
weights_list = []

for target in target_returns:
    m = gp.Model("Efficient_Frontier")
    m.setParam("OutputFlag", 0)  # silence solver output

    x = m.addVars(n, lb=0, ub=1, name="x")

    # Quadratic risk objective
    risk_expr = gp.quicksum(
        Sigma[i][j] * x[i] * x[j]
        for i in range(n)
        for j in range(n)
    )

    m.setObjective(risk_expr, GRB.MINIMIZE)

    # Return constraint
    m.addConstr(
        gp.quicksum(r[i] * x[i] for i in range(n)) >= target,
        name="target_return"
    )

    # Full investment
    m.addConstr(
        gp.quicksum(x[i] for i in range(n)) == 1,
        name="budget"
    )

    m.optimize()

    if m.status == GRB.OPTIMAL:
        w = np.array([x[i].X for i in range(n)])
        port_return = np.dot(r, w)
        port_variance = w @ Sigma @ w
        port_risk = np.sqrt(port_variance)

        realized_returns.append(port_return)
        risks.append(port_risk)
        weights_list.append(w)

# Plot Efficient Frontier
plt.figure(figsize=(8, 6))
plt.plot(risks, realized_returns, marker='o')
plt.xlabel("Portfolio Risk (Standard Deviation)")
plt.ylabel("Portfolio Return")
plt.title("Efficient Frontier")
plt.grid(True)
plt.show()

# Print a few portfolio points
print("\nSample Efficient Frontier Portfolios:")
for i in range(min(5, len(weights_list))):
    print(f"\nPortfolio {i+1}")
    print(f"Return: {realized_returns[i]:.8f}")
    print(f"Risk  : {risks[i]:.8f}")
    for j in range(n):
        print(f"  {asset_names[j]}: {weights_list[i][j]:.4f}")