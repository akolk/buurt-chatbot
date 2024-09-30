from langchain.agents import AgentType, initialize_agent, load_tools
# Import Azure OpenAI
from langchain_openai import AzureOpenAI
import services.config


# The API version you want to use: set this to `2023-12-01-preview` for the released version.
#export OPENAI_API_VERSION=2023-12-01-preview
# The base URL for your Azure OpenAI resource.  You can find this in the Azure portal under your Azure OpenAI resource.
#export AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com
# The API key for your Azure OpenAI resource.  You can find this in the Azure portal under your Azure OpenAI resource.
#export AZURE_OPENAI_API_KEY=<your Azure OpenAI API key>
llm = AzureOpenAI(temperature=0)

tools = load_tools(
    ["graphql"],
    graphql_endpoint=services.config.graphql_endpoint,
)

agent = initialize_agent(
    tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True
)
agent.run()
