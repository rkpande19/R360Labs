

from crewai import Agent, Task, Crew, Process
from langchain_community.llms import Ollama
from crewai_tools import tool
import configparser
import os
from docx import Document
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY
import re
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
    
    def ux_ui_requirements_a(self):
        """
        Performs requirement analysis for the UX/UI designer role.
        Sets the role, goal, backstory, verbose, allow_delegation, and llm attributes.
        """
        self.role = self.config['UXUIRequirementsGenerator']['role']
        self.goal = self.config['UXUIRequirementsGenerator']['goal']
        self.backstory = self.config['UXUIRequirementsGenerator']['backstory']
        self.verbose = self.config['UXUIRequirementsGenerator']['verbose']
        self.allow_delegation = self.config['UXUIRequirementsGenerator']['allow_delegation']
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
    
    def ux_ui_requirements_t(self):
        """
        Sets the task description and output for UX/UI requirements generation.
        """
        self.description = self.config['UXUIRequirementsGenerator']['task_description']
        self.output = self.config['UXUIRequirementsGenerator']['task_output']


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
    elif type.lower() == "ux_ui":
        product_analyst.ux_ui_requirements_a()
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
    elif type.lower() == "ux_ui":
        product_analyst.ux_ui_requirements_t()
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

def read_docx(file_path):
    doc = Document(file_path)
    return " ".join([paragraph.text for paragraph in doc.paragraphs])

def markdown_to_html(text):
    bold = re.compile(r'\*\*(.*?)\*\*')
    
    def repl(match):
        return '<b>' + match.group(1) + '</b>'
    return bold.sub(repl, text)

def write_to_pdf(file_name, text):
    directory = os.path.dirname(file_name)
    if not os.path.exists(directory):
        print("The directory doesn't exist. Please enter a valid directory.")
        return False

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY))
    text = markdown_to_html(text)
    doc = SimpleDocTemplate(file_name)
    story = [Paragraph(line, styles["Justify"]) for line in text.split('\n') if line]
    doc.build(story)
    return True


def main():
    """
    The main function of the program.
    """
    product_analyst = ProductAnalyst()
    product_analyst.load_config()
    requirement_analyser = create_agent(product_analyst, "analyse")
    user_story_writer = create_agent(product_analyst, "write")
    ux_ui_requirements_generator = create_agent(product_analyst, "ux_ui")
    
    is_analysed = False
    is_user_stories_written = False
    
    while True:
        print ('\n I am bot crafted by a human to assist you in your product analysis journey. I can help you with the following tasks:')
        print("\n1. Analyse requirements")
        print("\n2. Write user stories")
        print("\n3. Generate UX/UI requirements")
        print("\n4. Exit")
        choice = input("\nPlease enter your choice: ")
        
        
        if choice == "1" or not is_analysed:
            input_text = input("Please enter the text to analyze or a file path ")
            if os.path.isfile(input_text):
                file_extension = os.path.splitext(input_text)[1]
                if file_extension == ".txt":
                    with open(input_text, "r") as file:
                        input_text = file.read()
                elif file_extension in ['.doc', '.docx']:
                    input_text = read_docx(input_text)
                else:
                    print("Invalid file format. Please enter a text file")
                    continue
            task1 = create_tasks(product_analyst, "analyse", requirement_analyser)
            task1.description = product_analyst.config.get('TaskDescriptions', 'Analyse').format(input_text)
            crew = create_crew([requirement_analyser], [task1])
            result = crew.kickoff()
            while True:
                file_name = input('Please enter the file name and location to save the output in the format <location>/<filename>.pdf: ')
                if write_to_pdf(file_name, result):
                    break
            is_analysed = True
        elif choice == "2" or not is_user_stories_written:
            task2 = create_tasks(product_analyst, "write", user_story_writer)
            task2.description = product_analyst.config.get('TaskDescriptions', 'Write')
            crew = create_crew([user_story_writer], [task2])
            result = crew.kickoff()
            file_name = input('Please enter the file name and location to save the output in the format <location>/<filename>.pdf: ')
            while True:
                file_name = input('Please enter the file name and location to save the output in the format <location>/<filename>.pdf: ')
                if write_to_pdf(file_name, result):
                    break
            is_user_stories_written = True
        elif choice == "3":
            task3 = create_tasks(product_analyst, "ux_ui", ux_ui_requirements_generator)
            task3.description = product_analyst.config.get('TaskDescriptions', 'UXUI')
            crew = create_crew([ux_ui_requirements_generator], [task3])
            result = crew.kickoff()
            while True:
                file_name = input('Please enter the file name and location to save the output in the format <location>/<filename>.pdf: ')
                if write_to_pdf(file_name, result):
                    break
            write_to_pdf(file_name, result)
        elif choice == "4":
            break
        else:
            print("Invalid choice. Please try again")
            

if __name__ == "__main__":
    main()
    

