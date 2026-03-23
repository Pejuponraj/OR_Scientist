import gurobipy as gp
from gurobipy import GRB

# -----------------------------
# Data
# -----------------------------

crew_members = [
    "C1", "C2", "C3", "C4",
    "C5", "C6", "C7", "C8"
]

flights = {
    "F1":  {"start": 6,  "end": 8},
    "F2":  {"start": 7,  "end": 9},
    "F3":  {"start": 8,  "end": 10},
    "F4":  {"start": 9,  "end": 11},
    "F5":  {"start": 10, "end": 12},
    "F6":  {"start": 11, "end": 13},
    "F7":  {"start": 12, "end": 14},
    "F8":  {"start": 13, "end": 15},
    "F9":  {"start": 14, "end": 16},
    "F10": {"start": 15, "end": 17},
}

# Assignment cost for each crew-flight pair
cost = {
    ("C1", "F1"): 8,  ("C1", "F2"): 6,  ("C1", "F3"): 7,  ("C1", "F4"): 9,  ("C1", "F5"): 8,
    ("C1", "F6"): 7,  ("C1", "F7"): 6,  ("C1", "F8"): 9,  ("C1", "F9"): 8,  ("C1", "F10"): 7,

    ("C2", "F1"): 7,  ("C2", "F2"): 8,  ("C2", "F3"): 6,  ("C2", "F4"): 7,  ("C2", "F5"): 9,
    ("C2", "F6"): 8,  ("C2", "F7"): 7,  ("C2", "F8"): 6,  ("C2", "F9"): 9,  ("C2", "F10"): 8,

    ("C3", "F1"): 9,  ("C3", "F2"): 7,  ("C3", "F3"): 8,  ("C3", "F4"): 6,  ("C3", "F5"): 7,
    ("C3", "F6"): 9,  ("C3", "F7"): 8,  ("C3", "F8"): 7,  ("C3", "F9"): 6,  ("C3", "F10"): 8,

    ("C4", "F1"): 6,  ("C4", "F2"): 9,  ("C4", "F3"): 7,  ("C4", "F4"): 8,  ("C4", "F5"): 6,
    ("C4", "F6"): 7,  ("C4", "F7"): 9,  ("C4", "F8"): 8,  ("C4", "F9"): 7,  ("C4", "F10"): 6,

    ("C5", "F1"): 8,  ("C5", "F2"): 7,  ("C5", "F3"): 9,  ("C5", "F4"): 7,  ("C5", "F5"): 8,
    ("C5", "F6"): 6,  ("C5", "F7"): 7,  ("C5", "F8"): 9,  ("C5", "F9"): 8,  ("C5", "F10"): 7,

    ("C6", "F1"): 7,  ("C6", "F2"): 8,  ("C6", "F3"): 7,  ("C6", "F4"): 9,  ("C6", "F5"): 6,
    ("C6", "F6"): 8,  ("C6", "F7"): 7,  ("C6", "F8"): 6,  ("C6", "F9"): 8,  ("C6", "F10"): 9,

    ("C7", "F1"): 9,  ("C7", "F2"): 6,  ("C7", "F3"): 8,  ("C7", "F4"): 7,  ("C7", "F5"): 9,
    ("C7", "F6"): 7,  ("C7", "F7"): 6,  ("C7", "F8"): 8,  ("C7", "F9"): 7,  ("C7", "F10"): 6,

    ("C8", "F1"): 6,  ("C8", "F2"): 7,  ("C8", "F3"): 9,  ("C8", "F4"): 8,  ("C8", "F5"): 7,
    ("C8", "F6"): 6,  ("C8", "F7"): 8,  ("C8", "F8"): 7,  ("C8", "F9"): 9,  ("C8", "F10"): 8,
}

# Maximum number of flights per crew member
max_flights_per_crew = 2

# -----------------------------
# Helper function
# -----------------------------
def overlap(f1, f2):
    s1, e1 = flights[f1]["start"], flights[f1]["end"]
    s2, e2 = flights[f2]["start"], flights[f2]["end"]
    return max(s1, s2) < min(e1, e2)

# -----------------------------
# Model
# -----------------------------
model = gp.Model("Flight_Crew_Scheduling")

# Silence solver output if needed
model.setParam("OutputFlag", 1)

# Decision variables:
# x[c, f] = 1 if crew member c is assigned to flight f, else 0
x = model.addVars(crew_members, flights.keys(), vtype=GRB.BINARY, name="x")

# Objective: minimize total assignment cost
model.setObjective(
    gp.quicksum(cost[(c, f)] * x[c, f] for c in crew_members for f in flights),
    GRB.MINIMIZE
)

# -----------------------------
# Constraints
# -----------------------------

# 1. Each flight must be assigned exactly one crew member
for f in flights:
    model.addConstr(
        gp.quicksum(x[c, f] for c in crew_members) == 1,
        name=f"Cover_{f}"
    )

# 2. No crew member can handle overlapping flights
flight_list = list(flights.keys())
for c in crew_members:
    for i in range(len(flight_list)):
        for j in range(i + 1, len(flight_list)):
            f1 = flight_list[i]
            f2 = flight_list[j]
            if overlap(f1, f2):
                model.addConstr(
                    x[c, f1] + x[c, f2] <= 1,
                    name=f"NoOverlap_{c}_{f1}_{f2}"
                )

# 3. Limit the number of flights assigned to each crew member
for c in crew_members:
    model.addConstr(
        gp.quicksum(x[c, f] for f in flights) <= max_flights_per_crew,
        name=f"MaxFlights_{c}"
    )

# -----------------------------
# Solve
# -----------------------------
model.optimize()

# -----------------------------
# # -----------------------------
# Results (Save to file)
# -----------------------------
with open("solution_output.txt", "w") as file:

    if model.status == GRB.OPTIMAL:
        file.write("Optimal Solution Found\n")
        file.write(f"Minimum Total Cost: {model.objVal:.2f}\n\n")

        file.write("Flight Assignments:\n")
        for f in flights:
            assigned = False
            for c in crew_members:
                if x[c, f].X > 0.5:
                    file.write(f"{f} ({flights[f]['start']}:00 - {flights[f]['end']}:00) -> {c}\n")
                    assigned = True
            if not assigned:
                file.write(f"{f} -> No crew assigned\n")

        file.write("\nCrew-wise Schedule:\n")
        for c in crew_members:
            assigned_flights = [f for f in flights if x[c, f].X > 0.5]
            file.write(f"{c}: {assigned_flights}\n")

    else:
        file.write("No optimal solution found.\n")

print("✅ Results saved to solution_output.txt")
