from crewai import Agent, Task, Crew, Process
from agency.core.llm import get_llm


class SalesDepartment:
    """Sales Department — 5 agents driving revenue."""

    def __init__(self):
        llm = get_llm("sonnet")

        self.lead_generator = Agent(
            role="Lead Generator",
            goal="Find and research high-quality prospects for TRoyAI E-Automation Agency",
            backstory=(
                "You are the Lead Generator at TRoyAI E-Automation Agency. "
                "You specialize in identifying companies and individuals who need "
                "AI automation services and building targeted prospect lists."
            ),
            llm=llm,
            verbose=False,
        )

        self.lead_qualifier = Agent(
            role="Lead Qualifier",
            goal="Score and rank leads based on fit, budget, and urgency",
            backstory=(
                "You are the Lead Qualifier at TRoyAI E-Automation Agency. "
                "You evaluate each prospect against qualification criteria and "
                "assign priority scores so the team focuses on the best opportunities."
            ),
            llm=llm,
            verbose=False,
        )

        self.proposal_writer = Agent(
            role="Proposal Writer",
            goal="Write compelling, customized business proposals that win deals",
            backstory=(
                "You are the Proposal Writer at TRoyAI E-Automation Agency. "
                "You craft tailored proposals that clearly articulate the value "
                "of AI automation and why TRoyAI is the right partner."
            ),
            llm=llm,
            verbose=False,
        )

        self.deal_closer = Agent(
            role="Deal Closer",
            goal="Convert qualified leads into signed clients through follow-up sequences",
            backstory=(
                "You are the Deal Closer at TRoyAI E-Automation Agency. "
                "You handle objections, create urgency, and design follow-up "
                "sequences that move prospects to a 'yes'."
            ),
            llm=llm,
            verbose=False,
        )

        self.crm_manager = Agent(
            role="CRM Manager",
            goal="Maintain accurate client records and relationship history",
            backstory=(
                "You are the CRM Manager at TRoyAI E-Automation Agency. "
                "You keep all client data organized, track touchpoints, and "
                "ensure no relationship is neglected."
            ),
            llm=llm,
            verbose=False,
        )

    def run_pipeline(self, brief: str) -> str:
        task_generate = Task(
            description=f"Generate 5 qualified prospect profiles for this target: {brief}",
            expected_output="5 prospect profiles with: company, contact, need, estimated budget.",
            agent=self.lead_generator,
        )

        task_qualify = Task(
            description="Score and rank the 5 prospects from the lead generator. Top prospect first.",
            expected_output="Ranked list with score (1-10) and one-line reason per prospect.",
            agent=self.lead_qualifier,
            context=[task_generate],
        )

        task_proposal = Task(
            description="Write a proposal outline for the top-ranked prospect.",
            expected_output="Proposal outline: Problem, Solution, Deliverables, Timeline, Investment.",
            agent=self.proposal_writer,
            context=[task_qualify],
        )

        crew = Crew(
            agents=[self.lead_generator, self.lead_qualifier, self.proposal_writer],
            tasks=[task_generate, task_qualify, task_proposal],
            process=Process.sequential,
            verbose=False,
        )

        return str(crew.kickoff())

    def write_followup_sequence(self, prospect: str, stage: str) -> str:
        task = Task(
            description=f"Write a 3-email follow-up sequence for: {prospect}. Stage: {stage}.",
            expected_output="3 emails with subject line and body. Tone: professional and direct.",
            agent=self.deal_closer,
        )

        crew = Crew(agents=[self.deal_closer], tasks=[task], process=Process.sequential, verbose=False)
        return str(crew.kickoff())
