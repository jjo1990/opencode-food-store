# Database Design Skill

**Patterns and best practices for designing PostgreSQL schemas with SQLModel and Alembic migrations**

## Overview

This skill provides guidance for designing normalized database schemas, managing migrations, and ensuring data integrity in PostgreSQL using SQLModel ORM and Alembic for version control.

## Schema Design Principles

### 1. Normalization (3NF)

**Bad - Denormalized** ❌
```python
class User(Base):
    id: int
    email: str
    password_hash: str
    category_names: str  # CSV: "fruits,vegetables"
    category_ids: str    # CSV: "1,2,3"
```

**Good - Normalized** ✅
```python
class User(Base):
    __tablename__ = "users"
    id: int = Field(primary_key=True)
    email: str = Field(unique=True, index=True)
    password_hash: str

class UserCategory(Base):
    __tablename__ = "user_categories"
    id: int = Field(primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    category_id: int = Field(foreign_key="categories.id")
```

### 2. Relationships

**One-to-Many**
```python
class User(Base):
    __tablename__ = "users"
    id: int = Field(primary_key=True)
    email: str
    orders: List["Order"] = Relationship(back_populates="user")

class Order(Base):
    __tablename__ = "orders"
    id: int = Field(primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    user: User = Relationship(back_populates="orders")
```

**Many-to-Many**
```python
# Association table
class ProductCategory(Base):
    __tablename__ = "product_categories"
    product_id: int = Field(foreign_key="products.id", primary_key=True)
    category_id: int = Field(foreign_key="categories.id", primary_key=True)

class Product(Base):
    __tablename__ = "products"
    id: int = Field(primary_key=True)
    name: str
    categories: List["Category"] = Relationship(
        back_populates="products",
        link_model=ProductCategory
    )

class Category(Base):
    __tablename__ = "categories"
    id: int = Field(primary_key=True)
    name: str
    products: List["Product"] = Relationship(
        back_populates="categories",
        link_model=ProductCategory
    )
```

## Complete Food Store Schema

### User Management

```python
# File: backend/app/db/models/user.py

from sqlmodel import SQLModel, Field, Column, String, CHAR
from datetime import datetime
from typing import Optional, List
from enum import Enum

class RoleEnum(str, Enum):
    ADMIN = "admin"
    VENDOR = "vendor"
    CUSTOMER = "customer"

class User(SQLModel, table=True):
    __tablename__ = "users"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    password_hash: str = Field(max_length=255)
    first_name: str = Field(max_length=100)
    last_name: str = Field(max_length=100)
    role: RoleEnum = Field(default=RoleEnum.CUSTOMER)
    is_active: bool = Field(default=True, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    addresses: List["UserAddress"] = Relationship(back_populates="user")
    orders: List["Order"] = Relationship(back_populates="user")
    refresh_tokens: List["RefreshToken"] = Relationship(back_populates="user")
    audit_logs: List["AuditLog"] = Relationship(back_populates="user")
    
    class Config:
        orm_mode = True

class RefreshToken(SQLModel, table=True):
    __tablename__ = "refresh_tokens"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    token: str = Field(unique=True, index=True)
    expires_at: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    user: User = Relationship(back_populates="refresh_tokens")
```

### Product Catalog

```python
# File: backend/app/db/models/product.py

class Category(SQLModel, table=True):
    __tablename__ = "categories"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True, max_length=100)
    description: str
    parent_id: Optional[int] = Field(default=None, foreign_key="categories.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    products: List["Product"] = Relationship(back_populates="category")

class Product(SQLModel, table=True):
    __tablename__ = "products"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, max_length=255)
    description: str
    category_id: int = Field(foreign_key="categories.id")
    price: float = Field(gt=0)
    stock: int = Field(default=0)
    sku: str = Field(unique=True, index=True, max_length=50)
    image_url: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    category: Category = Relationship(back_populates="products")
    order_items: List["OrderItem"] = Relationship(back_populates="product")
    ingredients: List["Ingredient"] = Relationship(
        back_populates="products",
        link_model="ProductIngredient"
    )
```

### Orders & Payments

```python
# File: backend/app/db/models/order.py

class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PAID = "paid"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class Order(SQLModel, table=True):
    __tablename__ = "orders"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    status: OrderStatus = Field(default=OrderStatus.PENDING, index=True)
    total_amount: float = Field(gt=0)
    delivery_address_id: int = Field(foreign_key="user_addresses.id")
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    user: User = Relationship(back_populates="orders")
    items: List["OrderItem"] = Relationship(back_populates="order")
    payment: Optional["Payment"] = Relationship(back_populates="order")
    delivery_address: "UserAddress" = Relationship()

class OrderItem(SQLModel, table=True):
    __tablename__ = "order_items"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="orders.id", index=True)
    product_id: int = Field(foreign_key="products.id")
    quantity: int = Field(gt=0)
    unit_price: float = Field(gt=0)
    subtotal: float = Field(gt=0)
    
    # Relationships
    order: Order = Relationship(back_populates="items")
    product: Product = Relationship(back_populates="order_items")

class PaymentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    APPROVED = "approved"
    REJECTED = "rejected"
    REFUNDED = "refunded"

class Payment(SQLModel, table=True):
    __tablename__ = "payments"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="orders.id", unique=True, index=True)
    status: PaymentStatus = Field(default=PaymentStatus.PENDING, index=True)
    amount: float = Field(gt=0)
    payment_method: str = Field(max_length=50)  # "mercadopago", "credit_card"
    external_id: Optional[str] = Field(default=None, unique=True)  # MP transaction ID
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    order: Order = Relationship(back_populates="payment")
```

