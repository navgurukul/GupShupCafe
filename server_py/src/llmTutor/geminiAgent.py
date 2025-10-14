import os
from strands import Agent
from strands_agents.src.strands.models.gemini import GeminiModel # Import the specific GeminiModel provider
from strands_tools import calculator # Optional: Import a built-in tool
from dotenv import load_dotenv


class GeminiAgent(Agent):

		def __init__(self, system_prompt=None, tools=None):
			# 1. Configuration (Make sure to set the API Key)
			# It's best practice to set your API key as an environment variable
			# export GEMINI_API_KEY="YOUR_API_KEY"
			load_dotenv()
			_api_key = os.getenv("GEMINI_API_KEY")

			if not _api_key:
					raise ValueError("GEMINI_API_KEY environment variable not set.")

			# 2. Initialize the Gemini Model
			# You can specify the model_id (e.g., 'gemini-pro')
			self.gemini_model = GeminiModel(
					model_id="gemini-2.5-flash", # Using a common Gemini model ID
					params={
							"temperature": 0.7,
					}
					# streaming=True, # You can enable streaming if desired
			)

			# 3. Create the Strands Agent
			# The agent is instantiated with the model and an optional list of tools
			super().__init__(model=self.gemini_model, tools=tools, system_prompt=system_prompt)

if __name__ == "__main__":
			agent = GeminiAgent(tools=[calculator])

			# 4. Run the Agent
			user_prompt = "What is the result of 123 multiplied by 45 and then tell me a fun fact about the number 5?"

			print(f"User Prompt: {user_prompt}\n")
			print("Agent Response: ")
			response = agent(user_prompt)

