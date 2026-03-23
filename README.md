# OR_Scientist
Mini Projects
# Flight Crew Scheduling using Gurobi

## Overview
This project solves a flight crew scheduling problem using Mixed Integer Linear Programming (MILP) with Gurobi.

## Problem
Assign 8 crew members to 10 flights while:
- covering every flight
- preventing overlapping assignments
- limiting workload for each crew member
- minimizing assignment cost

## Tools
- Python
- Gurobi

## Optimization Model
Binary decision variables are used to determine whether a crew member is assigned to a flight.

## Constraints
1. Each flight must have exactly one crew member
2. No crew member can be assigned to overlapping flights
3. Each crew member can handle at most 2 flights

## Applications
- airline crew scheduling
- workforce allocation
- operations research
- scheduling optimization
