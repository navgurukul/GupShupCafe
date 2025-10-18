"""
MCP Tools Manager for GupShup Café
Manages MCP client connections and tool registration using Strands SDK patterns
Based on strands-agents/sdk-python and bedrock-agentcore-sdk-python integration patterns
"""

from typing import Dict, List, Optional, Any, Tuple
from mcp.client.streamable_http import streamablehttp_client
from strands.tools.mcp import MCPClient
from contextlib import contextmanager
import logging
import time

try:
    import httpx  # used for readiness probing
except Exception:  # pragma: no cover
    httpx = None

logger = logging.getLogger(__name__)


class MCPToolsManager:
    """
    Manages MCP client connections and tool availability for agents
    Follows Strands SDK MCPClient patterns with streamable HTTP transport
    """
    
    def __init__(self):
        """Initialize MCP Tools Manager"""
        self.clients: Dict[str, MCPClient] = {}
        self.active_clients: List[str] = []
        logger.info("✅ MCPToolsManager initialized")
    
    def register_client(self, name: str, endpoint: str, startup_timeout: int = 45) -> None:
        """
        Register an MCP client connection
        
        Args:
            name: Client identifier (e.g., 'debate_tools', 'grammar_tools')
            endpoint: HTTP endpoint for the MCP server (e.g., 'http://localhost:8000/mcp/')
            startup_timeout: Timeout for client initialization (default: 30 seconds)
        
        Example:
            manager.register_client('debate_tools', 'http://localhost:8000/mcp/')
        """
        if name in self.clients:
            logger.warning(f"Client '{name}' already registered. Skipping.")
            return
        
        # Normalize endpoint and probe alternates (with/without trailing slash)
        chosen_endpoint, probed = self._choose_reachable_endpoint(endpoint)
        if probed and chosen_endpoint != endpoint:
            logger.info(f"[MCP] Using reachable endpoint for '{name}': {chosen_endpoint} (from {endpoint})")
        elif not probed:
            logger.warning(f"[MCP] Endpoint not reachable yet for '{name}': {endpoint}. Client will retry on first use.")

        # Create transport callable following Strands SDK pattern (streamable HTTP)
        def create_transport():
            return streamablehttp_client(chosen_endpoint)
        
        # Initialize MCPClient with transport and timeout
        client = MCPClient(create_transport, startup_timeout=startup_timeout)
        
        self.clients[name] = client
        logger.info(f"✅ Registered MCP client: {name} -> {chosen_endpoint}")

    def _normalize_endpoint(self, endpoint: str) -> Tuple[str, str]:
        """Return tuple of (no-trailing, with-trailing) endpoint variants under /mcp.

        Examples:
            http://localhost:8000 → (http://localhost:8000/mcp, http://localhost:8000/mcp/)
            http://localhost:8000/mcp → (http://localhost:8000/mcp, http://localhost:8000/mcp/)
            http://localhost:8000/mcp/ → (http://localhost:8000/mcp, http://localhost:8000/mcp/)
        """
        e = endpoint.strip()
        # Ensure scheme
        if e.startswith('//'):
            e = 'http:' + e
        if not e.startswith('http://') and not e.startswith('https://'):
            e = 'http://' + e
        # Ensure path under /mcp
        if '/mcp' not in e:
            e = e.rstrip('/') + '/mcp'
        # Create both variants
        no_trailing = e.rstrip('/')
        with_trailing = no_trailing + '/'
        return no_trailing, with_trailing

    def _probe_endpoint_once(self, url: str, timeout: float = 1.0) -> bool:
        """Quick probe that returns True if TCP+HTTP respond at all (any status)."""
        if httpx is None:
            return False
        try:
            # A simple GET is enough to confirm reachability; many servers return 405/404/500 here, which is fine
            resp = httpx.get(url, timeout=timeout)
            return resp is not None
        except Exception:
            return False

    def _choose_reachable_endpoint(self, endpoint: str, total_timeout: float = 5.0) -> Tuple[str, bool]:
        """Try both /mcp and /mcp/ until one responds or timeout elapses.

        Returns: (chosen_endpoint, probed_ok)
        """
        primary, alt = self._normalize_endpoint(endpoint)
        # Try quick probes on both variants with small backoff
        start = time.time()
        while time.time() - start < total_timeout:
            if self._probe_endpoint_once(primary) or self._probe_endpoint_once(alt):
                # Prefer whatever returned True first; if only alt is reachable, use alt
                chosen = primary if self._probe_endpoint_once(primary) else alt
                return chosen, True
            time.sleep(0.3)
        # None reachable within timeout
        return primary, False
    
    @contextmanager
    def use_client(self, name: str):
        """
        Context manager for using an MCP client
        Follows the Strands SDK pattern: with client: ...
        
        Args:
            name: Client identifier
            
        Yields:
            MCPClient instance
            
        Example:
            with manager.use_client('debate_tools') as client:
                tools = client.list_tools_sync()
                agent = Agent(tools=tools)
        """
        if name not in self.clients:
            raise ValueError(f"MCP client '{name}' not registered")
        
        client = self.clients[name]
        
        try:
            with client:
                self.active_clients.append(name)
                logger.debug(f"[MCP] Activated client: {name}")
                yield client
        finally:
            if name in self.active_clients:
                self.active_clients.remove(name)
                logger.debug(f"[MCP] Deactivated client: {name}")
    
    def get_tools(self, name: str) -> List[Any]:
        """
        Get tools from an MCP client (must be used within context manager)
        
        Args:
            name: Client identifier
            
        Returns:
            List of MCPAgentTool instances
            
        Raises:
            ValueError: If client not registered or not active
            
        Example:
            with manager.use_client('debate_tools') as client:
                tools = manager.get_tools('debate_tools')
        """
        if name not in self.clients:
            raise ValueError(f"MCP client '{name}' not registered")
        
        if name not in self.active_clients:
            raise ValueError(
                f"Client '{name}' is not active. Use within context manager: "
                f"with manager.use_client('{name}') as client: ..."
            )
        
        client = self.clients[name]
        tools = client.list_tools_sync()
        
        logger.info(f"📋 Retrieved {len(tools)} tools from '{name}': "
                   f"{[tool.tool_name for tool in tools]}")
        
        return tools
    
    def call_tool(
        self,
        client_name: str,
        tool_name: str,
        arguments: Optional[Dict[str, Any]] = None,
        tool_use_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Call a tool directly on an MCP client
        
        Args:
            client_name: Client identifier
            tool_name: Name of the tool to call
            arguments: Tool arguments (optional)
            tool_use_id: Unique ID for this tool use (auto-generated if None)
            
        Returns:
            Tool result dictionary
            
        Example:
            result = manager.call_tool(
                'debate_tools',
                'topic_selector',
                {'category': 'technology'}
            )
        """
        if client_name not in self.clients:
            raise ValueError(f"MCP client '{client_name}' not registered")
        
        if client_name not in self.active_clients:
            raise ValueError(
                f"Client '{client_name}' is not active. Use within context manager"
            )
        
        import uuid
        if tool_use_id is None:
            tool_use_id = f"tool-{uuid.uuid4().hex[:8]}"
        
        client = self.clients[client_name]
        result = client.call_tool_sync(
            tool_use_id=tool_use_id,
            name=tool_name,
            arguments=arguments or {}
        )
        
        logger.debug(f"[MCP] Called tool '{tool_name}' on '{client_name}'")
        
        return result
    
    def list_all_clients(self) -> Dict[str, bool]:
        """
        List all registered clients and their active status
        
        Returns:
            Dictionary mapping client names to active status
        """
        return {
            name: name in self.active_clients
            for name in self.clients.keys()
        }
    
    def cleanup(self):
        """
        Cleanup all MCP clients
        Called during shutdown
        """
        for name in list(self.clients.keys()):
            logger.info(f"🧹 Cleaning up MCP client: {name}")
            # Clients auto-cleanup when exiting context manager
        
        self.clients.clear()
        self.active_clients.clear()
        logger.info("✅ All MCP clients cleaned up")


# Singleton instance for application-wide use
_mcp_tools_manager = None


def get_mcp_tools_manager() -> MCPToolsManager:
    """
    Get the singleton MCPToolsManager instance
    
    Returns:
        MCPToolsManager instance
    """
    global _mcp_tools_manager
    if _mcp_tools_manager is None:
        _mcp_tools_manager = MCPToolsManager()
    return _mcp_tools_manager


def initialize_mcp_clients(config: Optional[Dict[str, str]] = None):
    """
    Initialize MCP clients with default or custom configuration
    
    Args:
        config: Optional dict mapping client names to endpoints
                Default: {
                    'debate_tools': 'http://localhost:8000/mcp/',
                    'grammar_tools': 'http://localhost:8001/mcp/'
                }
    
    Example:
        # Use defaults
        initialize_mcp_clients()
        
        # Custom configuration
        initialize_mcp_clients({
            'debate_tools': 'http://mcp-server:8000/mcp/',
            'custom_tools': 'http://localhost:9000/mcp/'
        })
    """
    default_config = {
        'debate_tools': 'http://localhost:8000/mcp/',
        'grammar_tools': 'http://localhost:8001/mcp/'
    }
    
    config = config or default_config
    manager = get_mcp_tools_manager()
    
    for name, endpoint in config.items():
        manager.register_client(name, endpoint)
    
    logger.info(f"✅ Initialized {len(config)} MCP clients: {list(config.keys())}")
