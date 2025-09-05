"""
Requirements Management Module for Resume Customizer
Handles CRUD operations for job requirements
"""
import streamlit as st
from typing import Dict, List, Optional, Any
import json
import os
from pathlib import Path
from datetime import datetime
from logger import get_logger

logger = get_logger()

class RequirementsManager:
    """Manages job requirements CRUD operations."""
    
    def __init__(self, storage_file: str = "requirements.json"):
        """Initialize RequirementsManager with storage file."""
        self.storage_file = storage_file
        self.requirements = self._load_requirements()
        
    def _get_storage_path(self) -> Path:
        """Get the full path to the requirements storage file."""
        return Path(__file__).parent.parent / self.storage_file
    
    def _load_requirements(self) -> Dict[str, Dict[str, Any]]:
        """Load requirements from JSON file."""
        try:
            path = self._get_storage_path()
            if path.exists():
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading requirements: {e}")
        return {}
    
    def _save_requirements(self):
        """Save requirements to JSON file."""
        try:
            path = self._get_storage_path()
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(self.requirements, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving requirements: {e}")
            st.error("Failed to save requirements. Please check logs for details.")
    
    def create_requirement(self, requirement_data: Dict[str, Any]) -> str:
        """Create a new requirement."""
        try:
            requirement_id = f"req_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            # Create a copy to avoid modifying the input dictionary
            requirement_data = requirement_data.copy()
            requirement_data.update({
                'id': requirement_id,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            })
            # Ensure vendor_info exists
            if 'vendor_info' not in requirement_data:
                requirement_data['vendor_info'] = {}
            # Ensure consultants exists and is a list
            if 'consultants' not in requirement_data or not isinstance(requirement_data['consultants'], list):
                requirement_data['consultants'] = []
                
            self.requirements[requirement_id] = requirement_data
            self._save_requirements()
            return requirement_id
        except Exception as e:
            logger.error(f"Error creating requirement: {e}")
            st.error("Failed to create requirement. Please check logs for details.")
            raise
    
    def get_requirement(self, requirement_id: str) -> Optional[Dict[str, Any]]:
        """Get a requirement by ID."""
        return self.requirements.get(requirement_id)
    
    def update_requirement(self, requirement_id: str, update_data: Dict[str, Any]) -> bool:
        """Update an existing requirement."""
        try:
            if requirement_id not in self.requirements:
                logger.error(f"Requirement with ID {requirement_id} not found")
                return False
            
            # Preserve created_at if it exists
            if 'created_at' in self.requirements[requirement_id]:
                update_data['created_at'] = self.requirements[requirement_id]['created_at']
                
            update_data['updated_at'] = datetime.now().isoformat()
            self.requirements[requirement_id].update(update_data)
            self._save_requirements()
            return True
        except Exception as e:
            logger.error(f"Error updating requirement {requirement_id}: {e}")
            st.error("Failed to update requirement. Please check logs for details.")
            return False
    
    def delete_requirement(self, requirement_id: str) -> bool:
        """Delete a requirement."""
        if requirement_id in self.requirements:
            del self.requirements[requirement_id]
            self._save_requirements()
            return True
        return False
    
    def list_requirements(self) -> List[Dict[str, Any]]:
        """List all requirements."""
        return list(self.requirements.values())


def render_requirement_form(requirement_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Render the requirement form and return form data."""
    is_edit = requirement_data is not None
    
    # Initialize form data with defaults or existing values
    form_data = {
        'job_title': '',
        'client': '',
        'prime_vendor': '',
        'status': 'Applied',
        'next_steps': '',
        'consultants': [],
        'vendor_info': {
            'name': '',
            'company': '',
            'phone': '',
            'email': ''
        },
        'interview_id': ''
    }
    
    if is_edit:
        form_data.update(requirement_data)
        # Ensure nested dictionaries are properly initialized
        if 'vendor_info' not in form_data:
            form_data['vendor_info'] = {
                'name': '',
                'company': '',
                'phone': '',
                'email': ''
            }
        if 'consultants' not in form_data:
            form_data['consultants'] = []
    
    # Create form
    with st.form(key='requirement_form'):
        st.subheader("📝 " + ("Edit" if is_edit else "Create New") + " Requirement")
        
        # Record number (auto-generated)
        if is_edit and 'id' in form_data:
            st.caption(f"Record #: {form_data['id']}")
        
        # Date & Time
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if is_edit and 'created_at' in form_data:
            st.caption(f"Created: {form_data['created_at']}")
        else:
            st.caption(f"Date & Time: {current_time}")
        
        # Form fields
        col1, col2 = st.columns(2)
        
        with col1:
            # Job Title
            form_data['job_title'] = st.text_input(
                "Job Title*",
                value=form_data['job_title'],
                placeholder="E.g., Senior Software Engineer"
            )
            
            # Client
            form_data['client'] = st.text_input(
                "Client*",
                value=form_data.get('client', ''),
                placeholder="Client company name"
            )
            
            # Prime Vendor
            form_data['prime_vendor'] = st.text_input(
                "Prime Vendor",
                value=form_data.get('prime_vendor', ''),
                placeholder="Prime vendor company name"
            )
            
            # Status
            status_options = ["Applied", "No Response", "Submitted", "On Hold", "Interviewed"]
            form_data['status'] = st.selectbox(
                "Status*",
                options=status_options,
                index=status_options.index(form_data['status']) if 'status' in form_data and form_data['status'] in status_options else 0
            )
            
            # Next Steps
            form_data['next_steps'] = st.text_area(
                "Next Steps",
                value=form_data.get('next_steps', ''),
                height=100,
                placeholder="Add next steps for this requirement"
            )
            
            # Interview ID (visible only when status is Submitted)
            if form_data['status'] == 'Submitted':
                # Store current interview ID in session state
                interview_id_key = f"interview_id_{form_data.get('id', 'new')}"
                if interview_id_key not in st.session_state:
                    st.session_state[interview_id_key] = form_data.get('interview_id', '')
                
                # Display the interview ID field
                form_data['interview_id'] = st.text_input(
                    "Interview ID",
                    value=st.session_state[interview_id_key],
                    placeholder="Click 'Generate Interview ID' button below"
                )
        
        with col2:
            # Vendor Information Section
            st.subheader("Vendor Information")
            
            form_data['vendor_info']['name'] = st.text_input(
                "Vendor Name",
                value=form_data['vendor_info'].get('name', ''),
                placeholder="Vendor contact person"
            )
            
            form_data['vendor_info']['company'] = st.text_input(
                "Vendor Company",
                value=form_data['vendor_info'].get('company', ''),
                placeholder="Vendor company name"
            )
            
            form_data['vendor_info']['phone'] = st.text_input(
                "Vendor Phone",
                value=form_data['vendor_info'].get('phone', ''),
                placeholder="Vendor contact number"
            )
            
            form_data['vendor_info']['email'] = st.text_input(
                "Vendor Email",
                value=form_data['vendor_info'].get('email', ''),
                placeholder="Vendor email address"
            )
            
            # Consultants Section
            st.subheader("Consultants")
            
            # Set available consultants
            available_consultants = ['Raju', 'Eric']
            
            # Display consultant selection dropdown
            selected_consultants = st.multiselect(
                "Select Consultants",
                options=available_consultants,
                default=available_consultants,  # Both selected by default
                key=f"consultants_select_{form_data.get('id', 'new')}"
            )
            
            # Store selected consultants in form data
            form_data['consultants'] = selected_consultants
        
        # Form submit button
        submitted = st.form_submit_button("💾 Save Requirement")
    
    # Generate Interview ID button
    if form_data.get('status') == 'Submitted':
        if st.button("🎯 Generate Interview ID", key=f"gen_id_{form_data.get('id', 'new')}"):
            interview_id = f"INT-{datetime.now().strftime('%Y%m%d')}-{len(form_data.get('job_title', '').split())}{len(form_data.get('client', '').split())}"
            interview_id_key = f"interview_id_{form_data.get('id', 'new')}"
            st.session_state[interview_id_key] = interview_id
            form_data['interview_id'] = interview_id
            st.experimental_rerun()
            
        # Store the current interview ID in session state
        if 'interview_id' in form_data and form_data['interview_id']:
            interview_id_key = f"interview_id_{form_data.get('id', 'new')}"
            st.session_state[interview_id_key] = form_data['interview_id']
        
        if submitted:
            try:
                # Basic validation
                if not form_data['job_title'].strip() or not form_data['client'].strip():
                    st.error("Please fill in all required fields (marked with *)")
                    return None
                    
                # Get consultants from session state
                consultants_key = f"consultants_{form_data.get('id', 'new')}"
                if consultants_key in st.session_state:
                    form_data['consultants'] = [c.strip() for c in st.session_state[consultants_key] if c and c.strip()]
                    # Clean up session state after form submission
                    del st.session_state[consultants_key]
                
                # Ensure vendor_info exists and has all required fields
                if 'vendor_info' not in form_data:
                    form_data['vendor_info'] = {}
                    
                # Ensure all vendor_info fields exist
                for field in ['name', 'company', 'phone', 'email']:
                    if field not in form_data['vendor_info']:
                        form_data['vendor_info'][field] = ''
                
                # Set timestamps
                if not is_edit:
                    form_data['created_at'] = current_time
                form_data['updated_at'] = current_time
                
                return form_data
                
            except Exception as e:
                logger.error(f"Error processing form submission: {e}")
                st.error("An error occurred while processing your request. Please try again.")
                return None
    
    return None

def render_requirements_list(requirements_manager: RequirementsManager):
    """Render the list of requirements with actions."""
    st.subheader("📋 Requirements List")
    
    requirements = requirements_manager.list_requirements()
    
    if not requirements:
        st.info("No requirements found. Create one using the form above.")
        return
    
    # Sort requirements by creation date (newest first)
    requirements.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    
    for req in requirements:
        # Format the title with status, record number, job title and client
        status_emoji = {
            'Applied': '📝',
            'No Response': '⏳',
            'Submitted': '📤',
            'On Hold': '⏸️',
            'Interviewed': '✅'
        }.get(req.get('status', 'Applied'), '📌')
        
        record_num = f"#{req.get('id', 'N/A').split('_')[-1]}" if 'id' in req else "#N/A"
        title = f"{status_emoji} {record_num} - {req.get('job_title', 'Untitled')} @ {req.get('client', 'Unknown Client')}"
        
        with st.expander(title):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                # Status and Client Info
                st.markdown(f"**Status:** {req.get('status', 'Not specified')}")
                
                if req.get('client'):
                    st.markdown(f"**Client:** {req['client']}")
                
                if req.get('prime_vendor'):
                    st.markdown(f"**Prime Vendor:** {req['prime_vendor']}")
                
                # Vendor Information
                if 'vendor_info' in req and any(req['vendor_info'].values()):
                    with st.expander("Vendor Details"):
                        if req['vendor_info'].get('name'):
                            st.markdown(f"**Name:** {req['vendor_info']['name']}")
                        if req['vendor_info'].get('company'):
                            st.markdown(f"**Company:** {req['vendor_info']['company']}")
                        if req['vendor_info'].get('phone'):
                            st.markdown(f"**Phone:** {req['vendor_info']['phone']}")
                        if req['vendor_info'].get('email'):
                            st.markdown(f"**Email:** {req['vendor_info']['email']}")
                
                # Consultants
                if req.get('consultants'):
                    with st.expander(f"👥 Consultants ({len(req['consultants'])})"):
                        for consultant in req['consultants']:
                            if consultant.strip():
                                st.markdown(f"- {consultant}")
                
                # Next Steps
                if req.get('next_steps'):
                    with st.expander("Next Steps"):
                        st.write(req['next_steps'])
                
                # Interview ID (if exists)
                if req.get('status') == 'Submitted' and req.get('interview_id'):
                    st.markdown(f"**Interview ID:** `{req['interview_id']}`")
                
                # Timestamp
                if 'created_at' in req:
                    st.caption(f"Created: {req['created_at']}")
                if 'updated_at' in req and req['updated_at'] != req.get('created_at'):
                    st.caption(f"Last Updated: {req['updated_at']}")
            
            with col2:
                # Action buttons
                if st.button("✏️ Edit", key=f"edit_{req['id']}"):
                    st.session_state.editing_requirement = req
                    st.experimental_rerun()
                
                if st.button("🗑️ Delete", key=f"delete_{req['id']}"):
                    if requirements_manager.delete_requirement(req['id']):
                        st.success(f"Successfully deleted requirement: {req.get('job_title', 'Untitled')}")
                        st.experimental_rerun()
                    else:
                        st.error("Failed to delete requirement")
