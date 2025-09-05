"""
Main application file for Resume Customizer - Refactored version.
Uses modular components for better maintainability and code organization.
"""

import streamlit as st
import base64
import time
from io import BytesIO
from typing import Dict, Any, Optional

# Import custom modules
from config import get_app_config, get_smtp_servers, get_default_email_subject, get_default_email_body, APP_CONFIG, validate_config
from text_parser import parse_input_text, LegacyParser
from resume_processor import get_resume_manager
from email_handler import get_email_manager
from logger import get_logger, display_logs_in_sidebar
from validators import validate_session_state
from performance_monitor import get_performance_monitor
from retry_handler import get_retry_handler

# Import refactored UI and handlers
from ui.components import UIComponents
from ui.resume_tab_handler import ResumeTabHandler
from ui.bulk_processor import BulkProcessor
from ui.requirements_manager import RequirementsManager, render_requirement_form, render_requirements_list
from ui.utils import check_file_readiness, prepare_bulk_data

# Initialize components
logger = get_logger()
performance_monitor = get_performance_monitor()
resume_manager = get_resume_manager()
email_manager = get_email_manager()
config = get_app_config()

def check_application_health() -> Dict[str, Any]:
    """Check application health and return status."""
    health_status = {
        'healthy': True,
        'issues': [],
        'warnings': []
    }
    
    try:
        # Check if all required modules can be imported
        import streamlit
        import docx
        import io
        
        # Check performance monitor
        if not performance_monitor:
            health_status['warnings'].append("Performance monitor not available")
        
        # Check memory usage
        try:
            import psutil
            memory = psutil.virtual_memory()
            if memory.percent > 90:
                health_status['warnings'].append(f"High memory usage: {memory.percent:.1f}%")
                
                # Suggest memory cleanup
                if memory.percent > 95:
                    health_status['warnings'].append("⚠️ Critical memory usage - consider restarting the application")
                else:
                    health_status['warnings'].append("💡 Try processing fewer files at once or restart the application")
                    
                # Attempt automatic cleanup
                try:
                    from document_processor import force_memory_cleanup
                    force_memory_cleanup()
                    health_status['warnings'].append("🧹 Automatic memory cleanup performed")
                except Exception as e:
                    logger.warning(f"Automatic memory cleanup failed: {e}")
                    
        except ImportError:
            health_status['warnings'].append("psutil not available - memory monitoring disabled")
        
        # Check disk space
        try:
            import psutil
            disk = psutil.disk_usage('/')
            if disk.percent > 90:
                health_status['warnings'].append(f"Low disk space: {disk.percent:.1f}% used")
        except ImportError:
            pass
        except Exception as e:
            health_status['warnings'].append(f"Disk space check failed: {e}")
        
    except ImportError as e:
        health_status['healthy'] = False
        health_status['issues'].append(f"Missing required dependency: {e}")
    
    return health_status

def render_requirements_tab():
    """Render the Requirements Management tab."""
    st.title("📋 Requirements Manager")
    st.write("Create and manage job requirements to customize your resume for specific positions.")
    
    # Initialize requirements manager
    if 'requirements_manager' not in st.session_state:
        st.session_state.requirements_manager = RequirementsManager()
    
    # Tabs for different views
    tab1, tab2 = st.tabs(["📝 Create/Edit Requirement", "📋 View Requirements"])
    
    with tab1:
        # Check if we're editing an existing requirement
        edit_id = st.query_params.get("edit")
        requirement_to_edit = None
        
        if edit_id and 'requirements_manager' in st.session_state:
            requirement_to_edit = st.session_state.requirements_manager.get_requirement(edit_id)
            if not requirement_to_edit:
                st.warning("The requirement you're trying to edit doesn't exist.")
        
        # Render the form
        form_data = render_requirement_form(requirement_to_edit)
        
        # Handle form submission
        if form_data:
            try:
                if requirement_to_edit:
                    # Update existing requirement
                    if st.session_state.requirements_manager.update_requirement(edit_id, form_data):
                        st.success("✅ Requirement updated successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to update requirement. It may have been deleted.")
                else:
                    # Create new requirement
                    requirement_id = st.session_state.requirements_manager.create_requirement(form_data)
                    if requirement_id:
                        st.success("✅ Requirement created successfully!")
                        st.rerun()
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                logger.error(f"Error saving requirement: {str(e)}")
    
    with tab2:
        render_requirements_list(st.session_state.requirements_manager)

