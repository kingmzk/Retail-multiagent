"""Startup Script for Retail Customer Support POC.

Launches:
1. Order MCP Server (port 8101)
2. Product MCP Server (port 8102)
3. FastAPI Backend (port 8000)
"""
import subprocess
import sys
import time
import signal
import os

python_exe = sys.executable


def start_all():
    print("================================================================")
    print("  Starting Standalone POC - Retail Customer Support Assistant   ")
    print("================================================================")

    processes = []
    try:
        # 1. Start Order MCP Server
        print("Launching Order MCP Server on port 8101...")
        order_proc = subprocess.Popen(
            [python_exe, "-m", "uvicorn", "mcp_servers.order.server:app", "--port", "8101", "--host", "0.0.0.0"],
            cwd=os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        )
        processes.append(order_proc)

        # 2. Start Product MCP Server
        print("Launching Product MCP Server on port 8102...")
        prod_proc = subprocess.Popen(
            [python_exe, "-m", "uvicorn", "mcp_servers.product.server:app", "--port", "8102", "--host", "0.0.0.0"],
            cwd=os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        )
        processes.append(prod_proc)

        time.sleep(2)

        # 3. Start FastAPI Application
        print("Launching FastAPI Application on port 8000...")
        app_proc = subprocess.Popen(
            [python_exe, "-m", "uvicorn", "app.main:app", "--port", "8000", "--host", "0.0.0.0"],
            cwd=os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        )
        processes.append(app_proc)

        print("\nAll services started successfully!")
        print(" -> FastAPI API: http://localhost:8000/docs")
        print(" -> Health check: http://localhost:8000/health")
        print(" -> Order MCP: http://localhost:8101/mcp")
        print(" -> Product MCP: http://localhost:8102/mcp")
        print("\nPress Ctrl+C to terminate all services...\n")

        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nShutting down all processes...")
        for p in processes:
            p.terminate()
            p.wait()
        print("All processes terminated.")


if __name__ == "__main__":
    start_all()
