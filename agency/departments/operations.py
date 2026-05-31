from crewai import Agent, Task, Crew, Process
from agency.core.llm import get_llm


class OperationsDepartment:
    """Operations Department — CEO's Command Centre. 5 agents."""

    def __init__(self):
        llm = get_llm("sonnet")

        self.executive_assistant = Agent(
            role="Executive Assistant",
            goal="Support CEO Ertan Govdeli with daily priorities, schedule, and decisions",
            backstory=(
                "You are the Executive Assistant of TRoyAI E-Otomation Agency, "
                "working directly for CEO I. Ertan Govdeli. You distill complex "
                "information into clear action items and ensure the CEO is always "
                "informed and prepared."
            ),
            llm=llm,
            verbose=False,
        )

        self.project_manager = Agent(
            role="Project Manager",
            goal="Track all cross-department projects, milestones, and deadlines",
            backstory=(
                "You are the Project Manager of TRoyAI E-Otomation Agency. "
                "You coordinate between all 5 departments, track project status, "
                "and ensure nothing falls through the cracks."
            ),
            llm=llm,
            verbose=False,
        )

        self.resource_manager = Agent(
            role="Resource Manager",
            goal="Assign tasks to the right agents and monitor workloads across the agency",
            backstory=(
                "You are the Resource Manager of TRoyAI E-Otomation Agency. "
                "You understand each agent's strengths and current load, "
                "ensuring optimal task distribution across all departments."
            ),
            llm=llm,
            verbose=False,
        )

        self.report_generator = Agent(
            role="Report Generator",
            goal="Create clear executive reports and KPI summaries for the CEO",
            backstory=(
                "You are the Report Generator of TRoyAI E-Otomation Agency. "
                "You compile data from all departments into concise, actionable "
                "reports that the CEO can act on immediately."
            ),
            llm=llm,
            verbose=False,
        )

        self.process_optimizer = Agent(
            role="Process Optimizer",
            goal="Identify bottlenecks and continuously improve agency workflows",
            backstory=(
                "You are the Process Optimizer of TRoyAI E-Otomation Agency. "
                "You analyze how agents work, find inefficiencies, and propose "
                "concrete improvements using the Karpathy Loop: act, measure, improve."
            ),
            llm=llm,
            verbose=False,
        )

    def daily_briefing(self, context: str = "") -> str:
        task_brief = Task(
            description=(
                f"Prepare the daily CEO briefing for I. Ertan Govdeli at TRoyAI E-Otomation Agency. "
                f"Include: top 3 priorities for today, agency status, any blockers, quick wins. "
                f"Additional context: {context or 'Standard daily briefing.'}"
            ),
            expected_output=(
                "A structured briefing with sections: PRIORITIES, AGENCY STATUS, "
                "BLOCKERS, QUICK WINS. Bullet points only. Max 300 words."
            ),
            agent=self.executive_assistant,
        )

        task_report = Task(
            description="Summarize the current status of all active projects across departments.",
            expected_output="A 5-bullet project status summary, one bullet per department.",
            agent=self.project_manager,
        )

        crew = Crew(
            agents=[self.executive_assistant, self.project_manager],
            tasks=[task_brief, task_report],
            process=Process.sequential,
            verbose=False,
        )

        result = crew.kickoff()
        return str(result)

    def optimize_process(self, process_description: str) -> str:
        task = Task(
            description=(
                f"Analyze this process and suggest 3 concrete improvements: {process_description}"
            ),
            expected_output="3 numbered improvements with expected impact for each.",
            agent=self.process_optimizer,
        )

        crew = Crew(
            agents=[self.process_optimizer],
            tasks=[task],
            process=Process.sequential,
            verbose=False,
        )

        return str(crew.kickoff())
