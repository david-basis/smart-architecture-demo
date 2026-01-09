"""Mesh distance calculation utilities."""

from typing import Dict, Any, List, Tuple
import math
import numpy as np


def calculate_mesh_distance(
    vertices1: List[List[float]],
    faces1: List[List[int]],
    vertices2: List[List[float]],
    faces2: List[List[int]]
) -> float:
    """
    Calculate minimum distance between two meshes.
    
    Args:
        vertices1: List of vertices for first mesh [[x, y, z], ...]
        faces1: List of face indices for first mesh [[i1, i2, i3], ...]
        vertices2: List of vertices for second mesh
        faces2: List of face indices for second mesh
        
    Returns:
        Minimum distance in meters
    """
    # Convert to numpy arrays for efficient computation
    v1 = np.array(vertices1)
    v2 = np.array(vertices2)
    
    # Calculate minimum distance between all vertex pairs
    min_dist = float('inf')
    
    # Method 1: Vertex-to-vertex distance (fast approximation)
    for v in v1:
        distances = np.linalg.norm(v2 - v, axis=1)
        min_dist = min(min_dist, np.min(distances))
    
    # Method 2: Vertex-to-face distance (more accurate)
    # For each vertex in mesh1, find closest point on mesh2 faces
    for v in v1:
        for face in faces2:
            if len(face) >= 3:
                # Get triangle vertices
                p0 = v2[face[0]]
                p1 = v2[face[1]]
                p2 = v2[face[2]] if len(face) > 2 else v2[face[0]]
                
                # Calculate closest point on triangle
                closest = closest_point_on_triangle(v, p0, p1, p2)
                dist = np.linalg.norm(v - closest)
                min_dist = min(min_dist, dist)
    
    # Method 3: Face-to-face distance (most accurate but slower)
    # For small meshes, check face-to-face distances
    if len(faces1) < 100 and len(faces2) < 100:
        for face1 in faces1:
            if len(face1) >= 3:
                for face2 in faces2:
                    if len(face2) >= 3:
                        # Get triangle vertices
                        t1_v0 = v1[face1[0]]
                        t1_v1 = v1[face1[1]]
                        t1_v2 = v1[face1[2]] if len(face1) > 2 else v1[face1[0]]
                        
                        t2_v0 = v2[face2[0]]
                        t2_v1 = v2[face2[1]]
                        t2_v2 = v2[face2[2]] if len(face2) > 2 else v2[face2[0]]
                        
                        # Calculate minimum distance between two triangles
                        dist = triangle_triangle_distance(
                            t1_v0, t1_v1, t1_v2,
                            t2_v0, t2_v1, t2_v2
                        )
                        min_dist = min(min_dist, dist)
    
    return min_dist


def closest_point_on_triangle(
    point: np.ndarray,
    v0: np.ndarray,
    v1: np.ndarray,
    v2: np.ndarray
) -> np.ndarray:
    """
    Find closest point on triangle to given point.
    
    Args:
        point: Point to test
        v0, v1, v2: Triangle vertices
        
    Returns:
        Closest point on triangle
    """
    # Vector from v0 to v1 and v0 to v2
    edge1 = v1 - v0
    edge2 = v2 - v0
    v0_to_point = point - v0
    
    # Calculate dot products
    a = np.dot(edge1, edge1)
    b = np.dot(edge1, edge2)
    c = np.dot(edge2, edge2)
    d = np.dot(edge1, v0_to_point)
    e = np.dot(edge2, v0_to_point)
    
    # Barycentric coordinates
    det = a * c - b * b
    if abs(det) < 1e-10:
        # Degenerate triangle, return closest vertex
        dists = [
            np.linalg.norm(point - v0),
            np.linalg.norm(point - v1),
            np.linalg.norm(point - v2)
        ]
        idx = np.argmin(dists)
        return [v0, v1, v2][idx]
    
    s = b * e - c * d
    t = b * d - a * e
    
    if s + t < det:
        if s < 0:
            if t < 0:
                # Region 4: closest to v0
                return v0
            else:
                # Region 3: closest to edge v0-v2
                t = max(0, min(1, e / c))
                return v0 + t * edge2
        else:
            if t < 0:
                # Region 5: closest to edge v0-v1
                s = max(0, min(1, d / a))
                return v0 + s * edge1
            else:
                # Region 0: inside triangle
                inv_det = 1.0 / det
                s *= inv_det
                t *= inv_det
                return v0 + s * edge1 + t * edge2
    else:
        if s < 0:
            # Region 2: closest to v2
            return v2
        elif t < 0:
            # Region 6: closest to v1
            return v1
        else:
            # Region 1: closest to edge v1-v2
            t = max(0, min(1, (e + b - d) / (a - 2 * b + c)))
            return v1 + t * (v2 - v1)


