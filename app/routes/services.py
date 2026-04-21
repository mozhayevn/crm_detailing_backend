from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.deps import require_permission
from app.database import get_db
from app.models import Service, User
from app.schemas import ServiceCreate, ServiceUpdate, ServiceResponse

router = APIRouter(prefix="/services", tags=["Services"])


@router.post("/", response_model=ServiceResponse)
def create_service(
        service: ServiceCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(require_permission("services.create"))
):
    existing = db.query(Service).filter(Service.name == service.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Service already exists")

    new_service = Service(
        name=service.name,
        description=service.description,
        requires_brand=service.requires_brand,
        requires_package=service.requires_package,
        base_labor_cost=service.base_labor_cost,
    )

    db.add(new_service)
    db.commit()
    db.refresh(new_service)
    return new_service


@router.get("/", response_model=list[ServiceResponse])
def get_services(db: Session = Depends(get_db), current_user: User = Depends(require_permission("services.read"))):
    return db.query(Service).order_by(Service.id.desc()).all()


@router.get("/{service_id}", response_model=ServiceResponse)
def get_service(
        service_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(require_permission("services.read"))):

    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return service


@router.put("/{service_id}", response_model=ServiceResponse)
def update_service(
        service_id: int,
        service_data: ServiceUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(require_permission("services.update"))):

    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    update_data = service_data.model_dump(exclude_unset=True)

    if "name" in update_data:
        existing = (
            db.query(Service)
            .filter(Service.name == update_data["name"], Service.id != service_id)
            .first()
        )
        if existing:
            raise HTTPException(status_code=400, detail="Another service with this name already exists")

    for key, value in update_data.items():
        setattr(service, key, value)

    db.commit()
    db.refresh(service)
    return service


@router.delete("/{service_id}")
def delete_service(
        service_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(require_permission("service.delete")),
):

    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    db.delete(service)
    db.commit()
    return {"message": "Service deleted successfully"}


