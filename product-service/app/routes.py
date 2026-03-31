from uuid import uuid4

from fastapi import APIRouter, HTTPException, Query, status

from app.db import products_collection
from app.models import ProductCreate, ProductResponse, ProductUpdate

router = APIRouter(prefix="/products", tags=["Products"])


def serialize_product(document: dict) -> dict:
    return {
        "item_id": document["item_id"],
        "name": document["name"],
        "category": document["category"],
        "price": document["price"],
        "availability": document["availability"],
    }


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def add_product(payload: ProductCreate) -> ProductResponse:
    document = payload.model_dump()
    document["item_id"] = str(uuid4())
    await products_collection.insert_one(document)
    return ProductResponse(**serialize_product(document))


@router.get("", response_model=list[ProductResponse])
async def list_products(available_only: bool = Query(False, description="Return only currently available products")) -> list[ProductResponse]:
    query = {"availability": True} if available_only else {}
    products = await products_collection.find(query, {"_id": 0}).sort("name", 1).to_list(length=None)
    return [ProductResponse(**product) for product in products]


@router.get("/{item_id}", response_model=ProductResponse)
async def get_product(item_id: str) -> ProductResponse:
    product = await products_collection.find_one({"item_id": item_id}, {"_id": 0})
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found.")
    return ProductResponse(**product)


@router.put("/{item_id}", response_model=ProductResponse)
async def update_product(item_id: str, payload: ProductUpdate) -> ProductResponse:
    updates = payload.model_dump(exclude_unset=True)
    if not updates:
        existing_product = await products_collection.find_one({"item_id": item_id}, {"_id": 0})
        if not existing_product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found.")
        return ProductResponse(**existing_product)

    result = await products_collection.update_one({"item_id": item_id}, {"$set": updates})
    if result.matched_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found.")

    updated_product = await products_collection.find_one({"item_id": item_id}, {"_id": 0})
    return ProductResponse(**updated_product)


@router.delete("/{item_id}")
async def delete_product(item_id: str) -> dict:
    result = await products_collection.delete_one({"item_id": item_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found.")
    return {"message": "Product deleted successfully."}
