from crewai import Agent, Task, Crew, Process
from agency.core.llm import get_llm


class FinanceDepartment:
    """Finance Department — 5 agents managing TRoyAI's financial health."""

    def __init__(self):
        llm = get_llm("sonnet")

        self.bookkeeper = Agent(
            role="Bookkeeper",
            goal="Record and categorize all financial transactions accurately",
            backstory=(
                "You are the Bookkeeper at TRoyAI E-Otomation Agency. "
                "You maintain clean financial records, categorize income and expenses, "
                "and ensure the books are always up to date."
            ),
            llm=llm,
            verbose=False,
        )

        self.budget_planner = Agent(
            role="Budget Planner",
            goal="Create and maintain monthly and quarterly budgets for TRoyAI",
            backstory=(
                "You are the Budget Planner at TRoyAI E-Otomation Agency. "
                "You analyze spending patterns, forecast revenue, and build "
                "budgets that keep TRoyAI profitable and growing."
            ),
            llm=llm,
            verbose=False,
        )

        self.invoice_manager = Agent(
            role="Invoice Manager",
            goal="Create, send, and track all client invoices and payments",
            backstory=(
                "You are the Invoice Manager at TRoyAI E-Otomation Agency. "
                "You manage the entire invoicing lifecycle — from creating "
                "professional invoices to following up on overdue payments."
            ),
            llm=llm,
            verbose=False,
        )

        self.financial_reporter = Agent(
            role="Financial Reporter",
            goal="Generate clear P&L, cash flow, and financial health reports",
            backstory=(
                "You are the Financial Reporter at TRoyAI E-Otomation Agency. "
                "You translate raw financial data into clear executive reports "
                "that help CEO Ertan Govdeli make informed decisions."
            ),
            llm=llm,
            verbose=False,
        )

        self.cost_optimizer = Agent(
            role="Cost Optimizer",
            goal="Identify cost-saving opportunities without compromising quality",
            backstory=(
                "You are the Cost Optimizer at TRoyAI E-Otomation Agency. "
                "You constantly look for ways to reduce expenses, negotiate better "
                "rates, and improve the agency's margins."
            ),
            llm=llm,
            verbose=False,
        )

    def generate_report(self, period: str = "monthly") -> str:
        task_report = Task(
            description=(
                f"Generate a {period} financial report for TRoyAI E-Otomation Agency. "
                f"Include: revenue summary, expense categories, profit margin, cash flow."
            ),
            expected_output=(
                "Financial report with sections: REVENUE, EXPENSES, PROFIT MARGIN, "
                "CASH FLOW, KEY INSIGHTS. Use placeholder numbers if no real data provided."
            ),
            agent=self.financial_reporter,
        )

        task_optimize = Task(
            description="Based on the financial report, identify 3 cost-saving opportunities.",
            expected_output="3 specific cost-saving actions with estimated savings per month.",
            agent=self.cost_optimizer,
            context=[task_report],
        )

        crew = Crew(
            agents=[self.financial_reporter, self.cost_optimizer],
            tasks=[task_report, task_optimize],
            process=Process.sequential,
            verbose=False,
        )

        return str(crew.kickoff())

    def create_invoice(self, client: str, services: str, amount: str) -> str:
        task = Task(
            description=(
                f"Create a professional invoice for client: {client}. "
                f"Services: {services}. Amount: {amount}. "
                f"From: TRoyAI E-Otomation Agency, CEO: I. Ertan Govdeli, "
                f"Email: troyaiagent@gmail.com, Domain: troyaiagent.com"
            ),
            expected_output="Complete invoice text ready to send, including all line items and payment terms.",
            agent=self.invoice_manager,
        )

        crew = Crew(agents=[self.invoice_manager], tasks=[task], process=Process.sequential, verbose=False)
        return str(crew.kickoff())
