from langchain_openai import ChatOpenAI
from langchain import hub
from langchain.agents import create_openai_functions_agent
from langchain.agents import AgentExecutor

# List of tools to use
tools = [retriever_tool, search]

# Retrieve template from LangChain Hub
template = hub.pull("hwchase17/openai-functions-agent")

# Create the agent
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
agent = create_openai_functions_agent(llm, tools, template)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
