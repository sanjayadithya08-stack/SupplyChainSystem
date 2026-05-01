from dataclasses import dataclass
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@dataclass
class Supplier:
    id: str
    name: str
    country: str
    tier: int
    product_categories: list[str]
    risk_score: float # 0.0 to 1.0
    alternate_id: str

_SUPPLIERS = [
    Supplier("S001", "Global MicroTech", "Taiwan", 1, ["Semiconductors", "Controllers"], 0.85, "S002"),
    Supplier("S002", "Seoul Silicates", "South Korea", 2, ["Semiconductors"], 0.20, ""),
    Supplier("S003", "Bavarian Motors Parts", "Germany", 1, ["Auto Parts", "Engines"], 0.60, "S004"),
    Supplier("S004", "Czech Auto Works", "Czech Republic", 2, ["Auto Parts"], 0.15, ""),
    Supplier("S005", "Pan-Am Textiles", "Mexico", 1, ["Fabrics", "Apparel"], 0.30, "S006"),
    Supplier("S006", "Andes Weavers", "Peru", 2, ["Fabrics"], 0.10, ""),
    Supplier("S007", "Shenzhen Electronics", "China", 1, ["Consumer Tech"], 0.50, "S008"),
    Supplier("S008", "Hanoi Tech Assembly", "Vietnam", 2, ["Consumer Tech"], 0.40, ""),
    Supplier("S009", "Texas Polymers", "USA", 1, ["Plastics", "Chemicals"], 0.25, "S010"),
    Supplier("S010", "Calgary Petrochem", "Canada", 2, ["Chemicals"], 0.05, "")
]

def get_all_suppliers() -> list[Supplier]:
    return _SUPPLIERS

def get_suppliers_by_region(region: str) -> list[Supplier]:
    # Simplified region matching for stub
    region_map = {
        "east-asia": ["Taiwan", "South Korea", "China"],
        "europe": ["Germany", "Czech Republic"],
        "north-america": ["USA", "Canada"],
        "latin-america": ["Mexico", "Peru"],
        "southeast-asia": ["Vietnam"]
    }
    allowed = region_map.get(region, [])
    if not allowed: return []
    return [s for s in _SUPPLIERS if s.country in allowed]

def get_alternates(supplier_id: str) -> list[Supplier]:
    for s in _SUPPLIERS:
        if s.id == supplier_id and s.alternate_id:
            return [alt for alt in _SUPPLIERS if alt.id == s.alternate_id]
    return []

def assess_supplier_risk(supplier_id: str, geo_events: list) -> float:
    for s in _SUPPLIERS:
        if s.id == supplier_id:
            score = s.risk_score
            for event in geo_events:
                if event.country == s.country:
                    if event.severity == "CRITICAL": score += 0.5
                    elif event.severity == "HIGH": score += 0.3
            return min(score, 1.0)
    return 0.0
