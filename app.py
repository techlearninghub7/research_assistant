import gradio as gr
from dotenv import load_dotenv
from research_manager import ResearchManager
import asyncio
import time
import tempfile
import os
from typing import List
import json
import re
from bs4 import BeautifulSoup

load_dotenv()

# CSS for professional styling
professional_css = """
:root {
    --primary: #2563eb;
    --primary-dark: #1d4ed8;
    --secondary: #64748b;
    --success: #10b981;
    --warning: #f59e0b;
    --error: #ef4444;
    --background: #f8fafc;
    --card: #ffffff;
    --text: #1e293b;
    --border: #e2e8f0;
}

body {
    font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
    margin: 0;
    padding: 20px;
}

.gradio-container {
    max-width: 1200px !important;
    margin: 0 auto !important;
    background: transparent !important;
    box-shadow: none !important;
}

.main-container {
    background: var(--card) !important;
    border-radius: 16px !important;
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04) !important;
    border: 1px solid var(--border) !important;
}

.header {
    background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
    color: white;
    padding: 30px;
    border-radius: 16px 16px 0 0;
    text-align: center;
}

.header h1 {
    margin: 0;
    font-size: 2.5em;
    font-weight: 700;
    background: linear-gradient(45deg, #fff, #e0e7ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.header p {
    margin: 10px 0 0 0;
    opacity: 0.9;
    font-size: 1.1em;
}

.content {
    padding: 30px;
}

.config-section {
    background: var(--background);
    padding: 20px;
    border-radius: 12px;
    margin-bottom: 25px;
    border: 1px solid var(--border);
}

.config-section h3 {
    margin-top: 0;
    color: var(--primary);
    display: flex;
    align-items: center;
    gap: 10px;
}

.config-section h3::before {
    content: "⚙️";
}

.query-section {
    margin-bottom: 25px;
}

.query-textbox {
    border: 2px solid var(--border) !important;
    border-radius: 12px !important;
    padding: 15px !important;
    font-size: 16px !important;
}

.query-textbox:focus {
    border-color: var(--primary) !important;
    box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1) !important;
}

.btn-primary {
    background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%) !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 12px 24px !important;
    font-weight: 600 !important;
    transition: all 0.2s ease !important;
}

.btn-primary:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 10px 15px -3px rgba(37, 99, 235, 0.3) !important;
}

.btn-secondary {
    background: var(--background) !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    padding: 12px 24px !important;
}

.progress-section {
    background: var(--background);
    padding: 20px;
    border-radius: 12px;
    margin-bottom: 25px;
    border: 1px solid var(--border);
}

.progress-section h3 {
    margin-top: 0;
    color: var(--primary);
    display: flex;
    align-items: center;
    gap: 10px;
}

.progress-section h3::before {
    content: "📊";
}

.status-indicator {
    padding: 15px;
    border-radius: 12px;
    background: var(--card);
    border: 1px solid var(--border);
    font-weight: 500;
}

.report-section {
    background: var(--background);
    padding: 25px;
    border-radius: 12px;
    border: 1px solid var(--border);
}

.report-section h3 {
    margin-top: 0;
    color: var(--primary);
    display: flex;
    align-items: center;
    gap: 10px;
}

.report-section h3::before {
    content: "📋";
}

.report-output {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    padding: 20px !important;
    min-height: 400px !important;
    max-height: 600px !important;
    overflow-y: auto !important;
}

.report-output h1, .report-output h2, .report-output h3 {
    color: var(--primary) !important;
}

.report-output code {
    background: var(--background) !important;
    padding: 2px 6px !important;
    border-radius: 4px !important;
}

.footer {
    text-align: center;
    padding: 20px;
    color: var(--secondary);
    font-size: 0.9em;
    border-top: 1px solid var(--border);
}

/* Animation for status updates */
@keyframes pulse {
    0% { opacity: 1; }
    50% { opacity: 0.7; }
    100% { opacity: 1; }
}

.pulse {
    animation: pulse 2s infinite;
}

/* Loading spinner */
.spinner {
    border: 2px solid var(--border);
    border-top: 2px solid var(--primary);
    border-radius: 50%;
    width: 20px;
    height: 20px;
    animation: spin 1s linear infinite;
    display: inline-block;
    margin-right: 10px;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

/* Responsive design */
@media (max-width: 768px) {
    .gradio-container {
        padding: 10px !important;
    }
    
    .header h1 {
        font-size: 2em !important;
    }
    
    .content {
        padding: 15px !important;
    }
}
"""

async def run_research(query: str):
    """Run the research process and yield updates"""
    manager = ResearchManager()
    
    try:
        async for update in manager.run(query):
            yield update
    except Exception as e:
        yield f"❌ Error during research: {str(e)}"

def create_status_display(status_text: str) -> str:
    """Create formatted status display"""
    if status_text.startswith("✅"):
        return f"<div style='color: var(--success); padding: 10px; background: #f0fdf4; border-radius: 8px; border: 1px solid #bbf7d0;'>{status_text}</div>"
    elif status_text.startswith("⚠️"):
        return f"<div style='color: var(--warning); padding: 10px; background: #fffbeb; border-radius: 8px; border: 1px solid #fde68a;'>{status_text}</div>"
    elif status_text.startswith("❌"):
        return f"<div style='color: var(--error); padding: 10px; background: #fef2f2; border-radius: 8px; border: 1px solid #fecaca;'>{status_text}</div>"
    else:
        return f"<div style='color: var(--text); padding: 10px; background: var(--background); border-radius: 8px; border: 1px solid var(--border);'>{status_text}</div>"

