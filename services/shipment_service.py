"""
Shipment Service
Handles operations related to company active shipments.
"""
import sys, os
from dataclasses import dataclass
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.supplier_service import get_all_suppliers
from services.route_service import get_all_routes

@dataclass
class Shipment:
    id: str
    sku: str
    supplier_id: str
    receiver_id: str
    route_id: str
    status: str
    estimated_arrival: str
    value_usd: float
    units: int

def get_all_shipments() -> list[Shipment]:
    try:
        from db.models import get_session, ShipmentModel
        with get_session() as s:
            rows = s.query(ShipmentModel).all()
            return [Shipment(
                id=r.id, sku=r.sku, supplier_id=r.supplier_id,
                receiver_id=r.receiver_id, route_id=r.route_id,
                status=r.status, estimated_arrival=r.estimated_arrival,
                value_usd=r.value_usd, units=r.units
            ) for r in rows]
    except Exception as e:
        print(f"[ShipmentService] DB unavailable: {e}")
        return []

def get_enriched_shipments() -> list[dict]:
    """Returns shipments joined with supplier and route info."""
    shipments = get_all_shipments()
    suppliers = {s.id: s for s in get_all_suppliers()}
    routes = {r.id: r for r in get_all_routes()}
    
    enriched = []
    for shp in shipments:
        sup = suppliers.get(shp.supplier_id)
        route = routes.get(shp.route_id)
        enriched.append({
            "id": shp.id,
            "sku": shp.sku,
            "status": shp.status,
            "estimated_arrival": shp.estimated_arrival,
            "value_usd": shp.value_usd,
            "units": shp.units,
            "supplier_id": shp.supplier_id,
            "supplier_name": sup.name if sup else "Unknown",
            "supplier_country": sup.country if sup else "Unknown",
            "reliability_score": sup.risk_score if sup else 0.5, # treating risk_score loosely
            "route_id": shp.route_id,
            "origin": route.origin if route else "Unknown",
            "destination": route.destination if route else "Unknown",
            "region": _map_country_to_region(sup.country if sup else "Unknown"),
            "receiver_id": shp.receiver_id
        })
    return enriched

def _map_country_to_region(country: str) -> str:
    cmap = {
        "Taiwan": "east-asia", "China": "east-asia", "South Korea": "east-asia",
        "Germany": "europe", "Czech Republic": "europe", "USA": "north-america",
        "Canada": "north-america", "Mexico": "latin-america", "Peru": "latin-america",
        "Vietnam": "southeast-asia", "Indonesia": "southeast-asia", "Thailand": "southeast-asia",
        "India": "south-asia", "Egypt": "middle-east"
    }
    return cmap.get(country, "global")
