import logging
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
    "description": "ALWAYS use this tool first to search the knowledge base before answering any question. " + \
                   "The knowledge base is the ONLY source of information you can use to answer questions. " + \
                   "The knowledge base is in English, translate to and from English if needed. " + \
                   "Results are formatted as a source name first in square brackets, followed by the text " + \
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
    "description": "ALWAYS use this tool to report sources used from the knowledge base. This tool must be called after " + \
                   "using the search tool and before providing an answer. Sources appear in square brackets before each " + \
                   "knowledge base passage. Only respond with information that can be cited from these sources. " + \
                   "If no relevant sources were found, inform the user that the information is not in your database.",
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
    args: Any) -> ToolResult:
    logger = logging.getLogger("voicerag")
    
    # Validate args contains query
    if not args or 'query' not in args or not args['query']:
        logger.error(f"Invalid search arguments: {args}")
        return ToolResult("No valid search query provided. Please try again.", ToolResultDirection.TO_SERVER)
    
    query = args['query']
    logger.info(f"Searching for '{query}' in the knowledge base.")
    
    try:
        # Hybrid query using Azure AI Search with (optional) Semantic Ranker
        vector_queries = []
        if use_vector_query:
            vector_queries.append(VectorizableTextQuery(text=query, k_nearest_neighbors=50, fields=embedding_field))
        
        search_results = await search_client.search(
            search_text=query, 
            query_type="semantic" if semantic_configuration else "simple",
            semantic_configuration_name=semantic_configuration,
            top=5,
            vector_queries=vector_queries,
            select=", ".join([identifier_field, content_field])
        )
        
        result = ""
        result_count = 0
        async for r in search_results:
            result += f"[{r[identifier_field]}]: {r[content_field]}\n-----\n"
            result_count += 1
        
        if result_count == 0:
            logger.info(f"No results found for query: {query}")
            result = "No information found in the knowledge base for this query."
        else:
            logger.info(f"Found {result_count} results for query: {query}")
            
        return ToolResult(result, ToolResultDirection.TO_SERVER)
    except Exception as e:
        logger.error(f"Error in search tool: {e}")
        return ToolResult("An error occurred while searching. Please try a different query.", ToolResultDirection.TO_SERVER)

KEY_PATTERN = re.compile(r'^[a-zA-Z0-9_=\-]+$')

# TODO: move from sending all chunks used for grounding eagerly to only sending links to 
# the original content in storage, it'll be more efficient overall
async def _report_grounding_tool(search_client: SearchClient, identifier_field: str, title_field: str, content_field: str, args: Any) -> ToolResult:
    logger = logging.getLogger("voicerag")
    
    # Validate args contains sources
    if not args or 'sources' not in args or not isinstance(args['sources'], list) or not args['sources']:
        logger.error(f"Invalid grounding arguments: {args}")
        return ToolResult({"sources": []}, ToolResultDirection.TO_CLIENT)
    
    try:
        sources = [s for s in args["sources"] if KEY_PATTERN.match(s)]
        if not sources:
            logger.warning("No valid source IDs found in grounding request")
            return ToolResult({"sources": []}, ToolResultDirection.TO_CLIENT)
        
        list_query = " OR ".join(sources)
        logger.info(f"Grounding sources: {list_query}")
        
        # Use search instead of filter to align with how detailt integrated vectorization indexes
        # are generated, where chunk_id is searchable with a keyword tokenizer, not filterable 
        search_results = await search_client.search(
            search_text=list_query, 
            search_fields=[identifier_field], 
            select=[identifier_field, title_field, content_field], 
            top=len(sources), 
            query_type="full"
        )
        
        # If your index has a key field that's filterable but not searchable and with the keyword analyzer, you can 
        # use a filter instead (and you can remove the regex check above, just ensure you escape single quotes)
        # search_results = await search_client.search(filter=f"search.in(chunk_id, '{list}')", select=["chunk_id", "title", "chunk"])

        docs = []
        async for r in search_results:
            docs.append({"chunk_id": r[identifier_field], "title": r[title_field], "chunk": r[content_field]})
        
        logger.info(f"Found {len(docs)} documents for grounding")
        return ToolResult({"sources": docs}, ToolResultDirection.TO_CLIENT)
    except Exception as e:
        logger.error(f"Error in report_grounding tool: {e}")
        return ToolResult({"sources": [], "error": str(e)}, ToolResultDirection.TO_CLIENT)

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

    rtmt.tools["search"] = Tool(schema=_search_tool_schema, target=lambda args: _search_tool(search_client, semantic_configuration, identifier_field, content_field, embedding_field, use_vector_query, args))
    rtmt.tools["report_grounding"] = Tool(schema=_grounding_tool_schema, target=lambda args: _report_grounding_tool(search_client, identifier_field, title_field, content_field, args))
