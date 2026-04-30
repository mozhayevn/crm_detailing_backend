from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from app.database import Base
from sqlalchemy import DateTime, Date, Text
from datetime import datetime, date


class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    phone = Column(String, unique=True, nullable=False)
    birth_date = Column(Date, nullable=True)
    preferences = Column(Text, nullable=True)

    cars = relationship("Car", back_populates="client", cascade="all, delete")
    orders = relationship("Order", back_populates="client")


class CarType(Base):
    __tablename__ = "car_types"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)


class Car(Base):
    __tablename__ = "cars"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    car_type_id = Column(Integer, ForeignKey("car_types.id"), nullable=True)
    brand = Column(String, nullable=False)
    model = Column(String, nullable=False)
    year = Column(Integer, nullable=True)
    color = Column(String, nullable=True)
    plate_number = Column(String, unique=True, nullable=True)

    client = relationship("Client", back_populates="cars")


class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)
    requires_brand = Column(Boolean, default=False)
    requires_package = Column(Boolean, default=False)
    base_labor_cost = Column(Integer, nullable=False, default=0)


class MaterialBrand(Base):
    __tablename__ = "material_brands"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=True)


class ServicePackage(Base):
    __tablename__ = "service_packages"

    id = Column(Integer, primary_key=True, index=True)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)

    service = relationship("Service")


class ServicePriceRule(Base):
    __tablename__ = "service_price_rules"

    id = Column(Integer, primary_key=True, index=True)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)
    car_type_id = Column(Integer, ForeignKey("car_types.id"), nullable=False)
    material_brand_id = Column(Integer, ForeignKey("material_brands.id"), nullable=True)
    service_package_id = Column(Integer, ForeignKey("service_packages.id"), nullable=True)
    price = Column(Integer, nullable=False)

    service = relationship("Service")
    car_type = relationship("CarType")
    material_brand = relationship("MaterialBrand")
    service_package = relationship("ServicePackage")


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)
    parent_role_id = Column(Integer, ForeignKey("roles.id"), nullable=True)

    parent_role = relationship("Role", remote_side=[id])


class Permission(Base):
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)


class RolePermission(Base):
    __tablename__ = "role_permissions"

    id = Column(Integer, primary_key=True, index=True)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    permission_id = Column(Integer, ForeignKey("permissions.id"), nullable=False)

    role = relationship("Role")
    permission = relationship("Permission")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone = Column(String, unique=True, nullable=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_super_admin = Column(Boolean, default=False)
    must_change_password = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    #roles = relationship("Role", secondary="user_roles", back_populates="users")


class UserRole(Base):
    __tablename__ = "user_roles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)

    user = relationship("User")
    role = relationship("Role")


class WorkBay(Base):
    __tablename__ = "work_bays"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    is_active = Column(Boolean, default=True)


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    car_id = Column(Integer, ForeignKey("cars.id"), nullable=False)
    assigned_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    work_bay_id = Column(Integer, ForeignKey("work_bays.id"), nullable=True)

    status = Column(String, default="new")
    comment = Column(String, nullable=True)
    cancellation_reason = Column(String, nullable=True)

    total_price = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)
    scheduled_at = Column(DateTime, nullable=True)
    planned_start_at = Column(DateTime, nullable=True)
    planned_end_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    rescheduled_from = Column(DateTime, nullable=True)
    pricing_locked = Column(Boolean, nullable=False, default=False)

    client = relationship("Client", back_populates="orders")
    car = relationship("Car")
    assigned_user = relationship("User", foreign_keys=[assigned_user_id])
    work_bay = relationship("WorkBay")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)
    material_brand_id = Column(Integer, ForeignKey("material_brands.id"), nullable=True)
    service_package_id = Column(Integer, ForeignKey("service_packages.id"), nullable=True)

    price = Column(Integer, nullable=False, default=0)
    quantity = Column(Integer, nullable=False, default=1)

    discount_amount = Column(Integer, nullable=False, default=0)  # legacy / computed
    discount_percent = Column(Integer, nullable=False, default=0)
    discount_reason = Column(String, nullable=True)
    discount_applied_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    total = Column(Integer, nullable=False, default=0)

    base_cost_snapshot = Column(Integer, nullable=False, default=0)
    gross_price_snapshot = Column(Integer, nullable=False, default=0)
    discount_amount_snapshot = Column(Integer, nullable=False, default=0)
    final_price_snapshot = Column(Integer, nullable=False, default=0)
    profit_snapshot = Column(Integer, nullable=False, default=0)

    discount_applied_by_user = relationship("User", foreign_keys=[discount_applied_by_user_id])
    order = relationship("Order", back_populates="items")


