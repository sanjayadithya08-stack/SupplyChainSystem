"""
Upgrade 3: SQLite database for suppliers and routes.
Run `python db/init_db.py` once to create and seed the database.
"""
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sqlalchemy import create_engine, Column, String, Float, Integer, Text
from sqlalchemy.orm import DeclarativeBase, Session
from utils.config import Config

engine = create_engine(f"sqlite:///{Config.DB_PATH}", echo=False)

class Base(DeclarativeBase):
    pass

class SupplierModel(Base):
    __tablename__ = "suppliers"
    id          = Column(String, primary_key=True)
    name        = Column(String, nullable=False)
    country     = Column(String)
    tier        = Column(Integer)
    product_categories = Column(Text)  # comma-separated
    risk_score  = Column(Float)
    alternate_id= Column(String)

class RouteModel(Base):
    __tablename__ = "routes"
    id           = Column(String, primary_key=True)
    origin       = Column(String)
    destination  = Column(String)
    via_ports    = Column(Text)   # comma-separated
    carrier      = Column(String)
    transit_days = Column(Integer)
    risk_level   = Column(String)

def get_session() -> Session:
    return Session(engine)

def init_db():
    Base.metadata.create_all(engine)
    _seed()
    print(f"Database initialized at {Config.DB_PATH}")

def _seed():
    suppliers = [
        ("S001","Global MicroTech","Taiwan",1,"Semiconductors,Controllers",0.85,"S002"),
        ("S002","Seoul Silicates","South Korea",2,"Semiconductors",0.20,""),
        ("S003","Bavarian Motors Parts","Germany",1,"Auto Parts,Engines",0.60,"S004"),
        ("S004","Czech Auto Works","Czech Republic",2,"Auto Parts",0.15,""),
        ("S005","Pan-Am Textiles","Mexico",1,"Fabrics,Apparel",0.30,"S006"),
        ("S006","Andes Weavers","Peru",2,"Fabrics",0.10,""),
        ("S007","Shenzhen Electronics","China",1,"Consumer Tech",0.50,"S008"),
        ("S008","Hanoi Tech Assembly","Vietnam",2,"Consumer Tech",0.40,""),
        ("S009","Texas Polymers","USA",1,"Plastics,Chemicals",0.25,"S010"),
        ("S010","Calgary Petrochem","Canada",2,"Chemicals",0.05,""),
        ("S011","Jakarta Rubber Works","Indonesia",1,"Raw Materials",0.45,"S012"),
        ("S012","Bangkok Materials","Thailand",2,"Raw Materials",0.20,""),
        ("S013","Mumbai Pharma","India",1,"Pharmaceuticals",0.35,"S014"),
        ("S014","Hyderabad Biotech","India",2,"Pharmaceuticals",0.15,""),
        ("S015","Cairo Textiles","Egypt",1,"Fabrics",0.55,"S016"),
        ("S016","Tunis Apparel","Tunisia",2,"Fabrics",0.25,""),
    ]
    routes = [
        ("R1","Shanghai","Los Angeles","Trans-Pacific","Maersk",14,"MEDIUM"),
        ("R2","Shenzhen","Seattle","Trans-Pacific","MSC",16,"LOW"),
        ("R3","Rotterdam","New York","Trans-Atlantic","Hapag-Lloyd",10,"LOW"),
        ("R4","Mumbai","Rotterdam","Suez Canal,Red Sea","CMA CGM",22,"CRITICAL"),
        ("R5","Mumbai","Rotterdam","Cape of Good Hope","CMA CGM",35,"MEDIUM"),
        ("R6","Tokyo","Los Angeles","Trans-Pacific","ONE",12,"LOW"),
        ("R7","Singapore","Hamburg","Suez Canal","Evergreen",26,"HIGH"),
        ("R8","Veracruz","Houston","Gulf of Mexico","ZIM",4,"LOW"),
        ("R9","Busan","Vancouver","North Pacific","HMM",13,"LOW"),
        ("R10","Jakarta","Sydney","Intra-Pacific","Evergreen",8,"LOW"),
        ("R11","Cape Town","Rotterdam","South Atlantic","Hapag-Lloyd",20,"MEDIUM"),
        ("R12","Mumbai","Singapore","Bay of Bengal","PIL",7,"MEDIUM"),
    ]
    with get_session() as s:
        if s.query(SupplierModel).count() == 0:
            for row in suppliers:
                s.add(SupplierModel(id=row[0],name=row[1],country=row[2],tier=row[3],
                                    product_categories=row[4],risk_score=row[5],alternate_id=row[6]))
        if s.query(RouteModel).count() == 0:
            for row in routes:
                s.add(RouteModel(id=row[0],origin=row[1],destination=row[2],via_ports=row[3],
                                 carrier=row[4],transit_days=row[5],risk_level=row[6]))
        s.commit()

if __name__ == "__main__":
    init_db()
