"""
Tasklet Agent Browser Integration
Connects BrowserAutomation to Tasklet's browser tool for autonomous agent execution
"""

from typing import Optional, Dict, Any
from modules.browser_automation import BrowserAutomation, CaseInvestigationBrowser


class TaskletBrowserAgent:
    """Integrates BrowserAutomation with Tasklet's native browser tool"""

    def __init__(self):
        self.browser = BrowserAutomation()
        self.case_browser = CaseInvestigationBrowser()

    async def autonomous_case_search(self, url: str, case_number: str) -> Dict:
        """Autonomous case search and extraction"""
        await self.browser.navigate(url)
        await self.browser.fill_form({"case": case_number})
        await self.browser.click("button[type='submit']")
        return await self.browser.scrape("div.case-results")

    async def extract_case_details(self, case_url: str) -> Dict:
        """Extract complete case details from URL"""
        await self.browser.navigate(case_url)
        return {
            "title": await self.browser.scrape("h1.case-title"),
            "parties": await self.browser.scrape("div.parties"),
            "docket": await self.browser.scrape("table.docket"),
            "documents": await self.browser.scrape("div.documents")
        }

    async def autonomous_paginated_scrape(self, url: str, content_selector: str, next_button: str) -> Dict:
        """Autonomous multi-page scraping"""
        all_data = []
        await self.browser.navigate(url)
        
        while True:
            data = await self.browser.scrape(content_selector)
            all_data.append(data)
            
            try:
                await self.browser.click(next_button)
                await asyncio.sleep(1)
            except:
                break
        
        return {"pages": len(all_data), "total_items": all_data}

    async def autonomous_form_submission(self, url: str, form_data: Dict, submit_button: str) -> Dict:
        """Autonomous form filling and submission"""
        await self.browser.navigate(url)
        await self.browser.fill_form(form_data)
        await self.browser.click(submit_button)
        return {"status": "submitted", "confirmation": await self.browser.screenshot()}

    async def fill_and_submit(self, url: str, fields: Dict[str, str], button: str) -> Dict:
        """Simple form fill and submit"""
        await self.browser.navigate(url)
        await self.browser.fill_form(fields)
        await self.browser.click(button)
        return {"submitted": True}


class CaseInvestigationAgent:
    """Autonomous case investigation agent combining browser + connectors"""

    def __init__(self, connector_hub):
        self.browser_agent = TaskletBrowserAgent()
        self.connectors = connector_hub

    async def investigate_case(self, case_number: str) -> Dict:
        """Complete autonomous case investigation"""
        results = {
            "web_sources": await self._web_investigation(case_number),
            "connectors": await self.connectors.find_case_evidence(case_number)
        }
        return results

    async def _web_investigation(self, case_number: str) -> Dict:
        """Web-based investigation"""
        return {
            "jefs": await self.browser_agent.case_browser.search_jefs(case_number),
            "pacer": await self.browser_agent.case_browser.search_pacer(case_number)
        }


def create_case_investigation_agent(connector_hub):
    """Factory function to create investigation agent"""
    return CaseInvestigationAgent(connector_hub)
