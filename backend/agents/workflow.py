"""Backward compatibility shim — agents.workflow → agents.interview_graph.

The old workflow had three sub-graphs (start/message/end). 
The new architecture uses a single unified graph with pass-through logic.
This shim provides the old interface for backward compatibility.
"""

from agents.interview_graph import interview_graph

# Single compiled graph — all agents run in sequence
# Each agent's pass-through logic handles the correct behavior for each phase
_graph = interview_graph()

# Old API: three separate graphs
# Now all point to the same full graph (pass-through logic handles routing)
start_graph = _graph
message_graph = _graph
end_graph = _graph
