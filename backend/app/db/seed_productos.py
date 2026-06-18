"""
Database seed: productos, categorias y usuario admin.
"""

import logging
import os
import sys

from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.core.database import SessionLocal
from app.core.logging import setup_logging
from app.core.security import hash_password
from app.models.categoria import Categoria
from app.models.producto import Producto
from app.models.producto_categoria import ProductoCategoria
from app.models.user import User
from app.models.user_role import UserRole

logger = logging.getLogger(__name__)

categorias_data = [
    {"nombre": "Pizzas"},
    {"nombre": "Hamburguesas"},
    {"nombre": "Bebidas"},
    {"nombre": "Postres"},
    {"nombre": "Ensaladas"},
    {"nombre": "Pastas"},
]

productos_data = [
    {
        "nombre": "Pizza Margherita",
        "descripcion": "Pizza clasica con salsa de tomate, mozzarella fresca y albahaca. Horno de piedra.",
        "precio_base": 12.50,
        "stock_cantidad": 50,
        "imagen_url": "https://images.unsplash.com/photo-1574071318508-1cdbab80d002?w=600&h=400&fit=crop",
        "categorias": ["Pizzas"],
    },
    {
        "nombre": "Pizza Pepperoni",
        "descripcion": "Pizza con abundante pepperoni, queso mozzarella y salsa de tomate especiada.",
        "precio_base": 14.00,
        "stock_cantidad": 40,
        "imagen_url": "https://images.unsplash.com/photo-1628840042765-356cda07504e?w=600&h=400&fit=crop",
        "categorias": ["Pizzas"],
    },
    {
        "nombre": "Hamburguesa Clasica",
        "descripcion": "Hamburguesa de carne Angus 200g con lechuga, tomate, cebolla y salsa especial.",
        "precio_base": 10.50,
        "stock_cantidad": 60,
        "imagen_url": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=600&h=400&fit=crop",
        "categorias": ["Hamburguesas"],
    },
    {
        "nombre": "Hamburguesa BBQ",
        "descripcion": "Hamburguesa con bacon crocante, cheddar ahumado, aros de cebolla y salsa BBQ casera.",
        "precio_base": 13.00,
        "stock_cantidad": 45,
        "imagen_url": "https://images.unsplash.com/photo-1553979459-d2229ba7433b?w=600&h=400&fit=crop",
        "categorias": ["Hamburguesas"],
    },
    {
        "nombre": "Coca-Cola 500ml",
        "descripcion": "Botella de Coca-Cola 500ml bien fria.",
        "precio_base": 3.50,
        "stock_cantidad": 200,
        "imagen_url": "https://images.unsplash.com/photo-1554866585-cd94860890b7?w=600&h=400&fit=crop",
        "categorias": ["Bebidas"],
    },
    {
        "nombre": "Agua Mineral 500ml",
        "descripcion": "Agua mineral natural sin gas 500ml.",
        "precio_base": 2.50,
        "stock_cantidad": 250,
        "imagen_url": "https://images.unsplash.com/photo-1616118132534-381148898bb4?w=600&h=400&fit=crop",
        "categorias": ["Bebidas"],
    },
    {
        "nombre": "Limonada Natural",
        "descripcion": "Limonada recien exprimida con menta fresca y toque de jengibre.",
        "precio_base": 5.00,
        "stock_cantidad": 80,
        "imagen_url": "https://images.unsplash.com/photo-1621263764928-df1444c5e859?w=600&h=400&fit=crop",
        "categorias": ["Bebidas"],
    },
    {
        "nombre": "Tiramisu",
        "descripcion": "Postre italiano clasico con mascarpone, cafe espresso y cacao amargo.",
        "precio_base": 8.00,
        "stock_cantidad": 30,
        "imagen_url": "https://images.unsplash.com/photo-1571877227200-a0d98ea607e9?w=600&h=400&fit=crop",
        "categorias": ["Postres"],
    },
    {
        "nombre": "Ensalada Caesar",
        "descripcion": "Lechuga romana fresca, croutons caseros, queso parmesano y aderezo Caesar clasico.",
        "precio_base": 9.00,
        "stock_cantidad": 35,
        "imagen_url": "https://images.unsplash.com/photo-1546793665-c74683f339c1?w=600&h=400&fit=crop",
        "categorias": ["Ensaladas"],
    },
    {
        "nombre": "Ensalada Mediterranea",
        "descripcion": "Mix de hojas verdes, tomate cherry, aceitunas negras, queso feta y aderezo de oliva y limon.",
        "precio_base": 10.00,
        "stock_cantidad": 30,
        "imagen_url": "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=600&h=400&fit=crop",
        "categorias": ["Ensaladas"],
    },
    {
        "nombre": "Fettuccine Alfredo",
        "descripcion": "Pasta fettuccine con salsa cremosa de parmesano, manteca y ajo.",
        "precio_base": 11.50,
        "stock_cantidad": 40,
        "imagen_url": "https://images.unsplash.com/photo-1645112411341-6c4fd023714a?w=600&h=400&fit=crop",
        "categorias": ["Pastas"],
    },
    {
        "nombre": "Spaghetti Bolognese",
        "descripcion": "Spaghetti al dente con salsa bolognesa casera de carne y tomate, cocinada a fuego lento.",
        "precio_base": 12.00,
        "stock_cantidad": 45,
        "imagen_url": "https://images.unsplash.com/photo-1621996346565-e3dbc646d9a9?w=600&h=400&fit=crop",
        "categorias": ["Pastas"],
    },
]


