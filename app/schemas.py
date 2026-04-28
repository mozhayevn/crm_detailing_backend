from pydantic import BaseModel
from datetime import datetime, date


class ClientCreate(BaseModel):
    full_name: str
    phone: str
    birth_date: date | None = None
    preferences: str | None = None


class ClientUpdate(BaseModel):
    full_name: str | None = None
    phone: str | None = None
    birth_date: date | None = None
    preferences: str | None = None


class ClientResponse(BaseModel):
    id: int
    full_name: str
    phone: str
    birth_date: date | None = None
    preferences: str | None = None

    class Config:
        from_attributes = True


class ClientHistoryItemResponse(BaseModel):
    order_id: int
    status: str
    created_at: datetime
    scheduled_at: datetime | None = None
    planned_start_at: datetime | None = None
    planned_end_at: datetime | None = None
    total_price: int
    comment: str | None = None
    items_count: int

    class Config:
        from_attributes = True


class CarTypeCreate(BaseModel):
    name: str


class CarTypeUpdate(BaseModel):
    name: str | None = None


class CarTypeResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class CarCreate(BaseModel):
    client_id: int
    car_type_id: int | None = None
    brand: str
    model: str
    year: int | None = None
    color: str | None = None
    plate_number: str | None = None


class CarUpdate(BaseModel):
    client_id: int | None = None
    car_type_id: int | None = None
    brand: str | None = None
    model: str | None = None
    year: int | None = None
    color: str | None = None
    plate_number: str | None = None


class CarResponse(BaseModel):
    id: int
    client_id: int
    car_type_id: int | None = None
    brand: str
    model: str
    year: int | None = None
    color: str | None = None
    plate_number: str | None = None

    class Config:
        from_attributes = True


class ServiceCreate(BaseModel):
    name: str
    description: str | None = None
    requires_brand: bool = False
    requires_package: bool = False
    base_labor_cost: int = 0


class ServiceUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    requires_brand: bool | None = None
    requires_package: bool | None = None
    base_labor_cost: int | None = None


class ServiceResponse(BaseModel):
    id: int
    name: str
    description: str | None = None
    requires_brand: bool
    requires_package: bool
    base_labor_cost: int

    class Config:
        from_attributes = True


class ServicePriceCreate(BaseModel):
    service_id: int
    car_type_id: int
    price: int


class ServicePriceUpdate(BaseModel):
    service_id: int | None = None
    car_type_id: int | None = None
    price: int | None = None


class ServicePriceResponse(BaseModel):
    id: int
    service_id: int
    car_type_id: int
    price: int

    class Config:
        from_attributes = True


class PriceByCarAndServiceResponse(BaseModel):
    car_id: int
    service_id: int
    car_type_id: int
    price: int

    class Config:
        from_attributes = True


# class ServiceCreate(BaseModel):
#     name: str
#     description: str | None = None
#     requires_brand: bool = False
#     requires_package: bool = False
#
#
# class ServiceResponse(BaseModel):
#     id: int
#     name: str
#     description: str | None = None
#     requires_brand: bool
#     requires_package: bool
#
#     class Config:
#         from_attributes = True


# Бренды
class MaterialBrandCreate(BaseModel):
    name: str
    category: str | None = None


class MaterialBrandUpdate(BaseModel):
    name: str | None = None


class MaterialBrandResponse(BaseModel):
    id: int
    name: str
    category: str | None = None

    class Config:
        from_attributes = True


# Пакеты
class ServicePackageCreate(BaseModel):
    service_id: int
    name: str
    description: str | None = None


class ServicePackageUpdate(BaseModel):
    service_id: int | None = None
    name: str | None = None
    description: str | None = None


class ServicePackageResponse(BaseModel):
    id: int
    service_id: int
    name: str
    description: str | None = None

    class Config:
        from_attributes = True


class ServicePriceRuleCreate(BaseModel):
    service_id: int
    car_type_id: int
    material_brand_id: int | None = None
    service_package_id: int | None = None
    price: int


class ServicePriceRuleUpdate(BaseModel):
    service_id: int | None = None
    car_type_id: int | None = None
    material_brand_id: int | None = None
    service_package_id: int | None = None
    price: int | None = None


