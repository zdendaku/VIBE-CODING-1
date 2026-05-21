"""Demo order processing module.

Used as a target for the `code-reviewer` and `test-writer` subagents and for
the `project-insights` MCP server. Intentionally contains a couple of style
violations and a TODO marker so you can see the agents catch them.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Order:
    """Represents a single customer order."""

    order_id: int
    customer: str
    items: list[tuple[str, float, int]]  # (name, unit_price, qty)


def total(order: Order) -> float:
    """Return the total price of an order, without discounts or tax."""
    return sum(price * qty for _, price, qty in order.items)


def apply_discount(amount, percent):
    # TODO: validate percent range, currently accepts negative and >100
    return amount - amount * percent / 100


def format_receipt(order: Order) -> str:
    """Format a human-readable receipt for the order."""
    lines = [f"Receipt #{order.order_id} — {order.customer}"]
    for name, price, qty in order.items:
        lines.append(f"  {qty} x {name} @ {price:.2f} = {price * qty:.2f}")
    lines.append(f"TOTAL: {total(order):.2f}")
    return "\n".join(lines)
