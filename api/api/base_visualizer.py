class BaseVisualizer:
    def render(self, graph):
        raise NotImplementedError("Visualizer must implement render()")