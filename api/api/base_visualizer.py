from abc import ABC, abstractmethod

class BaseVisualizer(ABC):
    """
    Abstract base class for all graph visualizers.
    Defines the common interface and validation logic.
    """

    @abstractmethod
    def render(self, graph):
        """
        Render the provided graph.

        Parameters:
            graph: Graph object (format depends on concrete implementation)

        Returns:
            Any: output visualization (string, image, HTML, etc.)
        """
        pass

    def check_graph_compatibility(self, graph):
        """
        Checks whether the graph is compatible with this visualizer.

        Subclasses may override this to support:
        - Directed / undirected graphs
        - Weighted / unweighted edges
        - Required graph metadata

        Default behavior: only checks that graph is not None.

        Raises:
            ValueError if graph is not valid for this visualizer.
        """
        if graph is None:
            raise ValueError("Graph cannot be None.")