class ServicePriceRuleResponse(BaseModel):
    id: int
    service_id: int
    car_type_id: int
    material_brand_id: int | None = None
    service_package_id: int | None = None
    price: int

    class Config:
        from_attributes = True


class PriceCalculationResponse(BaseModel):
    car_id: int
    service_id: int
    car_type_id: int
    material_brand_id: int | None = None
    service_package_id: int | None = None
    price: int

    class Config:
        from_attributes = True


class OrderItemCreate(BaseModel):
    service_id: int
    material_brand_id: int | None = None
    service_package_id: int | None = None
    quantity: int = 1
    discount_percent: int = 0
    discount_reason: str | None = None


class OrderCreate(BaseModel):
    client_id: int
    car_id: int
    assigned_user_id: int | None = None
    work_bay_id: int | None = None
    scheduled_at: datetime | None = None
    planned_start_at: datetime | None = None
    planned_end_at: datetime | None = None
    comment: str | None = None
    items: list[OrderItemCreate]


class OrderItemResponse(BaseModel):
    id: int
    order_id: int
    service_id: int
    material_brand_id: int | None = None
    service_package_id: int | None = None
    price: int
    quantity: int
    discount_amount: int
    discount_percent: int
    discount_reason: str | None = None
    discount_applied_by_user_id: int | None = None
    total: int
    base_cost_snapshot: int
    gross_price_snapshot: int
    discount_amount_snapshot: int
    final_price_snapshot: int
    profit_snapshot: int

    class Config:
        from_attributes = True


class OrderResponse(BaseModel):
    id: int
    client_id: int
    car_id: int
    status: str
    assigned_user_id: int | None = None
    work_bay_id: int | None = None
    comment: str | None = None
    cancellation_reason: str | None = None
    total_price: int

    created_at: datetime
    scheduled_at: datetime | None = None
    planned_start_at: datetime | None = None
    planned_end_at: datetime | None = None
    completed_at: datetime | None = None
    delivered_at: datetime | None = None
    rescheduled_from: datetime | None = None
    pricing_locked: bool

    items: list[OrderItemResponse]

    class Config:
        from_attributes = True


#new
class OrderListItemResponse(BaseModel):
    id: int
    status: str
    total_price: int
    pricing_locked: bool

    created_at: datetime
    scheduled_at: datetime | None = None
    planned_start_at: datetime | None = None
    planned_end_at: datetime | None = None

    client_id: int
    client_full_name: str | None = None
    client_phone: str | None = None

    car_id: int
    car_brand: str | None = None
    car_model: str | None = None
    car_plate_number: str | None = None

    work_bay_id: int | None = None
    work_bay_name: str | None = None

    assigned_user_id: int | None = None
    assigned_user_full_name: str | None = None

    class Config:
        from_attributes = True

#new ends


class OrderItemUpdate(BaseModel):
    id: int | None = None
    service_id: int
    material_brand_id: int | None = None
    service_package_id: int | None = None
    quantity: int = 1
    discount_percent: int = 0
    discount_reason: str | None = None


class OrderStatusUpdate(BaseModel):
    status: str


class OrderUpdate(BaseModel):
    assigned_user_id: int | None = None
    work_bay_id: int | None = None
    scheduled_at: datetime | None = None
    planned_start_at: datetime | None = None
    planned_end_at: datetime | None = None
    comment: str | None = None
    items: list[OrderItemUpdate]


class OrderStatusHistoryResponse(BaseModel):
    id: int
    order_id: int
    old_status: str | None = None
    new_status: str
    changed_at: datetime

    class Config:
        from_attributes = True


class OrderReschedule(BaseModel):
    scheduled_at: datetime | None = None
    planned_start_at: datetime | None = None
    planned_end_at: datetime | None = None
    comment: str | None = None


class OrderCancel(BaseModel):
    reason: str


class RoleCreate(BaseModel):
    name: str
    description: str | None = None
    parent_role_id: int | None = None


class RoleResponse(BaseModel):
    id: int
    name: str
    description: str | None = None
    parent_role_id: int | None = None

    class Config:
        from_attributes = True


class PermissionCreate(BaseModel):
    code: str
    description: str | None = None


class PermissionResponse(BaseModel):
    id: int
    code: str
    description: str | None = None

    class Config:
        from_attributes = True


class RolePermissionAssign(BaseModel):
    role_id: int
    permission_id: int


