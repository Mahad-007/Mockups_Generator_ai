"""Product upload and management endpoints."""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from PIL import Image
import io

from app.core.database import get_db
from app.core.storage import save_upload, get_image, save_image
from app.core.background_remover import remove_background
from app.core.gemini import gemini_client
from app.core.utils import get_image_url
from app.models import Product
from app.schemas import ProductResponse
from app.config import settings

router = APIRouter()


@router.post("/upload", response_model=ProductResponse)
async def upload_product(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload a product image.

    - Saves the original image
    - Removes background
    - Analyzes product with AI
    - Returns product details
    """
    # Validate file type
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    # Read and validate file
    contents = await file.read()
    if len(contents) > settings.max_upload_size:
        raise HTTPException(status_code=400, detail="File too large (max 10MB)")

    try:
        # Load image
        image = Image.open(io.BytesIO(contents))
        if image.mode not in ("RGB", "RGBA"):
            image = image.convert("RGB")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid image file")

    # Save original
    original_path = save_upload(contents, "products", file.filename or "upload.png")

    # Remove background
    processed_image = await remove_background(image)
    processed_path = save_image(processed_image, "products")

    # Analyze with AI
    analysis = await gemini_client.analyze_product(image)

    # Consolidate attributes with richer context
    attributes = analysis.get("attributes") or {}
    if analysis.get("target_audience"):
        attributes["target_audience"] = analysis.get("target_audience")
    if analysis.get("usage_context"):
        attributes["usage_context"] = analysis.get("usage_context")
    if analysis.get("suggested_scenes"):
        attributes["suggested_scenes"] = analysis.get("suggested_scenes")

    # Create database record
    product = Product(
        original_image_path=original_path,
        processed_image_path=processed_path,
        category=analysis.get("category"),
        attributes=attributes,
    )
    db.add(product)
    await db.flush()
    await db.refresh(product)

    return ProductResponse(
        id=product.id,
        original_image_url=get_image_url(product.original_image_path),
        processed_image_url=get_image_url(product.processed_image_path) if product.processed_image_path else None,
        category=product.category,
        attributes=product.attributes,
        created_at=product.created_at,
    )


@router.get("/", response_model=list[ProductResponse])
async def list_products(
    db: AsyncSession = Depends(get_db),
    limit: int = 20,
):
    """List all products."""
    result = await db.execute(
        select(Product).order_by(Product.created_at.desc()).limit(limit)
    )
    products = result.scalars().all()

    return [
        ProductResponse(
            id=p.id,
            original_image_url=get_image_url(p.original_image_path),
            processed_image_url=get_image_url(p.processed_image_path) if p.processed_image_path else None,
            category=p.category,
            attributes=p.attributes,
            created_at=p.created_at,
        )
        for p in products
    ]


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get a specific product."""
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return ProductResponse(
        id=product.id,
        original_image_url=get_image_url(product.original_image_path),
        processed_image_url=get_image_url(product.processed_image_path) if product.processed_image_path else None,
        category=product.category,
        attributes=product.attributes,
        created_at=product.created_at,
    )


@router.delete("/{product_id}")
async def delete_product(
    product_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Delete a product."""
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    await db.delete(product)
    return {"message": "Product deleted", "id": product_id}