class OrderStatusHistory(Base):
    __tablename__ = "order_status_history"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    old_status = Column(String, nullable=True)
    new_status = Column(String, nullable=False)
    changed_at = Column(DateTime, default=datetime.utcnow)

    order = relationship("Order")


class Unit(Base):
    __tablename__ = "units"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    code = Column(String, unique=True, nullable=False)


class Material(Base):
    __tablename__ = "materials"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    brand_id = Column(Integer, ForeignKey("material_brands.id"), nullable=True)
    category = Column(String, nullable=True)
    unit_id = Column(Integer, ForeignKey("units.id"), nullable=False)
    cost_per_unit = Column(Integer, nullable=False, default=0)
    is_active = Column(Boolean, default=True)

    brand = relationship("MaterialBrand")
    unit = relationship("Unit")


class OrderItemMaterial(Base):
    __tablename__ = "order_item_materials"

    id = Column(Integer, primary_key=True, index=True)
    order_item_id = Column(Integer, ForeignKey("order_items.id"), nullable=False)
    material_id = Column(Integer, ForeignKey("materials.id"), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    unit_cost = Column(Integer, nullable=False)
    total_cost = Column(Integer, nullable=False)
    comment = Column(String, nullable=True)

    order_item = relationship("OrderItem")
    material = relationship("Material")


class CarTypePricingRule(Base):
    __tablename__ = "car_type_pricing_rules"

    id = Column(Integer, primary_key=True, index=True)
    car_type_id = Column(Integer, ForeignKey("car_types.id"), nullable=False, unique=True)
    multiplier = Column(Integer, nullable=False, default=100)

    car_type = relationship("CarType")


class UserRoleAuditLog(Base):
    __tablename__ = "user_role_audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    actor_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    target_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=True)
    action = Column(String, nullable=False)  # user_created / role_assigned / role_removed
    details = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    actor_user = relationship("User", foreign_keys=[actor_user_id])
    target_user = relationship("User", foreign_keys=[target_user_id])
    role = relationship("Role")

    @property
    def actor_user_full_name(self) -> str | None:
        return self.actor_user.full_name if self.actor_user else None

    @property
    def target_user_full_name(self) -> str | None:
        return self.target_user.full_name if self.target_user else None

    @property
    def role_name(self) -> str | None:
        return self.role.name if self.role else None


class OrderAuditLog(Base):
    __tablename__ = "order_audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    actor_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action = Column(String, nullable=False)  # created / updated / status_changed / rescheduled / canceled
    details = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    order = relationship("Order")
    actor_user = relationship("User")

    @property
    def actor_user_full_name(self) -> str | None:
        return self.actor_user.full_name if self.actor_user else None


class PricingAuditLog(Base):
    __tablename__ = "pricing_audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    actor_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action = Column(String, nullable=False)  # pricing_applied
    details = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    order = relationship("Order")
    actor_user = relationship("User")

    @property
    def actor_user_full_name(self) -> str | None:
        return self.actor_user.full_name if self.actor_user else None


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)

    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    amount = Column(Integer, nullable=False)

    method = Column(String, nullable=False)  # cash / kaspi / card / bank_transfer / other
    status = Column(String, nullable=False, default="completed")  # completed / canceled / refunded

    comment = Column(String, nullable=True)

    paid_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    created_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    canceled_at = Column(DateTime, nullable=True)
    canceled_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    cancel_reason = Column(String, nullable=True)

    order = relationship("Order")
    created_by_user = relationship("User", foreign_keys=[created_by_user_id])
    canceled_by_user = relationship("User", foreign_keys=[canceled_by_user_id])

    @property
    def created_by_user_full_name(self) -> str | None:
        return self.created_by_user.full_name if self.created_by_user else None

    @property
    def canceled_by_user_full_name(self) -> str | None:
        return self.canceled_by_user.full_name if self.canceled_by_user else None


class PaymentAuditLog(Base):
    __tablename__ = "payment_audit_logs"

    id = Column(Integer, primary_key=True, index=True)

    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    payment_id = Column(Integer, ForeignKey("payments.id"), nullable=True)

    actor_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    action = Column(String, nullable=False)  # payment_created / payment_canceled
    details = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    order = relationship("Order")
    payment = relationship("Payment")
    actor_user = relationship("User")

    @property
    def actor_user_full_name(self) -> str | None:
        return self.actor_user.full_name if self.actor_user else None

