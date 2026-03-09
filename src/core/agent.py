from collections import deque


class Agent:
    def __init__(self, name, agent_system, log_callback=None):
        self.name = name
        self.agent_system = agent_system
        self.inbox = deque()
        self.log_callback = log_callback
        self.current_step = 0

    def receive(self, message):
        self.inbox.append(message)

    def send(self, message):
        self.agent_system.deliver(message)

    def log(self, text):
        if self.log_callback:
            self.log_callback(f"[{self.name}] {text}")

    def run_cycle(self, current_step):
        self.current_step = current_step
        while self.inbox:
            msg = self.inbox.popleft()
            self.handle_message(msg)
        self.proactive_step()

    def handle_message(self, message):
        pass

    def proactive_step(self):
        pass
