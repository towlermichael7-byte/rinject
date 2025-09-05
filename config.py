import streamlit as st
"""
Configuration module for Resume Customizer application.
Contains all constants, default values, and configuration settings.
"""

from datetime import datetime
from typing import List, Dict, Any

# Application Configuration
APP_CONFIG = {
    "title": "📝 Resume Customizer + Email Sender",
    "page_title": "Resume Customizer",
    "layout": "wide",
    "max_workers_default": 4,
    "max_workers_limit": 8,
    "bulk_mode_threshold": 3,
    "version": "2.1.0",
    "build_date": "2024-01-15",
    "author": "Resume Customizer Team",
}

# SMTP Configuration
SMTP_SERVERS = {
    "Gmail": {"server": "smtp.gmail.com", "port": 465},
    "Office365": {"server": "smtp.office365.com", "port": 587},
    "Yahoo": {"server": "smtp.mail.yahoo.com", "port": 465},
    "Custom": {"server": "Custom", "port": 587}
}

SMTP_SERVER_OPTIONS = ["smtp.gmail.com", "smtp.office365.com", "smtp.mail.yahoo.com", "Custom"]

# Default Email Configuration
DEFAULT_EMAIL_CONFIG = {
    "subject": lambda: f"Customized Resume - {datetime.now().strftime('%Y-%m-%d')}",
    "body": "Hi,\n\nPlease find the customized resume attached.\n\nThis resume highlights experience with various technologies and skills.\n\nBest regards",
    "smtp_port": 465,
}

# Text Parsing Configuration
PARSING_CONFIG = {
    "tech_name_exclude_words": [
        'developed', 'created', 'implemented', 'designed', 
        'built', 'worked', 'managed', 'used', 'wrote', 'configured'
    ],
    "project_exclude_keywords": [
        "summary", "skills", "education", "achievements", "responsibilities:"
    ],
    "job_title_keywords": [
        "manager", "developer", "engineer", "analyst", "lead", 
        "senior", "junior", "architect", "consultant", "specialist", 
        "coordinator", "supervisor", "director", "designer", 
        "tester", "qa", "devops"
    ],
    "project_keywords": [
        "project", "team", "role", "position", "intern", 
        "trainee", "associate"
    ],
    "section_end_keywords": [
        "achievements", "technologies", "tools", "key"
    ]
}

# Document Processing Configuration
DOC_CONFIG = {
    "max_projects_enhanced": 3,
    "bullet_markers": ['-', '•', '*'],
    "default_filename": "resume.docx",
    "max_project_title_length": 100,
}

# UI Configuration
UI_CONFIG = {
    "sidebar_instructions": """
    1. Upload your resume(s) in DOCX format
    2. For each resume, provide:
       - Tech stacks with bullet points (format: 'TechName: • point1 • point2')
       - Email credentials for sending (optional)
    3. Click '🔍 Preview Changes' to see exactly what will be modified
    4. Review the preview and click 'Generate & Send Customized Resumes'
    5. Download or email the customized resumes
    """,
    
    "preview_features": """
    The preview will show you ONLY the changes:
    - ✅ Which projects will be enhanced
    - ➕ Exactly which NEW points will be added
    - 🎯 Where each point will be inserted
    - 📧 Email configuration status
    - 📊 Summary of additions only
    """,
    
    "project_selection_info": """
    **Top 3 Projects Focus:**
    - Points are added only to the first 3 projects
    - This highlights your most recent/relevant work
    - Projects 4+ remain unchanged
    - If you have ≤ 3 projects, all get points
    """,
    
    "format_preservation_info": """
    The app will preserve all formatting exactly:
    - Font family and size
    - Font color
    - Bold/italic/underline styles
    - Paragraph spacing and indentation
    - Bullet point styling
    """,
    
    "security_note": """
    - We recommend using app-specific passwords
    - Your credentials are not stored
    - Consider using a dedicated email for this purpose
    """,
    
    "bulk_benefits": """
    **Benefits of Bulk Mode:**
    - ⚡ **Up to 8x faster** processing with parallel workers
    - 🔄 **SMTP connection reuse** for faster email sending
    - 📊 **Real-time progress** tracking
    - 📈 **Performance metrics** and statistics
    - 🎯 **Batch processing** optimizations
    """,
    
    "example_format": """
Python: • Developed web applications using Django and Flask • Implemented RESTful APIs
JavaScript: • Created interactive UI components with React • Utilized Node.js for backend services
AWS: • Deployed applications using EC2 and S3 • Managed databases with RDS
SQL: • Designed and optimized database schemas • Wrote complex queries for reporting
    """,
    
    "file_upload_help": "Upload one or more .docx resumes",
    "tech_stack_help": "Format: 'TechName: • point1 • point2'",
}

