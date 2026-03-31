from uuid import uuid4

from fastapi import APIRouter, HTTPException, status

from app.db import reviews_collection
from app.models import ReviewCreate, ReviewResponse, ReviewSummary, ReviewUpdate

router = APIRouter(prefix="/reviews", tags=["Reviews"])


@router.post("", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def add_review(payload: ReviewCreate) -> ReviewResponse:
    document = payload.model_dump()
    document["review_id"] = str(uuid4())
    await reviews_collection.insert_one(document)
    return ReviewResponse(**document)


@router.get("", response_model=list[ReviewResponse])
async def list_reviews() -> list[ReviewResponse]:
    reviews = await reviews_collection.find({}, {"_id": 0}).to_list(length=None)
    return [ReviewResponse(**review) for review in reviews]


@router.get("/{review_id}", response_model=ReviewResponse)
async def get_review(review_id: str) -> ReviewResponse:
    review = await reviews_collection.find_one({"review_id": review_id}, {"_id": 0})
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found.")
    return ReviewResponse(**review)


@router.get("/item/{item_id}", response_model=list[ReviewResponse])
async def get_reviews_by_item(item_id: str) -> list[ReviewResponse]:
    reviews = await reviews_collection.find({"item_id": item_id}, {"_id": 0}).to_list(length=None)
    return [ReviewResponse(**review) for review in reviews]


@router.get("/item/{item_id}/summary", response_model=ReviewSummary)
async def get_item_review_summary(item_id: str) -> ReviewSummary:
    pipeline = [
        {"$match": {"item_id": item_id}},
        {
            "$group": {
                "_id": "$item_id",
                "average_rating": {"$avg": "$rating"},
                "total_reviews": {"$sum": 1},
            }
        },
    ]
    results = await reviews_collection.aggregate(pipeline).to_list(length=1)

    if not results:
        return ReviewSummary(item_id=item_id, average_rating=0.0, total_reviews=0)

    summary = results[0]
    return ReviewSummary(
        item_id=item_id,
        average_rating=round(summary["average_rating"], 2),
        total_reviews=summary["total_reviews"],
    )


@router.get("/user/{user_id}", response_model=list[ReviewResponse])
async def get_reviews_by_user(user_id: str) -> list[ReviewResponse]:
    reviews = await reviews_collection.find({"user_id": user_id}, {"_id": 0}).to_list(length=None)
    return [ReviewResponse(**review) for review in reviews]


@router.put("/{review_id}", response_model=ReviewResponse)
async def update_review(review_id: str, payload: ReviewUpdate) -> ReviewResponse:
    updates = payload.model_dump(exclude_unset=True)
    if updates:
        result = await reviews_collection.update_one({"review_id": review_id}, {"$set": updates})
        if result.matched_count == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found.")

    review = await reviews_collection.find_one({"review_id": review_id}, {"_id": 0})
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found.")
    return ReviewResponse(**review)


@router.delete("/{review_id}")
async def delete_review(review_id: str) -> dict:
    result = await reviews_collection.delete_one({"review_id": review_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found.")
    return {"message": "Review deleted successfully."}
