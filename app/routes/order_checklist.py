import json
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.deps import require_permission
from app.models import (
    Order,
    OrderChecklistAuditLog,
    OrderChecklistItem,
    User,
)
from app.schemas import (
    OrderChecklistAuditLogResponse,
    OrderChecklistItemComplete,
    OrderChecklistItemCreate,
    OrderChecklistItemResponse,
    OrderChecklistItemUpdate,
)

router = APIRouter(tags=["Order Checklist"])

DEFAULT_CHECKLIST_ITEMS = [
    {
        "key": "vehicle_accepted",
        "title": "Авто принято",
        "description": "Проверить данные клиента, автомобиль и первичное состояние.",
        "sort_order": 10,
        "is_required": True,
    },
    {
        "key": "before_photos",
        "title": "Фото до работ",
        "description": "Загрузить фото автомобиля до начала работ.",
        "sort_order": 20,
        "is_required": True,
    },
    {
        "key": "materials_added",
        "title": "Материалы добавлены",
        "description": "Добавить фактические материалы к позициям заказа.",
        "sort_order": 30,
        "is_required": True,
    },
    {
        "key": "work_started",
        "title": "Работы начаты",
        "description": "Подтвердить старт производственных работ.",
        "sort_order": 40,
        "is_required": True,
    },
    {
        "key": "quality_control",
        "title": "Контроль качества",
        "description": "Проверить качество выполненных работ перед выдачей.",
        "sort_order": 50,
        "is_required": True,
    },
    {
        "key": "after_photos",
        "title": "Фото после работ",
        "description": "Загрузить фото автомобиля после выполнения работ.",
        "sort_order": 60,
        "is_required": True,
    },
    {
        "key": "ready_for_delivery",
        "title": "Готово к выдаче",
        "description": "Финальная проверка перед выдачей клиенту.",
        "sort_order": 70,
        "is_required": True,
    },
]


def ensure_order_exists(order_id: int, db: Session) -> Order:
    order = db.query(Order).filter(Order.id == order_id).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    return order


def create_default_checklist_if_empty(
    order: Order,
    db: Session,
    current_user: User,
) -> None:
    existing_count = (
        db.query(OrderChecklistItem)
        .filter(OrderChecklistItem.order_id == order.id)
        .count()
    )

    if existing_count > 0:
        return

    for item in DEFAULT_CHECKLIST_ITEMS:
        db.add(
            OrderChecklistItem(
                order_id=order.id,
                key=item["key"],
                title=item["title"],
                description=item["description"],
                sort_order=item["sort_order"],
                is_required=item["is_required"],
                status="pending",
            )
        )

    audit_log = OrderChecklistAuditLog(
        order_id=order.id,
        checklist_item_id=None,
        actor_user_id=current_user.id,
        action="checklist_created",
        details=json.dumps(
            {
                "items_count": len(DEFAULT_CHECKLIST_ITEMS),
                "source": "default_template",
            },
            ensure_ascii=False,
        ),
    )

    db.add(audit_log)
    db.commit()


def get_order_checklist_items(order_id: int, db: Session):
    return (
        db.query(OrderChecklistItem)
        .options(joinedload(OrderChecklistItem.completed_by_user))
        .filter(OrderChecklistItem.order_id == order_id)
        .order_by(OrderChecklistItem.sort_order.asc(), OrderChecklistItem.id.asc())
        .all()
    )


@router.get(
    "/orders/{order_id}/checklist",
    response_model=list[OrderChecklistItemResponse],
)
def get_order_checklist(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("order_checklist.read")),
):
    order = ensure_order_exists(order_id, db)
    create_default_checklist_if_empty(order, db, current_user)

    return get_order_checklist_items(order.id, db)


@router.post(
    "/orders/{order_id}/checklist",
    response_model=OrderChecklistItemResponse,
)
def create_order_checklist_item(
    order_id: int,
    data: OrderChecklistItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("order_checklist.manage")),
):
    try:
        order = ensure_order_exists(order_id, db)

        if order.status in ["canceled", "delivered"]:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot add checklist item to order with status {order.status}",
            )

        item = OrderChecklistItem(
            order_id=order.id,
            key=data.key,
            title=data.title,
            description=data.description,
            status="pending",
            is_required=data.is_required,
            sort_order=data.sort_order,
            comment=data.comment,
        )

        db.add(item)
        db.flush()

        audit_log = OrderChecklistAuditLog(
            order_id=order.id,
            checklist_item_id=item.id,
            actor_user_id=current_user.id,
            action="item_created",
            details=json.dumps(
                {
                    "item": {
                        "id": item.id,
                        "key": item.key,
                        "title": item.title,
                        "sort_order": item.sort_order,
                        "is_required": item.is_required,
                    }
                },
                ensure_ascii=False,
            ),
        )

        db.add(audit_log)
        db.commit()
        db.refresh(item)

        return item

    except HTTPException:
        db.rollback()
        raise

    except Exception:
        db.rollback()
        raise


