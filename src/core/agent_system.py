class AgentSystem:
    def __init__(self):
        self.agents = {}

    def register(self, agent):
        self.agents[agent.name] = agent

    def deliver(self, message):
        recipient = self.agents.get(message.recipient)
        if recipient:
            recipient.receive(message)
