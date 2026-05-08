"""
Actionable churn recommendations engine.
Separates what we can fix from what we can't.
"""

def get_recommendation(row: dict, churn_prob: float) -> dict:
    """
    Analyse root cause of churn risk and return actionable recommendation.
    
    Returns:
        {
            "action": "call" | "coupon" | "notification" | "monitor" | "safe",
            "action_label": str,
            "action_color": str,
            "reason": str,
            "actionable": bool,
            "priority": int  (1=highest)
        }
    """
    tenure        = float(row.get("Tenure", 0))
    city_tier     = int(row.get("CityTier", 1))
    complain      = int(row.get("Complain", 0))
    days_since    = float(row.get("DaySinceLastOrder", 0))
    hour_spend    = float(row.get("HourSpendOnApp", 0))
    order_count   = float(row.get("OrderCount", 0))

    if churn_prob < 0.4:
        return {
            "action": "safe",
            "action_label": "Low Risk",
            "action_color": "#34d399",
            "reason": "Customer is stable.",
            "actionable": False,
            "priority": 99,
        }

    # ── Score actionable signals ──────────────────────────────────────────
    signals = []

    # Actionable signals (we can do something)
    if complain == 1:
        signals.append({
            "weight": 10,
            "actionable": True,
            "action": "call",
            "action_label": "Retention Call",
            "action_color": "#f87171",
            "reason": "Customer filed a complaint — personal outreach recommended.",
        })

    if days_since > 20:
        signals.append({
            "weight": 8,
            "actionable": True,
            "action": "coupon",
            "action_label": "Send Coupon",
            "action_color": "#fb923c",
            "reason": f"No order in {int(days_since)} days — a discount offer could re-engage.",
        })

    if hour_spend < 1.0:
        signals.append({
            "weight": 6,
            "actionable": True,
            "action": "notification",
            "action_label": "Push Notification",
            "action_color": "#fbbf24",
            "reason": f"Only {hour_spend:.1f}h/day on app — send a personalised push notification.",
        })

    if order_count < 2:
        signals.append({
            "weight": 5,
            "actionable": True,
            "action": "coupon",
            "action_label": "First-Order Offer",
            "action_color": "#fb923c",
            "reason": "Very low order count — offer an incentive to re-purchase.",
        })

    # Non-actionable signals (context only)
    if city_tier == 3:
        signals.append({
            "weight": 3,
            "actionable": False,
            "action": "monitor",
            "action_label": "Monitor",
            "action_color": "#94a3b8",
            "reason": "Tier 3 city has higher baseline churn — no direct action possible.",
        })

    if tenure < 3:
        signals.append({
            "weight": 2,
            "actionable": False,
            "action": "monitor",
            "action_label": "Monitor",
            "action_color": "#94a3b8",
            "reason": "New customer (< 3 months) — churn risk is naturally higher early on.",
        })

    if not signals:
        return {
            "action": "monitor",
            "action_label": "Monitor",
            "action_color": "#94a3b8",
            "reason": "Elevated risk but no specific actionable trigger detected.",
            "actionable": False,
            "priority": 5,
        }

    # Pick highest-weight signal
    top = sorted(signals, key=lambda x: x["weight"], reverse=True)[0]

    # Build combined reason if multiple signals
    actionable_signals = [s for s in signals if s["actionable"]]
    non_actionable    = [s for s in signals if not s["actionable"]]

    reasons = []
    if actionable_signals:
        reasons.append(actionable_signals[0]["reason"])
    if non_actionable:
        reasons.append(f"Context: {non_actionable[0]['reason']}")

    priority = 1 if churn_prob >= 0.7 else (2 if churn_prob >= 0.5 else 3)

    return {
        "action":        top["action"],
        "action_label":  top["action_label"],
        "action_color":  top["action_color"],
        "reason":        " | ".join(reasons) if reasons else top["reason"],
        "actionable":    top["actionable"],
        "priority":      priority,
    }


def build_chat_context(row: dict, churn_prob: float, rec: dict) -> str:
    """Build a rich context string for the AI chatbot."""
    risk_level = "HIGH" if churn_prob >= 0.7 else ("MEDIUM" if churn_prob >= 0.4 else "LOW")
    return f"""
Customer Data:
- Tenure: {row.get('Tenure', 'N/A')} months
- City Tier: {row.get('CityTier', 'N/A')}
- Hours on App/day: {row.get('HourSpendOnApp', 'N/A')}
- Devices Registered: {row.get('NumberOfDeviceRegistered', 'N/A')}
- Complained: {'Yes' if int(row.get('Complain', 0)) == 1 else 'No'}
- Order Count: {row.get('OrderCount', 'N/A')}
- Days Since Last Order: {row.get('DaySinceLastOrder', 'N/A')}

Prediction:
- Churn Probability: {churn_prob * 100:.1f}%
- Risk Level: {risk_level}
- Recommended Action: {rec['action_label']}
- Main Reason: {rec['reason']}
- Actionable: {'Yes' if rec['actionable'] else 'No — monitor only'}
""".strip()
