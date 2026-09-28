from crewai import Agent, Task, Crew, Process
from agency.core.llm import get_llm
from agency.core.memory import shared_memory, remember, recall_context
from agency.tools import search, scrape


class MarketingDepartment:
    """Marketing Department — 5 agents growing the TRoyAI brand.

    Tools added 2026-09-28 — previously had none (same gap CTO and Sales
    had until this same day). Without real search, any "trend" or
    "hashtag" this department produced was invented from the model's own
    training data, not grounded in what's actually current.
    """

    def __init__(self):
        llm = get_llm("sonnet")

        self.content_creator = Agent(
            role="Content Creator",
            goal="Create compelling, REAL content that positions TRoyAI as the leader in AI automation — never invented facts, trends, or hashtags.",
            backstory=(
                "You are the Content Creator at TRoyAI E-Automation Agency. "
                "You write blog posts, social media content, email campaigns, and "
                "scripts that educate prospects and build the TRoyAI brand.\n\n"
                "Hard rule: any trend, statistic, or hashtag you use must be something you "
                "actually found via search — real, currently-used hashtags and real, current "
                "industry trends, never plausible-sounding invented ones."
            ),
            llm=llm,
            tools=[search, scrape],
            verbose=False,
        )

        self.seo_optimizer = Agent(
            role="SEO Optimizer",
            goal="Drive organic traffic to troyaiagent.com through search engine optimization, using real search data",
            backstory=(
                "You are the SEO Optimizer at TRoyAI E-Automation Agency. "
                "You identify high-value keywords, optimize content, and build "
                "a content strategy that ranks TRoyAI at the top of search results.\n\n"
                "Hard rule: keyword volume/difficulty must come from what you actually find "
                "via search — never invent a plausible-sounding search volume number."
            ),
            llm=llm,
            tools=[search],
            verbose=False,
        )

        self.social_manager = Agent(
            role="Social Media Manager",
            goal="Build TRoyAI's presence across LinkedIn, Twitter/X, and Instagram",
            backstory=(
                "You are the Social Media Manager at TRoyAI E-Automation Agency. "
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
                "You are the Campaign Manager at TRoyAI E-Automation Agency. "
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
                "You are the Analytics Reporter at TRoyAI E-Automation Agency. "
                "You monitor website traffic, conversion rates, social engagement, "
                "and campaign performance, delivering weekly insight reports."
            ),
            llm=llm,
            verbose=False,
        )

    def run_campaign(self, brief: str) -> str:
        task_seo = Task(
            description=(
                f"{recall_context(brief)}"
                f"Search for 10 real target keywords relevant to this campaign: {brief}\n\n"
                "Use real search to find what people actually search for in this space — "
                "never invent a keyword, search volume, or difficulty rating."
            ),
            expected_output="10 real keywords found via search, with what evidence you have of demand/difficulty — flag clearly if exact volume isn't available rather than inventing a number.",
            agent=self.seo_optimizer,
        )

        task_content = Task(
            description=(
                "Write a blog post outline and 3 social posts for the campaign, using real, "
                "currently-used hashtags you find via search for this space — never invented ones."
            ),
            expected_output="Blog outline (5 sections) + 3 social posts (LinkedIn, Twitter, Instagram), each with real hashtags actually found via search, sourced.",
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
            memory=shared_memory,
            verbose=False,
        )

        crew_output = crew.kickoff()
        result = (
            f"## Keywords\n\n{crew_output.tasks_output[0].raw}\n\n---\n\n"
            f"## Content\n\n{crew_output.tasks_output[1].raw}\n\n---\n\n"
            f"## 30-Day Plan\n\n{crew_output.tasks_output[2].raw}"
        )
        remember(f"Marketing run_campaign for '{brief}':\n{result}", scope="/dept/marketing/run_campaign", categories=["marketing", "campaign"])
        return result

    def create_content(self, topic: str, format: str = "blog") -> str:
        task = Task(
            description=(
                f"{recall_context(topic)}"
                f"Write a {format} about: {topic}. Brand: TRoyAI E-Automation Agency.\n\n"
                "If this format uses hashtags or references current trends, search for real, "
                "currently-used ones — never invent a hashtag or trend."
            ),
            expected_output=f"Complete {format} ready to publish. Tone: confident, expert, direct. Any hashtags/trends cited must be real, found via search.",
            agent=self.content_creator,
        )

        crew = Crew(agents=[self.content_creator], tasks=[task], process=Process.sequential, memory=shared_memory, verbose=False)
        result = str(crew.kickoff())
        remember(f"Marketing create_content ({format}) for '{topic}':\n{result}", scope="/dept/marketing/create_content", categories=["marketing", "content"])
        return result
