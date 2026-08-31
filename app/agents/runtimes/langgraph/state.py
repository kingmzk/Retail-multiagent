"""LangGraph state schema for multi-agent retail customer support workflow."""
from typing import TypedDict, List, Dict, Any, Optional, Annotated
import operator


class CustomerSupportGraphState(TypedDict):
    # Customer query input
    customer_query: str

    # Router decisions
    intents: List[str]
    entities: Dict[str, Any]

    # Specialist outputs accumulated via operator.add (fan-in reducer)
    specialist_results: Annotated[List[Dict[str, Any]], operator.add]

    # Final synthesized answer
    final_response: Dict[str, Any]
