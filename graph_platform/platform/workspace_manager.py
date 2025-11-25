from typing import Dict, Optional, List
from .workspace import Workspace

class WorkspaceManager:
    def __init__(self):
        self.workspaces: Dict[str, Workspace] = {}
        self.active_workspace_id: Optional[str] = None

    def create_workspace(self, workspace: Workspace):
        self.workspaces[workspace.id] = workspace
        # Ako je ovo prvi workspace, postavi ga kao aktivnog
        if self.active_workspace_id is None:
            self.active_workspace_id = workspace.id
    
    def get_workspace(self, workspace_id: str) -> Optional[Workspace]:
        return self.workspaces.get(workspace_id)

    def get_active_workspace(self) -> Optional[Workspace]:
        if self.active_workspace_id:
            return self.workspaces.get(self.active_workspace_id)
        return None

    def set_active_workspace(self, workspace_id: str):
        if workspace_id in self.workspaces:
            self.active_workspace_id = workspace_id
        else:
            raise ValueError(f"Workspace {workspace_id} ne postoji.")

    def delete_workspace(self, workspace_id: str):
        if workspace_id in self.workspaces:
            del self.workspaces[workspace_id]
            if self.active_workspace_id == workspace_id:
                self.active_workspace_id = next(iter(self.workspaces)) if self.workspaces else None

    def get_all_workspaces(self) -> List[dict]:
        return [
            {
                "id": ws.id, 
                "name": ws.name, 
                "active": ws.id == self.active_workspace_id,
                "nodes": len(ws.current_graph.nodes) if ws.current_graph else 0,
                "visualizer": ws.selected_visualizer
            }
            for ws in self.workspaces.values()
        ]