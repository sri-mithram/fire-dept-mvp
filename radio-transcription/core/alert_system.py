"""
Alert Detection and Management System

Detects keywords and manages alert priorities

"""



from typing import List, Dict, Optional, Tuple

from datetime import datetime

import re



import config

from utils.logger import log





class AlertSystem:

    """

    Detects and manages alerts based on keywords

    Assigns priority levels and triggers notifications

    """

    

    def __init__(self):

        """Initialize alert system"""

        

        self.alert_keywords = [kw.lower() for kw in config.ALERT_KEYWORDS]

        self.alert_priority = {k.lower(): v for k, v in config.ALERT_PRIORITY.items()}

        

        # Compile regex patterns for efficient matching

        self.keyword_patterns = {

            keyword: re.compile(r'\b' + re.escape(keyword) + r'\b', re.IGNORECASE)

            for keyword in self.alert_keywords

        }

        

        log.info(f"Alert system initialized with {len(self.alert_keywords)} keywords")

    

    def check_for_alerts(self, text: str) -> Tuple[bool, List[str], str]:

        """

        Check text for alert keywords

        

        Args:

            text: Transcribed text to check

        

        Returns:

            Tuple of (is_alert, keywords_found, priority)

        """

        

        text_lower = text.lower()

        keywords_found = []

        

        # Check each keyword

        for keyword, pattern in self.keyword_patterns.items():

            if pattern.search(text):

                keywords_found.append(keyword)

                log.debug(f"Alert keyword detected: '{keyword}'")

        

        if not keywords_found:

            return False, [], "NORMAL"

        

        # Determine highest priority

        priority = self._get_highest_priority(keywords_found)

        

        return True, keywords_found, priority

    

    def _get_highest_priority(self, keywords: List[str]) -> str:

        """Determine highest priority from list of keywords"""

        

        priority_levels = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]

        

        priorities = [

            self.alert_priority.get(kw, "LOW")

            for kw in keywords

        ]

        

        # Return highest priority

        return max(priorities, key=lambda p: priority_levels.index(p))

    

    def format_alert_message(self, channel: str, text: str, 

                           keywords: List[str], priority: str,

                           timestamp: datetime) -> Dict:

        """

        Format alert for display/notification

        

        Args:

            channel: Channel name

            text: Alert text

            keywords: Detected keywords

            priority: Alert priority

            timestamp: When alert occurred

        

        Returns:

            Formatted alert dictionary

        """

        

        # Priority emoji

        priority_emoji = {

            "LOW": "ℹ️",

            "MEDIUM": "⚠️",

            "HIGH": "🚨",

            "CRITICAL": "🔴"

        }

        

        return {

            "channel": channel,

            "text": text,

            "keywords": keywords,

            "priority": priority,

            "emoji": priority_emoji.get(priority, "ℹ️"),

            "timestamp": timestamp.isoformat(),

            "formatted": f"{priority_emoji.get(priority, 'ℹ️')} [{priority}] [{channel}] {text}"

        }

    

    def should_notify(self, priority: str) -> bool:

        """

        Determine if alert should trigger notification

        

        Args:

            priority: Alert priority level

        

        Returns:

            True if notification should be sent

        """

        

        # Only notify for HIGH and CRITICAL

        return priority in ["HIGH", "CRITICAL"]