class UserCreate(BaseModel):
    full_name: str
    email: str
    phone: str | None = None
    password: str
    is_super_admin: bool = False
    is_active: bool = True
    must_change_password: bool = False


class UserResponse(BaseModel):
    id: int
    full_name: str
    email: str
    phone: str | None = None
    is_active: bool
    is_super_admin: bool
    must_change_password: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserRoleAssign(BaseModel):
    user_id: int
    role_id: int


class WorkBayCreate(BaseModel):
    name: str
    description: str | None = None


class WorkBayUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class WorkBayResponse(BaseModel):
    id: int
    name: str
    description: str | None = None

    class Config:
        from_attributes = True


class WorkBayAvailabilityResponse(BaseModel):
    id: int
    name: str
    description: str | None = None
    is_available: bool
    conflicting_order_id: int | None = None

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class LoginRequest(BaseModel):
    email: str
    password: str


class MyPermissionsResponse(BaseModel):
    user_id: int
    full_name: str
    email: str
    is_super_admin: bool
    roles: list[str]
    permissions: list[str]


class RolePermissionsResponse(BaseModel):
    role_id: int
    role_name: str
    parent_role_id: int | None = None
    parent_role_name: str | None = None
    direct_permissions: list[str]
    inherited_permissions: list[str]
    all_permissions: list[str]


class UserRolesResponse(BaseModel):
    user_id: int
    full_name: str
    roles: list[str]


class UnitCreate(BaseModel):
    name: str
    code: str


class UnitResponse(BaseModel):
    id: int
    name: str
    code: str

    class Config:
        from_attributes = True


class MaterialCreate(BaseModel):
    name: str
    brand_id: int | None = None
    category: str | None = None
    unit_id: int
    cost_per_unit: int
    is_active: bool = True


class MaterialUpdate(BaseModel):
    name: str | None = None
    brand_id: int | None = None
    category: str | None = None
    unit_id: int | None = None
    cost_per_unit: int | None = None
    is_active: bool | None = None


class MaterialResponse(BaseModel):
    id: int
    name: str
    brand_id: int | None = None
    category: str | None = None
    unit_id: int
    cost_per_unit: int
    is_active: bool

    class Config:
        from_attributes = True


class OrderItemMaterialCreate(BaseModel):
    material_id: int
    quantity: int
    comment: str | None = None


class OrderItemMaterialResponse(BaseModel):
    id: int
    order_item_id: int
    material_id: int
    quantity: int
    unit_cost: int
    total_cost: int
    comment: str | None = None

    class Config:
        from_attributes = True


class CarTypePricingRuleCreate(BaseModel):
    car_type_id: int
    multiplier: int


class CarTypePricingRuleUpdate(BaseModel):
    multiplier: int | None = None


class CarTypePricingRuleResponse(BaseModel):
    id: int
    car_type_id: int
    multiplier: int

    class Config:
        from_attributes = True


class OrderItemPricingResponse(BaseModel):
    order_item_id: int
    order_id: int
    service_id: int
    car_type_id: int
    materials_cost: int
    labor_cost: int
    car_type_multiplier: int
    base_cost: int
    gross_price: int
    discount_percent: int
    discount_amount: int
    final_price: int
    profit: int
    has_warning: bool
    warning_level: str
    warning_message: str | None = None


class OrderPricingResponse(BaseModel):
    order_id: int
    items_count: int
    total_materials_cost: int
    total_labor_cost: int
    total_gross_price: int
    total_discount_amount: int
    total_final_price: int
    total_profit: int
    has_warning: bool
    warning_level: str
    warning_message: str | None = None


class UserRoleAuditLogResponse(BaseModel):
    id: int
    actor_user_id: int
    actor_user_full_name: str | None = None
    target_user_id: int
    target_user_full_name: str | None = None
    role_id: int | None = None
    role_name: str | None = None
    action: str
    details: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class OrderAuditLogResponse(BaseModel):
    id: int
    order_id: int
    actor_user_id: int
    actor_user_full_name: str | None = None
    action: str
    details: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class PricingAuditLogResponse(BaseModel):
    id: int
    order_id: int
    actor_user_id: int
    actor_user_full_name: str | None = None
    action: str
    details: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class PricingUnlockRequest(BaseModel):
    reason: str
