# -*- coding: utf-8 -*-
"""
Native QGIS MCP Server
Exposes professional-grade PyQGIS 4.0.2 tools and geoprocessing algorithms via Model Context Protocol.
"""

import sys
import os
import atexit
import traceback
from datetime import datetime, date

# 1. CRITICAL: Redirect all standard output to standard error during initialization.
# This prevents QGIS, GDAL, or Qt DLL warning prints from contaminating stdout,
# which would violate the MCP JSON-RPC protocol and crash the MCP client.
_original_stdout = sys.stdout
sys.stdout = sys.stderr

print("[QGIS-MCP] Bootstrapping QGIS Environment...", file=sys.stderr)

try:
    # Setup paths for standalone QGIS 4.0.2
    QGIS_PREFIX = r"C:\Program Files\QGIS 4.0.2\apps\qgis"
    QGIS_PLUGINS = r"C:\Program Files\QGIS 4.0.2\apps\qgis\python\plugins"
    
    if QGIS_PLUGINS not in sys.path:
        sys.path.append(QGIS_PLUGINS)

    # Import core PyQGIS bindings
    from qgis.core import (
        QgsApplication,
        QgsVectorLayer,
        QgsCoordinateReferenceSystem,
        QgsCoordinateTransform,
        QgsGeometry,
        QgsPointXY,
        QgsProject,
        QgsFeatureRequest,
        QgsExpression,
        NULL
    )
    
    # Initialize QGIS Application (No GUI)
    QgsApplication.setPrefixPath(QGIS_PREFIX, True)
    qgs = QgsApplication([], False)
    qgs.initQgis()
    
    # Register clean shutdown handler
    def shutdown_qgis():
        print("[QGIS-MCP] Terminating QGIS Application...", file=sys.stderr)
        qgs.exitQgis()
    atexit.register(shutdown_qgis)
    
    # Initialize the Geoprocessing Framework
    import processing
    from processing.core.Processing import Processing
    Processing.initialize()
    
    ALGORITHMS_COUNT = len(QgsApplication.processingRegistry().algorithms())
    print(f"[QGIS-MCP] Initialization successful! Loaded {ALGORITHMS_COUNT} processing algorithms.", file=sys.stderr)

except Exception as e:
    print(f"[QGIS-MCP] CRITICAL ERROR during startup: {e}", file=sys.stderr)
    traceback.print_exc(file=sys.stderr)
    sys.exit(1)

# 2. Restore standard output so the MCP server can communicate with the client
sys.stdout = _original_stdout

# 3. Create the FastMCP Server
from mcp.server.fastmcp import FastMCP
mcp = FastMCP("QGIS Spatial Engine")


@mcp.tool()
def get_qgis_info() -> dict:
    """Get metadata about the current QGIS installation, Python environment, and loaded geoprocessing tools."""
    try:
        from qgis.core import Qgis
        return {
            "qgis_version": Qgis.version(),
            "qgis_release_name": Qgis.releaseName(),
            "qgis_prefix_path": QgsApplication.prefixPath(),
            "python_version": sys.version,
            "algorithms_loaded": len(QgsApplication.processingRegistry().algorithms()),
            "status": "Running",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"error": f"Failed to retrieve QGIS info: {str(e)}"}


@mcp.tool()
def reproject_coordinates(x: float, y: float, source_crs: str = "EPSG:4326", target_crs: str = "EPSG:3857") -> dict:
    """
    Reproject a coordinate point (X, Y) from a source CRS to a target CRS.
    Default reprojects Latitude/Longitude (EPSG:4326) to Web Mercator (EPSG:3857).
    Also supports local coordinate systems like Colombia (EPSG:3116 / Magna-Sirgas).
    """
    try:
        src = QgsCoordinateReferenceSystem(source_crs)
        tgt = QgsCoordinateReferenceSystem(target_crs)
        
        if not src.isValid():
            return {"error": f"Invalid source CRS: '{source_crs}'"}
        if not tgt.isValid():
            return {"error": f"Invalid target CRS: '{target_crs}'"}
            
        transform = QgsCoordinateTransform(src, tgt, QgsProject.instance())
        point = QgsPointXY(x, y)
        reprojected = transform.transform(point)
        
        return {
            "source": {"x": x, "y": y, "crs": source_crs},
            "result": {"x": reprojected.x(), "y": reprojected.y(), "crs": target_crs},
            "status": "Success"
        }
    except Exception as e:
        return {"error": f"Reprojection failed: {str(e)}"}


