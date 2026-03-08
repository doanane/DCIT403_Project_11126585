from src.core.message import Message


class AgentSystem:
    def __init__(self):
        self._agents = {}

    def register(self, agent):
        self._agents[agent.name] = agent

    def deliver(self, message: Message):
        agent = self._agents.get(message.receiver)
        if agent:
            agent.inbox.append(message)
        else:
            print(f"[AgentSystem] WARNING: No agent named '{message.receiver}' found.")

    def get_agent(self, name):
        return self._agents.get(name)

    def get_all_agents(self):
        return list(self._agents.values())
