import argparse
import asyncio
from decimal import Decimal
import json
from pathlib import Path
from typing import Any

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config import ROOT_PATH
from infrastructure.db import SessionFactory
from models import Client, Order, OrderItem, Product, StockItem, Warehouse


async def get_or_create_client(
    session: AsyncSession,
    name: str,
    email: str,
) -> Client:
    result = await session.execute(select(Client).where(Client.email == email))
    client = result.scalar_one_or_none()

    if client:
        client.name = name
        await session.flush()
        return client

    client = Client(
        name=name,
        email=email,
    )

    session.add(client)
    await session.flush()

    return client


async def get_or_create_product(
    session: AsyncSession,
    name: str,
    sku: str,
    price: float,
) -> Product:
    result = await session.execute(select(Product).where(Product.sku == sku))
    product = result.scalar_one_or_none()

    if product:
        product.name = name
        product.price = Decimal(str(price))
        await session.flush()
        return product

    product = Product(
        name=name,
        sku=sku,
        price=Decimal(str(price)),
    )

    session.add(product)
    await session.flush()

    return product


async def get_or_create_warehouse(
    session: AsyncSession,
    name: str,
) -> Warehouse:
    result = await session.execute(select(Warehouse).where(Warehouse.name == name))
    warehouse = result.scalar_one_or_none()

    if warehouse:
        return warehouse

    warehouse = Warehouse(name=name)

    session.add(warehouse)
    await session.flush()

    return warehouse


async def get_or_create_stock_item(
    session: AsyncSession,
    warehouse_id: int,
    product_id: int,
    quantity: int,
) -> StockItem:
    result = await session.execute(
        select(StockItem).where(
            StockItem.warehouse_id == warehouse_id,
            StockItem.product_id == product_id,
        )
    )
    stock_item = result.scalar_one_or_none()

    if stock_item:
        stock_item.quantity = quantity

        if stock_item.reserved_quantity > stock_item.quantity:
            stock_item.reserved_quantity = stock_item.quantity

        await session.flush()
        return stock_item

    stock_item = StockItem(
        warehouse_id=warehouse_id,
        product_id=product_id,
        quantity=quantity,
        reserved_quantity=0,
    )

    session.add(stock_item)
    await session.flush()

    return stock_item


async def create_order_from_json(
    session: AsyncSession,
    client: Client,
    warehouse: Warehouse,
    items: list[dict[str, Any]],
    products_by_sku: dict[str, Product],
) -> Order:
    order_items: list[OrderItem] = []
    total_amount = Decimal("0.00")

    for item in items:
        product_sku = item["product_sku"]
        quantity = int(item["quantity"])

        product = products_by_sku.get(product_sku)

        if product is None:
            raise RuntimeError(f"Product with sku={product_sku!r} not found")

        result = await session.execute(
            select(StockItem).where(
                StockItem.warehouse_id == warehouse.id,
                StockItem.product_id == product.id,
            )
        )
        stock_item = result.scalar_one_or_none()

        if stock_item is None:
            raise RuntimeError(
                f"Product {product.sku!r} is not available in warehouse {warehouse.name!r}"
            )

        available_quantity = stock_item.quantity - stock_item.reserved_quantity

        if available_quantity < quantity:
            raise RuntimeError(
                f"Not enough stock for product {product.sku!r}. "
                f"Available: {available_quantity}, requested: {quantity}"
            )

        stock_item.reserved_quantity += quantity

        unit_price = product.price
        total_price = unit_price * quantity
        total_amount += total_price

        order_items.append(
            OrderItem(
                product_id=product.id,
                quantity=quantity,
                unit_price=unit_price,
                total_price=total_price,
            )
        )

    order = Order(
        client_id=client.id,
        total_amount=total_amount,
        items=order_items,
    )

    session.add(order)
    await session.flush()

    return order


async def seed_from_json(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Seed file not found: {path}")

    data = json.loads(path.read_text(encoding="utf-8"))

    async with SessionFactory() as session:
        async with session.begin():
            clients_by_email: dict[str, Client] = {}
            products_by_sku: dict[str, Product] = {}
            warehouses_by_name: dict[str, Warehouse] = {}

            for item in data.get("clients", []):
                client = await get_or_create_client(
                    session,
                    name=item["name"],
                    email=item["email"],
                )
                clients_by_email[client.email] = client

            for item in data.get("products", []):
                product = await get_or_create_product(
                    session,
                    name=item["name"],
                    sku=item["sku"],
                    price=item["price"],
                )
                products_by_sku[product.sku] = product

            for item in data.get("warehouses", []):
                warehouse = await get_or_create_warehouse(
                    session,
                    name=item["name"],
                )
                warehouses_by_name[warehouse.name] = warehouse

            for item in data.get("stock_items", []):
                warehouse_name = item["warehouse_name"]
                product_sku = item["product_sku"]

                warehouse = warehouses_by_name.get(warehouse_name)
                product = products_by_sku.get(product_sku)

                if warehouse is None:
                    raise RuntimeError(f"Warehouse {warehouse_name!r} not found")

                if product is None:
                    raise RuntimeError(f"Product {product_sku!r} not found")

                await get_or_create_stock_item(
                    session,
                    warehouse_id=warehouse.id,
                    product_id=product.id,
                    quantity=int(item["quantity"]),
                )

            created_orders = 0

            for item in data.get("orders", []):
                client_email = item["client_email"]
                warehouse_name = item["warehouse_name"]

                client = clients_by_email.get(client_email)
                warehouse = warehouses_by_name.get(warehouse_name)

                if client is None:
                    raise RuntimeError(f"Client {client_email!r} not found")

                if warehouse is None:
                    raise RuntimeError(f"Warehouse {warehouse_name!r} not found")

                await create_order_from_json(
                    session,
                    client=client,
                    warehouse=warehouse,
                    items=item["items"],
                    products_by_sku=products_by_sku,
                )

                created_orders += 1

        logger.info("Seed completed successfully.")
        logger.info(f"Clients: {len(clients_by_email)}")
        logger.info(f"Products: {len(products_by_sku)}")
        logger.info(f"Warehouses: {len(warehouses_by_name)}")
        logger.info(f"Orders: {created_orders}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Seed database from JSON file")

    parser.add_argument(
        "--file",
        default=ROOT_PATH / "data/seed.json",
        help="Path to seed JSON file",
    )

    return parser.parse_args()


async def main() -> None:
    args = parse_args()
    await seed_from_json(Path(args.file))


if __name__ == "__main__":
    asyncio.run(main())
