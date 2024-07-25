from crewai import Agent, Task, Crew, Process
from langchain_community.llms import Ollama
from crewai_tools import tool
import configparser

class ProductAnalyst:
        
    def load_config(self):
        self.config = configparser.ConfigParser()
        self.config.read('config/config.ini')
        return self.config

    def requirement_analysis_a(self):
        self.role = self.config['RequirementsAnalyser']['role']
        self.goal = self.config['RequirementsAnalyser']['goal']
        self.backstory = self.config['RequirementsAnalyser']['backstory']
        self.verbose = self.config['RequirementsAnalyser']['verbose']
        self.allow_delegation = self.config['RequirementsAnalyser']['allow_delegation']
        self.llm = Ollama(model=self.config['ProductAnalyst']['llm'])

        
    def user_stories_a(self):
        self.role = self.config['UserStoryWriter']['role']
        self.goal = self.config['UserStoryWriter']['goal']
        self.backstory = self.config['UserStoryWriter']['backstory']
        self.verbose = self.config['UserStoryWriter']['verbose']
        self.allow_delegation = self.config['UserStoryWriter']['allow_delegation']
        self.llm = Ollama(model=self.config['ProductAnalyst']['llm'])
        
    def requirement_analysis_t(self):
        self.description = self.config['RequirementsAnalyser']['task_description']
        self.output = self.config['RequirementsAnalyser']['task_output'] 
        
    def user_stories_t(self):
        self.description = self.config['UserStoryWriter']['task_description']
        self.output = self.config['UserStoryWriter']['task_output']
        
   
def create_agent(product_analyst,type):
    
    if type.lower()=="analyse":
        product_analyst.requirement_analysis_a()
    elif type.lower()=="write":
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
        llm = product_analyst.llm
    )
    return agent


def create_tasks(product_analyst,type,agent):
    if type.lower()=="analyse":
        product_analyst.requirement_analysis_t()
    elif type.lower()=="write":
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
    crew = Crew(agents=agents, tasks=tasks, verbose=True)
    return crew


def main():
    input_text=input("Please enter the text to analyze: ")
    product_analyst = ProductAnalyst()
    product_analyst.load_config()
    requirment_analyser = create_agent(product_analyst,"analyse")
    user_story_writer = create_agent(product_analyst,"write")
    task1 = create_tasks(product_analyst,"analyse",requirment_analyser)
    task1.description = product_analyst.config.get('TaskDescriptions', 'Analyse').format(input_text)
    task2 = create_tasks(product_analyst,"write",user_story_writer)
    task2.description = product_analyst.config.get('TaskDescriptions', 'Write')

    crew = create_crew([requirment_analyser,user_story_writer],[task1,task2])
    crew.kickoff()
    
if __name__ == "__main__":
    main()
    

