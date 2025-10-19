#!/usr/bin/env python3
"""
MCP Server Launcher for GupShup Café
Utility to start/stop MCP servers for development and testing

Usage:
    # Start all MCP servers
    python server_py/src/mcp/launcher.py start --all
    
    # Start specific server
    python server_py/src/mcp/launcher.py start --server debate_tools
    
    # Stop all servers
    python server_py/src/mcp/launcher.py stop --all
    
    # Check server status
    python server_py/src/mcp/launcher.py status
"""

import subprocess
import time
import signal
import sys
import os
from typing import Dict, List, Optional
import logging
import argparse
import json
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

# Server configurations
MCP_SERVERS = {
    'debate_tools': {
        'module': 'server_py.src.mcp.debate_room_tools',
        'port': 8000,
        'name': 'Debate Room Tools',
        'pid_file': '/tmp/mcp_debate_tools.pid'
    },
    'grammar_tools': {
        'module': 'server_py.src.mcp.grammar_tools',
        'port': 8001,
        'name': 'Grammar Tools',
        'pid_file': '/tmp/mcp_grammar_tools.pid'
    }
}


class MCPServerLauncher:
    """Manages MCP server processes for development and testing"""
    
    def __init__(self):
        self.processes: Dict[str, subprocess.Popen] = {}
    
    def start_server(self, server_id: str, detached: bool = False) -> bool:
        """
        Start an MCP server
        
        Args:
            server_id: Server identifier ('debate_tools', 'grammar_tools')
            detached: Run server in background (default: False)
            
        Returns:
            True if started successfully, False otherwise
        """
        if server_id not in MCP_SERVERS:
            logger.error(f"Unknown server: {server_id}")
            logger.info(f"Available servers: {', '.join(MCP_SERVERS.keys())}")
            return False
        
        server_config = MCP_SERVERS[server_id]
        
        # Check if server is already running
        if self.is_server_running(server_id):
            logger.warning(f"{server_config['name']} is already running on port {server_config['port']}")
            return False
        
        logger.info(f"🚀 Starting {server_config['name']} on port {server_config['port']}...")
        
        try:
            if detached:
                # Run in background
                # Ensure module import works regardless of CWD by setting PYTHONPATH to repo root
                repo_root = Path(__file__).resolve().parents[3]
                env = os.environ.copy()
                env['PYTHONPATH'] = f"{repo_root}:{env.get('PYTHONPATH','')}"

                # Detach stdio to avoid PIPE buffering deadlocks for noisy servers
                # Run via uvicorn against module:app to ensure HTTP endpoint at /mcp/
                uvicorn_target = f"{server_config['module']}:app"
                process = subprocess.Popen(
                    [sys.executable, '-m', 'uvicorn', uvicorn_target, '--host', '127.0.0.1', '--port', str(server_config['port'])],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    stdin=subprocess.DEVNULL,
                    start_new_room=True,
                    cwd=str(repo_root),
                    env=env
                )
                
                # Save PID
                with open(server_config['pid_file'], 'w') as f:
                    f.write(str(process.pid))
                
                # Give it a moment to start
                time.sleep(2)
                
                if process.poll() is None:
                    logger.info(f"✅ {server_config['name']} started in background (PID: {process.pid})")
                    logger.info(f"   MCP endpoint: http://localhost:{server_config['port']}/mcp/")
                    return True
                else:
                    logger.error(f"❌ {server_config['name']} failed to start")
                    return False
            else:
                # Run in foreground
                repo_root = Path(__file__).resolve().parents[3]
                env = os.environ.copy()
                env['PYTHONPATH'] = f"{repo_root}:{env.get('PYTHONPATH','')}"

                uvicorn_target = f"{server_config['module']}:app"
                process = subprocess.Popen(
                    [sys.executable, '-m', 'uvicorn', uvicorn_target, '--host', '127.0.0.1', '--port', str(server_config['port'])],
                    stdout=sys.stdout,
                    stderr=sys.stderr,
                    cwd=str(repo_root),
                    env=env
                )
                
                self.processes[server_id] = process
                
                # Wait for process (blocking)
                process.wait()
                return True
                
        except Exception as e:
            logger.error(f"❌ Error starting {server_config['name']}: {e}")
            return False
    
    def stop_server(self, server_id: str) -> bool:
        """
        Stop an MCP server
        
        Args:
            server_id: Server identifier
            
        Returns:
            True if stopped successfully, False otherwise
        """
        if server_id not in MCP_SERVERS:
            logger.error(f"Unknown server: {server_id}")
            return False
        
        server_config = MCP_SERVERS[server_id]
        
        # Try to read PID from file
        pid_file = server_config['pid_file']
        if os.path.exists(pid_file):
            try:
                with open(pid_file, 'r') as f:
                    pid = int(f.read().strip())
                
                # Try to kill process
                try:
                    os.kill(pid, signal.SIGTERM)
                    time.sleep(1)
                    logger.info(f"✅ Stopped {server_config['name']} (PID: {pid})")
                    os.remove(pid_file)
                    return True
                except ProcessLookupError:
                    logger.warning(f"Process {pid} not found, cleaning up PID file")
                    os.remove(pid_file)
                    return False
                    
            except Exception as e:
                logger.error(f"Error stopping server: {e}")
                return False
        
        # Check in-process servers
        if server_id in self.processes:
            process = self.processes[server_id]
            process.terminate()
            process.wait(timeout=5)
            del self.processes[server_id]
            logger.info(f"✅ Stopped {server_config['name']}")
            return True
        
        logger.warning(f"{server_config['name']} is not running")
        return False
    
    def is_server_running(self, server_id: str) -> bool:
        """
        Check if an MCP server is running
        
        Args:
            server_id: Server identifier
            
        Returns:
            True if running, False otherwise
        """
        if server_id not in MCP_SERVERS:
            return False
        
        server_config = MCP_SERVERS[server_id]
        pid_file = server_config['pid_file']
        
        if os.path.exists(pid_file):
            try:
                with open(pid_file, 'r') as f:
                    pid = int(f.read().strip())
                
                # Check if process exists
                try:
                    os.kill(pid, 0)  # Signal 0 doesn't kill, just checks if process exists
                    return True
                except ProcessLookupError:
                    # Process doesn't exist, clean up stale PID file
                    os.remove(pid_file)
                    return False
                    
            except Exception:
                return False
        
        return server_id in self.processes and self.processes[server_id].poll() is None
    
    def start_all(self, detached: bool = True):
        """Start all MCP servers"""
        logger.info("🚀 Starting all MCP servers...")
        
        success_count = 0
        for server_id in MCP_SERVERS.keys():
            if self.start_server(server_id, detached=detached):
                success_count += 1
        
        logger.info(f"✅ Started {success_count}/{len(MCP_SERVERS)} MCP servers")
    
    def stop_all(self):
        """Stop all MCP servers"""
        logger.info("🛑 Stopping all MCP servers...")
        
        for server_id in MCP_SERVERS.keys():
            self.stop_server(server_id)
        
        logger.info("✅ All MCP servers stopped")
    
    def status(self):
        """Show status of all MCP servers"""
        logger.info("📊 MCP Server Status:")
        logger.info("-" * 60)
        
        for server_id, config in MCP_SERVERS.items():
            running = self.is_server_running(server_id)
            status_icon = "✅" if running else "❌"
            status_text = "Running" if running else "Stopped"
            
            logger.info(f"{status_icon} {config['name']:<25} | Port: {config['port']} | {status_text}")
        
        logger.info("-" * 60)


