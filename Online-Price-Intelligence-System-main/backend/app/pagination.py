"""
Pagination Utilities for API Endpoints

Provides:
- Pagination helpers
- Total count queries
- Cursor-based pagination for large datasets
- Standard pagination format (limit, offset)
"""

from typing import Any, Dict, List, Optional, TypeVar, Generic
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T')


class PaginationParams(BaseModel):
    """Standard pagination parameters"""
    limit: int = 10  # items per page
    offset: int = 0  # page offset
    
    class Config:
        schema_extra = {
            "example": {
                "limit": 20,
                "offset": 0
            }
        }


class PaginationResult(BaseModel, Generic[T]):
    """Standard pagination response format"""
    data: List[T]
    pagination: Dict[str, Any]
    total: int
    limit: int
    offset: int
    
    @property
    def has_more(self) -> bool:
        """Check if there are more results"""
        return (self.offset + self.limit) < self.total


class Paginator:
    """Helper class for pagination operations"""
    
    @staticmethod
    def paginate(
        items: List[Any],
        limit: int = 10,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Paginate a list of items
        
        Args:
            items: List to paginate
            limit: Items per page
            offset: Current offset
            
        Returns:
            Paginated result with metadata
        """
        total = len(items)
        paginated = items[offset : offset + limit]
        
        return {
            "data": paginated,
            "pagination": {
                "total": total,
                "limit": limit,
                "offset": offset,
                "has_more": (offset + limit) < total,
                "pages": (total + limit - 1) // limit,
                "current_page": (offset // limit) + 1 if limit > 0 else 1
            }
        }
    
    @staticmethod
    def paginate_with_metadata(
        items: List[Any],
        total: int,
        limit: int = 10,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Paginate items with separate total count (useful for DB queries)
        
        Args:
            items: Items to return for current page
            total: Total count of all items
            limit: Items per page
            offset: Current offset
            
        Returns:
            Paginated result with metadata
        """
        return {
            "data": items,
            "pagination": {
                "total": total,
                "limit": limit,
                "offset": offset,
                "has_more": (offset + limit) < total,
                "pages": (total + limit - 1) // limit,
                "current_page": (offset // limit) + 1 if limit > 0 else 1
            }
        }
    
    @staticmethod
    def get_offset_limit(page: int = 1, per_page: int = 10) -> tuple:
        """
        Convert page number to offset/limit
        
        Args:
            page: Page number (1-indexed)
            per_page: Items per page
            
        Returns:
            (limit, offset) tuple
        """
        if page < 1:
            page = 1
        offset = (page - 1) * per_page
        return per_page, offset
    
    @staticmethod
    def build_pagination_sql(limit: int = 10, offset: int = 0) -> str:
        """
        Build pagination SQL clause
        
        Args:
            limit: Items per page (max 100)
            offset: Page offset
            
        Returns:
            SQL LIMIT clause
        """
        # Cap limit at 100 to prevent excessive load
        limit = min(limit, 100)
        offset = max(offset, 0)
        return f"LIMIT {limit} OFFSET {offset}"


class CursorPagination:
    """
    Cursor-based pagination for better performance on large datasets
    
    Advantages over offset/limit:
    - Faster for large offsets
    - Handles insertions better
    - Better for real-time data
    """
    
    @staticmethod
    def encode_cursor(id_value: Any, timestamp: Any) -> str:
        """Create a cursor token from ID and timestamp"""
        import base64
        cursor_data = f"{id_value}:{timestamp}".encode()
        return base64.b64encode(cursor_data).decode()
    
    @staticmethod
    def decode_cursor(cursor: str) -> tuple:
        """Decode cursor token"""
        try:
            import base64
            cursor_data = base64.b64decode(cursor).decode()
            id_val, timestamp = cursor_data.split(':')
            return id_val, timestamp
        except Exception as e:
            logger.error(f"Error decoding cursor: {e}")
            return None, None
    
    @staticmethod
    def build_cursor_sql(
        id_value: Any,
        direction: str = "next"
    ) -> str:
        """
        Build SQL WHERE clause for cursor pagination
        
        Args:
            id_value: Current cursor ID
            direction: "next" or "prev"
            
        Returns:
            SQL WHERE clause
        """
        operator = ">" if direction == "next" else "<"
        return f"WHERE id {operator} {id_value}"


# Pagination examples for common queries

PAGINATION_EXAMPLES = {
    "wishlist": {
        "description": "Paginate wishlist items",
        "query": """
            SELECT id, product_name, price, store
            FROM wishlist
            WHERE user_id = $1
            ORDER BY created_at DESC
            LIMIT $2 OFFSET $3
        """,
        "default_limit": 20,
        "max_limit": 100
    },
    "price_alerts": {
        "description": "Paginate price alerts",
        "query": """
            SELECT id, product_name, target_price, created_at
            FROM price_alerts
            WHERE user_id = $1
            ORDER BY created_at DESC
            LIMIT $2 OFFSET $3
        """,
        "default_limit": 10,
        "max_limit": 50
    },
    "search_history": {
        "description": "Paginate search history",
        "query": """
            SELECT search_query, search_time
            FROM search_history
            WHERE user_id = $1
            ORDER BY search_time DESC
            LIMIT $2 OFFSET $3
        """,
        "default_limit": 30,
        "max_limit": 100
    },
    "price_history": {
        "description": "Paginate price history",
        "query": """
            SELECT price, recorded_at
            FROM price_history
            WHERE product_id = $1
            AND recorded_at > CURRENT_TIMESTAMP - INTERVAL '90 days'
            ORDER BY recorded_at DESC
            LIMIT $2 OFFSET $3
        """,
        "default_limit": 100,
        "max_limit": 500
    },
    "comparison_results": {
        "description": "Paginate comparison products",
        "note": "Handled by Redis/caching layer",
        "default_limit": 10,
        "max_limit": 50
    }
}


def create_pagination_response(
    data: List[Any],
    total: int,
    limit: int,
    offset: int
) -> Dict[str, Any]:
    """
    Create standard pagination response
    
    Args:
        data: Results for current page
        total: Total number of items
        limit: Items per page
        offset: Current offset
        
    Returns:
        Formatted response with pagination metadata
    """
    return {
        "data": data,
        "pagination": {
            "total": total,
            "count": len(data),
            "limit": limit,
            "offset": offset,
            "pages": (total + limit - 1) // limit if limit > 0 else 0,
            "current_page": (offset // limit) + 1 if limit > 0 else 1,
            "has_next": (offset + limit) < total,
            "has_previous": offset > 0
        }
    }
