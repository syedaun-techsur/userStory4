from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
import subprocess
import os
# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class AgenticTesting():
    """AgenticTesting crew for Gherkin feature file generation"""

    agents: List[BaseAgent]
    tasks: List[Task]

    @agent
    def gherkin_generator(self) -> Agent:
        return Agent(
            config=self.agents_config['gherkin_generator'],
            verbose=True
        )

    @task
    def gherkin_generation(self) -> Task:
        return Task(
            config=self.tasks_config['gherkin_generation'],
        )

    @agent
    def step_definition_generator(self) -> Agent:
        return Agent(
            config=self.agents_config['step_definition_generator'],
            verbose=True
        )

    @task
    def step_definition_generation(self) -> Task:
        return Task(
            config=self.tasks_config['step_definition_generation'],
        )

    @agent
    def selenium_test_generator(self) -> Agent:
        return Agent(
            config=self.agents_config['selenium_test_generator'],
            verbose=True
        )

    @task
    def selenium_test_generation(self) -> Task:
        return Task(
            config=self.tasks_config['selenium_test_generation'],
        )

    @agent
    def environment_generator(self) -> Agent:
        return Agent(
            config=self.agents_config['environment_generator'],
            verbose=True
        )

    @task
    def enhance_environment_for_test(self) -> Task:
        return Task(
            config=self.tasks_config['enhance_environment_for_test'],
        )

    @crew
    def crew(self) -> Crew:
        """Creates the AgenticTesting crew for Gherkin and step definition generation"""
        return Crew(
            agents=[
                self.gherkin_generator(),
                self.step_definition_generator()
            ],
            tasks=[
                self.gherkin_generation(),
                self.step_definition_generation()
            ],
            process=Process.sequential,
            verbose=True,
        )
