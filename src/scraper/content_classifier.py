from typing import List, Dict, Optional

class ContentClassifier:
    @staticmethod
    def filter_posts(
        posts: List[Dict],
        exclude_ads: bool = False,
        exclude_suggested: bool = False,
        post_type: Optional[str] = None
    ) -> List[Dict]:
        """Filter posts based on criteria"""
        filtered = posts
        
        if exclude_ads:
            filtered = [p for p in filtered if not p.get("is_sponsored", False)]
        
        if exclude_suggested:
            filtered = [p for p in filtered if not p.get("is_suggested", False)]
        
        if post_type:
            filtered = [p for p in filtered if p.get("post_type") == post_type]
        
        return filtered
