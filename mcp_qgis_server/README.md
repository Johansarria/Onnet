# QGIS Native MCP Server 🌍

A Model Context Protocol (MCP) server that interfaces directly with **QGIS 4.0.2-Norrköping**'s native Python bindings on Windows. This enables LLM agents to execute advanced geospatial analysis, handle geometries in WKT, and run any of the **769 native QGIS geoprocessing algorithms** directly via conversational interfaces.

---

## Features & Tools

The server exposes the following tools to your AI agent:

1. **`get_qgis_info`**: Inspects QGIS installation path, version, and validates that all 769 processing algorithms are active.
2. **`reproject_coordinates`**: Translates coordinates (X, Y) or Latitude/Longitude between any two Coordinate Reference Systems (CRS) (e.g., reprojecting GPS coordinates `EPSG:4326` to Colombia's local grid `EPSG:3116` / Magna-Sirgas).
3. **`get_layer_metadata`**: Opens shapefiles, GeoJSON, KML, or Excel sheets to report schema field types, feature count, CRS, and geographical extent.
4. **`geometry_analysis`**: Calculates planar area/length, and performs single-geometry calculations like **buffers** and **centroids** via WKT.
5. **`geometry_relation`**: Checks topological relationships between WKT geometries (`intersects`, `contains`, `touches`, `disjoint`, `overlaps`, etc.).
6. **`query_vector_layer`**: Queries spatial files using advanced SQL-like attribute filters and gets matching geometry features as WKT.
7. **`run_qgis_processing`**: Runs **any native QGIS geoprocessing algorithm** by ID (e.g., `native:buffer`, `native:clip`, `native:centroids`) with a dictionary of parameters.

---

## Installation & Configuration

This server is self-installing! It wraps the execution inside QGIS's native `python-qgis.bat` script, which automatically resolves all C++ native DLLs, path variables, and pre-packaged scientific packages like `numpy`, `pandas`, `geopandas`, and `PyQt6`.

### 1. Integration with Claude Desktop

To add this server to the official **Claude Desktop** application:

1. Open your Windows File Explorer and navigate to:
   `%APPDATA%\Claude\` (e.g., `C:\Users\<YourUser>\AppData\Roaming\Claude\`)
2. Open the file `claude_desktop_config.json` in a text editor (create it if it doesn't exist).
3. Add the following entry inside the `mcpServers` block:

```json
{
  "mcpServers": {
    "qgis-spatial-engine": {
      "command": "cmd.exe",
      "args": [
        "/c",
        "c:\\Onnet\\mcp_qgis_server\\run_mcp_server.bat"
      ]
    }
  }
}
```

4. **Restart Claude Desktop**. The app will automatically run `run_mcp_server.bat`, download dependencies (`mcp`, `fastmcp`), and initialize the QGIS spatial engine. You can now tell Claude: *"Analyze this shapefile at C:\data\points.shp"* or *"Help me reproject this point from EPSG:4326 to EPSG:3116"*.

### 2. Integration with Cursor / VS Code (Cline / Windsurf)

To add the server in **Cursor**:
1. Go to **Settings > Features > MCP**.
2. Click **+ Add New MCP Server**.
3. Configure:
   * **Name**: `qgis-spatial-engine`
   * **Type**: `command`
   * **Command**: `cmd.exe /c c:\Onnet\mcp_qgis_server\run_mcp_server.bat`
4. Click **Save**.

---

## Developer Operations

The workspace at `c:\Onnet\mcp_qgis_server` is structured as follows:
* **`mcp_qgis_server.py`**: The server codebase using the high-level `fastmcp` framework. It implements custom stdout redirecting to prevent native C++ warning logs from polluting the JSON-RPC interface.
* **`run_mcp_server.bat`**: Automatic launcher script that handles dependency updates and environment binding.
