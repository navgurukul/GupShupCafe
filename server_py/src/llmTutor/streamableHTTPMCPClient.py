from mcp.client.streamable_http import streamablehttp_client
from geminiAgent import GeminiAgent
from strands.tools.mcp.mcp_client import MCPClient


def create_streamable_http_transport():
    return streamablehttp_client("http://localhost:8000/mcp/")


streamable_http_mcp_client = MCPClient(create_streamable_http_transport)

# Use the MCP server in a context manager
with streamable_http_mcp_client:
		# Get the tools from the MCP server
		tools = streamable_http_mcp_client.list_tools_sync()

		# Debugging line to check available tools
		print(
				f"Available tools from MCP server: {[tool.tool_name for tool in tools]}")
		# Create an agent with the MCP tools
		agent = GeminiAgent(tools=tools)

		# Let the agent handle the tool selection and parameter extraction
		response = agent("What is 125 plus 375?")
		response = agent("If I have 1000 and spend 246, how much do I have left?")
		response = agent("What is 24 multiplied by 7 divided by 3?")

# Explicit tool call example
with streamable_http_mcp_client:
	result = streamable_http_mcp_client.call_tool_sync(
			tool_use_id="tool-add",
			name="add",
			arguments={"x": 125, "y": 375}
	)

	agent = GeminiAgent(tools=tools)
	print(agent.add(x=125, y=375))  # Debugging line to check model parameters
	
	# Process the result
	print(f"Calculation result: {result['content'][0]['text']}")
