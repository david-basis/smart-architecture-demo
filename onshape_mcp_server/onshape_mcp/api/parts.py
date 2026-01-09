"""OnShape Parts API for terminal and part queries."""

import asyncio
from typing import Dict, Any, Optional, List
from .client import OnShapeClient


class PartsAPI:
    """API for querying OnShape parts and terminals."""
    
    def __init__(self, client: OnShapeClient):
        self.client = client
    
    async def get_part(
        self,
        document_id: str,
        workspace_id: str,
        element_id: str,
        part_id: str
    ) -> Dict[str, Any]:
        """
        Get part information by ID.
        
        For STEP-imported documents, this may need to use partQuery instead of partId.
        First tries the standard partId endpoint, then falls back to querying all parts
        and finding the matching part.
        
        Args:
            document_id: OnShape document ID
            workspace_id: Workspace ID
            element_id: Element (Part Studio) ID
            part_id: Part ID
            
        Returns:
            Part information dictionary
        """
        # Try standard endpoint first
        try:
            endpoint = f"/parts/d/{document_id}/w/{workspace_id}/e/{element_id}/partid/{part_id}"
            return await self.client.get(endpoint)
        except Exception:
            # For STEP-imported documents, partId endpoint may not work
            # Fall back to getting all parts and finding the matching one
            all_parts = await self.get_all_parts(document_id, workspace_id, element_id)
            for part in all_parts:
                if (part.get("partId") == part_id or 
                    part.get("id") == part_id):
                    return part
            # If not found, raise an error
            raise ValueError(f"Part {part_id} not found in element {element_id}")
    
    async def get_part_mass_properties(
        self,
        document_id: str,
        workspace_id: str,
        element_id: str,
        part_id: str
    ) -> Dict[str, Any]:
        """
        Get mass properties of a part (includes bounding box for clearance).
        
        Args:
            document_id: OnShape document ID
            workspace_id: Workspace ID
            element_id: Element (Part Studio) ID
            part_id: Part ID
            
        Returns:
            Mass properties including bounding box
        """
        endpoint = f"/parts/d/{document_id}/w/{workspace_id}/e/{element_id}/partid/{part_id}/massproperties"
        return await self.client.get(endpoint)
    
    async def get_part_bounding_box(
        self,
        document_id: str,
        workspace_id: str,
        element_id: str,
        part_id: str
    ) -> Dict[str, Any]:
        """
        Get bounding box of a part for clearance analysis.
        
        Args:
            document_id: OnShape document ID
            workspace_id: Workspace ID
            element_id: Element (Part Studio) ID
            part_id: Part ID
            
        Returns:
            Bounding box information with minCorner and maxCorner
        """
        # Try to get bounding box from tessellation endpoint
        try:
            endpoint = f"/parts/d/{document_id}/w/{workspace_id}/e/{element_id}/partid/{part_id}/boundingboxes"
            response = await self.client.get(endpoint)
            if response and len(response) > 0:
                return response[0]  # Return first bounding box
        except:
            pass
        
        # Fallback: Calculate from mass properties centroid and approximate size
        try:
            mass_props = await self.get_part_mass_properties(
                document_id, workspace_id, element_id, part_id
            )
            body_data = mass_props.get("bodies", {}).get(part_id, {})
            
            # Check if boundingBox exists
            if "boundingBox" in body_data:
                return body_data["boundingBox"]
            
            # Calculate approximate bounding box from volume
            # This is a fallback - not as accurate but better than nothing
            volume = body_data.get("volume", [0])[0] if body_data.get("volume") else 0
            centroid = body_data.get("centroid", [0, 0, 0])[:3] if body_data.get("centroid") else [0, 0, 0]
            
            # Approximate size from volume (cube root)
            if volume > 0:
                size = (volume ** (1/3)) * 1.5  # Add some margin
                return {
                    "minCorner": [
                        centroid[0] - size/2,
                        centroid[1] - size/2,
                        centroid[2] - size/2
                    ],
                    "maxCorner": [
                        centroid[0] + size/2,
                        centroid[1] + size/2,
                        centroid[2] + size/2
                    ]
                }
        except:
            pass
        
        return {}
    
    async def get_all_parts(
        self,
        document_id: str,
        workspace_id: str,
        element_id: str
    ) -> List[Dict[str, Any]]:
        """
        Get all parts from a Part Studio.
        
        Args:
            document_id: OnShape document ID
            workspace_id: Workspace ID
            element_id: Element (Part Studio) ID
            
        Returns:
            List of part information dictionaries
        """
        endpoint = f"/parts/d/{document_id}/w/{workspace_id}/e/{element_id}"
        response = await self.client.get(endpoint)
        
        # Handle different response formats
        if isinstance(response, list):
            return response
        elif isinstance(response, dict):
            return response.get("parts", [])
        else:
            return []
    
    async def verify_part_exists(
        self,
        document_id: str,
        workspace_id: str,
        element_id: str,
        part_id: str
    ) -> bool:
        """
        Verify that a part exists in OnShape.
        
        Args:
            document_id: OnShape document ID
            workspace_id: Workspace ID
            element_id: Element (Part Studio) ID
            part_id: Part ID to verify
            
        Returns:
            True if part exists, False otherwise
        """
        try:
            await self.get_part(document_id, workspace_id, element_id, part_id)
            return True
        except Exception:
            return False
    
    async def get_part_feature(
        self,
        document_id: str,
        workspace_id: str,
        element_id: str,
        part_id: str,
        feature_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get feature information for a part (if terminal is a specific feature).
        
        Args:
            document_id: OnShape document ID
            workspace_id: Workspace ID
            element_id: Element (Part Studio) ID
            part_id: Part ID
            feature_id: Optional feature ID if terminal is a specific feature
            
        Returns:
            Feature information
        """
        if feature_id:
            endpoint = f"/parts/d/{document_id}/w/{workspace_id}/e/{element_id}/partid/{part_id}/features/{feature_id}"
        else:
            endpoint = f"/parts/d/{document_id}/w/{workspace_id}/e/{element_id}/partid/{part_id}/features"
        return await self.client.get(endpoint)
    
    
    async def get_minimum_distance(
        self,
        document_id: str,
        workspace_id: str,
        element_id: str,
        part_id1: str,
        part_id2: str
    ) -> Dict[str, Any]:
        """
        Get minimum distance between two parts using OnShape's evDistance via FeatureScript.
        
        Uses the evalFeatureScript endpoint: /partstudios/d/{did}/w/{wid}/e/{eid}/featurescript
        
        Args:
            document_id: OnShape document ID
            workspace_id: Workspace ID
            element_id: Element (Part Studio) ID
            part_id1: First part ID
            part_id2: Second part ID
            
        Returns:
            Dictionary with distance information including:
            - distance: Minimum distance in meters
            - status: "success" or "error"
        """
        # First, get the list of parts to find their indices
        parts = await self.get_all_parts(document_id, workspace_id, element_id)
        
        # Find indices of the target parts
        index1 = None
        index2 = None
        for i, part in enumerate(parts):
            part_id = part.get("partId") or part.get("id")
            if part_id == part_id1:
                index1 = i
            if part_id == part_id2:
                index2 = i
        
        if index1 is None or index2 is None:
            return {
                "distance": None,
                "status": "error",
                "error": f"Could not find part indices. Part 1: {part_id1} (found: {index1 is not None}), Part 2: {part_id2} (found: {index2 is not None})"
            }
        
        # Add delay between get_all_parts and FeatureScript call to avoid rate limiting
        await asyncio.sleep(1.5)
        
        # Use evalFeatureScript endpoint (correct format from OnShape API docs)
        endpoint = f"/partstudios/d/{document_id}/w/{workspace_id}/e/{element_id}/featurescript"
        
        # FeatureScript using OnShape's built-in evDistance function
        # Use array indices to select the correct parts
        feature_script = f'''
        function(context is Context, definition is map) {{
            // Get all solid bodies
            var allBodies = qBodyType(qEverything(EntityType.BODY), BodyType.SOLID);
            var bodies = evaluateQuery(context, allBodies);
            
            // Select parts by their index in the array
            var part1 = bodies[{index1}];
            var part2 = bodies[{index2}];
            
            // Calculate minimum distance using evDistance
            var distance = evDistance(context, {{
                "side0" : part1,
                "side1" : part2
            }});
            
            return distance;
        }}
        '''
        
        # Request format per OnShape API documentation
        request = {
            "libraryVersion": 2144,  # Current FeatureScript library version
            "script": feature_script.strip()
        }
        
        try:
            # POST to featurescript endpoint with rollbackBarIndex parameter
            response = await self.client.post(
                endpoint,
                json_data=request,
                params={"rollbackBarIndex": -1}
            )
            
            # Parse response - FeatureScript returns complex nested structure
            # evDistance returns a DistanceResult map with 'distance' field containing BTFSValueWithUnits
            if isinstance(response, dict):
                # Check for errors in notices
                notices = response.get("notices", [])
                errors = [n for n in notices if isinstance(n, dict) and 
                         n.get("message", {}).get("level") == "ERROR"]
                if errors:
                    error_msg = errors[0].get("message", {}).get("message", "FeatureScript error")
                    return {
                        "distance": None,
                        "status": "error",
                        "error": error_msg
                    }
                
                # Extract result from response
                result = response.get("result", {})
                
                # evDistance returns a DistanceResult map with 'distance' field
                if isinstance(result, dict):
                    # Check if result is a DistanceResult (has 'distance' field)
                    # Format: {"type": 2062, "typeName": "BTFSValueMap", "message": {"value": [...]}}
                    result_message = result.get("message", {})
                    result_value = result_message.get("value", [])
                    
                    # Find the 'distance' entry in the map
                    if isinstance(result_value, list):
                        for entry in result_value:
                            if isinstance(entry, dict):
                                entry_message = entry.get("message", {})
                                if isinstance(entry_message, dict):
                                    key = entry_message.get("key", {}).get("message", {}).get("value", "")
                                    if key == "distance":
                                        # Found distance field
                                        value_entry = entry_message.get("value", {})
                                        value_message = value_entry.get("message", {})
                                        distance_value = value_message.get("value")
                                        if distance_value is not None:
                                            return {
                                                "distance": float(distance_value),
                                                "status": "success"
                                            }
                    
                    # Alternative: try direct value extraction
                    distance_data = result.get("distance") or result.get("value")
                    if distance_data:
                        if isinstance(distance_data, dict):
                            distance_value = distance_data.get("value") or distance_data.get("message", {}).get("value")
                            if distance_value is not None:
                                return {
                                    "distance": float(distance_value),
                                    "status": "success"
                                }
                        elif isinstance(distance_data, (int, float)):
                            return {
                                "distance": float(distance_data),
                                "status": "success"
                            }
                
                # Check if result type indicates error (type: 0)
                if result.get("type") == 0 and not result.get("message"):
                    return {
                        "distance": None,
                        "status": "error",
                        "error": "FeatureScript execution failed (result type 0)"
                    }
            
            # If we get here, response format is unexpected
            return {
                "distance": None,
                "status": "error",
                "error": f"Could not parse distance from response",
                "raw_response": response
            }
            
        except Exception as e:
            return {
                "distance": None,
                "status": "error",
                "error": str(e)
            }
