from langchain.chains.ConversationChain import ConversationChain
from langchain.memory import ConversationBufferMemory

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import AzureChatOpenAI

llm = AzureChatOpenAI(model="gpt-35-turbo", api_version="2023-05-15")


conversation = ConversationChain(
    llm=llm, 
    verbose=True,
    memory=ConversationBufferMemory()
)