@router.patch(
    "/order-checklist/{item_id}",
    response_model=OrderChecklistItemResponse,
)
def update_order_checklist_item(
    item_id: int,
    data: OrderChecklistItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("order_checklist.manage")),
):
    try:
        item = (
            db.query(OrderChecklistItem)
            .options(joinedload(OrderChecklistItem.completed_by_user))
            .filter(OrderChecklistItem.id == item_id)
            .first()
        )

        if not item:
            raise HTTPException(status_code=404, detail="Checklist item not found")

        order = ensure_order_exists(item.order_id, db)

        if order.status in ["canceled", "delivered"]:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot update checklist item for order with status {order.status}",
            )

        before = {
            "title": item.title,
            "description": item.description,
            "is_required": item.is_required,
            "sort_order": item.sort_order,
            "comment": item.comment,
        }

        if data.title is not None:
            item.title = data.title

        if data.description is not None:
            item.description = data.description

        if data.is_required is not None:
            item.is_required = data.is_required

        if data.sort_order is not None:
            item.sort_order = data.sort_order

        if data.comment is not None:
            item.comment = data.comment

        item.updated_at = datetime.utcnow()

        after = {
            "title": item.title,
            "description": item.description,
            "is_required": item.is_required,
            "sort_order": item.sort_order,
            "comment": item.comment,
        }

        audit_log = OrderChecklistAuditLog(
            order_id=order.id,
            checklist_item_id=item.id,
            actor_user_id=current_user.id,
            action="item_updated",
            details=json.dumps(
                {
                    "before": before,
                    "after": after,
                },
                ensure_ascii=False,
            ),
        )

        db.add(audit_log)
        db.commit()
        db.refresh(item)

        return item

    except HTTPException:
        db.rollback()
        raise

    except Exception:
        db.rollback()
        raise


@router.patch(
    "/order-checklist/{item_id}/complete",
    response_model=OrderChecklistItemResponse,
)
def complete_order_checklist_item(
    item_id: int,
    data: OrderChecklistItemComplete,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("order_checklist.update")),
):
    try:
        item = (
            db.query(OrderChecklistItem)
            .options(joinedload(OrderChecklistItem.completed_by_user))
            .filter(OrderChecklistItem.id == item_id)
            .first()
        )

        if not item:
            raise HTTPException(status_code=404, detail="Checklist item not found")

        order = ensure_order_exists(item.order_id, db)

        if order.status in ["canceled", "delivered"]:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot complete checklist item for order with status {order.status}",
            )

        if item.status == "done":
            return item

        item.status = "done"
        item.completed_at = datetime.utcnow()
        item.completed_by_user_id = current_user.id

        if data.comment is not None:
            item.comment = data.comment

        item.updated_at = datetime.utcnow()

        audit_log = OrderChecklistAuditLog(
            order_id=order.id,
            checklist_item_id=item.id,
            actor_user_id=current_user.id,
            action="item_completed",
            details=json.dumps(
                {
                    "item": {
                        "id": item.id,
                        "key": item.key,
                        "title": item.title,
                        "comment": item.comment,
                    }
                },
                ensure_ascii=False,
            ),
        )

        db.add(audit_log)
        db.commit()
        db.refresh(item)

        return item

    except HTTPException:
        db.rollback()
        raise

    except Exception:
        db.rollback()
        raise


@router.patch(
    "/order-checklist/{item_id}/reopen",
    response_model=OrderChecklistItemResponse,
)
def reopen_order_checklist_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("order_checklist.update")),
):
    try:
        item = (
            db.query(OrderChecklistItem)
            .options(joinedload(OrderChecklistItem.completed_by_user))
            .filter(OrderChecklistItem.id == item_id)
            .first()
        )

        if not item:
            raise HTTPException(status_code=404, detail="Checklist item not found")

        order = ensure_order_exists(item.order_id, db)

        if order.status in ["canceled", "delivered"]:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot reopen checklist item for order with status {order.status}",
            )

        if item.status == "pending":
            return item

        item.status = "pending"
        item.completed_at = None
        item.completed_by_user_id = None
        item.updated_at = datetime.utcnow()

        audit_log = OrderChecklistAuditLog(
            order_id=order.id,
            checklist_item_id=item.id,
            actor_user_id=current_user.id,
            action="item_reopened",
            details=json.dumps(
                {
                    "item": {
                        "id": item.id,
                        "key": item.key,
                        "title": item.title,
                    }
                },
                ensure_ascii=False,
            ),
        )

        db.add(audit_log)
        db.commit()
        db.refresh(item)

        return item

    except HTTPException:
        db.rollback()
        raise

    except Exception:
        db.rollback()
        raise


@router.get(
    "/orders/{order_id}/checklist/audit-logs",
    response_model=list[OrderChecklistAuditLogResponse],
)
def get_order_checklist_audit_logs(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("order_checklist.read")),
):
    ensure_order_exists(order_id, db)

    return (
        db.query(OrderChecklistAuditLog)
        .options(joinedload(OrderChecklistAuditLog.actor_user))
        .filter(OrderChecklistAuditLog.order_id == order_id)
        .order_by(OrderChecklistAuditLog.created_at.desc())
        .all()
    )