### Audit & Logging

```python
# File: backend/app/db/models/audit.py

class AuditLog(SQLModel, table=True):
    __tablename__ = "audit_logs"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="users.id", index=True)
    action: str = Field(index=True, max_length=50)  # "login", "register", "purchase"
    resource_type: str = Field(max_length=50)  # "user", "order", "product"
    resource_id: Optional[int] = None
    details: Optional[str] = None  # JSON
    ip_address: str = Field(max_length=45)
    user_agent: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow, index=True)
    
    # Relationships
    user: Optional[User] = Relationship(back_populates="audit_logs")
```

## Alembic Migrations

### Create Migration

```bash
# Create empty migration
alembic revision --autogenerate -m "Add user authentication"

# Generated file: backend/app/db/migrations/versions/xxxx_add_user_authentication.py
```

### Migration Template

```python
# File: backend/app/db/migrations/versions/001_add_users_table.py

from alembic import op
import sqlalchemy as sa

revision = '001'
down_revision = None

def upgrade():
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('role', sa.String(50), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
    op.create_index('ix_users_is_active', 'users', ['is_active'])

def downgrade():
    op.drop_index('ix_users_is_active')
    op.drop_index('ix_users_email')
    op.drop_table('users')
```

### Running Migrations

```bash
# Apply all migrations
alembic upgrade head

# Show current version
alembic current

# Rollback one migration
alembic downgrade -1

# View history
alembic history --verbose
```

## Indexing Strategy

### Indexes for Performance

```python
# High cardinality fields (good for indexing)
email: str = Field(unique=True, index=True)  # ✅ Unique values
is_active: bool = Field(index=True)           # ✅ Fast filtering
created_at: datetime = Field(index=True)      # ✅ Range queries
user_id: int = Field(foreign_key="users.id", index=True)  # ✅ Foreign key

# Low cardinality fields (avoid indexing)
role: RoleEnum = Field()  # ❌ Only 3 values
is_deleted: bool = Field() # ❌ Only 2 values
```

### Composite Indexes

```python
# Multiple columns that are often queried together
__table_args__ = (
    Index('ix_order_user_status', 'user_id', 'status'),
    Index('ix_product_category_active', 'category_id', 'is_active'),
)
```

## Query Optimization

### N+1 Problem

**Bad** ❌
```python
orders = session.query(Order).all()
for order in orders:
    print(order.user.email)  # N+1 query per order!
```

**Good** ✅
```python
from sqlalchemy.orm import selectinload
orders = session.query(Order).options(selectinload(Order.user)).all()
for order in orders:
    print(order.user.email)  # Only 2 queries total
```

## Food Store Phase 1 Schema

### Minimal Schema (Auth Only)

```python
# Users table
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  role VARCHAR(50) DEFAULT 'customer',
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX ix_users_email ON users(email);
CREATE INDEX ix_users_is_active ON users(is_active);

# Refresh tokens
CREATE TABLE refresh_tokens (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id),
  token VARCHAR(500) UNIQUE NOT NULL,
  expires_at TIMESTAMP NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX ix_refresh_tokens_token ON refresh_tokens(token);
CREATE INDEX ix_refresh_tokens_user_id ON refresh_tokens(user_id);

# Audit logs
CREATE TABLE audit_logs (
  id SERIAL PRIMARY KEY,
  user_id INTEGER REFERENCES users(id),
  action VARCHAR(50) NOT NULL,
  resource_type VARCHAR(50),
  resource_id INTEGER,
  details TEXT,
  ip_address VARCHAR(45) NOT NULL,
  user_agent VARCHAR(500),
  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX ix_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX ix_audit_logs_action ON audit_logs(action);
CREATE INDEX ix_audit_logs_timestamp ON audit_logs(timestamp);
```

## Best Practices

1. **Always Add Timestamps**
   ```python
   created_at: datetime = Field(default_factory=datetime.utcnow)
   updated_at: datetime = Field(default_factory=datetime.utcnow)
   ```

2. **Use Appropriate Data Types**
   ```python
   ✅ price: Decimal
   ✅ email: str with max_length
   ✅ role: Enum
   ❌ price: str
   ❌ email: str without validation
   ```

3. **Index Foreign Keys**
   ```python
   user_id: int = Field(foreign_key="users.id", index=True)
   ```

4. **Use Constraints**
   ```python
   price: float = Field(gt=0)  # Prevent negative prices
   quantity: int = Field(ge=0) # Prevent negative quantities
   email: str = Field(unique=True, index=True)  # Unique email
   ```

5. **Document Complex Models**
   ```python
   class Order(SQLModel, table=True):
       """
       Represents a customer order.
       
       States: pending → confirmed → paid → shipped → delivered
       Can transition to cancelled at any time.
       """
   ```

## See Also

- `backend/app/db/base.py` — Base models
- `backend/app/db/models/` — All model definitions
- `backend/app/db/migrations/` — Alembic migration history
- `docs/Integrador.txt` — Data model ERD