def main():
    """Main application function."""
    # Check application health first
    health_status = check_application_health()
    if not health_status['healthy']:
        st.error("❌ Application Health Check Failed")
        for issue in health_status['issues']:
            st.error(issue)
        return
    
    # Initialize session state
    if 'resume_tab_handler' not in st.session_state:
        from resume_processor import get_resume_manager
        st.session_state.resume_tab_handler = ResumeTabHandler(resume_manager=get_resume_manager())
    
    if 'bulk_processor' not in st.session_state:
        from resume_processor import get_resume_manager
        st.session_state.bulk_processor = BulkProcessor(resume_manager=get_resume_manager())
    
    # Set page config
    st.set_page_config(
        page_title=APP_CONFIG["title"],
        page_icon="📝",
        layout=APP_CONFIG["layout"],
        initial_sidebar_state="expanded"
    )

    # Validate configuration first
    config_validation = validate_config()
    if not config_validation['valid']:
        st.error("❌ Configuration Error")
        for issue in config_validation['issues']:
            st.error(f"• {issue}")
        st.stop()
    
    validate_session_state()
    if 'resume_inputs' not in st.session_state:
        st.session_state.resume_inputs = {}
    if 'user_id' not in st.session_state:
        import uuid
        st.session_state.user_id = str(uuid.uuid4())
    logger.info("Application started")

    ui = UIComponents()
    tab_handler = ResumeTabHandler(resume_manager)
    bulk_processor = BulkProcessor(resume_manager)

    # Main app layout
    st.title(APP_CONFIG["title"])
    st.markdown("Customize your resume and send it to multiple recipients")
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📄 Resume Customizer", 
        "📤 Bulk Processor", 
        "📋 Requirements",
        "⚙️ Settings"
    ])

    with tab1:
        # Resume Customizer Tab
        ui.render_sidebar()
        display_logs_in_sidebar()
        # Performance metrics are now displayed in the sidebar via the UI components

        uploaded_files = ui.render_file_upload()

        if uploaded_files:
            st.markdown("### 🔽 Paste Tech Stack + Points for Each Resume")
            tabs = st.tabs([file.name for file in uploaded_files])
            for i, file in enumerate(uploaded_files):
                with tabs[i]:
                    tab_handler.render_tab(file)

            st.markdown("---")
            st.markdown("## 🚀 Bulk Operations (High Performance Mode)")

            st.markdown("### 📧 Quick Email All Resumes")
            col1, col2 = st.columns([2, 1])
            with col1:
                st.info("📨 Send all configured resumes via email simultaneously (processes and emails in one click)")
            with col2:
                if st.button(
                    f"📧 SEND ALL {len(uploaded_files)} RESUMES VIA EMAIL",
                    type="secondary",
                    help="Process and send all resumes with email configuration via email simultaneously",
                    key="send_all_emails_btn"
                ):
                    with st.spinner("📨 Sending all resumes via email…"):
                        try:
                            bulk_processor.send_all_resumes_via_email(uploaded_files)
                        except Exception as e:
                            st.error(f"Error sending emails: {e}")

            if len(uploaded_files) >= config["bulk_mode_threshold"]:
                st.markdown("### ⚡ Fast Bulk Processing for Multiple Resumes")
                max_workers, bulk_email_mode, show_progress, performance_stats = ui.render_bulk_settings(len(uploaded_files))
                ready_files, missing_data_files = check_file_readiness(uploaded_files)
                if missing_data_files:
                    st.warning(f"⚠️ Missing tech stack data for: {', '.join(missing_data_files)}")
                    st.info("Please fill in the tech stack data in the individual tabs above before using bulk mode.")
                if ready_files:
                    st.success(f"✅ Ready to process {len(ready_files)} resumes: {', '.join(ready_files)}")
                    if st.button(
                        f"🚀 BULK PROCESS ALL {len(ready_files)} RESUMES",
                        type="primary",
                        help="Process all resumes simultaneously for maximum speed",
                        key="bulk_process_btn"
                    ):
                        files_data = prepare_bulk_data(uploaded_files, ready_files)
                        with st.spinner("⚡ Processing all resumes…"):
                            try:
                                bulk_processor.process_bulk_resumes(
                                    ready_files, files_data, max_workers, show_progress, performance_stats, bulk_email_mode
                                )
                            except Exception as e:
                                st.error(f"Error during bulk processing: {e}")
            else:
                st.info(f"💡 Bulk mode is available when you have {config['bulk_mode_threshold']}+ resumes (currently: {len(uploaded_files)})")
                st.markdown("Process multiple resumes simultaneously to save time and effort. Bulk mode enables parallel processing for faster results.")
        else:
            st.info("👆 Please upload one or more DOCX resumes to get started.")

    with tab2:
        # Bulk Processor Tab
        st.header("📤 Bulk Processor")
        st.write("Process multiple resumes simultaneously for maximum speed.")
        
        # Display application health status
        st.subheader("🔍 Application Health")
        if health_status['healthy']:
            st.success("✅ Application is healthy")
        else:
            st.error("❌ Application has issues")
        
        if health_status['warnings']:
            st.warning("\n".join(["⚠️ " + w for w in health_status['warnings']]))

    with tab3:
        # Requirements Management Tab
        render_requirements_tab()

    with tab4:
        # Settings Tab
        st.header("⚙️ Application Settings")
        st.write("Configure application settings and preferences.")
        
        # Display application health status
        st.subheader("🔍 Application Health")
        if health_status['healthy']:
            st.success("✅ Application is healthy")
        else:
            st.error("❌ Application has issues")
        
        if health_status['warnings']:
            st.warning("\n".join(["⚠️ " + w for w in health_status['warnings']]))

    st.markdown("---")
    if st.checkbox("Show Performance Summary", value=False):
        summary = performance_monitor.get_performance_summary()
        if summary.get('system'):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("CPU Usage", f"{summary['system'].get('cpu_percent', 0):.1f}%")
            with col2:
                st.metric("Memory Usage", f"{summary['system'].get('memory_percent', 0):.1f}%")
            with col3:
                st.metric("Memory Used", f"{summary['system'].get('memory_used_mb', 0):.0f}MB")

    # Footer with version info
    version = config.get('version', '1.0.0')
    st.markdown(
        f"""
        <style>
        .footer {{
            text-align: center;
            padding: 10px;
            border-top: 1px solid #e0e0e0;
            margin-top: 20px;
        }}
        .footer a {{
            color: #1f77b4;
            text-decoration: none;
        }}
        .footer a:hover {{
            text-decoration: underline;
        }}
        </style>
        <div class="footer">
            <p>
                <strong>Resume Customizer Pro v{version}</strong> | 
                Enhanced with Security & Performance Monitoring |
                <a href="#" onclick="alert('Support: contact@resumecustomizer.com')">Support</a> |
                <a href="#" onclick="alert('Documentation available in README.md')">Docs</a>
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

def cleanup_on_exit():
    """Cleanup resources on application exit."""
    try:
        # Cleanup performance monitor
        from performance_monitor import cleanup_performance_monitor
        cleanup_performance_monitor()
        
        # Cleanup document resources
        from document_processor import cleanup_document_resources
        cleanup_document_resources()
        
        # Cleanup email connections
        email_manager.close_all_connections()
        
        logger.info("Application cleanup completed")
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")

if __name__ == "__main__":
    try:
        main()
    finally:
        cleanup_on_exit()
