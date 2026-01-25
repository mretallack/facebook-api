"""
Preflight checker for proactive issue detection before Facebook actions.
Validates conditions and calculates risk scores to prevent account blocks.
"""
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


@dataclass
class RateLimitConfig:
    """Rate limit configuration for an action type."""
    max_actions: int
    time_window: timedelta
    

class PreflightChecker:
    """Proactive validation before Facebook actions to prevent blocks."""
    
    # Rate limits based on research (conservative values)
    RATE_LIMITS = {
        'friend_request': RateLimitConfig(15, timedelta(hours=1)),
        'post': RateLimitConfig(8, timedelta(hours=1)),
        'message': RateLimitConfig(40, timedelta(hours=1)),
        'like': RateLimitConfig(80, timedelta(hours=1)),
        'comment': RateLimitConfig(20, timedelta(hours=1)),
        'group_join': RateLimitConfig(5, timedelta(hours=1)),
        'page_like': RateLimitConfig(10, timedelta(hours=1)),
    }
    
    def __init__(self):
        self.action_history: Dict[str, List[datetime]] = {}
        self.account_created_at: Optional[datetime] = None
        self.last_ip: Optional[str] = None
        
    def check(self, action_type: str, account_age_days: Optional[int] = None) -> Dict:
        """
        Run all preflight checks and return risk assessment.
        
        Args:
            action_type: Type of action (friend_request, post, etc.)
            account_age_days: Age of account in days (for warmth check)
            
        Returns:
            Dict with risk_score (0.0-1.0), passed (bool), and failed_checks (list)
        """
        checks = [
            self._check_rate_limit(action_type),
            self._check_automation_flags(),
            self._check_session_health(),
            self._check_suspicious_patterns(action_type),
            self._check_timing_analysis(),
            self._check_account_warmth(account_age_days),
            self._check_captcha_risk(),
            self._check_ip_consistency(),
            self._check_proxy_reputation(),
            self._check_fingerprint_consistency(),
        ]
        
        failed_checks = [c for c in checks if not c['passed']]
        risk_score = sum(c['risk_weight'] for c in failed_checks)
        
        result = {
            'passed': risk_score < 0.7,
            'risk_score': risk_score,
            'failed_checks': [c['name'] for c in failed_checks],
            'details': failed_checks
        }
        
        if not result['passed']:
            logger.warning(f"Preflight check failed for {action_type}: {result}")
        
        return result
    
    def record_action(self, action_type: str):
        """Record an action for rate limit tracking."""
        if action_type not in self.action_history:
            self.action_history[action_type] = []
        self.action_history[action_type].append(datetime.now())
        
    def _check_rate_limit(self, action_type: str) -> Dict:
        """Check if action would exceed rate limits."""
        if action_type not in self.RATE_LIMITS:
            return {'name': 'rate_limit', 'passed': True, 'risk_weight': 0.0}
        
        config = self.RATE_LIMITS[action_type]
        history = self.action_history.get(action_type, [])
        
        # Clean old history
        cutoff = datetime.now() - config.time_window
        recent = [t for t in history if t > cutoff]
        self.action_history[action_type] = recent
        
        if len(recent) >= config.max_actions:
            return {
                'name': 'rate_limit',
                'passed': False,
                'risk_weight': 0.4,
                'message': f'{action_type} rate limit exceeded: {len(recent)}/{config.max_actions}'
            }
        
        return {'name': 'rate_limit', 'passed': True, 'risk_weight': 0.0}
    
    def _check_automation_flags(self) -> Dict:
        """Check for automation detection flags in browser."""
        # TODO: Implement browser flag detection
        # Check for: navigator.webdriver, chrome.runtime, etc.
        return {'name': 'automation_flags', 'passed': True, 'risk_weight': 0.0}
    
    def _check_session_health(self) -> Dict:
        """Check if session is healthy and authenticated."""
        # TODO: Implement session validation
        # Check cookies, auth tokens, session age
        return {'name': 'session_health', 'passed': True, 'risk_weight': 0.0}
    
    def _check_suspicious_patterns(self, action_type: str) -> Dict:
        """Detect suspicious activity patterns."""
        # Check for rapid repeated actions
        history = self.action_history.get(action_type, [])
        if len(history) < 3:
            return {'name': 'suspicious_patterns', 'passed': True, 'risk_weight': 0.0}
        
        # Check if last 3 actions were within 10 seconds
        recent = sorted(history[-3:])
        if (recent[-1] - recent[0]).total_seconds() < 10:
            return {
                'name': 'suspicious_patterns',
                'passed': False,
                'risk_weight': 0.3,
                'message': 'Actions too rapid (3 in <10s)'
            }
        
        return {'name': 'suspicious_patterns', 'passed': True, 'risk_weight': 0.0}
    
    def _check_timing_analysis(self) -> Dict:
        """Analyze timing patterns for bot-like behavior."""
        # Check for perfectly regular intervals (bot-like)
        all_times = []
        for times in self.action_history.values():
            all_times.extend(times)
        
        if len(all_times) < 5:
            return {'name': 'timing_analysis', 'passed': True, 'risk_weight': 0.0}
        
        # TODO: Implement interval variance analysis
        return {'name': 'timing_analysis', 'passed': True, 'risk_weight': 0.0}
    
    def _check_account_warmth(self, account_age_days: Optional[int]) -> Dict:
        """Check if account is warmed up for this action level."""
        if account_age_days is None:
            return {'name': 'account_warmth', 'passed': True, 'risk_weight': 0.0}
        
        # New accounts (<14 days) should have limited activity
        if account_age_days < 14:
            total_actions = sum(len(h) for h in self.action_history.values())
            if total_actions > 20:
                return {
                    'name': 'account_warmth',
                    'passed': False,
                    'risk_weight': 0.3,
                    'message': f'New account ({account_age_days}d) with high activity ({total_actions})'
                }
        
        return {'name': 'account_warmth', 'passed': True, 'risk_weight': 0.0}
    
    def _check_captcha_risk(self) -> Dict:
        """Assess risk of triggering CAPTCHA."""
        # TODO: Implement CAPTCHA risk scoring
        # Based on: recent failures, action velocity, session age
        return {'name': 'captcha_risk', 'passed': True, 'risk_weight': 0.0}
    
    def _check_ip_consistency(self) -> Dict:
        """Check for suspicious IP changes."""
        # TODO: Implement IP tracking
        # Flag rapid IP changes or datacenter IPs
        return {'name': 'ip_consistency', 'passed': True, 'risk_weight': 0.0}
    
    def _check_proxy_reputation(self) -> Dict:
        """Check if proxy/IP has good reputation."""
        # TODO: Implement proxy reputation check
        # Verify residential proxy, not in blacklists
        return {'name': 'proxy_reputation', 'passed': True, 'risk_weight': 0.0}
    
    def _check_fingerprint_consistency(self) -> Dict:
        """Check browser fingerprint consistency."""
        # TODO: Implement fingerprint tracking
        # Verify consistent canvas, WebGL, fonts, etc.
        return {'name': 'fingerprint_consistency', 'passed': True, 'risk_weight': 0.0}
