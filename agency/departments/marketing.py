from crewai import Agent, Task, Crew, Process
from agency.core.llm import get_llm


class MarketingDepartment:
    """Marketing Department — 5 agents growing the TRoyAI brand."""

    def __init__(self):
        llm = get_llm("sonnet")

        self.content_creator = Agent(
            role="Content Creator",
            goal="Create compelling content that positions TRoyAI as the leader in AI automation",
            backstory=(
                "You are the Content Creator at TRoyAI E-Otomation Agency. "
                "You write blog posts, social media content, email campaigns, and "
                "scripts that educate prospects and build the TRoyAI brand."
            ),
            llm=llm,
            verbose=False,
        )

        self.seo_optimizer = Agent(
            role="SEO Optimizer",
            goal="Drive organic traffic to troyaiagent.com through search engine optimization",
            backstory=(
                "You are the SEO Optimizer at TRoyAI E-Otomation Agency. "
                "You identify high-value keywords, optimize content, and build "
                "a content strategy that ranks TRoyAI at the top of search results."
            ),
            llm=llm,
            verbose=False,
        )

        self.social_manager = Agent(
            role="Social Media Manager",
            goal="Build TRoyAI's presence across LinkedIn, Twitter/X, and Instagram",
            backstory=(
                "You are the Social Media Manager at TRoyAI E-Otomation Agency. "
                "You create platform-specific content, manage posting schedules, "
                "and grow engagement with the AI automation audience."
            ),
            llm=llm,
            verbose=False,
        )

        self.campaign_manager = Agent(
            role="Campaign Manager",
            goal="Plan and execute marketing campaigns that generate qualified leads",
            backstory=(
                "You are the Campaign Manager at TRoyAI E-Otomation Agency. "
                "You design multi-channel campaigns with clear objectives, "
                "budgets, and measurable KPIs."
            ),
            llm=llm,
            verbose=False,
        )

        self.analytics_reporter = Agent(
            role="Analytics Reporter",
            goal="Track all marketing metrics and translate data into actionable insights",
            backstory=(
                "You are the Analytics Reporter at TRoyAI E-Otomation Agency. "
                "You monitor website traffic, conversion rates, social engagement, "
                "and campaign performance, delivering weekly insight reports."
            ),
            llm=llm,
            verbose=False,
        )

    def run_campaign(self, brief: str) -> str:
        task_seo = Task(
            description=f"Research 10 target keywords for this campaign: {brief}",
            expected_output="10 keywords with monthly search volume and difficulty (low/med/high).",
            agent=self.seo_optimizer,
        )

        task_content = Task(
            description="Write a blog post outline and 3 social posts for the campaign.",
            expected_output="Blog outline (5 sections) + 3 social posts (LinkedIn, Twitter, Instagram).",
            agent=self.content_creator,
            context=[task_seo],
        )

        task_campaign = Task(
            description="Create a campaign plan for the next 30 days using the content above.",
            expected_output="30-day campaign calendar with weekly themes, channels, and KPIs.",
            agent=self.campaign_manager,
            context=[task_content],
        )

        crew = Crew(
            agents=[self.seo_optimizer, self.content_creator, self.campaign_manager],
            tasks=[task_seo, task_content, task_campaign],
            process=Process.sequential,
            verbose=False,
        )

        return str(crew.kickoff())

    def create_content(self, topic: str, format: str = "blog") -> str:
        task = Task(
            description=f"Write a {format} about: {topic}. Brand: TRoyAI E-Otomation Agency.",
            expected_output=f"Complete {format} ready to publish. Tone: confident, expert, direct.",
            agent=self.content_creator,
        )

        crew = Crew(agents=[self.content_creator], tasks=[task], process=Process.sequential, verbose=False)
        return str(crew.kickoff())
