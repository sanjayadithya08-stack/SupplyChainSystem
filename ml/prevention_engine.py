def generate_prevention_plan(prediction: dict) -> dict:
    """
    Takes a risk prediction and returns a structured prevention plan.
    """
    try:
        disruption_type = prediction.get("disruption_type", "normal")
        label = prediction.get("label", "LOW")
        regions = prediction.get("affected_regions", ["global"])
        
        plan = {
            "immediate_actions": [],
            "short_term_actions": [],
            "long_term_actions": [],
            "rerouting_options": [],
            "supplier_alternatives": [],
            "inventory_recommendations": [],
            "estimated_cost_impact": "Minimal",
            "priority": "P3"
        }

        if label in ["CRITICAL", "HIGH"]:
            plan["priority"] = "P1" if label == "CRITICAL" else "P2"
            plan["estimated_cost_impact"] = "High ($100k+)" if label == "CRITICAL" else "Medium ($10k-$100k)"

        if disruption_type == "port_strike":
            plan["immediate_actions"] = ["Reroute to nearest alternate port", "Notify procurement team"]
            plan["short_term_actions"] = ["Activate air freight for critical SKUs"]
            plan["long_term_actions"] = ["Buffer stock at inland warehouses"]
        elif disruption_type == "weather":
            plan["immediate_actions"] = [f"Suspend shipments to {regions[0]}", "Issue carrier alerts"]
            plan["short_term_actions"] = ["Switch to inland routes if possible"]
            plan["long_term_actions"] = ["Pre-position inventory at safe hubs"]
        elif disruption_type == "war":
            plan["immediate_actions"] = ["Escalate to executive team", f"Blacklist routes through {regions[0]}"]
            plan["short_term_actions"] = ["Activate secondary supplier network"]
            plan["long_term_actions"] = ["Trigger force majeure review"]
        elif disruption_type == "cyber":
            plan["immediate_actions"] = ["Switch to manual booking systems", "Alert IT security"]
            plan["short_term_actions"] = ["Verify all in-transit shipments"]
            plan["long_term_actions"] = ["Pause automated order triggers"]
        elif disruption_type == "logistics":
            plan["immediate_actions"] = ["Notify sales team of delays"]
            plan["short_term_actions"] = ["Activate backup carrier contracts", "Extend lead times to customers"]
            plan["long_term_actions"] = ["Increase safety stock targets"]
        elif disruption_type == "supplier":
            plan["immediate_actions"] = ["Assess inventory depletion timeline"]
            plan["short_term_actions"] = ["Emergency purchase orders to Tier 2"]
            plan["long_term_actions"] = ["Activate tier-2 suppliers fully"]
        elif disruption_type == "customs":
            plan["immediate_actions"] = ["Engage customs broker"]
            plan["short_term_actions"] = ["Prepare required documentation packages"]
            plan["long_term_actions"] = ["Estimate delay buffer in planning system"]
        else:
            plan["immediate_actions"] = ["Routine monitoring"]
            plan["short_term_actions"] = ["No action needed"]
            plan["long_term_actions"] = ["No action needed"]
            
        return plan
    except Exception as e:
        print(f"Error in generate_prevention_plan: {e}")
        return {
            "immediate_actions": ["Error generating plan"],
            "short_term_actions": [],
            "long_term_actions": [],
            "rerouting_options": [],
            "supplier_alternatives": [],
            "inventory_recommendations": [],
            "estimated_cost_impact": "Unknown",
            "priority": "P3"
        }