def format_report(markdown_text: str) -> str:
    """Format the report with better styling"""
    if not markdown_text or markdown_text.startswith("❌"):
        return markdown_text
    
    # Basic markdown to HTML conversion for better display
    html_content = markdown_text
    html_content = html_content.replace("# ", "<h1>").replace("\n#", "</h1>\n<h1>")
    html_content = html_content.replace("## ", "<h2>").replace("\n##", "</h2>\n<h2>")
    html_content = html_content.replace("### ", "<h3>").replace("\n###", "</h3>\n<h3>")
    html_content = html_content.replace("**", "<strong>").replace("**", "</strong>")
    html_content = html_content.replace("*", "<em>").replace("*", "</em>")
    html_content = html_content.replace("`", "<code>").replace("`", "</code>")
    html_content = html_content.replace("\n- ", "\n<li>").replace("\n-", "</li>\n<li>")
    html_content = html_content.replace("\n", "<br>")
    
    return f"""
    <div style="font-family: 'Inter', sans-serif; line-height: 1.6;">
        {html_content}
    </div>
    """

def export_report(report_html: str):
    """Export report to a temporary file and return the file path"""
    # Extract text content from HTML

    
    # Try to extract text from HTML
    try:
        soup = BeautifulSoup(report_html, 'html.parser')
        report_text = soup.get_text()
    except:
        # Fallback: use regex to remove HTML tags
        report_text = re.sub('<[^<]+?>', '', report_html)
    
    # If no meaningful content, return None
    if not report_text or len(report_text.strip()) < 10:
        return None
    
    # Create a temporary file
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    temp_dir = tempfile.mkdtemp()
    file_path = os.path.join(temp_dir, f"research_report_{timestamp}.md")
    
    # Write the report content to the file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(report_text)
    
    # Return the file path
    return file_path

def clear_all():
    """Clear all inputs and outputs"""
    return "", "<div style='color: var(--secondary); text-align: center; padding: 20px;'>Waiting to start research...</div>", "<div style='color: var(--secondary); text-align: center; padding: 40px;'>Research report will appear here</div>"

with gr.Blocks(
    theme=gr.themes.Soft(primary_hue="blue"), 
    css=professional_css,
    title="Deep Research Pro | AI-Powered Research Assistant"
) as app:
    
    # Header Section
    with gr.Column(elem_classes="header"):
        gr.Markdown("""
        # 🔍 Deep Research Pro
        *Enterprise-Grade AI Research Assistant*
        """)
    
    # Main Content
    with gr.Column(elem_classes="content"):
        # Configuration Section
        with gr.Column(elem_classes="config-section"):
            gr.Markdown("""
            ### Configuration
            """)
            with gr.Row():
                model_info = gr.Textbox(
                    label="Active AI Model",
                    value="Gemini Pro (AI-Powered)",
                    interactive=False,
                    elem_classes="status-indicator"
                )
                status_indicator = gr.Textbox(
                    label="System Status",
                    value="🟢 Online & Ready",
                    interactive=False,
                    elem_classes="status-indicator"
                )
        
        # Query Section
        with gr.Column(elem_classes="query-section"):
            gr.Markdown("""
            ### Research Query
            """)
            query_input = gr.Textbox(
                label="What would you like to research today?",
                placeholder="Enter a detailed research topic (e.g., 'Impact of artificial intelligence on healthcare in 2024')...",
                lines=3,
                max_lines=5,
                elem_classes="query-textbox"
            )
            
            with gr.Row():
                run_btn = gr.Button("🚀 Start Research", variant="primary", elem_classes="btn-primary")
                clear_btn = gr.Button("🗑️ Clear All", elem_classes="btn-secondary")
                export_btn = gr.Button("📤 Export Report", elem_classes="btn-secondary")
        
        # Progress Section
        with gr.Column(elem_classes="progress-section"):
            gr.Markdown("""
            ### Research Progress
            """)
            progress_status = gr.HTML(
                value="<div style='color: var(--secondary); text-align: center; padding: 20px;'>Waiting to start research...</div>",
                label="Current Status"
            )
        
        # Report Section
        with gr.Column(elem_classes="report-section"):
            gr.Markdown("""
            ### Research Report
            """)
            report_output = gr.HTML(
                label="Comprehensive Analysis",
                elem_classes="report-output"
            )
    
    # Footer
    with gr.Column(elem_classes="footer"):
        gr.Markdown("""
        ---
        **Deep Research Pro** v2.0 • Powered by Gemini AI • © 2024 Research Assistant Inc.
        *Enterprise-grade AI research solutions for professionals*
        """)
    
    # Store the report content for export
    current_report = gr.State(value="")
    
    # Event Handlers
    def update_progress(status_text):
        """Update progress display with formatted status"""
        return create_status_display(status_text)
    
    def update_report(report_text):
        """Update report display with formatted content"""
        formatted = format_report(report_text)
        return formatted, report_text  # Return both formatted HTML and raw text
    
    # Connect event handlers
    run_btn.click(
        fn=run_research,
        inputs=[query_input],
        outputs=[progress_status]
    ).then(
        fn=update_report,
        inputs=[progress_status],
        outputs=[report_output, current_report]
    )
    
    clear_btn.click(
        fn=clear_all,
        outputs=[query_input, progress_status, report_output]
    ).then(
        fn=lambda: "",  # Clear the stored report
        outputs=[current_report]
    )
    
    export_btn.click(
        fn=export_report,
        inputs=[current_report],
        outputs=[gr.File(label="Download Report")]
    )
    
    query_input.submit(
        fn=run_research,
        inputs=[query_input],
        outputs=[progress_status]
    ).then(
        fn=update_report,
        inputs=[progress_status],
        outputs=[report_output, current_report]
    )

if __name__ == "__main__":
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        favicon_path=None,
        inbrowser=True
    )