def seed():
    db = SessionLocal()
    try:
        # 1. Create admin user if not exists
        admin_exists = db.query(User).filter(User.email == "admin@foodstore.com").first()
        admin = admin_exists
        if not admin_exists:
            admin = User(
                email="admin@foodstore.com",
                hashed_password=hash_password("Admin123"),
                full_name="Administrador",
            )
            db.add(admin)
            db.flush()
            admin_role = UserRole(user_id=admin.id, role="ADMIN")
            db.add(admin_role)
            logger.info("Usuario admin creado.")
        else:
            logger.info("Usuario admin ya existe.")
            # Ensure ADMIN role exists
            existing_role = (
                db.query(UserRole)
                .filter(UserRole.user_id == admin.id, UserRole.role == "ADMIN")
                .first()
            )
            if not existing_role:
                db.add(UserRole(user_id=admin.id, role="ADMIN"))
                logger.info("Rol ADMIN asignado al usuario existente.")

        # 2. Create categories
        categorias_creadas = {}
        for cat_data in categorias_data:
            exists = db.query(Categoria).filter(Categoria.nombre == cat_data["nombre"]).first()
            if not exists:
                categoria = Categoria(nombre=cat_data["nombre"])
                db.add(categoria)
                db.flush()
                categorias_creadas[cat_data["nombre"]] = categoria
                logger.info(f"Categoria '{cat_data['nombre']}' creada.")
            else:
                categorias_creadas[cat_data["nombre"]] = exists
                logger.info(f"Categoria '{cat_data['nombre']}' ya existe.")

        # 3. Create products and assign categories
        productos_count = 0
        for prod_data in productos_data:
            exists = db.query(Producto).filter(Producto.nombre == prod_data["nombre"]).first()
            if not exists:
                producto = Producto(
                    nombre=prod_data["nombre"],
                    descripcion=prod_data["descripcion"],
                    precio_base=prod_data["precio_base"],
                    stock_cantidad=prod_data["stock_cantidad"],
                    disponible=True,
                    imagen_url=prod_data["imagen_url"],
                )
                db.add(producto)
                db.flush()

                # Assign categories
                for cat_nombre in prod_data["categorias"]:
                    categoria = categorias_creadas.get(cat_nombre)
                    if categoria:
                        db.add(ProductoCategoria(producto_id=producto.id, categoria_id=categoria.id))

                productos_count += 1
                logger.info(f"Producto '{prod_data['nombre']}' creado.")
            else:
                logger.info(f"Producto '{prod_data['nombre']}' ya existe.")

        db.commit()
        logger.info(f"Seed completado exitosamente. {productos_count} productos creados.")
    except Exception as e:
        db.rollback()
        logger.error("Error en seed", exc_info=True)
        raise
    finally:
        db.close()


if __name__ == "__main__":
    setup_logging()
    seed()
