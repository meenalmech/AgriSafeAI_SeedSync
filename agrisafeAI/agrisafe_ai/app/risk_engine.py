from dataclasses import dataclass, field
from .seed import load_chemical


@dataclass
class RiskResult:
    score: int
    level: str
    decision: str
    reasons: list[str] = field(default_factory=list)
    actions: list[str] = field(default_factory=list)
    rules: list[str] = field(default_factory=list)
    blockers: list[str] = field(default_factory=list)


def assess(
    task: str,
    crop: str,
    temperature_c: float,
    humidity_pct: float,
    wind_kmh: float,
    rain_probability_pct: float,
    worker_exposure_hours: float,
    ppe_complete: bool,
    chemical: str | None,
    growth_stage: str | None = None,
    equipment: str | None = None,
    workers_count: int = 1,
    vulnerability_flags: list[str] | None = None,
) -> RiskResult:
    task_l = task.lower()
    score = 0
    reasons: list[str] = []
    actions: list[str] = []
    rules: list[str] = []
    blockers: list[str] = []
    vulnerability_flags = vulnerability_flags or []

    outdoor = True
    spray = any(x in task_l for x in ["spray", "pesticide", "chemical application"])
    machinery = any(x in task_l for x in ["tractor", "machinery", "machine"])

    if temperature_c >= 35:
        score += 25
        reasons.append("Very high temperature increases heat exposure risk.")
        actions.append("Move the task to a cooler period and increase rest and hydration controls.")
        rules.append("HEAT_HIGH")
    elif temperature_c >= 32:
        score += 15
        reasons.append("High temperature increases heat exposure risk.")
        actions.append("Schedule breaks, hydration and a cooler work window.")
        rules.append("HEAT_ELEVATED")

    if humidity_pct >= 80 and temperature_c >= 30:
        score += 10
        reasons.append("High humidity combined with heat can reduce the body's ability to cool.")
        actions.append("Increase rest and hydration controls.")
        rules.append("HUMIDITY_HEAT")

    if spray:
        if wind_kmh >= 20:
            score += 30
            reasons.append("Strong wind can increase spray drift risk.")
            actions.append("Do not spray in strong wind. Reassess before starting.")
            rules.append("SPRAY_WIND_HIGH")
        elif wind_kmh >= 12:
            score += 20
            reasons.append("Elevated wind can increase spray drift risk.")
            actions.append("Reassess wind immediately before spraying and follow the product label.")
            rules.append("SPRAY_WIND_ELEVATED")
        if rain_probability_pct >= 70:
            score += 20
            reasons.append("High rain probability makes the planned spraying window unfavorable.")
            actions.append("Consider a later dry window and follow the product label for rain restrictions.")
            rules.append("SPRAY_RAIN_HIGH")
        elif rain_probability_pct >= 40:
            score += 10
            reasons.append("Rain probability is elevated for a weather-sensitive spraying task.")
            actions.append("Check the short-term forecast again immediately before spraying.")
            rules.append("SPRAY_RAIN_ELEVATED")

        if not chemical:
            blockers.append("Chemical identity and its label/SDS were not provided.")
            rules.append("CHEMICAL_MISSING")
        else:
            profile = load_chemical(chemical)
            if profile:
                score += int(profile.get("hazard_score", 0))
                reasons.append(f"Chemical hazard profile contributes {profile.get('hazard_score', 0)} risk points.")
                rules.append("CHEMICAL_PROFILE")
            else:
                blockers.append("The chemical could not be verified against the configured reference data.")
                rules.append("CHEMICAL_UNVERIFIED")

        if not ppe_complete:
            blockers.append("Required PPE has not been confirmed as complete.")
            rules.append("PPE_INCOMPLETE")
            actions.append("Confirm all PPE required by the product label/SDS before starting.")

    if worker_exposure_hours >= 6:
        score += 20
        reasons.append("Long prior outdoor exposure increases worker exposure risk.")
        actions.append("Allow a recovery period before additional physically demanding outdoor work.")
        rules.append("WORKER_EXPOSURE_HIGH")
    elif worker_exposure_hours >= 4:
        score += 10
        reasons.append("Several hours of prior outdoor work increase exposure risk.")
        actions.append("Take a recovery break and reassess worker readiness.")
        rules.append("WORKER_EXPOSURE_ELEVATED")

    if vulnerability_flags:
        score += min(15, len(vulnerability_flags) * 5)
        reasons.append("Worker vulnerability information requires additional controls before outdoor work.")
        actions.append("Review worker suitability, supervision and task controls before starting.")
        rules.append("WORKER_VULNERABILITY")

    if growth_stage and any(token in (growth_stage or "").lower() for token in ["flower", "fruit", "pod", "grain", "maturity"]):
        score += 8
        reasons.append("The crop growth stage increases sensitivity to drift and residue exposure.")
        actions.append("Reduce drift risk and check the crop stage-specific label restrictions before proceeding.")
        rules.append("CROP_STAGE_SENSITIVE")

    if equipment and any(token in (equipment or "").lower() for token in ["drone", "mist", "airblast", "boom"]):
        score += 10
        reasons.append("The selected equipment can increase exposure and drift risk under marginal conditions.")
        actions.append("Use a lower drift-risk method or adjust equipment settings before starting.")
        rules.append("EQUIPMENT_HIGH_DRIFT")

    if workers_count >= 8:
        score += 8
        reasons.append("Large crew size increases coordination and supervision pressure for a risky task.")
        actions.append("Assign a dedicated supervisor and shorten the working window to maintain control.")
        rules.append("WORKERS_HIGH_COUNT")

    if machinery and wind_kmh >= 25:
        score += 15
        reasons.append("High wind can make machinery and field operations more difficult.")
        actions.append("Reassess operating conditions and follow equipment safety procedures.")
        rules.append("MACHINERY_WIND")

    if outdoor and rain_probability_pct >= 80:
        score += 10
        reasons.append("Very high rain probability increases uncertainty for outdoor work.")
        rules.append("OUTDOOR_RAIN_HIGH")

    score = min(score, 100)

    if blockers:
        level = "INCOMPLETE"
        decision = "AVOID"
        actions.insert(0, "Do not treat this assessment as a safe-to-proceed decision until the missing information is verified.")
    elif score <= 30:
        level, decision = "LOW", "PROCEED"
    elif score <= 55:
        level, decision = "MODERATE", "MODIFY"
    elif score <= 75:
        level, decision = "HIGH", "DELAY"
    else:
        level, decision = "CRITICAL", "AVOID"

    if not reasons:
        reasons.append("No elevated risk factors were detected by the configured prototype rules.")
    if not actions:
        actions.append("Complete the standard farm safety checklist and follow the task SOP.")

    return RiskResult(score, level, decision, reasons, actions, rules, blockers)
