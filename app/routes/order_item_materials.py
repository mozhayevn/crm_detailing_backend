from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import require_permission
from app.models import OrderItem, OrderItemMaterial, Material, User, Order
from app.schemas import OrderItemMaterialCreate, OrderItemMaterialResponse

router = APIRouter(prefix="/order-item-materials", tags=["Order Item Materials"])


@router.post("/{order_item_id}", response_model=OrderItemMaterialResponse)
def add_material_to_order_item(
    order_item_id: int,
    data: OrderItemMaterialCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("materials.consume")),
):
    order_item = db.query(OrderItem).filter(OrderItem.id == order_item_id).first()
    order = db.query(Order).filter(Order.id == order_item.order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.pricing_locked:
        raise HTTPException(status_code=400, detail="Pricing is locked for this order")

    #------

    if not order_item:
        raise HTTPException(status_code=404, detail="Order item not found")

    material = db.query(Material).filter(Material.id == data.material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")

    if data.quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be greater than zero")

    existing_row = (
        db.query(OrderItemMaterial)
        .filter(
            OrderItemMaterial.order_item_id == order_item_id,
            OrderItemMaterial.material_id == data.material_id,
        )
        .first()
    )

    if existing_row:
        existing_row.quantity += data.quantity
        existing_row.unit_cost = material.cost_per_unit
        existing_row.total_cost = existing_row.quantity * existing_row.unit_cost

        if data.comment:
            existing_row.comment = data.comment

        db.commit()
        db.refresh(existing_row)
        return existing_row

    total_cost = material.cost_per_unit * data.quantity

    row = OrderItemMaterial(
        order_item_id=order_item_id,
        material_id=data.material_id,
        quantity=data.quantity,
        unit_cost=material.cost_per_unit,
        total_cost=total_cost,
        comment=data.comment,
    )

    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.get("/{order_item_id}", response_model=list[OrderItemMaterialResponse])
def get_order_item_materials(
    order_item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("materials.read")),
):
    order_item = db.query(OrderItem).filter(OrderItem.id == order_item_id).first()
    if not order_item:
        raise HTTPException(status_code=404, detail="Order item not found")

    return (
        db.query(OrderItemMaterial)
        .filter(OrderItemMaterial.order_item_id == order_item_id)
        .order_by(OrderItemMaterial.id.desc())
        .all()
    )