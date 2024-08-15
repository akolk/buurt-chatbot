from langchain_community.llms.OpenAI import OpenAI
from langchain.chains.ConversationChain import ConversationChain
from langchain.memory import ConversationBufferMemory

chat = OpenAI(temperature=0)

conversation = ConversationChain(
    llm=chat, 
    verbose=True,
    memory=ConversationBufferMemory()
)
