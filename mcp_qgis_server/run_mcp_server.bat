@echo off
setlocal

:: Define QGIS Python Wrapper
set QGIS_PYTHON="C:\Program Files\QGIS 4.0.2\bin\python-qgis.bat"

echo =======================================================================
echo [QGIS-MCP] Verifying and installing required packages (mcp, fastmcp)...
echo =======================================================================

call %QGIS_PYTHON% -m pip install mcp fastmcp pydantic --quiet

echo =======================================================================
echo [QGIS-MCP] Booting Native QGIS MCP Server over JSON-RPC...
echo =======================================================================

call %QGIS_PYTHON% "%~dp0mcp_qgis_server.py"

endlocal
