from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import (
    ServicePriceRule,
    Service,
    CarType,
    MaterialBrand,
    ServicePackage,
)
from app.schemas import (
    ServicePriceRuleCreate,
    ServicePriceRuleUpdate,
    ServicePriceRuleResponse,
)

router = APIRouter(prefix="/service-price-rules", tags=["Service Price Rules"])


@router.post("/", response_model=ServicePriceRuleResponse)
def create_service_price_rule(rule: ServicePriceRuleCreate, db: Session = Depends(get_db)):
    service = db.query(Service).filter(Service.id == rule.service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    car_type = db.query(CarType).filter(CarType.id == rule.car_type_id).first()
    if not car_type:
        raise HTTPException(status_code=404, detail="Car type not found")

    if rule.material_brand_id is not None:
        brand = db.query(MaterialBrand).filter(MaterialBrand.id == rule.material_brand_id).first()
        if not brand:
            raise HTTPException(status_code=404, detail="Material brand not found")

    if rule.service_package_id is not None:
        package = db.query(ServicePackage).filter(ServicePackage.id == rule.service_package_id).first()
        if not package:
            raise HTTPException(status_code=404, detail="Service package not found")

    existing_rule = (
        db.query(ServicePriceRule)
        .filter(
            ServicePriceRule.service_id == rule.service_id,
            ServicePriceRule.car_type_id == rule.car_type_id,
            ServicePriceRule.material_brand_id == rule.material_brand_id,
            ServicePriceRule.service_package_id == rule.service_package_id,
        )
        .first()
    )
    if existing_rule:
        raise HTTPException(status_code=400, detail="Such price rule already exists")

    new_rule = ServicePriceRule(
        service_id=rule.service_id,
        car_type_id=rule.car_type_id,
        material_brand_id=rule.material_brand_id,
        service_package_id=rule.service_package_id,
        price=rule.price,
    )

    db.add(new_rule)
    db.commit()
    db.refresh(new_rule)
    return new_rule


@router.get("/", response_model=list[ServicePriceRuleResponse])
def get_service_price_rules(db: Session = Depends(get_db)):
    return db.query(ServicePriceRule).order_by(ServicePriceRule.id.desc()).all()


@router.get("/{rule_id}", response_model=ServicePriceRuleResponse)
def get_service_price_rule(rule_id: int, db: Session = Depends(get_db)):
    rule = db.query(ServicePriceRule).filter(ServicePriceRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Service price rule not found")
    return rule


@router.put("/{rule_id}", response_model=ServicePriceRuleResponse)
def update_service_price_rule(
    rule_id: int,
    rule_data: ServicePriceRuleUpdate,
    db: Session = Depends(get_db),
):
    rule = db.query(ServicePriceRule).filter(ServicePriceRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Service price rule not found")

    update_data = rule_data.model_dump(exclude_unset=True)

    new_service_id = update_data.get("service_id", rule.service_id)
    new_car_type_id = update_data.get("car_type_id", rule.car_type_id)
    new_material_brand_id = update_data.get("material_brand_id", rule.material_brand_id)
    new_service_package_id = update_data.get("service_package_id", rule.service_package_id)

    service = db.query(Service).filter(Service.id == new_service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    car_type = db.query(CarType).filter(CarType.id == new_car_type_id).first()
    if not car_type:
        raise HTTPException(status_code=404, detail="Car type not found")

    if new_material_brand_id is not None:
        brand = db.query(MaterialBrand).filter(MaterialBrand.id == new_material_brand_id).first()
        if not brand:
            raise HTTPException(status_code=404, detail="Material brand not found")

        if new_service_package_id is not None:
            package = db.query(ServicePackage).filter(ServicePackage.id == new_service_package_id).first()
            if not package:
                raise HTTPException(status_code=404, detail="Service package not found")

        duplicate_rule = (
            db.query(ServicePriceRule)
            .filter(
                ServicePriceRule.service_id == new_service_id,
                ServicePriceRule.car_type_id == new_car_type_id,
                ServicePriceRule.material_brand_id == new_material_brand_id,
                ServicePriceRule.service_package_id == new_service_package_id,
                ServicePriceRule.id != rule_id,
            )
            .first()
        )
        if duplicate_rule:
            raise HTTPException(status_code=400, detail="Another identical price rule already exists")

        for key, value in update_data.items():
            setattr(rule, key, value)

        db.commit()
        db.refresh(rule)
        return rule

    @router.delete("/{rule_id}")
    def delete_service_price_rule(rule_id: int, db: Session = Depends(get_db)):
        rule = db.query(ServicePriceRule).filter(ServicePriceRule.id == rule_id).first()
        if not rule:
            raise HTTPException(status_code=404, detail="Service price rule not found")

        db.delete(rule)
        db.commit()
        return {"message": "Service price rule deleted successfully"}