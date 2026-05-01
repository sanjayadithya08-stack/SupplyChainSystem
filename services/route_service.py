from dataclasses import dataclass
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@dataclass
class Route:
    id: str
    origin: str
    destination: str
    via_ports: list[str]
    carrier: str
    transit_days: int
    risk_level: str

_ROUTES = [
    Route("R1", "Shanghai", "Los Angeles", ["Trans-Pacific"], "Maersk", 14, "MEDIUM"),
    Route("R2", "Shenzhen", "Seattle", ["Trans-Pacific"], "MSC", 16, "LOW"),
    Route("R3", "Rotterdam", "New York", ["Trans-Atlantic"], "Hapag-Lloyd", 10, "LOW"),
    Route("R4", "Mumbai", "Rotterdam", ["Suez Canal", "Red Sea"], "CMA CGM", 22, "CRITICAL"),
    Route("R5", "Mumbai", "Rotterdam", ["Cape of Good Hope"], "CMA CGM", 35, "MEDIUM"), # Alternate for R4
    Route("R6", "Tokyo", "Los Angeles", ["Trans-Pacific"], "ONE", 12, "LOW"),
    Route("R7", "Singapore", "Hamburg", ["Suez Canal"], "Evergreen", 26, "HIGH"),
    Route("R8", "Veracruz", "Houston", ["Gulf of Mexico"], "ZIM", 4, "LOW")
]

def get_all_routes() -> list[Route]:
    return _ROUTES

def get_alternate_routes(origin: str, destination: str) -> list[Route]:
    # Very simple logic for the stub
    primary = [r for r in _ROUTES if r.origin == origin and r.destination == destination]
    if not primary: return []
    
    # Return any other route to the same destination
    return [r for r in _ROUTES if r.destination == destination and r.id != primary[0].id]

def estimate_delay(route_id: str, disruption_type: str) -> int:
    delay_matrix = {
        "port_strike": 7,
        "weather": 4,
        "war": 14,
        "cyber": 2,
        "logistics": 3,
        "customs": 5
    }
    return delay_matrix.get(disruption_type, 0)
