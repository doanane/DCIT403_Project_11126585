from abc import ABC, abstractmethod
from src.core.message import Message, Performative


class Agent(ABC):
    def __init__(self, name: str, agent_system):
        self.name = name
        self.agent_system = agent_system
        self.inbox = []
        self.beliefs = {}

    def send(self, receiver: str, performative: Performative, content: dict) -> Message:
        msg = Message(
            sender=self.name,
            receiver=receiver,
            performative=performative,
            content=content,
        )
        self.agent_system.deliver(msg)
        return msg

    def perceive(self) -> list:
        percepts = list(self.inbox)
        self.inbox.clear()
        return percepts

    def deliberate(self, percepts: list) -> list:
        intentions = []
        for percept in percepts:
            plan = self.select_plan(percept)
            if plan is not None:
                intentions.append((plan, percept))
        return intentions

    def act(self, intentions: list):
        for plan, percept in intentions:
            plan(percept)

    def run_cycle(self, step: int):
        percepts = self.perceive()
        if percepts:
            intentions = self.deliberate(percepts)
            self.act(intentions)

    @abstractmethod
    def select_plan(self, percept):
        pass
