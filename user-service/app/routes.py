from uuid import uuid4

from fastapi import APIRouter, HTTPException, status
from passlib.context import CryptContext
from pymongo.errors import DuplicateKeyError

from app.db import users_collection
from app.models import LoginResponse, UserCreate, UserLogin, UserResponse, UserUpdate

router = APIRouter(prefix="/users", tags=["Users"])
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def serialize_user(document: dict) -> dict:
    return {
        "user_id": document["user_id"],
        "name": document["name"],
        "phone": document["phone"],
        "email": document["email"],
    }


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(payload: UserCreate) -> UserResponse:
    existing_user = await users_collection.find_one({"email": payload.email.lower()})
    if existing_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email is already registered.")

    document = payload.model_dump()
    document["user_id"] = str(uuid4())
    document["email"] = payload.email.lower()
    document["password"] = pwd_context.hash(payload.password)

    try:
        await users_collection.insert_one(document)
    except DuplicateKeyError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email is already registered.") from exc

    return UserResponse(**serialize_user(document))


@router.post("/login", response_model=LoginResponse)
async def login_user(payload: UserLogin) -> LoginResponse:
    user = await users_collection.find_one({"email": payload.email.lower()})
    if not user or not pwd_context.verify(payload.password, user["password"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password.")

    return LoginResponse(
        message="Login successful.",
        user=UserResponse(**serialize_user(user)),
    )


@router.get("", response_model=list[UserResponse])
async def list_users() -> list[UserResponse]:
    cursor = users_collection.find({}, {"_id": 0, "password": 0})
    users = await cursor.to_list(length=None)
    return [UserResponse(**user) for user in users]


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_profile(user_id: str) -> UserResponse:
    user = await users_collection.find_one({"user_id": user_id}, {"_id": 0, "password": 0})
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    return UserResponse(**user)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user_profile(user_id: str, payload: UserUpdate) -> UserResponse:
    existing_user = await users_collection.find_one({"user_id": user_id})
    if not existing_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    updates = payload.model_dump(exclude_unset=True)

    if "email" in updates:
        updates["email"] = updates["email"].lower()
        conflict = await users_collection.find_one({"email": updates["email"], "user_id": {"$ne": user_id}})
        if conflict:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email is already in use.")

    if "password" in updates:
        updates["password"] = pwd_context.hash(updates["password"])

    if updates:
        await users_collection.update_one({"user_id": user_id}, {"$set": updates})

    updated_user = await users_collection.find_one({"user_id": user_id}, {"_id": 0, "password": 0})
    return UserResponse(**updated_user)


@router.delete("/{user_id}")
async def delete_user(user_id: str) -> dict:
    result = await users_collection.delete_one({"user_id": user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    return {"message": "User deleted successfully."}