@mcp.tool()
def get_layer_metadata(file_path: str) -> dict:
    """
    Load a spatial vector layer (Shapefile, GeoJSON, KML, GPX, SQLite/SpatiaLite, CSV) and retrieve its metadata.
    Includes feature count, CRS, geometry type, bounding extent, and attribute fields.
    """
    try:
        # Resolve absolute path if needed
        abs_path = os.path.abspath(file_path)
        if not os.path.exists(abs_path):
            return {"error": f"File does not exist: {file_path}"}
            
        # Initialize Vector Layer using OGR driver
        layer = QgsVectorLayer(abs_path, os.path.basename(file_path), "ogr")
        if not layer.isValid():
            return {"error": f"Failed to load layer as OGR vector: {file_path}"}
            
        fields = [f"{field.name()} ({field.typeName()})" for field in layer.fields()]
        extent = layer.extent()
        
        geom_names = ["Point", "Line", "Polygon", "Null Geometry", "Unknown"]
        geom_type_idx = min(layer.geometryType(), 4)
        
        return {
            "layer_name": layer.name(),
            "valid": True,
            "feature_count": layer.featureCount(),
            "geometry_type": geom_names[geom_type_idx],
            "crs": layer.crs().authid(),
            "crs_description": layer.crs().description(),
            "extent": {
                "xmin": extent.xMinimum(),
                "xmax": extent.xMaximum(),
                "ymin": extent.yMinimum(),
                "ymax": extent.yMaximum()
            },
            "fields": fields,
            "status": "Success"
        }
    except Exception as e:
        return {"error": f"Metadata retrieval failed: {str(e)}"}


@mcp.tool()
def geometry_analysis(geometry_wkt: str, operation: str, distance: float = 10.0) -> dict:
    """
    Perform single geometry operations on a Well-Known Text (WKT) geometry.
    Operations available:
    - 'centroid': Calculate the center point.
    - 'buffer': Create a buffer polygon around the geometry by a specified distance.
    - 'envelope': Get the bounding box/envelope polygon.
    - 'area': Calculate planar area (for polygons).
    - 'length': Calculate planar length/perimeter (for lines/polygons).
    """
    try:
        geom = QgsGeometry.fromWkt(geometry_wkt)
        if geom.isEmpty():
            return {"error": "Invalid or empty WKT geometry."}
            
        op = operation.lower().strip()
        
        if op == "centroid":
            centroid = geom.centroid()
            return {"operation": op, "result_wkt": centroid.asWkt(), "status": "Success"}
            
        elif op == "buffer":
            buffered = geom.buffer(distance, 5) # 5 segments for curves
            return {"operation": op, "distance": distance, "result_wkt": buffered.asWkt(), "status": "Success"}
            
        elif op == "envelope":
            envelope = geom.envelope()
            return {"operation": op, "result_wkt": envelope.asWkt(), "status": "Success"}
            
        elif op == "area":
            return {"operation": op, "area": geom.area(), "status": "Success"}
            
        elif op == "length":
            return {"operation": op, "length": geom.length(), "status": "Success"}
            
        else:
            return {"error": f"Unsupported operation '{operation}'. Choose from: centroid, buffer, envelope, area, length."}
            
    except Exception as e:
        return {"error": f"Geometry analysis failed: {str(e)}"}


@mcp.tool()
def geometry_relation(geom1_wkt: str, geom2_wkt: str) -> dict:
    """
    Check topological spatial relationships between two WKT geometries (e.g., checks if they intersect, overlap, etc.).
    Returns boolean values for: intersects, contains, within, touches, disjoint, overlaps, crosses.
    """
    try:
        g1 = QgsGeometry.fromWkt(geom1_wkt)
        g2 = QgsGeometry.fromWkt(geom2_wkt)
        
        if g1.isEmpty() or g2.isEmpty():
            return {"error": "One or both WKT geometries are invalid/empty."}
            
        return {
            "intersects": g1.intersects(g2),
            "contains": g1.contains(g2),
            "within": g1.within(g2),
            "touches": g1.touches(g2),
            "disjoint": g1.disjoint(g2),
            "overlaps": g1.overlaps(g2),
            "crosses": g1.crosses(g2),
            "status": "Success"
        }
    except Exception as e:
        return {"error": f"Spatial relationship evaluation failed: {str(e)}"}


