

from crewai import Agent, Task, Crew, Process
from langchain_community.llms import Ollama
from crewai_tools import tool
import configparser

class ProductAnalyst:
    """
    A class representing a product analyst.

    Attributes:
    - config: A ConfigParser object to store configuration settings.

    Methods:
    - load_config: Loads the configuration from the config.ini file.
    - requirement_analysis_a: Performs requirement analysis for the analyst role.
    - user_stories_a: Generates user stories for the writer role.
    - requirement_analysis_t: Sets the task description and output for requirement analysis.
    - user_stories_t: Sets the task description and output for user story writing.
    """

    def load_config(self):
        """
        Loads the configuration from the config.ini file.

        Returns:
        - config: A ConfigParser object containing the loaded configuration settings.
        """
        self.config = configparser.ConfigParser()
        self.config.read('config/config.ini')
        return self.config

    def requirement_analysis_a(self):
        """
        Performs requirement analysis for the analyst role.
        Sets the role, goal, backstory, verbose, allow_delegation, and llm attributes.
        """
        self.role = self.config['RequirementsAnalyser']['role']
        self.goal = self.config['RequirementsAnalyser']['goal']
        self.backstory = self.config['RequirementsAnalyser']['backstory']
        self.verbose = self.config['RequirementsAnalyser']['verbose']
        self.allow_delegation = self.config['RequirementsAnalyser']['allow_delegation']
        self.llm = Ollama(model=self.config['ProductAnalyst']['llm'])

    def user_stories_a(self):
        """
        Generates user stories for the writer role.
        Sets the role, goal, backstory, verbose, allow_delegation, and llm attributes.
        """
        self.role = self.config['UserStoryWriter']['role']
        self.goal = self.config['UserStoryWriter']['goal']
        self.backstory = self.config['UserStoryWriter']['backstory']
        self.verbose = self.config['UserStoryWriter']['verbose']
        self.allow_delegation = self.config['UserStoryWriter']['allow_delegation']
        self.llm = Ollama(model=self.config['ProductAnalyst']['llm'])

    def requirement_analysis_t(self):
        """
        Sets the task description and output for requirement analysis.
        """
        self.description = self.config['RequirementsAnalyser']['task_description']
        self.output = self.config['RequirementsAnalyser']['task_output']

    def user_stories_t(self):
        """
        Sets the task description and output for user story writing.
        """
        self.description = self.config['UserStoryWriter']['task_description']
        self.output = self.config['UserStoryWriter']['task_output']


def create_agent(product_analyst, type):
    """
    Creates an agent based on the given type.

    Parameters:
    - product_analyst: A ProductAnalyst object.
    - type: A string indicating the type of agent to create.

    Returns:
    - agent: An Agent object.
    """
    if type.lower() == "analyse":
        product_analyst.requirement_analysis_a()
    elif type.lower() == "write":
        product_analyst.user_stories_a()
    else:
        print("Invalid type")
        return

    agent = Agent(
        role=product_analyst.role,
        goal=product_analyst.goal,
        backstory=product_analyst.backstory,
        verbose=True,
        allow_delegation=product_analyst.allow_delegation,
        llm=product_analyst.llm
    )
    return agent


def create_tasks(product_analyst, type, agent):
    """
    Creates a task based on the given type.

    Parameters:
    - product_analyst: A ProductAnalyst object.
    - type: A string indicating the type of task to create.
    - agent: An Agent object.

    Returns:
    - task: A Task object.
    """
    if type.lower() == "analyse":
        product_analyst.requirement_analysis_t()
    elif type.lower() == "write":
        product_analyst.user_stories_t()
    else:
        print("Invalid type")
        return

    task = Task(
        description=product_analyst.description,
        agent=agent,
        expected_output=product_analyst.output
    )

    return task


def create_crew(agents, tasks):
    """
    Creates a crew with the given agents and tasks.

    Parameters:
    - agents: A list of Agent objects.
    - tasks: A list of Task objects.

    Returns:
    - crew: A Crew object.
    """
    crew = Crew(agents=agents, tasks=tasks, verbose=True)
    return crew


def main():
    """
    The main function of the program.
    """
    input_text = input("Please enter the text to analyze: ")
    product_analyst = ProductAnalyst()
    product_analyst.load_config()
    requirement_analyser = create_agent(product_analyst, "analyse")
    user_story_writer = create_agent(product_analyst, "write")
    task1 = create_tasks(product_analyst, "analyse", requirement_analyser)
    task1.description = product_analyst.config.get('TaskDescriptions', 'Analyse').format(input_text)
    task2 = create_tasks(product_analyst, "write", user_story_writer)
    task2.description = product_analyst.config.get('TaskDescriptions', 'Write')

    crew = create_crew([requirement_analyser, user_story_writer], [task1, task2])
    crew.kickoff()


if __name__ == "__main__":
    main()
    

