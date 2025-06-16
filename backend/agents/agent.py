from abc import ABC, abstractmethod
from state import AgentState

class ServiceContainer:
    """
    Simple dependency injection container for registering and resolving shared services
    like DatabaseManager, LLMManager, configuration, etc.
    """
    _services: dict[str, object] = {}

    @classmethod
    def register(cls, key: str, instance: object) -> None:
        """Register a service instance under a unique key."""
        cls._services[key] = instance

    @classmethod
    def resolve(cls, key: str) -> object:
        """Resolve and return a previously registered service instance."""
        service = cls._services.get(key)
        if service is None:
            raise KeyError(f"Service '{key}' not found in container.")
        return service


class Agent(ABC):
    """Abstract base class for all task agents in the multi-agent system."""

    def __init__(self) -> None:
        # Attach the service container for DI
        self.container = ServiceContainer

    @abstractmethod
    def run(self, state: AgentState) -> AgentState:
        """
        Execute the agent's logic on the shared state.

        Args:
            state (AgentState): The shared state object carrying all request data and intermediate results.

        Returns:
            AgentState: The updated state after this agent's processing.
        """
        ...
