import streamlit as st
import time

from performance_monitor import performance_decorator
from logger import get_logger

logger = get_logger()

class BulkProcessor:
    """Handles bulk processing operations."""

    def __init__(self, resume_manager):
        self.resume_manager = resume_manager
        self.ui = __import__("ui.components", fromlist=["UIComponents"]).UIComponents()

    @performance_decorator("bulk_processing")
    def process_bulk_resumes(self, ready_files, files_data, max_workers, show_progress, performance_stats, bulk_email_mode):
        """Process multiple resumes in bulk mode."""
        from validators import get_rate_limiter
        user_id = st.session_state.get('user_id', 'anonymous')
        rate_limiter = get_rate_limiter()
        if rate_limiter.is_rate_limited(user_id, 'bulk_processing', max_requests=5, time_window=600):
            st.error("⚠️ Bulk processing rate limit reached. Please wait before trying again.")
            return

        start_time = time.time()
        logger.log_user_action("bulk_processing", files_count=len(ready_files), max_workers=max_workers)

        st.markdown("---")
        st.markdown(f"### 🚀 Bulk Processing {len(ready_files)} Resumes...")

        if show_progress:
            progress_bar = st.progress(0)
            status_text = st.empty()
            progress_bar.progress(0.1)
            status_text.text("Starting parallel processing...")

        with st.spinner("Processing resumes in parallel..."):
            processed_resumes, failed_resumes = self.resume_manager.process_bulk_resumes(files_data, max_workers)

        processing_time = time.time() - start_time

        if show_progress:
            progress_bar.progress(0.6)
            status_text.text(f"Processed {len(processed_resumes)} resumes successfully...")

        email_results = []
        if bulk_email_mode == "Send emails in parallel" and processed_resumes:
            if show_progress:
                status_text.text("Sending emails in batches...")
            with st.spinner("Sending emails in batches..."):
                email_results = self.resume_manager.send_batch_emails(processed_resumes)

        total_time = time.time() - start_time

        if show_progress:
            progress_bar.progress(1.0)
            status_text.text("✅ Bulk processing completed!")

        self.display_bulk_results(processed_resumes, failed_resumes, email_results, start_time, processing_time, max_workers)
        if performance_stats:
            self.display_performance_stats(total_time, processing_time, max_workers, len(processed_resumes))

    def display_bulk_results(self, processed_resumes, failed_resumes, email_results, start_time, processing_time, max_workers):
        """Display bulk processing results."""
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Processed", len(processed_resumes))
        with col2:
            st.metric("Failed", len(failed_resumes))
        with col3:
            st.metric("Emails Sent", len([r for r in email_results if r['success']]))

        if failed_resumes:
            st.error(f"❌ Failed resumes: {', '.join(failed_resumes)}")
        if email_results:
            self.display_email_results(email_results)

    def display_performance_stats(self, total_time, processing_time, max_workers, num_processed):
        """Display detailed performance statistics."""
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Time (s)", f"{total_time:.2f}")
        col2.metric("Processing Time (s)", f"{processing_time:.2f}")
        col3.metric("Workers", max_workers)

    def display_email_results(self, email_results):
        """Display email sending results."""
        for result in email_results:
            status = "✅" if result['success'] else "❌"
            st.write(f"{status} {result['recipient']}: {result.get('error', 'Sent')}")

    def send_all_resumes_via_email(self, uploaded_files):
        """Process and send all resumes via email in one go."""
        tasks = []
        for file in uploaded_files:
            data = st.session_state.resume_inputs.get(file.name, {})
            tasks.append({
                'file': file,
                'data': data
            })
        if not tasks:
            st.error("❌ No resumes are ready for email sending. Please configure email settings and add tech stack data for at least one resume.")
            return

        with st.spinner(f"Sending {len(tasks)} emails..."):
            successful_emails = self.resume_manager.send_all_resumes_via_email([t['file'] for t in tasks])
        st.success(f"🎉 Bulk email operation completed! {len(successful_emails)}/{len(tasks)} emails sent successfully.")