"""Clearance analysis utilities for terminal spacing."""

from typing import Dict, Any, List, Tuple, Optional
import math
from .parts import PartsAPI


class ClearanceAnalyzer:
    """Analyzer for calculating clearances between terminals."""
    
    def __init__(self, parts_api: PartsAPI):
        self.parts_api = parts_api
    
    def calculate_distance(
        self,
        bbox1: Dict[str, Any],
        bbox2: Dict[str, Any]
    ) -> float:
        """
        Calculate minimum distance between two bounding boxes.
        NOTE: This is approximate. Use get_minimum_distance() for accurate measurements.
        
        Args:
            bbox1: First bounding box with minCorner and maxCorner
            bbox2: Second bounding box with minCorner and maxCorner
            
        Returns:
            Minimum distance in meters
        """
        # Extract corner coordinates
        min1 = bbox1.get("minCorner", [0, 0, 0])
        max1 = bbox1.get("maxCorner", [0, 0, 0])
        min2 = bbox2.get("minCorner", [0, 0, 0])
        max2 = bbox2.get("maxCorner", [0, 0, 0])
        
        # Calculate minimum distance between boxes
        # For axis-aligned bounding boxes
        dx = max(0, max(min1[0] - max2[0], min2[0] - max1[0]))
        dy = max(0, max(min1[1] - max2[1], min2[1] - max1[1]))
        dz = max(0, max(min1[2] - max2[2], min2[2] - max1[2]))
        
        distance = math.sqrt(dx*dx + dy*dy + dz*dz)
        return distance
    
    async def get_minimum_distance(
        self,
        document_id: str,
        workspace_id: str,
        element_id: str,
        part_id1: str,
        part_id2: str
    ) -> Optional[float]:
        """
        Get accurate minimum distance between two parts using OnShape measure API.
        
        Args:
            document_id: OnShape document ID
            workspace_id: Workspace ID
            element_id: Element (Part Studio) ID
            part_id1: First part ID
            part_id2: Second part ID
            
        Returns:
            Minimum distance in meters, or None if calculation failed
        """
        result = await self.parts_api.get_minimum_distance(
            document_id, workspace_id, element_id, part_id1, part_id2
        )
        
        if result.get("status") == "success":
            return result.get("distance")
        else:
            return None
    
    async def analyze_terminal_clearances(
        self,
        document_id: str,
        workspace_id: str,
        element_id: str,
        terminals: List[Dict[str, str]],
        required_clearance: float = 0.0,
        use_measure_api: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Analyze clearances between multiple terminals.
        
        Args:
            document_id: OnShape document ID
            workspace_id: Workspace ID
            element_id: Element (Part Studio) ID
            terminals: List of terminal dicts with 'part_id' and optional 'name'
            required_clearance: Required clearance in meters (default: 0.0)
            use_measure_api: If True, use accurate measure API (default: True)
            
        Returns:
            List of clearance analysis results
        """
        results = []
        
        if use_measure_api:
            # Use accurate measure API for distance calculations
            terminal_list = list(terminals)
            for i, terminal1 in enumerate(terminal_list):
                for terminal2 in terminal_list[i+1:]:
                    part_id1 = terminal1["part_id"]
                    part_id2 = terminal2["part_id"]
                    
                    try:
                        distance = await self.get_minimum_distance(
                            document_id, workspace_id, element_id, part_id1, part_id2
                        )
                        
                        if distance is not None:
                            meets_requirement = distance >= required_clearance
                            results.append({
                                "terminal1": terminal1.get("name", part_id1),
                                "terminal2": terminal2.get("name", part_id2),
                                "part_id1": part_id1,
                                "part_id2": part_id2,
                                "distance": distance,
                                "required_clearance": required_clearance,
                                "meets_requirement": meets_requirement,
                                "status": "pass" if meets_requirement else "fail"
                            })
                        else:
                            results.append({
                                "terminal1": terminal1.get("name", part_id1),
                                "terminal2": terminal2.get("name", part_id2),
                                "part_id1": part_id1,
                                "part_id2": part_id2,
                                "distance": None,
                                "status": "error",
                                "error": "Could not calculate distance"
                            })
                    except Exception as e:
                        results.append({
                            "terminal1": terminal1.get("name", part_id1),
                            "terminal2": terminal2.get("name", part_id2),
                            "part_id1": part_id1,
                            "part_id2": part_id2,
                            "distance": None,
                            "status": "error",
                            "error": str(e)
                        })
        else:
            # Fallback to bounding box method (less accurate)
            terminal_bboxes = {}
            for terminal in terminals:
                part_id = terminal["part_id"]
                try:
                    bbox = await self.parts_api.get_part_bounding_box(
                        document_id, workspace_id, element_id, part_id
                    )
                    terminal_bboxes[part_id] = {
                        "bbox": bbox,
                        "name": terminal.get("name", part_id)
                    }
                except Exception as e:
                    results.append({
                        "terminal1": terminal.get("name", part_id),
                        "terminal2": None,
                        "distance": None,
                        "status": "error",
                        "error": str(e)
                    })
                    continue
            
            # Calculate distances between all pairs
            terminal_list = list(terminal_bboxes.items())
            for i, (part_id1, data1) in enumerate(terminal_list):
                for j, (part_id2, data2) in enumerate(terminal_list[i+1:], start=i+1):
                    distance = self.calculate_distance(data1["bbox"], data2["bbox"])
                    meets_requirement = distance >= required_clearance
                    
                    results.append({
                        "terminal1": data1["name"],
                        "terminal2": data2["name"],
                        "part_id1": part_id1,
                        "part_id2": part_id2,
                        "distance": distance,
                        "required_clearance": required_clearance,
                        "meets_requirement": meets_requirement,
                        "status": "pass" if meets_requirement else "fail"
                    })
        
        return results
