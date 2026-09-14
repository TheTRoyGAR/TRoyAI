from crewai import Agent, Task, Crew, Process
from agency.core.llm import get_llm


class CTODepartment:
    """CTO Department — 5 agents running all technology for TRoyAI."""

    def __init__(self):
        llm_opus = get_llm("opus")
        llm = get_llm("sonnet")

        self.developer = Agent(
            role="Software Developer",
            goal="Write, maintain, and improve all code for TRoyAI's products and infrastructure",
            backstory=(
                "You are the Software Developer at TRoyAI E-Automation Agency. "
                "You build Python agents, Cloudflare Workers, and web dashboards. "
                "Stack: Python, CrewAI, Cloudflare Workers, D1, Pages."
            ),
            llm=llm_opus,
            verbose=False,
        )

        self.code_reviewer = Agent(
            role="Code Reviewer",
            goal="Ensure all code is clean, secure, and production-ready before deployment",
            backstory=(
                "You are the Code Reviewer at TRoyAI E-Automation Agency. "
                "You review every piece of code for bugs, security issues, "
                "and maintainability. Nothing ships without your approval."
            ),
            llm=llm,
            verbose=False,
        )

        self.architect = Agent(
            role="System Architect",
            goal="Design scalable, reliable system architecture for all TRoyAI products",
            backstory=(
                "You are the System Architect at TRoyAI E-Automation Agency. "
                "You make high-level technology decisions, design data models, "
                "and ensure the system can scale as TRoyAI grows."
            ),
            llm=llm_opus,
            verbose=False,
        )

        self.security_auditor = Agent(
            role="Security Auditor",
            goal="Identify and remediate security vulnerabilities across all TRoyAI systems",
            backstory=(
                "You are the Security Auditor at TRoyAI E-Automation Agency. "
                "You run security reviews, check for OWASP top 10 vulnerabilities, "
                "and ensure client data and API keys are always protected."
            ),
            llm=llm,
            verbose=False,
        )

        self.devops = Agent(
            role="DevOps Engineer",
            goal="Deploy, monitor, and maintain all TRoyAI infrastructure on Cloudflare",
            backstory=(
                "You are the DevOps Engineer at TRoyAI E-Automation Agency. "
                "You manage deployments to Cloudflare Workers, Pages, and D1. "
                "You ensure 99.9% uptime and fast deployments."
            ),
            llm=llm,
            verbose=False,
        )

    def run_task(self, brief: str) -> str:
        task_arch = Task(
            description=f"Design the technical approach for: {brief}",
            expected_output="Technical design: components, data flow, stack choices. Max 200 words.",
            agent=self.architect,
        )

        task_dev = Task(
            description="Implement the solution based on the architect's design.",
            expected_output="Complete working code with inline comments on non-obvious parts only.",
            agent=self.developer,
            context=[task_arch],
        )

        task_review = Task(
            description="Review the code for bugs, security issues, and quality.",
            expected_output="Review summary: APPROVED or NEEDS CHANGES, with specific issues listed.",
            agent=self.code_reviewer,
            context=[task_dev],
        )

        crew = Crew(
            agents=[self.architect, self.developer, self.code_reviewer],
            tasks=[task_arch, task_dev, task_review],
            process=Process.sequential,
            verbose=False,
        )

        return str(crew.kickoff())

    def security_audit(self, target: str) -> str:
        task = Task(
            description=f"Run a security audit on: {target}. Check OWASP top 10.",
            expected_output="Security report: CRITICAL, HIGH, MEDIUM, LOW findings with remediation steps.",
            agent=self.security_auditor,
        )

        crew = Crew(agents=[self.security_auditor], tasks=[task], process=Process.sequential, verbose=False)
        return str(crew.kickoff())

    def deploy(self, what: str) -> str:
        task = Task(
            description=f"Create deployment plan and commands for: {what}. Target: Cloudflare.",
            expected_output="Step-by-step deployment commands with verification steps.",
            agent=self.devops,
        )

        crew = Crew(agents=[self.devops], tasks=[task], process=Process.sequential, verbose=False)
        return str(crew.kickoff())
