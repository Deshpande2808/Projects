"""
Mock Database Tool: Simulates database queries without hitting real Postgres.

Used in Phase 1 for testing orchestration logic without external dependencies.
In Phase 7, swap this for RealDatabaseTool — agents won't know the difference.
"""

from typing import Any, Dict, List
import logging

logger = logging.getLogger(__name__)


class MockDatabaseTool:
    """Mock database tool that returns fixture data."""

    name = "database"
    capability_tags = ["database_query", "customer_lookup", "data_retrieval"]

    def __init__(self):
        """Initialize with fixture data."""
        self.customers = {
            123: {
                "id": 123,
                "name": "Alice Johnson",
                "email": "alice@example.com",
                "status": "active",
                "plan": "pro",
                "joined": "2023-01-15",
            },
            456: {
                "id": 456,
                "name": "Bob Smith",
                "email": "bob@example.com",
                "status": "active",
                "plan": "free",
                "joined": "2023-06-20",
            },
            789: {
                "id": 789,
                "name": "Charlie Brown",
                "email": "charlie@example.com",
                "status": "inactive",
                "plan": "free",
                "joined": "2022-03-10",
            },
        }

        self.invoices = {
            "INV-001": {"id": "INV-001", "customer_id": 123, "amount": 99.99, "status": "paid"},
            "INV-002": {"id": "INV-002", "customer_id": 123, "amount": 99.99, "status": "unpaid"},
            "INV-003": {"id": "INV-003", "customer_id": 456, "amount": 0.00, "status": "free"},
        }

    async def call(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a mock database query.

        Args:
            input_data: {
                "operation": "query" | "lookup" | "list",
                "resource": "customer" | "invoice" | "order",
                "id": int (for lookup),
                "filters": dict (optional)
            }

        Returns:
            Fixture data matching the query.
        """
        operation = input_data.get("operation", "lookup")
        resource = input_data.get("resource", "customer")

        logger.info(f"MockDatabaseTool: {operation} {resource}")

        if operation == "lookup":
            if resource == "customer":
                customer_id = input_data.get("id")
                if customer_id in self.customers:
                    return {
                        "success": True,
                        "data": self.customers[customer_id],
                    }
                return {
                    "success": False,
                    "error": f"Customer {customer_id} not found",
                }

            elif resource == "invoice":
                invoice_id = input_data.get("id")
                if invoice_id in self.invoices:
                    return {
                        "success": True,
                        "data": self.invoices[invoice_id],
                    }
                return {
                    "success": False,
                    "error": f"Invoice {invoice_id} not found",
                }

        elif operation == "list":
            if resource == "customer":
                return {
                    "success": True,
                    "data": list(self.customers.values()),
                }
            elif resource == "invoice":
                customer_id = input_data.get("customer_id")
                if customer_id:
                    invoices = [
                        inv for inv in self.invoices.values()
                        if inv["customer_id"] == customer_id
                    ]
                    return {"success": True, "data": invoices}
                return {"success": True, "data": list(self.invoices.values())}

        elif operation == "query":
            # Simulate a generic SQL-like query
            filters = input_data.get("filters", {})
            if resource == "customer":
                results = [c for c in self.customers.values()]
                # Apply filters
                for key, value in filters.items():
                    results = [r for r in results if r.get(key) == value]
                return {"success": True, "data": results}

        return {
            "success": False,
            "error": f"Unknown operation or resource: {operation} {resource}",
        }
