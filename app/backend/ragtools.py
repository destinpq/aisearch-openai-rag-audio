import re
from typing import Any

from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential
from azure.search.documents.aio import SearchClient
from azure.search.documents.models import VectorizableTextQuery

from rtmt import RTMiddleTier, Tool, ToolResult, ToolResultDirection

_search_tool_schema = {
    "type": "function",
    "name": "search",
    "description": "Search the knowledge base. The knowledge base is in English, translate to and from English if " + \
                   "needed. Results are formatted as a source name first in square brackets, followed by the text " + \
                   "content, and a line with '-----' at the end of each result.",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search query"
            }
        },
        "required": ["query"],
        "additionalProperties": False
    }
}

_grounding_tool_schema = {
    "type": "function",
    "name": "report_grounding",
    "description": "Report use of a source from the knowledge base as part of an answer (effectively, cite the source). Sources " + \
                   "appear in square brackets before each knowledge base passage. Always use this tool to cite sources when responding " + \
                   "with information from the knowledge base.",
    "parameters": {
        "type": "object",
        "properties": {
            "sources": {
                "type": "array",
                "items": {
                    "type": "string"
                },
                "description": "List of source names from last statement actually used, do not include the ones not used to formulate a response"
            }
        },
        "required": ["sources"],
        "additionalProperties": False
    }
}

async def _search_tool(
    search_client: SearchClient, 
    semantic_configuration: str | None,
    identifier_field: str,
    content_field: str,
    embedding_field: str,
    use_vector_query: bool,
    args: Any,
    context: Any = None) -> ToolResult:
    
    # Check if args is valid and has required query field
    if not args or 'query' not in args:
        return ToolResult("Error: No search query provided", False)
    
    print(f"Searching for '{args['query']}' in the knowledge base.")
    
    # Get search mode and user_id from context (websocket object)
    search_mode = getattr(context, 'search_mode', 'unguarded') if context else 'unguarded'
    user_id = getattr(context, 'user_id', None) if context else None
    print(f"Search mode: {search_mode}, user_id: {user_id}")
    
    # Build filter for user and folder scope based on search mode
    filter_conditions = []
    
    # If guarded mode, only search user's documents
    if search_mode == "guarded":
        if user_id:
            filter_conditions.append(f"user_id eq '{user_id}'")
        else:
            # If no user_id in guarded mode, return empty results
            return ToolResult("No user documents found", ToolResultDirection.TO_SERVER)
    
    # Add folder filters if specified
    if folder_ids:
        folder_filters = " or ".join([f"folder_id eq '{folder_id}'" for folder_id in folder_ids])
        filter_conditions.append(f"({folder_filters})")
    
    search_filter = " and ".join(filter_conditions) if filter_conditions else None

KEY_PATTERN = re.compile(r'^[a-zA-Z0-9_=\-]+$')

# TODO: move from sending all chunks used for grounding eagerly to only sending links to 
# the original content in storage, it'll be more efficient overall
async def _report_grounding_tool(search_client: SearchClient, identifier_field: str, title_field: str, content_field: str, args: Any, context: Any = None) -> ToolResult:
    try:
        sources = [s for s in args["sources"] if KEY_PATTERN.match(s)]
        list = " OR ".join(sources)
        print(f"Grounding source: {list}")
        # Use search instead of filter to align with how detailt integrated vectorization indexes
        # are generated, where chunk_id is searchable with a keyword tokenizer, not filterable 
        search_results = await search_client.search(search_text=list, 
                                                    search_fields=[identifier_field], 
                                                    select=[identifier_field, title_field, content_field], 
                                                    top=len(sources), 
                                                    query_type="full")
        
        # If your index has a key field that's filterable but not searchable and with the keyword analyzer, you can 
        # use a filter instead (and you can remove the regex check above, just ensure you escape single quotes)
        # search_results = await search_client.search(filter=f"search.in(chunk_id, '{list}')", select=["chunk_id", "title", "chunk"])

        docs = []
        async for r in search_results:
            docs.append({"chunk_id": r[identifier_field], "title": r[title_field], "chunk": r[content_field]})
        
        # Get search mode from context
        search_mode = getattr(context, 'search_mode', 'unguarded') if context else 'unguarded'
        print(f"Report grounding tool - search mode: {search_mode}, docs found: {len(docs)}")
        
        return ToolResult({"sources": docs, "search_mode": search_mode}, ToolResultDirection.TO_CLIENT)
    except Exception as e:
        print(f"Error in _report_grounding_tool: {e}")
        return ToolResult({"sources": [], "search_mode": "unguarded"}, ToolResultDirection.TO_CLIENT)

def attach_rag_tools(rtmt: RTMiddleTier,
    credentials: AzureKeyCredential | DefaultAzureCredential,
    search_endpoint: str, search_index: str,
    semantic_configuration: str | None,
    identifier_field: str,
    content_field: str,
    embedding_field: str,
    title_field: str,
    use_vector_query: bool
    ) -> None:
    if not isinstance(credentials, AzureKeyCredential):
        credentials.get_token("https://search.azure.com/.default") # warm this up before we start getting requests
    search_client = SearchClient(search_endpoint, search_index, credentials, user_agent="RTMiddleTier")

    rtmt.tools["search"] = Tool(schema=_search_tool_schema, target=lambda args, context=None: _search_tool(search_client, semantic_configuration, identifier_field, content_field, embedding_field, use_vector_query, args, context))
    rtmt.tools["report_grounding"] = Tool(schema=_grounding_tool_schema, target=lambda args, context=None: _report_grounding_tool(search_client, identifier_field, title_field, content_field, args, context))