@mcp.tool()
def query_vector_layer(file_path: str, expression: str = "", limit: int = 100) -> dict:
    """
    Load a vector file and query its attributes and geometries using SQL-like expressions (QGIS Expression engine).
    Returns list of matching records with their primary properties, attributes, and WKT geometries.
    """
    try:
        abs_path = os.path.abspath(file_path)
        if not os.path.exists(abs_path):
            return {"error": f"File not found: {file_path}"}
            
        layer = QgsVectorLayer(abs_path, os.path.basename(file_path), "ogr")
        if not layer.isValid():
            return {"error": f"Failed to load layer: {file_path}"}
            
        request = QgsFeatureRequest()
        if expression:
            qgs_exp = QgsExpression(expression)
            if qgs_exp.hasParserError():
                return {"error": f"Expression parse error: {qgs_exp.parserErrorString()}"}
            request.setFilterExpression(expression)
            
        features = []
        count = 0
        for feat in layer.getFeatures(request):
            if count >= limit:
                break
                
            attrs = {}
            for field in layer.fields():
                val = feat[field.name()]
                if val == NULL:
                    val = None
                else:
                    # Resolve PyQt6 QDate/QDateTime/QTime to standard python date/datetime/time
                    if hasattr(val, 'toPyDate') and callable(getattr(val, 'toPyDate')):
                        val = val.toPyDate()
                    elif hasattr(val, 'toPyDateTime') and callable(getattr(val, 'toPyDateTime')):
                        val = val.toPyDateTime()
                    elif hasattr(val, 'toPyTime') and callable(getattr(val, 'toPyTime')):
                        val = val.toPyTime()
                    
                    # Convert standard datetime/date/time to ISO format strings
                    if isinstance(val, (datetime, date)):
                        val = val.isoformat()
                attrs[field.name()] = val
                
            geom = feat.geometry()
            wkt = geom.asWkt() if not geom.isEmpty() else None
            
            features.append({
                "fid": feat.id(),
                "attributes": attrs,
                "geometry": wkt
            })
            count += 1
            
        return {
            "layer_name": layer.name(),
            "query_expression": expression,
            "records_returned": len(features),
            "limit": limit,
            "features": features,
            "status": "Success"
        }
    except Exception as e:
        return {"error": f"Layer query failed: {str(e)}"}


@mcp.tool()
def run_qgis_processing(algorithm_id: str, parameters: dict) -> dict:
    """
    Run any of the 769 native QGIS geoprocessing algorithms (e.g., 'native:buffer', 'native:centroids', 'native:clip').
    Inputs:
    - algorithm_id: Fully qualified QGIS ID, e.g., 'native:buffer'.
    - parameters: A dictionary of key-value pairs of parameters matching the algorithm's requirements.
    
    Example running native:buffer:
    algorithm_id = "native:buffer"
    parameters = {
        "INPUT": "C:/data/points.shp",
        "DISTANCE": 50,
        "OUTPUT": "C:/data/buffered_points.shp"
    }
    """
    try:
        # Load and verify the algorithm exists in the registry
        alg = QgsApplication.processingRegistry().algorithmById(algorithm_id)
        if not alg:
            return {"error": f"Algorithm '{algorithm_id}' not found in QGIS processing registry."}
            
        # Run processing algorithm safely
        print(f"[QGIS-MCP] Running processing algorithm '{algorithm_id}'...", file=sys.stderr)
        results = processing.run(algorithm_id, parameters)
        
        # Format results (handling non-JSON serializable layers in QGIS return structures)
        serializable_results = {}
        for k, v in results.items():
            if hasattr(v, 'source') and callable(getattr(v, 'source')):
                serializable_results[k] = v.source()
            elif hasattr(v, 'id') and hasattr(v, 'name'):
                serializable_results[k] = {"id": v.id(), "name": v.name(), "source": getattr(v, 'source', lambda: "")()}
            else:
                serializable_results[k] = str(v)
                
        return {
            "algorithm_run": algorithm_id,
            "results": serializable_results,
            "status": "Success"
        }
    except Exception as e:
        return {"error": f"Processing algorithm execution failed: {str(e)}"}


if __name__ == "__main__":
    mcp.run()
