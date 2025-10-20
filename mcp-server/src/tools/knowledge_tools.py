from ..services import KnowledgeBaseService

kb_service = KnowledgeBaseService()


async def search_policy(query: str) -> str:
    """Search company policy and knowledge base for relevant information."""
    try:
        return kb_service.search(query)
    except Exception as e:
        return f"Search error: {str(e)}"
