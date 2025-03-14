"""
Runner module for managing the execution flow between agents.
"""

from .agent import Agent
from typing import Dict, Any


class Runner:
    """
    Manages the execution flow between agents.

    The runner starts with an initial agent and input, then handles
    any handoffs between agents, tool usage, and final output generation.
    """

    @classmethod
    def run(
        cls, starting_agent: Agent, input: str, max_iterations: int = 5
    ) -> Dict[str, Any]:
        """
        Run a conversation through agents, handling handoffs.

        Args:
            starting_agent: The agent to start with
            input: Initial user input
            max_iterations: Maximum number of agent handoffs to prevent infinite loops

        Returns:
            Dict containing the final response and execution trace
        """
        current_agent = starting_agent
        current_input = input
        iterations = 0
        execution_trace = []

        while iterations < max_iterations:
            iterations += 1

            # Process the input with the current agent
            result = current_agent.process(current_input)

            # Add to execution trace
            execution_trace.append(
                {"agent": current_agent.name, "input": current_input, "output": result}
            )

            # Check if there's a handoff
            if result["handoff"]:
                current_agent = result["handoff"]
                # Continue with the same input for the new agent
                continue

            # If tool calls were made and need follow-up, we could handle that here
            if result["tool_calls"]:
                # For now, just continue with the current agent if tools were used
                tool_results = []
                for tool_call in result["tool_calls"]:
                    tool_results.append(
                        f"Tool {tool_call['tool']} returned: {tool_call['result']}"
                    )

                if tool_results:
                    current_input = f"The following tools were used: {' '.join(tool_results)}. Please continue."
                    continue

            # No handoffs or tool follow-ups needed, we're done
            return {
                "agent": current_agent.name,
                "response": result["content"],
                "execution_trace": execution_trace,
            }

        # If we reach here, we hit the max iterations
        return {
            "agent": current_agent.name,
            "response": "Maximum number of agent iterations reached without resolution.",
            "execution_trace": execution_trace,
        }
