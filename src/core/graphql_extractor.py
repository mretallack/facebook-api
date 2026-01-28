"""GraphQL response extraction for Facebook data"""
import json
import logging
from typing import Dict, List, Optional
from playwright.async_api import Page, Response

logger = logging.getLogger(__name__)


class GraphQLExtractor:
    """Extract data from Facebook GraphQL responses"""
    
    QUERY_TYPES = {
        'ProfileCometHeaderQuery': 'profile_header',
        'ProfileCometTimelineQuery': 'profile_timeline',
        'CometFeedQuery': 'feed',
        'SearchResultsQuery': 'search',
    }
    
    def __init__(self):
        self.responses: List[Dict] = []
    
    async def intercept_responses(self, page: Page):
        """Set up GraphQL response interception"""
        
        async def handle_response(response: Response):
            try:
                if 'graphql' in response.url.lower() and response.status == 200:
                    try:
                        data = await response.json()
                        if self._is_relevant(data):
                            self.responses.append(data)
                            query_type = self._identify_query(response.url)
                            logger.info(f"Captured GraphQL: {query_type} ({len(str(data))} bytes)")
                    except:
                        pass
            except:
                pass
        
        page.on('response', handle_response)
    
    def _is_relevant(self, data: Dict) -> bool:
        """Check if response contains useful data"""
        if not isinstance(data, dict) or 'data' not in data:
            return False
        
        data_obj = data['data']
        return any(key in data_obj for key in ['user', 'node', 'viewer', 'actor'])
    
    def _identify_query(self, url: str) -> str:
        """Identify GraphQL query type"""
        for query_name, query_type in self.QUERY_TYPES.items():
            if query_name in url:
                return query_type
        return 'unknown'
    
    def extract_profile(self) -> Dict:
        """Extract profile data from captured responses"""
        profile = {}
        
        for response in self.responses:
            if 'data' not in response:
                continue
            
            data = response['data']
            user_data = data.get('user') or data.get('node') or data.get('viewer', {}).get('actor')
            
            if user_data:
                profile.update(self._extract_fields(user_data))
        
        return profile
    
    def _extract_fields(self, user_data: Dict) -> Dict:
        """Extract fields from user object"""
        fields = {}
        
        # Direct fields
        for field in ['id', 'name', 'short_name']:
            if field in user_data:
                fields[field] = user_data[field]
        
        # Profile picture
        if 'profile_picture' in user_data:
            pp = user_data['profile_picture']
            if isinstance(pp, dict) and 'uri' in pp:
                fields['profile_picture'] = pp['uri']
        
        # Cover photo
        if 'cover_photo' in user_data:
            cp = user_data['cover_photo']
            if isinstance(cp, dict) and 'uri' in cp:
                fields['cover_photo'] = cp['uri']
        
        # Friends count
        if 'friends' in user_data:
            friends = user_data['friends']
            if isinstance(friends, dict) and 'count' in friends:
                fields['friends_count'] = str(friends['count'])
        
        # Location
        if 'current_city' in user_data:
            city = user_data['current_city']
            if isinstance(city, dict) and 'name' in city:
                fields['location'] = city['name']
        
        # Work
        if 'work' in user_data and isinstance(user_data['work'], list) and user_data['work']:
            work = user_data['work'][0]
            if isinstance(work, dict) and 'employer' in work:
                employer = work['employer']
                if isinstance(employer, dict) and 'name' in employer:
                    fields['work'] = employer['name']
        
        # Education
        if 'education' in user_data and isinstance(user_data['education'], list) and user_data['education']:
            edu = user_data['education'][0]
            if isinstance(edu, dict) and 'school' in edu:
                school = edu['school']
                if isinstance(school, dict) and 'name' in school:
                    fields['education'] = school['name']
        
        return fields
    
    def save_responses(self, filepath: str):
        """Save captured responses for debugging"""
        try:
            with open(filepath, 'w') as f:
                json.dump(self.responses, f, indent=2)
            logger.info(f"Saved {len(self.responses)} GraphQL responses to {filepath}")
        except Exception as e:
            logger.error(f"Failed to save responses: {e}")
    
    def clear(self):
        """Clear captured responses"""
        self.responses = []
