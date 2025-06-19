from services.agent_base import AgentBase


class AgentRunner:
    def __init__(self, agent):
        self.agents: list[AgentBase] = []

    def run(self, task: str) -> str:
        for agent in self.agents:
            res = agent.process(task)
            task = res
