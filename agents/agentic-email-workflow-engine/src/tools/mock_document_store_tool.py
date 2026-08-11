"""
Mock Document Store Tool: Simulates SharePoint/document storage without real access.

Used in Phase 1 for testing orchestration logic without external dependencies.
In Phase 7, swap this for RealDocumentStoreTool — agents won't know the difference.
"""

from typing import Any, Dict, List
import logging

logger = logging.getLogger(__name__)


class MockDocumentStoreTool:
    """Mock document store tool that returns fixture data."""

    name = "document_store"
    capability_tags = ["document_search", "document_retrieval", "knowledge_base"]

    def __init__(self):
        """Initialize with fixture documents."""
        self.documents = {
            "KB-001": {
                "id": "KB-001",
                "title": "Password Reset Guide",
                "category": "account",
                "content": "To reset your password: 1. Click 'Forgot Password' on login page...",
            },
            "KB-002": {
                "id": "KB-002",
                "title": "Account Locked Troubleshooting",
                "category": "account",
                "content": "Your account may be locked after 5 failed login attempts...",
            },
            "KB-003": {
                "id": "KB-003",
                "title": "Billing & Payments FAQ",
                "category": "billing",
                "content": "We accept all major credit cards. Billing cycle starts on...",
            },
            "KB-004": {
                "id": "KB-004",
                "title": "Pro Plan Features",
                "category": "pricing",
                "content": "Pro plan includes: unlimited storage, advanced analytics, priority support...",
            },
            "KB-005": {
                "id": "KB-005",
                "title": "API Documentation",
                "category": "developer",
                "content": "Base URL: https://api.example.com/v1. Authentication: Bearer token...",
            },
        }

    async def call(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a mock document store query.

        Args:
            input_data: {
                "operation": "search" | "retrieve",
                "query": str (for search),
                "doc_id": str (for retrieve),
                "category": str (optional filter)
            }

        Returns:
            Fixture documents matching the query.
        """
        operation = input_data.get("operation", "search")

        logger.info(f"MockDocumentStoreTool: {operation}")

        if operation == "search":
            query = input_data.get("query", "").lower()
            category = input_data.get("category")

            # Simple keyword matching
            results = []
            for doc_id, doc in self.documents.items():
                matches = (
                    query in doc["title"].lower()
                    or query in doc["content"].lower()
                )
                if matches and (category is None or doc["category"] == category):
                    results.append(doc)

            return {
                "success": True,
                "count": len(results),
                "data": results,
            }

        elif operation == "retrieve":
            doc_id = input_data.get("doc_id")
            if doc_id in self.documents:
                return {
                    "success": True,
                    "data": self.documents[doc_id],
                }
            return {
                "success": False,
                "error": f"Document {doc_id} not found",
            }

        elif operation == "list":
            category = input_data.get("category")
            docs = [
                doc for doc in self.documents.values()
                if category is None or doc["category"] == category
            ]
            return {
                "success": True,
                "count": len(docs),
                "data": docs,
            }

        return {
            "success": False,
            "error": f"Unknown operation: {operation}",
        }
