# !/bin/bash

# Install/update uvswitcher and Python 3.12
cd ~
curl -LsSf https://astral.sh/uv/install.sh | sh
if [ "$SHELL" = "/bin/bash" ]; then
  echo 'eval "$(uv generate-shell-completion bash)"' >> ~/.bashrc
  echo 'eval "$(uvx --generate-shell-completion bash)"' >> ~/.bashrc
fi
uv --version
uv self update
uv python install 3.12
uv python update-shell

# Create a requirements.txt file with the necessary dependencies
cd "Documents/Courses/AWS Strands Workshop"
pwd
cat << EOF > requirements.txt # Manually create if not created by script
aws-opentelemetry-distro>=0.10.0
bedrock-agentcore
bedrock-agentcore-starter-toolkit
boto3
litellm
mcp[cli]
nova-act
opensearch-py
pandas
retrying
strands-agents 
strands-agents-tools[mem0_memory]
streamlit
tqdm
uv
google-genai
dotenv
EOF

uv venv
source ~/.venv/bin/activate
uv pip install -r requirements.txt --target .venv/lib/python3.12/site-packages

# sudo apt install -y jq

# Clone the strands-agents/sdk-python repository
git clone https://github.com/strands-agents/sdk-python.git .venv/lib/python3.12/site-packages/strands_agents

git clone https://github.com/strands-agents/docs.git .venv/lib/python3.12/site-packages/strands_agents_docs

cd .venv/lib/python3.12/site-packages/strands_agents
git checkout eef11cc890266b48a22dcc3e555880926d52ec88

cd .venv/lib/python3.12/site-packages/strands_agents_docs
git checkout 8237e89c8bdb6d0b73fc7d60b13cfcff876793d2