from agency.departments.operations import OperationsDepartment
from agency.departments.sales import SalesDepartment
from agency.departments.marketing import MarketingDepartment
from agency.departments.finance import FinanceDepartment
from agency.departments.cto import CTODepartment


class TRoyAIAgency:
    """TRoyAI E-Otomation Agency — 5 departments, 25 agents, zero employees."""

    CEO = "I. Ertan Govdeli"
    NAME = "TRoyAI E-Otomation Agency"

    def __init__(self):
        self.operations = OperationsDepartment()
        self.sales = SalesDepartment()
        self.marketing = MarketingDepartment()
        self.finance = FinanceDepartment()
        self.cto = CTODepartment()

    def run_daily_briefing(self, context: str = "") -> str:
        return self.operations.daily_briefing(context)

    def run_sales_pipeline(self, brief: str) -> str:
        return self.sales.run_pipeline(brief)

    def run_marketing_campaign(self, brief: str) -> str:
        return self.marketing.run_campaign(brief)

    def run_finance_report(self, period: str = "monthly") -> str:
        return self.finance.generate_report(period)

    def run_cto_task(self, brief: str) -> str:
        return self.cto.run_task(brief)

    def status(self) -> dict:
        return {
            "agency": self.NAME,
            "ceo": self.CEO,
            "departments": 5,
            "agents_per_department": 5,
            "total_agents": 25,
            "beta_agents": ["delivery_agent", "qa_agent"],
            "status": "online",
        }