def triangle_triangle_distance(
    t1_v0: np.ndarray, t1_v1: np.ndarray, t1_v2: np.ndarray,
    t2_v0: np.ndarray, t2_v1: np.ndarray, t2_v2: np.ndarray
) -> float:
    """
    Calculate minimum distance between two triangles.
    
    Args:
        t1_v0, t1_v1, t1_v2: First triangle vertices
        t2_v0, t2_v1, t2_v2: Second triangle vertices
        
    Returns:
        Minimum distance
    """
    min_dist = float('inf')
    
    # Check all vertex-to-triangle distances
    for v in [t1_v0, t1_v1, t1_v2]:
        closest = closest_point_on_triangle(v, t2_v0, t2_v1, t2_v2)
        dist = np.linalg.norm(v - closest)
        min_dist = min(min_dist, dist)
    
    for v in [t2_v0, t2_v1, t2_v2]:
        closest = closest_point_on_triangle(v, t1_v0, t1_v1, t1_v2)
        dist = np.linalg.norm(v - closest)
        min_dist = min(min_dist, dist)
    
    return min_dist


def parse_tessellation_response(response: Any) -> Tuple[List[List[float]], List[List[int]]]:
    """
    Parse OnShape tessellated edges response into vertices and faces.
    
    Args:
        response: OnShape API tessellated edges response (can be dict or list)
        
    Returns:
        Tuple of (vertices, faces)
    """
    vertices = []
    faces = []
    vertex_set = set()  # To deduplicate vertices
    
    # Handle list format (tessellated edges)
    if isinstance(response, list):
        for item in response:
            if isinstance(item, dict) and "edges" in item:
                # Format: [{"id": "...", "edges": [{"id": "...", "vertices": [[x,y,z], ...]}]}]
                for edge in item["edges"]:
                    if "vertices" in edge:
                        for vertex in edge["vertices"]:
                            if isinstance(vertex, list) and len(vertex) >= 3:
                                # Create tuple for deduplication
                                vertex_tuple = tuple(vertex[:3])
                                if vertex_tuple not in vertex_set:
                                    vertex_set.add(vertex_tuple)
                                    vertices.append(vertex[:3])
            elif isinstance(item, dict) and "vertices" in item:
                # Direct vertices format
                for vertex in item["vertices"]:
                    if isinstance(vertex, list) and len(vertex) >= 3:
                        vertex_tuple = tuple(vertex[:3])
                        if vertex_tuple not in vertex_set:
                            vertex_set.add(vertex_tuple)
                            vertices.append(vertex[:3])
    
    # Handle dict format
    elif isinstance(response, dict):
        if "bodies" in response:
            # Multi-body format
            for body_id, body_data in response["bodies"].items():
                if "faces" in body_data:
                    for face in body_data["faces"]:
                        if "vertices" in face:
                            for vertex in face["vertices"]:
                                if isinstance(vertex, dict) and "position" in vertex:
                                    pos = vertex["position"]
                                    if isinstance(pos, list) and len(pos) >= 3:
                                        vertex_tuple = tuple(pos[:3])
                                        if vertex_tuple not in vertex_set:
                                            vertex_set.add(vertex_tuple)
                                            vertices.append(pos[:3])
                        if "indices" in face:
                            faces.append(face["indices"])
        elif "faces" in response:
            # Direct faces format
            for face in response["faces"]:
                if "vertices" in face:
                    for vertex in face["vertices"]:
                        if isinstance(vertex, dict) and "position" in vertex:
                            pos = vertex["position"]
                            if isinstance(pos, list) and len(pos) >= 3:
                                vertex_tuple = tuple(pos[:3])
                                if vertex_tuple not in vertex_set:
                                    vertex_set.add(vertex_tuple)
                                    vertices.append(pos[:3])
                if "indices" in face:
                    faces.append(face["indices"])
        elif "vertices" in response and "faces" in response:
            # Simple format
            for vertex in response["vertices"]:
                if isinstance(vertex, list) and len(vertex) >= 3:
                    vertex_tuple = tuple(vertex[:3])
                    if vertex_tuple not in vertex_set:
                        vertex_set.add(vertex_tuple)
                        vertices.append(vertex[:3])
            faces = response.get("faces", [])
    
    # If no faces, create a simple point cloud (all vertices are separate points)
    # For distance calculation, we can use vertices directly
    if not faces and vertices:
        # Create degenerate faces (each vertex is its own "face" for distance calc)
        faces = [[i] for i in range(len(vertices))]
    
    return vertices, faces


