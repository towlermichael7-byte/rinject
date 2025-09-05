"""
Project detection module for Resume Customizer.
Handles detection of projects and responsibilities sections in documents.
"""
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Any
from docx.document import Document as DocumentType

@dataclass
class ProjectInfo:
    """Data class to hold project information."""
    name: str
    start_index: int
    end_index: int
    role: str = ""
    company: str = ""
    date_range: str = ""
    bullet_points: List[str] = None

    def __post_init__(self):
        self.bullet_points = self.bullet_points or []


class ProjectDetector:
    """Handles detection of projects and responsibilities sections in resumes."""
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize the ProjectDetector.
        
        Args:
            config: Configuration dictionary with parsing settings
        """
        self.config = config or {
            "project_exclude_keywords": [
                "summary", "skills", "education", "achievements", "responsibilities:"
            ],
            "job_title_keywords": [
                "manager", "developer", "engineer", "analyst", "lead", 
                "architect", "specialist", "consultant"
            ]
        }
    
    def find_projects(self, doc: DocumentType) -> List[ProjectInfo]:
        """
        Find all projects and their responsibilities sections in the resume.
        
        Args:
            doc: Document to search
            
        Returns:
            List of ProjectInfo objects
        """
        projects = []
        current_project = None
        in_responsibilities = False
        
        for i, para in enumerate(doc.paragraphs):
            text = para.text.strip()
            
            # Skip empty paragraphs
            if not text:
                continue
                
            # Check if this is a project header
            if self._is_potential_project(text):
                # Save previous project if exists
                if current_project:
                    projects.append(current_project)
                
                # Start new project
                role, company, date_range = self._parse_project_header(text)
                current_project = ProjectInfo(
                    name=role or f"Project {len(projects) + 1}",
                    start_index=i,
                    end_index=i,
                    role=role,
                    company=company,
                    date_range=date_range
                )
                in_responsibilities = False
                continue
                
            # Check if we're in a responsibilities section
            if self._is_responsibilities_heading(text):
                in_responsibilities = True
                continue
                
            # If we have an active project, collect bullet points
            if current_project and (in_responsibilities or self._is_bullet_point(text)):
                current_project.bullet_points.append(text)
                current_project.end_index = i
        
        # Add the last project if exists
        if current_project:
            projects.append(current_project)
            
        return projects
    
    def _is_potential_project(self, text: str) -> bool:
        """
        Check if text looks like a project/role heading.
        
        Args:
            text: Text to check
            
        Returns:
            True if text looks like a project heading
        """
        # Skip excluded keywords
        text_lower = text.lower()
        if any(keyword in text_lower for keyword in self.config["project_exclude_keywords"]):
            return False
            
        # Check for company | date format
        if self._looks_like_company_date(text):
            return True
            
        # Check for common job title patterns
        if any(keyword in text_lower for keyword in self.config["job_title_keywords"]):
            return True
            
        return False
    
    def _parse_project_header(self, text: str) -> Tuple[str, str, str]:
        """
        Parse project header into role, company, and date range.
        
        Args:
            text: Header text to parse
            
        Returns:
            Tuple of (role, company, date_range)
        """
        # Handle company | date format
        if '|' in text:
            parts = [p.strip() for p in text.split('|')]
            if len(parts) >= 2:
                # Try to extract date range (usually the last part)
                date_range = parts[-1].strip()
                
                # The rest is company/role
                company_role = '|'.join(parts[:-1]).strip()
                
                # Try to split company and role if possible
                if ',' in company_role:
                    role, company = company_role.split(',', 1)
                    return role.strip(), company.strip(), date_range
                return company_role, "", date_range
        
        # Default: use entire text as role
        return text, "", ""
    
    def _is_responsibilities_heading(self, text: str) -> bool:
        """Check if text is a responsibilities heading."""
        text_lower = text.lower()
        return any(
            text_lower.startswith(prefix)
            for prefix in ["responsibilities", "key responsibilities", "duties:"]
        )
    
    def _is_bullet_point(self, text: str) -> bool:
        """Check if text looks like a bullet point."""
        text = text.strip()
        bullet_markers = ['•', '●', '◦', '▪', '▫', '‣', '*', '-']
        return any(text.startswith(marker) for marker in bullet_markers) or \
               (text and text[0].isdigit() and '.' in text[:3])
    
    def _looks_like_company_date(self, text: str) -> bool:
        """
        Check if text looks like "Company | Date" format.
        
        Args:
            text: Text to check
            
        Returns:
            True if text looks like company|date format
        """
        if '|' not in text:
            return False
            
        parts = [p.strip() for p in text.split('|')]
        if len(parts) != 2:
            return False
            
        # Check if second part looks like a date range
        date_part = parts[1].strip()
        return any(sep in date_part for sep in ['-', '–', '—', 'to', 'present'])