def main():
    parser = argparse.ArgumentParser(description="MCP Server Launcher for GupShup Café")
    parser.add_argument(
        'action',
        choices=['start', 'stop', 'restart', 'status'],
        help='Action to perform'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Apply action to all servers'
    )
    parser.add_argument(
        '--server',
        choices=list(MCP_SERVERS.keys()),
        help='Specific server to control'
    )
    parser.add_argument(
        '--foreground',
        action='store_true',
        help='Run server in foreground (default: background)'
    )
    
    args = parser.parse_args()
    
    launcher = MCPServerLauncher()
    
    if args.action == 'start':
        if args.all:
            launcher.start_all(detached=not args.foreground)
        elif args.server:
            launcher.start_server(args.server, detached=not args.foreground)
        else:
            parser.error("Specify --all or --server")
    
    elif args.action == 'stop':
        if args.all:
            launcher.stop_all()
        elif args.server:
            launcher.stop_server(args.server)
        else:
            parser.error("Specify --all or --server")
    
    elif args.action == 'restart':
        if args.all:
            launcher.stop_all()
            time.sleep(1)
            launcher.start_all(detached=not args.foreground)
        elif args.server:
            launcher.stop_server(args.server)
            time.sleep(1)
            launcher.start_server(args.server, detached=not args.foreground)
        else:
            parser.error("Specify --all or --server")
    
    elif args.action == 'status':
        launcher.status()


if __name__ == "__main__":
    main()
