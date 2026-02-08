"""
Streamlit frontend for Document Analyzer.
"""
import json
import time
from pathlib import Path
from datetime import datetime
import streamlit as st
import requests

# Configure page
st.set_page_config(
    page_title="Document Analyzer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .status-box {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .status-processing {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
    }
    .status-completed {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
    }
    .status-failed {
        background-color: #f8d7da;
        border-left: 4px solid #dc3545;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #dee2e6;
    }
    .stButton>button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# API Configuration
API_BASE_URL = "http://localhost:8000"

# Initialize session state
if 'job_id' not in st.session_state:
    st.session_state.job_id = None
if 'results' not in st.session_state:
    st.session_state.results = None
if 'status' not in st.session_state:
    st.session_state.status = None


def upload_file(file):
    """Upload file to backend API."""
    try:
        files = {"file": (file.name, file, file.type)}
        response = requests.post(f"{API_BASE_URL}/api/analyze", files=files)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error uploading file: {str(e)}")
        return None


def check_status(job_id):
    """Check job status."""
    try:
        response = requests.get(f"{API_BASE_URL}/api/status/{job_id}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error checking status: {str(e)}")
        return None


def get_results(job_id):
    """Get analysis results."""
    try:
        response = requests.get(f"{API_BASE_URL}/api/results/{job_id}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        if "202" in str(e):
            return None  # Still processing
        st.error(f"Error getting results: {str(e)}")
        return None


def display_result_summary(result):
    """Display summary of analysis results."""
    st.markdown("### 📊 Document Summary")
    
    # Extract key information
    doc_class = result.get('document_classification', {})
    source = result.get('source', {})
    content = result.get('content', {})
    confidence = result.get('confidence_quality', {})
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Document Type", doc_class.get('type', 'N/A'))
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Category", doc_class.get('category', 'N/A'))
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Language", doc_class.get('primary_language', 'N/A'))
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Confidence", confidence.get('overall_confidence', 'N/A'))
        st.markdown('</div>', unsafe_allow_html=True)


def display_detailed_results(result, page_num):
    """Display detailed analysis results."""
    
    # Tabs for different sections
    tabs = st.tabs([
        "📋 Content",
        "🏢 Source Info",
        "✍️ Signatures",
        "📊 Data",
        "🔍 Full JSON"
    ])
    
    # Content Tab
    with tabs[0]:
        content = result.get('content', {})
        
        if content.get('subject'):
            st.markdown("#### Subject")
            st.write(content['subject'])
        
        if content.get('full_text'):
            st.markdown("#### Full Text")
            with st.expander("View full text", expanded=False):
                st.text(content['full_text'])
        
        if content.get('keywords'):
            st.markdown("#### Keywords")
            st.write(", ".join(content['keywords']))
        
        # Tables
        if content.get('has_tables') and content.get('tables'):
            st.markdown("#### Tables")
            for i, table in enumerate(content['tables'], 1):
                st.markdown(f"**Table {i}**")
                if table.get('title'):
                    st.caption(table['title'])
                
                # Display table
                if table.get('headers') and table.get('rows'):
                    import pandas as pd
                    df = pd.DataFrame(table['rows'], columns=table['headers'])
                    st.dataframe(df, use_container_width=True)
        
        # Charts
        if content.get('has_charts') and content.get('charts'):
            st.markdown("#### Charts")
            for i, chart in enumerate(content['charts'], 1):
                st.markdown(f"**Chart {i}: {chart.get('title', 'Untitled')}**")
                st.caption(chart.get('description', ''))
                
                if chart.get('data'):
                    import pandas as pd
                    df = pd.DataFrame(chart['data'])
                    st.bar_chart(df.set_index('label')['value'])
    
    # Source Info Tab
    with tabs[1]:
        source = result.get('source', {})
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Issuing Authority")
            st.write(source.get('issuing_authority', 'N/A'))
            
            if source.get('department'):
                st.markdown("#### Department")
                st.write(source['department'])
            
            if source.get('document_number'):
                st.markdown("#### Document Number")
                st.code(source['document_number'])
        
        with col2:
            dates = source.get('dates', {})
            if dates.get('primary_date'):
                st.markdown("#### Primary Date")
                pd = dates['primary_date']
                st.write(f"{pd.get('date_text', 'N/A')} ({pd.get('calendar_type', 'unknown')})")
            
            if source.get('location'):
                st.markdown("#### Location")
                st.write(source['location'])
    
    # Signatures Tab
    with tabs[2]:
        sig_auth = result.get('signatures_authorization', {})
        
        if sig_auth.get('signatories'):
            st.markdown("#### Signatories")
            for sig in sig_auth['signatories']:
                with st.container():
                    st.markdown(f"**{sig.get('name', 'N/A')}**")
                    st.caption(f"Title: {sig.get('title', 'N/A')}")
                    st.caption(f"Type: {sig.get('signature_type', 'N/A')} | Role: {sig.get('role', 'N/A')}")
                    st.divider()
        
        if sig_auth.get('approval_chain'):
            st.markdown("#### Approval Chain")
            for step in sig_auth['approval_chain']:
                st.write(f"**Step {step.get('step')}:** {step.get('role', 'N/A')}")
                if step.get('name'):
                    st.write(f"Name: {step['name']}")
                if step.get('title'):
                    st.write(f"Title: {step['title']}")
    
    # Data Tab
    with tabs[3]:
        content = result.get('content', {})
        
        # Financial Data
        if content.get('financial_data'):
            st.markdown("#### Financial Data")
            for item in content['financial_data']:
                st.write(f"**{item.get('description', 'N/A')}:** {item.get('amount', 'N/A')} {item.get('currency', '')}")
        
        # Legal Articles
        if content.get('legal_articles'):
            st.markdown("#### Legal Articles")
            for article in content['legal_articles']:
                with st.expander(f"{article.get('article_number', 'N/A')}"):
                    if article.get('article_title'):
                        st.markdown(f"**{article['article_title']}**")
                    st.write(article.get('content', 'N/A'))
        
        # Official Marks
        official = result.get('official_marks', {})
        
        if official.get('seals'):
            st.markdown("#### Seals")
            for seal in official['seals']:
                st.write(f"**{seal.get('organization', 'N/A')}** ({seal.get('shape', 'N/A')})")
        
        if official.get('stamps'):
            st.markdown("#### Stamps")
            for stamp in official['stamps']:
                st.write(f"**{stamp.get('type', 'N/A')}:** {stamp.get('text_content', 'N/A')}")
    
    # Full JSON Tab
    with tabs[4]:
        st.json(result)


def main():
    """Main application."""
    
    # Header
    st.markdown('<div class="main-header">📄 Document Analyzer</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Extract structured data from documents using AI</div>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 🎯 Upload Document")
        st.markdown("Supported formats: PDF, JPG, PNG")
        
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=['pdf', 'jpg', 'jpeg', 'png'],
            help="Upload a document to analyze"
        )
        
        analyze_button = st.button("🚀 Analyze Document", type="primary", disabled=uploaded_file is None)
        
        st.divider()
        
        # Instructions
        with st.expander("ℹ️ How to use"):
            st.markdown("""
            1. Upload a PDF or image document
            2. Click "Analyze Document"
            3. Wait for processing to complete
            4. Review the extracted data
            5. Download results as JSON
            """)
        
        # API Status
        st.divider()
        st.markdown("### 🔌 API Status")
        try:
            response = requests.get(f"{API_BASE_URL}/health", timeout=2)
            if response.status_code == 200:
                st.success("✅ Connected")
                data = response.json()
                st.caption(f"Model: {data.get('model', 'N/A')}")
            else:
                st.error("❌ API Error")
        except:
            st.error("❌ Disconnected")
            st.caption("Make sure backend is running")
    
    # Main content area
    if analyze_button and uploaded_file:
        # Upload file
        with st.spinner("Uploading file..."):
            result = upload_file(uploaded_file)
        
        if result:
            st.session_state.job_id = result.get('job_id')
            st.session_state.status = 'processing'
            st.success(f"✅ File uploaded! Job ID: {st.session_state.job_id}")
    
    # Display status and results
    if st.session_state.job_id:
        
        # Status section
        status_placeholder = st.empty()
        results_placeholder = st.empty()
        
        # Check status
        status_data = check_status(st.session_state.job_id)
        
        if status_data:
            status = status_data.get('status')
            
            # Display status
            with status_placeholder.container():
                if status == 'processing':
                    st.markdown('<div class="status-box status-processing">', unsafe_allow_html=True)
                    st.markdown("#### ⏳ Processing...")
                    st.write(f"**File:** {status_data.get('filename')}")
                    st.write(f"**Job ID:** {st.session_state.job_id}")
                    st.progress(0.5)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Auto-refresh
                    time.sleep(2)
                    st.rerun()
                
                elif status == 'completed':
                    st.markdown('<div class="status-box status-completed">', unsafe_allow_html=True)
                    st.markdown("#### ✅ Completed!")
                    st.write(f"**File:** {status_data.get('filename')}")
                    st.write(f"**Pages:** {status_data.get('page_count', 0)}")
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Get results
                    if st.session_state.results is None:
                        results_data = get_results(st.session_state.job_id)
                        if results_data:
                            st.session_state.results = results_data
                
                elif status == 'failed':
                    st.markdown('<div class="status-box status-failed">', unsafe_allow_html=True)
                    st.markdown("#### ❌ Failed")
                    st.error(f"Error: {status_data.get('error', 'Unknown error')}")
                    st.markdown('</div>', unsafe_allow_html=True)
        
        # Display results
        if st.session_state.results:
            results_data = st.session_state.results
            results_list = results_data.get('results', [])
            
            with results_placeholder.container():
                st.divider()
                
                # Download button
                col1, col2, col3 = st.columns([2, 1, 1])
                with col2:
                    json_str = json.dumps(results_data, ensure_ascii=False, indent=2)
                    st.download_button(
                        label="📥 Download JSON",
                        data=json_str,
                        file_name=f"analysis_{st.session_state.job_id}.json",
                        mime="application/json"
                    )
                with col3:
                    if st.button("🔄 New Analysis"):
                        st.session_state.job_id = None
                        st.session_state.results = None
                        st.session_state.status = None
                        st.rerun()
                
                # Display each page
                for i, result in enumerate(results_list, 1):
                    if 'error' not in result:
                        st.markdown(f"## 📄 Page {i}")
                        display_result_summary(result)
                        st.divider()
                        display_detailed_results(result, i)
                        st.divider()
                    else:
                        st.error(f"Page {i} - Error: {result['error']}")


if __name__ == "__main__":
    main()
