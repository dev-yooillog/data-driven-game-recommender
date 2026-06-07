import pandas as pd
import numpy as np
from scipy import stats

def simulate_experiment(n_per_group: int = 5000,
                        control_cvr: float = 0.032,
                        treatment_cvr: float = 0.039,
                        control_arpu: float = 2.1,
                        treatment_arpu: float = 2.58,
                        seed: int = 42) -> dict:
    rng = np.random.default_rng(seed)

    control_conversions = rng.binomial(1, control_cvr, n_per_group)
    treatment_conversions = rng.binomial(1, treatment_cvr, n_per_group)

# ARPU: 구매자 기준 정규분포 시뮬레이션
    control_revenue = rng.normal(control_arpu, 0.8, n_per_group)
    treatment_revenue = rng.normal(treatment_arpu, 0.9, n_per_group)

    return {
        "control_conversions": control_conversions,
        "treatment_conversions": treatment_conversions,
        "control_revenue": control_revenue,
        "treatment_revenue": treatment_revenue,
    }

def test_cvr(control: np.ndarray, treatment: np.ndarray) -> dict:
    n = len(control)
    contingency = [
        [control.sum(), n - control.sum()],
        [treatment.sum(), n - treatment.sum()],
    ]
    chi2, p, _, _ = stats.chi2_contingency(contingency)

    control_rate = control.mean()
    treatment_rate = treatment.mean()
    lift = (treatment_rate / control_rate - 1) * 100

    return {
        "control_cvr": round(control_rate * 100, 2),
        "treatment_cvr": round(treatment_rate * 100, 2),
        "lift_pct": round(lift, 2),
        "chi2": round(chi2, 4),
        "p_value": round(p, 6),
        "significant": p < 0.05,
    }

def test_arpu(control: np.ndarray, treatment: np.ndarray) -> dict:
    t_stat, p = stats.ttest_ind(treatment, control, equal_var=False)
    lift = (treatment.mean() / control.mean() - 1) * 100

    return {
        "control_arpu": round(control.mean(), 2),
        "treatment_arpu": round(treatment.mean(), 2),
        "lift_pct": round(lift, 2),
        "t_stat": round(t_stat, 4),
        "p_value": round(p, 6),
        "significant": p < 0.05,
    }

def run_full_analysis(sim: dict) -> dict:
    cvr_result = test_cvr(sim["control_conversions"], sim["treatment_conversions"])
    arpu_result = test_arpu(sim["control_revenue"], sim["treatment_revenue"])
    return {"cvr": cvr_result, "arpu": arpu_result}