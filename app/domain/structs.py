from enum import Enum
from typing import List, Optional, TypeVar, Type, Any
from datetime import datetime
from uuid import UUID
import msgspec

T = TypeVar("T", bound="BaseModel")

class BaseModel(msgspec.Struct):
    def to_dict(self) -> dict[str, Any]:
        return msgspec.to_builtins(self) 

    @classmethod
    def from_dict(cls: Type[T], data: dict[str, Any]) -> T:
        return msgspec.convert(data, type=cls)

class UserRole(str, Enum):
    STUDENT = "student"
    DM = "dm"
    ADMIN = "admin"

class LoginPayload(BaseModel):
    email: str
    password: str

class RegisterPayload(BaseModel):
    email: str
    password: str
    role: Optional[UserRole] = UserRole.STUDENT

class SessionItem(BaseModel):
    activity_type: str
    start_time: datetime
    end_time: datetime   
    room_id: Optional[UUID] = None 
    xp_multiplier: float = 1.0

class SyncPayload(BaseModel):
    sessions: List[SessionItem]


class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class RegisterResponse(BaseModel):
    message: str 
    id: UUID    
    email: str

class RewardItem(BaseModel):
    id: UUID    
    name: str

class SyncResponse(BaseModel):
    status: str
    processed_sessions_count: int
    total_exp: int
    total_exp_gained: int
    current_level: int
    leveled_up: bool
    levels_gained: int
    rewards: List[RewardItem]

class SessionReportItem(BaseModel):
    id: UUID        
    user_id: UUID    
    activity_type: str
    start_time: datetime
    end_time: datetime
    exp_earned: int
    room_id: Optional[UUID] = None

class SessionReportResponse(BaseModel):
    reports: List[SessionReportItem]
    total_count: int

class BatchExpPayload(BaseModel):
    exp_to_add: int

class BatchExpResponse(BaseModel):
    new_level: int
    levels_gained: int
    leveled_up: bool
    total_exp: int

class SyncSessionResponse(BaseModel):
    total_exp_gained: int
    time_trials_completed: int

class MSItemResponse(BaseModel):
    id: UUID
    name: str

class MSInventoryPayload(BaseModel):
    user_id: UUID
    item_id: UUID
    is_equipped: bool = False

class ReportFilters(BaseModel):
    user_id: Optional[UUID] = None
    room_id: Optional[UUID] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    sort_order: str = "desc"
    limit: int = 50
    offset: int = 0

class RoomCreate(BaseModel):
    name: str
    description: Optional[str] = None
    capacity: int = 5
    xp_multiplier: float = 1.3

class RoomResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    capacity: int
    creator_id: UUID
    status: str
    xp_multiplier: float
    invitation_code: Optional[str] = None
    qr_code: Optional[str] = None
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None

class JoinRoomRequest(BaseModel):
    invitation_code: str

class MemberResponse(BaseModel):
    message: str
    room_id: Optional[UUID] = None

class UserStatsResponse(BaseModel):
    total_exp: int
    current_level: int