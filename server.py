from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone
import bcrypt
import jwt

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# JWT Configuration
JWT_SECRET = os.environ.get('JWT_SECRET', 'stok-takip-secret-key-2024')
JWT_ALGORITHM = "HS256"

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Security
security = HTTPBearer()

# Fixed Categories
CATEGORIES = [
    "Motor Parçaları",
    "Fren Sistemi",
    "Elektrik",
    "Şanzıman",
    "Süspansiyon",
    "Soğutma Sistemi",
    "Yakıt Sistemi",
    "Egzoz Sistemi"
]

# ========== MODELS ==========

class UserCreate(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: str
    username: str

class TokenResponse(BaseModel):
    token: str
    user: UserResponse

class PartCreate(BaseModel):
    name: str
    category: str
    sku: str
    quantity: int = 0
    unit_price: float = 0.0
    critical_level: int = 5

class PartUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    sku: Optional[str] = None
    quantity: Optional[int] = None
    unit_price: Optional[float] = None
    critical_level: Optional[int] = None

class Part(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    category: str
    sku: str
    quantity: int = 0
    unit_price: float = 0.0
    critical_level: int = 5
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class StockMovement(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    part_id: str
    part_name: str
    movement_type: str  # "in" or "out"
    quantity: int
    previous_quantity: int
    new_quantity: int
    user_id: str
    username: str
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class DashboardMetrics(BaseModel):
    total_part_types: int
    total_stock_value: float
    critical_stock_count: int

class StockAdjustment(BaseModel):
    quantity: int  # positive for increment, negative for decrement

# ========== AUTH HELPERS ==========

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_token(user_id: str, username: str) -> str:
    payload = {
        "user_id": user_id,
        "username": username,
        "exp": datetime.now(timezone.utc).timestamp() + 86400 * 7  # 7 days
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return {"user_id": payload["user_id"], "username": payload["username"]}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token süresi dolmuş")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Geçersiz token")

# ========== AUTH ENDPOINTS ==========

@api_router.post("/auth/register", response_model=TokenResponse)
async def register(user: UserCreate):
    # Check if user exists
    existing = await db.users.find_one({"username": user.username})
    if existing:
        raise HTTPException(status_code=400, detail="Bu kullanıcı adı zaten kullanılıyor")
    
    user_id = str(uuid.uuid4())
    user_doc = {
        "id": user_id,
        "username": user.username,
        "password": hash_password(user.password),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.users.insert_one(user_doc)
    
    token = create_token(user_id, user.username)
    return TokenResponse(
        token=token,
        user=UserResponse(id=user_id, username=user.username)
    )

@api_router.post("/auth/login", response_model=TokenResponse)
async def login(user: UserLogin):
    user_doc = await db.users.find_one({"username": user.username}, {"_id": 0})
    if not user_doc or not verify_password(user.password, user_doc["password"]):
        raise HTTPException(status_code=401, detail="Kullanıcı adı veya şifre hatalı")
    
    token = create_token(user_doc["id"], user_doc["username"])
    return TokenResponse(
        token=token,
        user=UserResponse(id=user_doc["id"], username=user_doc["username"])
    )

@api_router.get("/auth/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    return UserResponse(id=current_user["user_id"], username=current_user["username"])

# ========== CATEGORIES ENDPOINT ==========

@api_router.get("/categories", response_model=List[str])
async def get_categories():
    return CATEGORIES

# ========== PARTS ENDPOINTS ==========

@api_router.get("/parts", response_model=List[Part])
async def get_parts(
    search: Optional[str] = None,
    category: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    query = {}
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"sku": {"$regex": search, "$options": "i"}},
            {"category": {"$regex": search, "$options": "i"}}
        ]
    if category:
        query["category"] = category
    
    parts = await db.parts.find(query, {"_id": 0}).to_list(1000)
    return parts

@api_router.post("/parts", response_model=Part)
async def create_part(part: PartCreate, current_user: dict = Depends(get_current_user)):
    # Check if SKU exists
    existing = await db.parts.find_one({"sku": part.sku})
    if existing:
        raise HTTPException(status_code=400, detail="Bu parça numarası (SKU) zaten kullanılıyor")
    
    if part.category not in CATEGORIES:
        raise HTTPException(status_code=400, detail="Geçersiz kategori")
    
    part_obj = Part(**part.model_dump())
    await db.parts.insert_one(part_obj.model_dump())
    
    # Log movement if initial quantity > 0
    if part.quantity > 0:
        movement = StockMovement(
            part_id=part_obj.id,
            part_name=part_obj.name,
            movement_type="in",
            quantity=part.quantity,
            previous_quantity=0,
            new_quantity=part.quantity,
            user_id=current_user["user_id"],
            username=current_user["username"]
        )
        await db.stock_movements.insert_one(movement.model_dump())
    
    return part_obj

@api_router.get("/parts/{part_id}", response_model=Part)
async def get_part(part_id: str, current_user: dict = Depends(get_current_user)):
    part = await db.parts.find_one({"id": part_id}, {"_id": 0})
    if not part:
        raise HTTPException(status_code=404, detail="Parça bulunamadı")
    return part

@api_router.put("/parts/{part_id}", response_model=Part)
async def update_part(part_id: str, part_update: PartUpdate, current_user: dict = Depends(get_current_user)):
    part = await db.parts.find_one({"id": part_id}, {"_id": 0})
    if not part:
        raise HTTPException(status_code=404, detail="Parça bulunamadı")
    
    update_data = {k: v for k, v in part_update.model_dump().items() if v is not None}
    if not update_data:
        return Part(**part)
    
    if "category" in update_data and update_data["category"] not in CATEGORIES:
        raise HTTPException(status_code=400, detail="Geçersiz kategori")
    
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    # Track quantity changes
    if "quantity" in update_data and update_data["quantity"] != part["quantity"]:
        diff = update_data["quantity"] - part["quantity"]
        movement = StockMovement(
            part_id=part_id,
            part_name=part["name"],
            movement_type="in" if diff > 0 else "out",
            quantity=abs(diff),
            previous_quantity=part["quantity"],
            new_quantity=update_data["quantity"],
            user_id=current_user["user_id"],
            username=current_user["username"]
        )
        await db.stock_movements.insert_one(movement.model_dump())
    
    await db.parts.update_one({"id": part_id}, {"$set": update_data})
    updated_part = await db.parts.find_one({"id": part_id}, {"_id": 0})
    return Part(**updated_part)

@api_router.delete("/parts/{part_id}")
async def delete_part(part_id: str, current_user: dict = Depends(get_current_user)):
    part = await db.parts.find_one({"id": part_id}, {"_id": 0})
    if not part:
        raise HTTPException(status_code=404, detail="Parça bulunamadı")
    
    await db.parts.delete_one({"id": part_id})
    return {"message": "Parça başarıyla silindi"}

@api_router.post("/parts/{part_id}/adjust", response_model=Part)
async def adjust_stock(part_id: str, adjustment: StockAdjustment, current_user: dict = Depends(get_current_user)):
    part = await db.parts.find_one({"id": part_id}, {"_id": 0})
    if not part:
        raise HTTPException(status_code=404, detail="Parça bulunamadı")
    
    new_quantity = part["quantity"] + adjustment.quantity
    if new_quantity < 0:
        raise HTTPException(status_code=400, detail="Stok miktarı negatif olamaz")
    
    # Log movement
    movement = StockMovement(
        part_id=part_id,
        part_name=part["name"],
        movement_type="in" if adjustment.quantity > 0 else "out",
        quantity=abs(adjustment.quantity),
        previous_quantity=part["quantity"],
        new_quantity=new_quantity,
        user_id=current_user["user_id"],
        username=current_user["username"]
    )
    await db.stock_movements.insert_one(movement.model_dump())
    
    # Update part
    await db.parts.update_one(
        {"id": part_id},
        {"$set": {
            "quantity": new_quantity,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    updated_part = await db.parts.find_one({"id": part_id}, {"_id": 0})
    return Part(**updated_part)

# ========== DASHBOARD ENDPOINT ==========

@api_router.get("/dashboard/metrics", response_model=DashboardMetrics)
async def get_dashboard_metrics(current_user: dict = Depends(get_current_user)):
    parts = await db.parts.find({}, {"_id": 0}).to_list(1000)
    
    total_part_types = len(parts)
    total_stock_value = sum(p["quantity"] * p["unit_price"] for p in parts)
    critical_stock_count = sum(1 for p in parts if p["quantity"] <= p["critical_level"])
    
    return DashboardMetrics(
        total_part_types=total_part_types,
        total_stock_value=total_stock_value,
        critical_stock_count=critical_stock_count
    )

# ========== STOCK MOVEMENTS ENDPOINT ==========

@api_router.get("/stock-movements", response_model=List[StockMovement])
async def get_stock_movements(
    part_id: Optional[str] = None,
    limit: int = 100,
    current_user: dict = Depends(get_current_user)
):
    query = {}
    if part_id:
        query["part_id"] = part_id
    
    movements = await db.stock_movements.find(query, {"_id": 0}).sort("timestamp", -1).to_list(limit)
    return movements

# ========== HEALTH CHECK ==========

@api_router.get("/")
async def root():
    return {"message": "StokTakip Pro API"}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
