import numpy as np
import pandas as pd
import plotly.express as px

acmilan_xgs = np.array([
    0.07, 0.04, 0.02, 0.02, 0.14, 0.14, 0.04, 0.08, 0.21,
    0.08, 0.05, 0.03, 0.04, 0.05, 0.11, 0.03, 0.06, 0.06,
    0.06, 0.02, 0.22, 0.04, 0.28, 0.06
    ])
cremonese_xgs = np.array([
    0.04, 0.02, 0.05, 0.09
    ])

print(f"AC Milan: {len(acmilan_xgs)} shots, xG: {acmilan_xgs.sum()}\nCremonese: {len(cremonese_xgs)} shots, xG: {cremonese_xgs.sum()}")

def simulate_match(team_a_xgs, team_b_xgs):
    team_a_shots_simulation = np.random.random_sample(len(team_a_xgs))
    team_b_shots_simulation = np.random.random_sample(len(team_b_xgs))

    team_a_goals = (team_a_shots_simulation <= team_a_xgs).sum()
    team_b_goals = (team_b_shots_simulation <= team_b_xgs).sum()

    return [team_a_goals, team_b_goals]

n_times = 1000000
result = []
for i in range(n_times):
    result.append(simulate_match(team_a_xgs=acmilan_xgs, team_b_xgs=cremonese_xgs))

result = pd.DataFrame(result, columns=["AC Milan", "Cremonese"])
print(result)

fig = px.histogram(result["AC Milan"])
fig.update_layout(title="AC Milan goals")
fig.show()

fig = px.histogram(result["Cremonese"])
fig.update_layout(title="Cremonese goals")
fig.show()

fig = px.density_heatmap(data_frame=result, x="AC Milan", y="Cremonese", marginal_x="histogram", marginal_y="histogram")
fig.show()

result["result"] = result.apply(lambda x: f"{x['AC Milan']}-{x['Cremonese']}", axis=1)
fig = px.histogram(data_frame=result, x="result", histnorm="probability")
fig.show()