import streamlit as st
from config import UI_CONFIG, get_smtp_servers, get_default_email_subject, get_default_email_body, get_app_config
from validators import get_file_validator, EmailValidator, TextValidator
from text_parser import LegacyParser
from logger import get_logger

file_validator = get_file_validator()
config = get_app_config()
logger = get_logger()

class UIComponents:
    """Handles UI component rendering and interactions."""
    
    @staticmethod
    def render_sidebar():
        """Render the application sidebar with instructions."""
        with st.sidebar:
            st.header("ℹ️ Instructions")
            st.markdown(UI_CONFIG["sidebar_instructions"])
            
            st.header("👀 Preview Features")
            st.markdown(UI_CONFIG["preview_features"])
            
            st.header("🎯 Project Selection")
            st.markdown(UI_CONFIG["project_selection_info"])
            
            st.header("🔍 Format Preservation")
            st.markdown(UI_CONFIG["format_preservation_info"])
            
            st.header("🔒 Security Note")
            st.markdown(UI_CONFIG["security_note"])

    @staticmethod
    def render_file_upload():
        """Render the file upload component with validation."""
        uploaded_files = st.file_uploader(
            UI_CONFIG["file_upload_help"], 
            type="docx", 
            accept_multiple_files=True
        )
        
        if uploaded_files:
            validation_result = file_validator.validate_batch(uploaded_files)
            
            if not validation_result['valid']:
                for error in validation_result['summary']['errors']:
                    st.error(f"❌ {error}")
                return None
            
            for warning in validation_result['summary']['warnings']:
                st.warning(f"⚠️ {warning}")
            
            summary = validation_result['summary']
            if summary['valid_files'] > 0:
                st.success(
                    f"✅ {summary['valid_files']} valid files uploaded "
                    f"({summary['total_size_mb']:.1f}MB total)"
                )
                logger.log_user_action("file_upload", files_count=summary['valid_files'], total_size_mb=summary['total_size_mb'])
        
        return uploaded_files

    @staticmethod
    def render_example_format():
        """Render the example format section."""
        with st.expander("💡 Example Input Format"):
            st.code(UI_CONFIG["example_format"])

    @staticmethod
    def render_email_fields(file_name):
        """Render email configuration fields for a file with validation."""
        col1, col2 = st.columns(2)
        
        with col1:
            email_to = st.text_input(f"Recipient email for {file_name}", key=f"to_{file_name}")
            if email_to:
                validation = EmailValidator.validate_email(email_to)
                if not validation['valid']:
                    st.error(f"Invalid recipient email: {', '.join(validation['errors'])}")
            
            sender_email = st.text_input(f"Sender email for {file_name}", key=f"from_{file_name}")
            if sender_email:
                validation = EmailValidator.validate_email(sender_email)
                if not validation['valid']:
                    st.error(f"Invalid sender email: {', '.join(validation['errors'])}")
        
        with col2:
            sender_password = st.text_input(
                f"Sender email password for {file_name}", 
                type="password",
                help="For Gmail, use an app-specific password",
                key=f"pwd_{file_name}"
            )
            smtp_server = st.selectbox(
                f"SMTP Server for {file_name}",
                get_smtp_servers(),
                key=f"smtp_{file_name}"
            )
            smtp_port = st.number_input(
                f"SMTP Port for {file_name}",
                value=465,
                min_value=1,
                max_value=65535,
                key=f"port_{file_name}"
            )
        
        return email_to, sender_email, sender_password, smtp_server, smtp_port

    @staticmethod
    def render_email_customization(file_name):
        """Render email customization fields."""
        st.markdown("#### 📧 Email Customization (Optional)")
        
        email_subject = st.text_input(
            f"Email Subject for {file_name}",
            value=get_default_email_subject(),
            help="Customize the email subject line",
            key=f"subject_{file_name}"
        )
        
        email_body = st.text_area(
            f"Email Body for {file_name}",
            value=get_default_email_body(),
            height=120,
            help="Customize the email message content",
            key=f"body_{file_name}"
        )
        
        return email_subject, email_body

    @staticmethod
    def render_manual_points_editor(file_name, user_input):
        """Render the manual points editor section."""
        with st.expander("✏️ Optional: Edit points before preview", expanded=False):
            edit_enable_key = f"edit_points_enable_{file_name}"
            edit_text_key = f"edit_points_text_{file_name}"
            
            edit_points_enabled = st.checkbox(
                "Enable manual edit of points (one point per line)",
                key=edit_enable_key
            )
            
            if edit_points_enabled:
                if edit_text_key not in st.session_state:
                    legacy_parser = LegacyParser()
                    default_points, _ = legacy_parser.extract_points_from_legacy_format(user_input or "")
                    st.session_state[edit_text_key] = "\n".join(default_points)
                
                st.text_area(
                    "Points to add (one per line)",
                    key=edit_text_key,
                    height=200,
                    help="These points will be used instead of the auto-parsed ones when previewing or generating."
                )
                
                if st.button("Reset edited points to parsed defaults", key=f"reset_points_{file_name}"):
                    legacy_parser = LegacyParser()
                    default_points, _ = legacy_parser.extract_points_from_legacy_format(user_input or "")
                    st.session_state[edit_text_key] = "\n".join(default_points)
                    st.success("✅ Points reset to parsed defaults.")
                    st.rerun()
        
        return edit_points_enabled

    @staticmethod
    def render_bulk_settings(num_files):
        """Render bulk processing settings."""
        with st.expander("⚡ Bulk Mode Settings", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                max_workers = st.slider(
                    "🔄 Parallel Workers (Higher = Faster)",
                    min_value=2,
                    max_value=min(config["max_workers_limit"], num_files),
                    value=min(config["max_workers_default"], num_files),
                    help="Number of parallel processes. More workers = faster processing but higher CPU usage"
                )
                
                bulk_email_mode = st.selectbox(
                    "📧 Email Sending Mode",
                    ["Send emails in parallel", "Process resumes only (no emails)", "Download all as ZIP"],
                    help="Choose how to handle email sending for optimal speed"
                )
            
            with col2:
                show_progress = st.checkbox(
                    "📊 Show Real-time Progress",
                    value=True,
                    help="Display progress updates (may slow down slightly)"
                )
                
                performance_stats = st.checkbox(
                    "📈 Show Performance Stats",
                    value=True,
                    help="Display timing and throughput information"
                )
        
        return max_workers, bulk_email_mode, show_progress, performance_stats