"""
Mock CRM Tool: Simulates CRM (Salesforce-like) operations without real access.

Used in Phase 1 for testing orchestration logic without external dependencies.
In Phase 7, swap this for RealCRMTool — agents won't know the difference.
"""

from typing import Any, Dict
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class MockCRMTool:
    """Mock CRM tool that returns fixture data."""

    name = "crm"
    capability_tags = ["crm_lookup", "lead_management", "customer_update"]

    def __init__(self):
        """Initialize with fixture CRM data."""
        self.accounts = {
            123: {
                "id": 123,
                "name": "Alice Johnson",
                "email": "alice@example.com",
                "company": "TechCorp",
                "account_value": 50000,
                "last_interaction": "2024-08-10",
                "notes": "High-value customer, prefers email communication",
            },
            456: {
                "id": 456,
                "name": "Bob Smith",
                "email": "bob@example.com",
                "company": "StartupXYZ",
                "account_value": 5000,
                "last_interaction": "2024-08-05",
                "notes": "Free tier customer",
            },
        }

        self.opportunities = {
            "OPP-001": {
                "id": "OPP-001",
                "account_id": 123,
                "title": "Upgrade to Enterprise",
                "value": 100000,
                "stage": "negotiation",
                "close_date": "2024-09-30",
            },
            "OPP-002": {
                "id": "OPP-002",
                "account_id": 456,
                "title": "Free to Pro conversion",
                "value": 5000,
                "stage": "proposal",
                "close_date": "2024-08-31",
            },
        }

    async def call(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a mock CRM operation.

        Args:
            input_data: {
                "operation": "lookup_account" | "lookup_opportunity" | "update" | "list",
                "id": str|int (for lookup/update),
                "update_data": dict (for update)
            }

        Returns:
            CRM data matching the query.
        """
        operation = input_data.get("operation", "lookup_account")

        logger.info(f"MockCRMTool: {operation}")

        if operation == "lookup_account":
            account_id = input_data.get("id")
            if account_id in self.accounts:
                return {
                    "success": True,
                    "data": self.accounts[account_id],
                }
            return {
                "success": False,
                "error": f"Account {account_id} not found",
            }

        elif operation == "lookup_opportunity":
            opp_id = input_data.get("id")
            if opp_id in self.opportunities:
                return {
                    "success": True,
                    "data": self.opportunities[opp_id],
                }
            return {
                "success": False,
                "error": f"Opportunity {opp_id} not found",
            }

        elif operation == "update":
            account_id = input_data.get("id")
            update_data = input_data.get("update_data", {})

            if account_id in self.accounts:
                # Mock update: just merge the data
                self.accounts[account_id].update(update_data)
                self.accounts[account_id]["last_updated"] = datetime.now().isoformat()
                return {
                    "success": True,
                    "data": self.accounts[account_id],
                    "message": f"Account {account_id} updated successfully",
                }
            return {
                "success": False,
                "error": f"Account {account_id} not found",
            }

        elif operation == "list_accounts":
            return {
                "success": True,
                "count": len(self.accounts),
                "data": list(self.accounts.values()),
            }

        elif operation == "list_opportunities":
            account_id = input_data.get("account_id")
            if account_id:
                opps = [
                    opp for opp in self.opportunities.values()
                    if opp["account_id"] == account_id
                ]
                return {
                    "success": True,
                    "count": len(opps),
                    "data": opps,
                }
            return {
                "success": True,
                "count": len(self.opportunities),
                "data": list(self.opportunities.values()),
            }

        return {
            "success": False,
            "error": f"Unknown operation: {operation}",
        }
