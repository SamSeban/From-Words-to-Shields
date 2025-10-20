"""Base API for privacy protection tools."""

from abc import ABC, abstractmethod
from typing import Dict, Any


class PrivacyTool(ABC):
    """Base class for all privacy protection tools."""
    
    name: str = None
    
    @abstractmethod
    def apply(self, **kwargs) -> Dict[str, Any]:
        """
        Apply the privacy protection operation.
        
        Returns:
            Dict containing the results of the operation (e.g., {"video_path": "..."})
        """
        pass
    
    @abstractmethod 
    def verify(self, **kwargs) -> Dict[str, bool]:
        """
        Verify that the privacy protection was applied correctly.
        
        Returns:
            Dict with verification results (e.g., {"ok": True})
        """
        pass
    
    def __repr__(self):
        return f"<{self.__class__.__name__}(name='{self.name}')>"
