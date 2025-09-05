"""
Text parsing module for Resume Customizer application.
Handles parsing of tech stacks and bullet points from different input formats.
"""

import re
from typing import List, Tuple
from config import PARSING_CONFIG


class TechStackParser:
    """Parser for extracting tech stacks and bullet points from text input."""
    
    def __init__(self):
        self.tech_exclude_words = PARSING_CONFIG["tech_name_exclude_words"]
    
    def parse_new_format(self, text: str) -> Tuple[List[str], List[str]]:
        """
        Parse the new format:
        TechName1
        bulletPoint1
        bulletPoint2
        ...
        
        TechName2
        bulletPoint1
        bulletPoint2
        ...
        
        Args:
            text: Input text to parse
            
        Returns:
            Tuple of (selected_points, tech_stacks_used)
        """
        lines = text.strip().split('\n')
        tech_stacks_used = []
        selected_points = []
        current_tech = None
        
        # Split input into blocks separated by blank lines
        blocks = []
        current_block = []
        
        for line in lines:
            line = line.strip()
            if not line:  # Empty line - end of block
                if current_block:
                    blocks.append(current_block)
                    current_block = []
            else:
                current_block.append(line)
        
        # Add the last block if it exists
        if current_block:
            blocks.append(current_block)
        
        # Process each block
        for block in blocks:
            if not block:
                continue
                
            # First line is tech stack name, rest are bullet points
            first_line = block[0]
            
            # Heuristic to determine if this is a tech stack name vs bullet point
            if self._looks_like_tech_name(first_line):
                tech_stacks_used.append(first_line)
                # Add remaining lines as bullet points
                for line in block[1:]:
                    selected_points.append(line)
            else:
                # If first line looks like a bullet point, treat all lines as bullet points
                for line in block:
                    selected_points.append(line)
        
        return selected_points, tech_stacks_used
    
    def parse_original_format(self, text: str) -> Tuple[List[str], List[str]]:
        """
        Parse the original format: TechName: • point1 • point2
        
        Args:
            text: Input text to parse
            
        Returns:
            Tuple of (selected_points, tech_stacks_used)
        """
        techstack_pattern = r"(?P<stack>[A-Za-z0-9_+#\- ]+):\s*(?P<points>(?:• .+\n?)+)"
        matches = list(re.finditer(techstack_pattern, text))
        
        if not matches:
            return [], []
        
        selected_points = []
        tech_stacks_used = []
        
        for match in matches:
            stack = match.group("stack").strip()
            points_block = match.group("points").strip()
            points = re.findall(r"•\s*(.+)", points_block)
            selected_points.extend(points)
            tech_stacks_used.append(stack)
        
        return selected_points, tech_stacks_used
    
    def parse_tech_stacks(self, text: str) -> Tuple[List[str], List[str]]:
        """
        Try to parse both formats and return the one that works.
        
        Args:
            text: Input text to parse
            
        Returns:
            Tuple of (selected_points, tech_stacks_used)
        """
        # First try the new format
        selected_points, tech_stacks_used = self.parse_new_format(text)
        
        # If we got results, use them
        if selected_points and tech_stacks_used:
            return selected_points, tech_stacks_used
        
        # Otherwise try the original format
        return self.parse_original_format(text)
    
    def _is_bullet_point_text(self, line: str) -> bool:
        """
        Check if a line looks like a bullet point rather than a tech stack name.
        
        Args:
            line: Text line to check
            
        Returns:
            True if line looks like a bullet point
        """
        return any(line.lower().startswith(word) for word in self.tech_exclude_words)
    
    def _looks_like_tech_name(self, line: str) -> bool:
        """
        Determine if a line looks like a technology name.
        
        Args:
            line: Text line to check
            
        Returns:
            True if line looks like a technology name
        """
        line_lower = line.lower().strip()
        
        # Skip empty lines
        if not line_lower:
            return False
        
        # If it starts with action words, it's likely a bullet point
        if any(line_lower.startswith(word) for word in self.tech_exclude_words):
            return False
        
        # If it's short and doesn't contain common sentence patterns, likely a tech name
        if len(line.split()) <= 3:
            return True
            
        # If it contains common tech keywords, likely a tech name
        tech_keywords = ['python', 'javascript', 'java', 'react', 'node', 'aws', 'sql', 'html', 'css', 'git', 'docker', 'kubernetes', 'angular', 'vue', 'typescript', 'c++', 'c#', '.net', 'php', 'ruby', 'go', 'rust', 'swift', 'kotlin', 'flutter', 'django', 'flask', 'spring', 'laravel', 'express']
        if any(keyword in line_lower for keyword in tech_keywords):
            return True
            
        # Default: if it's a short line without action words, treat as tech name
        return len(line.split()) <= 2


class ManualPointsParser:
    """Parser for handling manually edited points."""
    
    @staticmethod
    def parse_manual_points(text: str) -> List[str]:
        """
        Parse manually entered points (one per line).
        
        Args:
            text: Manual points text
            
        Returns:
            List of cleaned points
        """
        if not text.strip():
            return []
        
        return [
            line.strip().lstrip("-•* ") 
            for line in text.splitlines() 
            if line.strip()
        ]


class LegacyParser:
    """Parser for legacy format handling (for backward compatibility)."""
    
    @staticmethod
    def extract_points_from_legacy_format(raw_text: str) -> Tuple[List[str], List[str]]:
        """
        Extract points from legacy regex-based format.
        Used for backward compatibility in preview sections.
        
        Args:
            raw_text: Raw input text
            
        Returns:
            Tuple of (selected_points, tech_stacks_used)
        """
        techstack_pattern = r"(?P<stack>[A-Za-z0-9_+#\- ]+):\s*(?P<points>(?:• .+\n?)+)"
        matches = list(re.finditer(techstack_pattern, raw_text))
        
        if not matches:
            return [], []
        
        selected_points = []
        tech_stacks_used = []
        
        for match in matches:
            stack = match.group("stack").strip()
            points_block = match.group("points").strip()
            points = re.findall(r"•\s*(.+)", points_block)
            selected_points.extend(points)
            tech_stacks_used.append(stack)
        
        return selected_points, tech_stacks_used


def get_parser() -> TechStackParser:
    """
    Get a new instance of the tech stack parser.
    
    Returns:
        TechStackParser instance
    """
    return TechStackParser()


def parse_input_text(text: str, manual_text: str = "") -> Tuple[List[str], List[str]]:
    """
    Convenience function to parse input text with optional manual override.
    
    Args:
        text: Main input text
        manual_text: Optional manual points text (overrides parsed points)
        
    Returns:
        Tuple of (selected_points, tech_stacks_used)
    """
    try:
        parser = TechStackParser()
        selected_points, tech_stacks_used = parser.parse_tech_stacks(text)
        
        # Override with manual points if provided
        if manual_text.strip():
            manual_parser = ManualPointsParser()
            selected_points = manual_parser.parse_manual_points(manual_text)
        
        return selected_points, tech_stacks_used
    except Exception as e:
        # Return empty results on parsing error
        return [], []