# Performance Configuration
PERFORMANCE_CONFIG = {
    "estimated_sequential_time_per_resume": 8,  # seconds
    "memory_cleanup_threshold": 10,  # number of processed files
    "connection_pool_timeout": 30,  # seconds
}

# Error Messages
ERROR_MESSAGES = {
    "no_tech_stacks": "Could not parse tech stacks for {filename}. Please check your input format.",
    "no_projects": "No projects found in {filename}. Ensure your resume has project sections.",
    "parsing_failed": "Could not parse tech stacks from input for {filename}. Please use the format 'TechName: • point1 • point2' or the new block format.",
    "no_responsibilities": "Could not find projects with Responsibilities sections or bullet points in {filename}. Please ensure your resume has work experience sections with bullet points describing your responsibilities.",
    "custom_smtp_not_supported": "Custom SMTP server not supported in bulk mode. Please use Gmail, Office365, or Yahoo.",
    "smtp_connection_failed": "Failed to create SMTP connection: {error}. Please check your email credentials and network connection.",
    "email_send_failed": "Failed to send email for {filename}: {error}. Please verify your email settings.",
    "file_validation_failed": "File validation failed: {error}. Please check file format and size.",
    "memory_error": "Memory error during processing. Please try with fewer files or restart the application.",
    "processing_timeout": "Processing timeout. Please try again or reduce the number of files.",
}

# Success Messages
SUCCESS_MESSAGES = {
    "preview_generated": "✅ Preview generated with {points_added} points added!",
    "email_sent": "📧 Email sent successfully for {filename} to {recipient}",
    "processing_complete": "✅ {filename} has been processed successfully!",
    "bulk_complete": "🚀 Bulk processing completed successfully!",
    "file_uploaded": "📁 {filename} uploaded successfully ({size_mb:.1f}MB)",
    "validation_passed": "✅ All files validated successfully",
    "health_check_passed": "✅ Application health check passed",
    "config_validated": "✅ Configuration validated successfully",
}

@st.cache_data
def get_app_config() -> Dict[str, Any]:
    """Get application configuration.
    
    Returns:
        Dict[str, Any]: Application configuration dictionary
    """
    return APP_CONFIG.copy()

@st.cache_data
def get_smtp_servers() -> List[str]:
    """Get list of available SMTP servers.
    
    Returns:
        List[str]: List of available SMTP server options
    """
    return SMTP_SERVER_OPTIONS.copy()

def get_default_email_subject() -> str:
    """Get default email subject with current date."""
    try:
        return DEFAULT_EMAIL_CONFIG["subject"]()
    except Exception:
        return f"Customized Resume - {datetime.now().strftime('%Y-%m-%d')}"

def get_default_email_body() -> str:
    """Get default email body."""
    return DEFAULT_EMAIL_CONFIG["body"]

def validate_config() -> Dict[str, Any]:
    """Validate configuration and return any issues."""
    issues = []
    
    # Validate required configurations
    required_configs = ['title', 'page_title', 'layout', 'max_workers_default', 'max_workers_limit', 'bulk_mode_threshold']
    for config_key in required_configs:
        if config_key not in APP_CONFIG:
            issues.append(f"Missing required config: {config_key}")
    
    # Validate SMTP servers
    if not SMTP_SERVER_OPTIONS:
        issues.append("No SMTP servers configured")
    
    # Validate performance settings
    if APP_CONFIG.get('max_workers_limit', 0) < APP_CONFIG.get('max_workers_default', 0):
        issues.append("max_workers_limit should be >= max_workers_default")
    
    return {
        'valid': len(issues) == 0,
        'issues': issues
    }
