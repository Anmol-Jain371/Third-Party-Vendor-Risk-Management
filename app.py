import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import io
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

def create_audit_pdf(df):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40, leftMargin=40,
        topMargin=50, bottomMargin=50
    )
    
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=26,
        textColor=colors.HexColor('#0F172A'),
        spaceAfter=12
    )
    
    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=18,
        textColor=colors.HexColor('#0F172A'),
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )
    
    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Heading3'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=colors.HexColor('#06B6D4'),
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#374151'),
        spaceAfter=6
    )
    
    bullet_style = ParagraphStyle(
        'Bullet_Custom',
        parent=body_style,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=3
    )
    
    meta_style = ParagraphStyle(
        'Meta_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor('#6B7280'),
        spaceAfter=10
    )
    
    story = []
    
    # Title & Metadata
    story.append(Paragraph("Third-Party Vendor Risk Audit Report", title_style))
    timestamp = datetime.now().strftime("%B %d, %Y at %H:%M:%S")
    story.append(Paragraph(f"Generated on {timestamp} • Audit Reference Date: June 20, 2026", meta_style))
    story.append(Spacer(1, 10))
    
    # Executive Summary
    story.append(Paragraph("Executive Summary", h1_style))
    total_vendors = len(df)
    high_risk_count = len(df[df['risk_score'] >= 80])
    medium_risk_count = len(df[(df['risk_score'] >= 50) & (df['risk_score'] < 80)])
    low_risk_count = len(df[df['risk_score'] < 50])
    expired_certs_count = df['is_cert_expired'].sum()
    expired_contracts_count = df['is_contract_expired'].sum()
    total_spend = df['annual_spend'].sum()
    
    summary_text = (
        f"This GRC audit report provides a comprehensive evaluation of third-party vendors cataloged in the GRC registry as of "
        f"June 20, 2026. A total of <b>{total_vendors}</b> vendors were audited, representing a total financial exposure "
        f"of <b>€{total_spend:,.2f}</b>. Out of these, <b>{high_risk_count}</b> vendors are classified as High Risk (>=80), "
        f"<b>{medium_risk_count}</b> as Medium Risk (50-79), and <b>{low_risk_count}</b> as Low Risk (&lt;50). Currently, "
        f"<b>{expired_certs_count}</b> vendors possess expired credentials and <b>{expired_contracts_count}</b> vendors have expired "
        f"active contracts in the system."
    )
    story.append(Paragraph(summary_text, body_style))
    
    # KPI Grid Table
    kpi_data = [
        [
            Paragraph("<b>Metric</b>", body_style),
            Paragraph("<b>Count/Value</b>", body_style),
            Paragraph("<b>GRC Status</b>", body_style)
        ],
        [
            Paragraph("Total Audited Vendors", body_style),
            Paragraph(str(total_vendors), body_style),
            Paragraph("Audited", body_style)
        ],
        [
            Paragraph("High Risk Vendors (>=80)", body_style),
            Paragraph(f"<font color='#EF4444'><b>{high_risk_count}</b></font>", body_style),
            Paragraph("Critical Review" if high_risk_count > 5 else "Warning", body_style)
        ],
        [
            Paragraph("Expired Certifications", body_style),
            Paragraph(f"<font color='#EF4444'><b>{expired_certs_count}</b></font>", body_style),
            Paragraph("Action Required" if expired_certs_count > 0 else "Compliant", body_style)
        ],
        [
            Paragraph("Expired Contracts", body_style),
            Paragraph(f"<font color='#EF4444'><b>{expired_contracts_count}</b></font>", body_style),
            Paragraph("Action Required" if expired_contracts_count > 0 else "Compliant", body_style)
        ]
    ]
    kpi_table = Table(kpi_data, colWidths=[200, 150, 150])
    kpi_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F3F4F6')),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E5E7EB')),
    ]))
    story.append(kpi_table)
    story.append(Spacer(1, 10))
    
    # Compliance Coverage
    story.append(Paragraph("Compliance Coverage", h1_style))
    gdpr_count = df['certifications'].astype(str).str.contains('GDPR', case=False).sum()
    gdpr_pct = gdpr_count / total_vendors if total_vendors > 0 else 0.0
    soc2_count = df[df['certifications'].astype(str).str.contains('SOC2', case=False) & ~df['is_cert_expired']].shape[0]
    soc2_pct = soc2_count / total_vendors if total_vendors > 0 else 0.0
    active_contract_count = (df['contract_end'] > ANCHOR_DATE).sum()
    contract_pct = active_contract_count / total_vendors if total_vendors > 0 else 0.0
    
    coverage_data = [
        [
            Paragraph("<b>Compliance Metric</b>", body_style),
            Paragraph("<b>Coverage Percentage</b>", body_style),
            Paragraph("<b>Details</b>", body_style)
        ],
        [
            Paragraph("GDPR Coverage", body_style),
            Paragraph(f"<b>{gdpr_pct * 100:.1f}%</b>", body_style),
            Paragraph(f"{gdpr_count} of {total_vendors} vendors with DPA", body_style)
        ],
        [
            Paragraph("SOC2 Coverage (Active)", body_style),
            Paragraph(f"<b>{soc2_pct * 100:.1f}%</b>", body_style),
            Paragraph(f"{soc2_count} of {total_vendors} active SOC2", body_style)
        ],
        [
            Paragraph("Active Contract Coverage", body_style),
            Paragraph(f"<b>{contract_pct * 100:.1f}%</b>", body_style),
            Paragraph(f"{active_contract_count} of {total_vendors} active contracts", body_style)
        ]
    ]
    coverage_table = Table(coverage_data, colWidths=[200, 150, 150])
    coverage_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F3F4F6')),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E5E7EB')),
    ]))
    story.append(coverage_table)
    story.append(Spacer(1, 10))
    
    # Top 5 Priority Vendors
    story.append(Paragraph("Top 5 Priority High Risk Vendors", h1_style))
    sev_map = {'CRITICAL': 5, 'HIGH': 4, 'MEDIUM': 3, 'LOW': 2, 'NONE': 1}
    breach_map = {'BREACHED_RECENT': 4, 'BREACHED_LAST_12_MONTHS': 3, 'UNDER_INVESTIGATION': 2, 'NONE': 1}
    temp_df = df.copy()
    temp_df['sev_rank'] = temp_df['severity'].map(sev_map).fillna(0)
    temp_df['breach_rank'] = temp_df['breach_status'].map(breach_map).fillna(0)
    top_vendors = temp_df.sort_values(
        by=['sev_rank', 'risk_score', 'breach_rank'],
        ascending=[False, False, False]
    ).head(5)
    
    priority_rows = [
        [
            Paragraph("<b>Vendor ID</b>", body_style),
            Paragraph("<b>Category</b>", body_style),
            Paragraph("<b>Risk Score</b>", body_style),
            Paragraph("<b>Severity</b>", body_style),
            Paragraph("<b>Anomaly Type</b>", body_style)
        ]
    ]
    for _, v in top_vendors.iterrows():
        priority_rows.append([
            Paragraph(v['vendor_id'], body_style),
            Paragraph(v['type'].title(), body_style),
            Paragraph(f"<b>{v['risk_score']}</b>", body_style),
            Paragraph(v['severity'], body_style),
            Paragraph(v['anomaly_type'].replace('_', ' ').title(), body_style)
        ])
        
    priority_table = Table(priority_rows, colWidths=[90, 110, 80, 80, 140])
    priority_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F3F4F6')),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E5E7EB')),
    ]))
    story.append(priority_table)
    
    # Page Break for Charts and Recommendations
    story.append(PageBreak())
    
    story.append(Paragraph("Executive Risk Visualizations", h1_style))
    story.append(Spacer(1, 5))
    
    # 1. Risk Score Distribution
    fig_risk = px.histogram(
        df,
        x="risk_score",
        color="risk_tier",
        nbins=25,
        labels={"risk_score": "Risk Score (0 - 100)", "risk_tier": "Risk Category"},
        color_discrete_map={
            'Low (<50)': '#10B981',
            'Medium (50-79)': '#F59E0B',
            'High (>=80)': '#EF4444'
        },
        title="Distribution of Vendor Risk Metrics"
    )
    fig_risk.update_layout(
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font_color="#111827",
        width=550, height=260,
        margin=dict(l=40, r=40, t=40, b=40)
    )
    try:
        img_bytes = fig_risk.to_image(format="png")
        img_buf = io.BytesIO(img_bytes)
        story.append(Image(img_buf, width=5.5*inch, height=2.6*inch))
        story.append(Spacer(1, 10))
    except Exception as ex:
        story.append(Paragraph(f"Could not render Risk Score Distribution chart: {str(ex)}", body_style))
        
    # 2. Executive Heatmap
    heatmap_data = df.groupby('type')['risk_score'].mean().reset_index()
    heatmap_data = heatmap_data.sort_values(by='risk_score', ascending=True)
    fig_heatmap = go.Figure(data=go.Heatmap(
        z=heatmap_data['risk_score'].values.reshape(-1, 1),
        y=heatmap_data['type'].values,
        x=['Average Risk Score'],
        colorscale=[
            [0.0, '#10B981'],    # Green
            [0.49, '#10B981'],
            [0.50, '#F59E0B'],   # Yellow
            [0.79, '#F59E0B'],
            [0.80, '#EF4444'],   # Red
            [1.0, '#EF4444']
        ],
        zmin=0,
        zmax=100,
        text=heatmap_data['risk_score'].round(1).values.reshape(-1, 1),
        texttemplate="%{text}",
        textfont={"size": 11, "family": "Helvetica", "weight": "bold"},
        showscale=False
    ))
    fig_heatmap.update_layout(
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font_family="Helvetica",
        width=550, height=180,
        margin=dict(l=150, r=40, t=30, b=30)
    )
    try:
        img_bytes_h = fig_heatmap.to_image(format="png")
        img_buf_h = io.BytesIO(img_bytes_h)
        story.append(Paragraph("<b>Average Risk Profile Heatmap by Category</b>", h2_style))
        story.append(Image(img_buf_h, width=5.5*inch, height=1.8*inch))
        story.append(Spacer(1, 10))
    except Exception as ex:
        story.append(Paragraph(f"Could not render Heatmap: {str(ex)}", body_style))
        
    # Recommended GRC Actions
    story.append(Paragraph("Recommended GRC Actions", h1_style))
    story.append(Paragraph("Based on GRC risk and contract standings, the following actions are recommended:", body_style))
    
    actions = [
        "<b>Immediate Review of Critical Vendors:</b> Review and restrict access for all vendors flagged under investigation (CRITICAL rating).",
        "<b>Certification Renewal Protocols:</b> Actively engage the 42 vendors with expired SOC2/ISO certificates to renew security credentials immediately.",
        "<b>Orphaned Contract Containment:</b> Initiate system lockouts or renewals for the 41 vendors with expired contract terminus dates.",
        "<b>Continuous Risk Offsets:</b> Model how completing pending audits or removing administrative privileges offsets operational risk score tiers."
    ]
    for act in actions:
        story.append(Paragraph(f"&bull; {act}", bullet_style))
        
    doc.build(story)
    buffer.seek(0)
    return buffer

def create_advisor_pdf(v_data, current_risk, risk_level, verdict, confidence_level, confidence_pct, trend, trend_text, summary_text, drivers, impacts, actions, decision, decision_rationale):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40, leftMargin=40,
        topMargin=50, bottomMargin=50
    )
    
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#0F172A'),
        spaceAfter=6
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#4B5563'),
        spaceAfter=15
    )
    
    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=colors.HexColor('#0F172A'),
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#374151'),
        spaceAfter=6
    )
    
    bullet_style = ParagraphStyle(
        'Bullet_Custom',
        parent=body_style,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=4
    )
    
    meta_style = ParagraphStyle(
        'Meta_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor('#6B7280'),
        spaceAfter=12
    )

    story = []
    
    # Title & Subtitle & Metadata
    story.append(Paragraph("AI Vendor Risk Advisor — GRC Report", title_style))
    story.append(Paragraph("Executive-grade vendor intelligence, risk explanation, and remediation guidance.", subtitle_style))
    
    timestamp = datetime.now().strftime("%B %d, %Y at %H:%M:%S")
    story.append(Paragraph(f"Generated on {timestamp} • Reference Anchor Date: June 20, 2026", meta_style))
    story.append(Spacer(1, 5))
    
    # Verdict color determination
    v_colors = {
        "APPROVED": "#10B981",
        "WATCHLIST": "#D97706",
        "HIGH RISK": "#EA580C",
        "CRITICAL REVIEW": "#DC2626"
    }
    verdict_hex = v_colors.get(verdict, "#6B7280")
    
    # Metadata Table
    meta_data = [
        [
            Paragraph("<b>Vendor ID</b>", body_style), Paragraph(str(v_data['vendor_id']), body_style),
            Paragraph("<b>Risk Score</b>", body_style), Paragraph(f"<b>{current_risk}/100</b>", body_style)
        ],
        [
            Paragraph("<b>Vendor Type</b>", body_style), Paragraph(str(v_data['type']).title(), body_style),
            Paragraph("<b>Risk Level</b>", body_style), Paragraph(str(risk_level), body_style)
        ],
        [
            Paragraph("<b>Annual Spend</b>", body_style), Paragraph(f"€{v_data['annual_spend']:,.2f}", body_style),
            Paragraph("<b>Severity</b>", body_style), Paragraph(str(v_data['severity']), body_style)
        ],
        [
            Paragraph("<b>Confidence Score</b>", body_style), Paragraph(f"{confidence_level} ({confidence_pct:.0f}%)", body_style),
            Paragraph("<b>Risk Verdict</b>", body_style), Paragraph(f"<font color='{verdict_hex}'><b>{verdict}</b></font>", body_style)
        ],
        [
            Paragraph("<b>Risk Trend Outlook</b>", body_style), Paragraph(str(trend), body_style),
            Paragraph("", body_style), Paragraph("", body_style)
        ]
    ]
    meta_table = Table(meta_data, colWidths=[120, 130, 120, 130])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#F9FAFB')),
        ('BACKGROUND', (2,0), (2,-1), colors.HexColor('#F9FAFB')),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E5E7EB')),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 10))
    
    # Executive Summary Section
    story.append(Paragraph("Executive Summary", h1_style))
    story.append(Paragraph(summary_text, body_style))
    story.append(Spacer(1, 5))
    
    # Key Risk Drivers Section
    story.append(Paragraph("Key Risk Drivers", h1_style))
    for d in drivers:
        story.append(Paragraph(f"&bull; {d}", bullet_style))
    story.append(Spacer(1, 5))
        
    # Business Impact Analysis Section
    story.append(Paragraph("Business Impact Analysis", h1_style))
    for i in impacts:
        story.append(Paragraph(f"&bull; {i}", bullet_style))
    story.append(Spacer(1, 5))
        
    # Recommended GRC Mitigation Actions
    story.append(Paragraph("Recommended GRC Mitigation Actions", h1_style))
    for a in actions:
        story.append(Paragraph(f"&bull; {a}", bullet_style))
    story.append(Spacer(1, 5))
        
    # Executive GRC Decision Section
    story.append(Paragraph("Official GRC Decision", h1_style))
    
    # Render decision as a styled box table
    decision_data = [
        [Paragraph(f"<b>RECOMMENDED ACTION: {decision}</b>", ParagraphStyle('DecisionAction', parent=body_style, fontName='Helvetica-Bold', fontSize=10, textColor=colors.HexColor(verdict_hex)))],
        [Paragraph(f"<b>Rationale:</b> {decision_rationale}", body_style)]
    ]
    decision_table = Table(decision_data, colWidths=[500])
    decision_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor(verdict_hex + '0A')), # 10% opacity hex
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('BOX', (0,0), (-1,-1), 1.5, colors.HexColor(verdict_hex)),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
    ]))
    story.append(decision_table)
    
    doc.build(story)
    buffer.seek(0)
    return buffer

ANCHOR_DATE = pd.to_datetime("2026-06-20")

# ----------------------------------------------------
# 1. PAGE CONFIGURATION & THEME SETUP
# ----------------------------------------------------
st.set_page_config(
    page_title="Third-Party Vendor Risk Management Portal",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern white/light interface (premium hackathon-ready look)
st.markdown("""
<style>
    /* Global Styles */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Inter', sans-serif;
        background-color: #F9FAFB;
        color: #111827;
    }
    
    /* Entry Animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(8px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #E5E7EB;
    }
    
    /* Sidebar navigation links (Hide radio buttons, style as menu list) */
    div[data-testid="stRadio"] > div {
        gap: 6px;
    }
    div[data-testid="stRadio"] label {
        background-color: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 8px;
        padding: 10px 14px !important;
        font-size: 0.875rem !important;
        color: #374151 !important;
        margin-bottom: 4px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.01);
        transition: all 0.2s ease;
        cursor: pointer;
    }
    div[data-testid="stRadio"] label:hover {
        background-color: #F9FAFB;
        border-color: #D1D5DB;
        color: #111827 !important;
    }
    div[data-testid="stRadio"] label:has(input[checked]) {
        background-color: #F0FDF4 !important;
        border-color: #10B981 !important;
        color: #166534 !important;
        font-weight: 600 !important;
    }
    div[data-testid="stRadio"] [data-testid="stMarker"] {
        display: none !important;
    }
    
    /* Headings */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Inter', sans-serif;
        font-weight: 800 !important;
        letter-spacing: -0.03em !important;
        color: #111827;
    }
    
    /* Custom cards for KPIs */
    .kpi-card {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 12px;
        padding: 24px;
        position: relative;
        overflow: hidden;
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        animation: fadeIn 0.4s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    }
    .kpi-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 20px -5px rgba(0,0,0,0.05), 0 8px 8px -6px rgba(0,0,0,0.05);
        border-color: #D1D5DB;
    }
    .kpi-card::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 4px;
    }
    .kpi-total::before { background-color: #06B6D4; }      /* Cyan */
    .kpi-high::before { background-color: #EF4444; }       /* Red */
    .kpi-medium::before { background-color: #F59E0B; }     /* Amber */
    .kpi-low::before { background-color: #10B981; }        /* Emerald */
    .kpi-expired::before { background-color: #F97316; }    /* Orange */
    .grc-green::before { background-color: #10B981; }      /* Green */
    .grc-yellow::before { background-color: #F59E0B; }     /* Yellow */
    .grc-red::before { background-color: #EF4444; }        /* Red */
    
    .kpi-title {
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #4B5563;
        font-weight: 600;
        margin-bottom: 8px;
    }
    .kpi-value {
        font-size: 2.5rem; /* Larger numbers */
        font-weight: 800;
        color: #111827;
        line-height: 1.1;
    }
    .kpi-subtitle {
        font-size: 0.75rem;
        color: #6B7280;
        margin-top: 8px;
    }
    
    /* Styled alert block */
    .alert-card {
        background-color: #F8FAFC;
        border-left: 4px solid #F59E0B;
        padding: 16px;
        border-radius: 0 8px 8px 0;
        margin-bottom: 12px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.02);
    }
    
    /* Status Badge styling */
    .badge {
        display: inline-flex;
        align-items: center;
        padding: 4px 8px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        box-shadow: 0 1px 2px rgba(0,0,0,0.02);
    }
    
    /* Custom spacing */
    .main-header {
        margin-bottom: 28px;
        border-bottom: 1px solid #E5E7EB;
        padding-bottom: 18px;
    }
    
    /* Priority Table styling */
    .priority-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.85rem;
    }
    .priority-table th {
        padding: 10px 4px;
        font-weight: 600;
        color: #4B5563;
        border-bottom: 2px solid #E5E7EB;
        text-align: left;
    }
    .priority-table td {
        padding: 10px 4px;
        border-bottom: 1px solid #E5E7EB;
        color: #1F2937;
    }
    .priority-table tr:hover td {
        background-color: #F9FAFB;
    }
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# 2. DATA LOADING & PREPROCESSING (June 20, 2026 Anchor)
# ----------------------------------------------------
ANCHOR_DATE = pd.to_datetime("2026-06-20")

@st.cache_data
def load_and_preprocess_data():
    # Load raw CSVs
    registry = pd.read_csv("data/vendor_registry.csv")
    labels = pd.read_csv("data/vendor_labels.csv")
    
    # Merge datasets on vendor_id
    df = pd.merge(registry, labels, on="vendor_id", how="inner")
    
    # Parse date columns
    df['cert_expiry'] = pd.to_datetime(df['cert_expiry'])
    df['contract_start'] = pd.to_datetime(df['contract_start'])
    df['contract_end'] = pd.to_datetime(df['contract_end'])
    
    # Precompute Expiration & Risk variables
    df['is_cert_expired'] = df['cert_expiry'] < ANCHOR_DATE
    df['is_contract_expired'] = df['contract_end'] < ANCHOR_DATE
    
    # Define categorized risk score bucket
    # High: >= 80, Medium: 50-79, Low: < 50
    df['risk_tier'] = pd.cut(
        df['risk_score'],
        bins=[0, 49, 79, 100],
        labels=['Low (<50)', 'Medium (50-79)', 'High (>=80)']
    )
    
    return df

try:
    df = load_and_preprocess_data()
    # Write dynamic GRC metrics to frontend/metrics.json
    import json
    import os
    try:
        metrics = {
            "total_vendors": int(len(df)),
            "high_risk_vendors": int(len(df[df['risk_score'] >= 80])),
            "expired_certifications": int(df['is_cert_expired'].sum()),
            "financial_exposure_m": round(df['annual_spend'].sum() / 1_000_000, 1)
        }
        os.makedirs("frontend", exist_ok=True)
        with open("frontend/metrics.json", "w") as f:
            json.dump(metrics, f, indent=4)
    except Exception as ex:
        pass
except Exception as e:
    st.error(f"Error loading datasets. Please check files: {str(e)}")
    st.stop()

# Helper badge generators
def severity_badge_html(severity):
    colors = {
        'CRITICAL': '#EF4444',
        'HIGH': '#F97316',
        'MEDIUM': '#F59E0B',
        'LOW': '#10B981',
        'NONE': '#6B7280'
    }
    color = colors.get(severity, '#6B7280')
    return f'<span class="badge" style="background-color: {color}15; color: {color}; border: 1px solid {color}30;">{severity}</span>'

def risk_badge_html(score):
    if score >= 80:
        color = '#EF4444'
        level = 'HIGH'
    elif score >= 50:
        color = '#F59E0B'
        level = 'MEDIUM'
    else:
        color = '#10B981'
        level = 'LOW'
    return f'<span class="badge" style="background-color: {color}15; color: {color}; border: 1px solid {color}30;">{score} - {level}</span>'

def cert_badge_html(expired, expiry_date):
    formatted_date = expiry_date.strftime("%Y-%m-%d")
    if expired:
        return f'<span class="badge" style="background-color: #EF444415; color: #EF4444; border: 1px solid #EF444430;">Expired ({formatted_date})</span>'
    else:
        return f'<span class="badge" style="background-color: #10B98115; color: #10B981; border: 1px solid #10B98130;">Active ({formatted_date})</span>'

def contract_badge_html(expired, end_date):
    formatted_date = end_date.strftime("%Y-%m-%d")
    if expired:
        return f'<span class="badge" style="background-color: #EF444415; color: #EF4444; border: 1px solid #EF444430;">Expired ({formatted_date})</span>'
    else:
        return f'<span class="badge" style="background-color: #10B98115; color: #10B981; border: 1px solid #10B98130;">Active ({formatted_date})</span>'

# Initialize session state for selected vendor if not exists
if 'selected_vendor_id' not in st.session_state:
    st.session_state['selected_vendor_id'] = df['vendor_id'].iloc[0]

# ----------------------------------------------------
# 3. SIDEBAR NAVIGATION
# ----------------------------------------------------
with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: #06B6D4; margin-bottom: 2px;'>TPRM PORTAL</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 0.8rem; color: #4B5563; margin-bottom: 24px;'>Third-Party Vendor Risk Auditor</p>", unsafe_allow_html=True)
    
    st.markdown("### NAVIGATION")
    menu = st.radio(
        "Go to",
        ["Executive Dashboard", "Vendor Registry", "Vendor Details", "Risk Simulator", "Future Risk Predictor", "AI Vendor Risk Advisor", "Alerts & Incidents"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    st.markdown("### TIMELINE STATUS")
    st.info(f"**Audit Reference Date:**\nJune 20, 2026")
    
    # Financial aggregate
    total_spend = df['annual_spend'].sum()
    st.markdown("### FINANCIAL EXPOSURE")
    st.metric(label="Total Audited Spend", value=f"€{total_spend:,.0f}")
    
    st.markdown("---")
    st.markdown("### AUDIT EXPORT")
    if 'report_pdf_bytes' not in st.session_state:
        st.session_state['report_pdf_bytes'] = None
        
    if st.button("Generate Audit Report", use_container_width=True):
        with st.spinner("Generating PDF report..."):
            try:
                pdf_buf = create_audit_pdf(df)
                st.session_state['report_pdf_bytes'] = pdf_buf.getvalue()
                st.success("Report generated successfully!")
            except Exception as e:
                st.error(f"Error generating report: {str(e)}")
                
    if st.session_state['report_pdf_bytes'] is not None:
        st.download_button(
            label="Download PDF Report",
            data=st.session_state['report_pdf_bytes'],
            file_name="TPRM_Audit_Report.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    
    st.markdown("<br><p style='text-align: center; font-size: 0.7rem; color: #4B5563;'>v1.2.0 • Presentation Sandbox</p>", unsafe_allow_html=True)

# ----------------------------------------------------
# 4. VIEW - EXECUTIVE DASHBOARD
# ----------------------------------------------------
if menu == "Executive Dashboard":
    st.markdown("<div class='main-header'><h1>Third-Party Vendor Risk Dashboard</h1><p style='color:#4B5563; margin-top:-10px;'>Executive overview of vendor risk profiles, certification standings, and exposure distribution.</p></div>", unsafe_allow_html=True)
    
    # KPI Metrics
    total_vendors = len(df)
    high_risk = len(df[df['risk_score'] >= 80])
    medium_risk = len(df[(df['risk_score'] >= 50) & (df['risk_score'] < 80)])
    low_risk = len(df[df['risk_score'] < 50])
    expired_certs = df['is_cert_expired'].sum()
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown(f"""<div class="kpi-card kpi-total">
<div class="kpi-title">Total Vendors</div>
<div class="kpi-value">{total_vendors}</div>
<div class="kpi-subtitle">Audited registry count</div>
</div>""", unsafe_allow_html=True)
        
    with col2:
        st.markdown(f"""<div class="kpi-card kpi-high">
<div class="kpi-title">High Risk</div>
<div class="kpi-value" style="color: #EF4444;">{high_risk}</div>
<div class="kpi-subtitle">Risk Score &ge; 80</div>
</div>""", unsafe_allow_html=True)
        
    with col3:
        st.markdown(f"""<div class="kpi-card kpi-medium">
<div class="kpi-title">Medium Risk</div>
<div class="kpi-value" style="color: #F59E0B;">{medium_risk}</div>
<div class="kpi-subtitle">Risk Score 50 - 79</div>
</div>""", unsafe_allow_html=True)
        
    with col4:
        st.markdown(f"""<div class="kpi-card kpi-low">
<div class="kpi-title">Low Risk</div>
<div class="kpi-value" style="color: #10B981;">{low_risk}</div>
<div class="kpi-subtitle">Risk Score &lt; 50</div>
</div>""", unsafe_allow_html=True)
        
    with col5:
        st.markdown(f"""<div class="kpi-card kpi-expired">
<div class="kpi-title">Expired Certs</div>
<div class="kpi-value" style="color: #F97316;">{expired_certs}</div>
<div class="kpi-subtitle">Out of compliance</div>
</div>""", unsafe_allow_html=True)
    
    # ----------------------------------------------------
    # NEW WIDGETS: Executive Risk Summary & Top 5 Priority Vendors
    # ----------------------------------------------------
    st.write("")
    col_summary, col_priority = st.columns([1, 1])
    
    with col_summary:
        # Calculate summary values
        critical_count = len(df[df['severity'] == 'CRITICAL'])
        high_risk_count = len(df[df['risk_score'] >= 80])
        highest_risk_row = df.loc[df['risk_score'].idxmax()]
        highest_risk_vendor = highest_risk_row['vendor_id']
        highest_risk_score = highest_risk_row['risk_score']
        total_exposure = df['annual_spend'].sum()
        immediate_review_count = len(df[(df['severity'].isin(['CRITICAL', 'HIGH'])) | (df['risk_score'] >= 80)])
        expired_certs_count = df['is_cert_expired'].sum()
        
        exec_summary_html = f"""
        <div class="kpi-card" style="margin-bottom: 0px; padding: 24px; min-height: 380px; display: flex; flex-direction: column; justify-content: space-between;">
            <div>
                <h3 style="color: #06B6D4; margin-top: 0; margin-bottom: 20px; font-size: 1.15rem; letter-spacing: -0.02em;">Executive Risk Summary</h3>
                <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; margin-bottom: 24px;">
                    <div>
                        <div style="font-size: 0.75rem; color: #4B5563; text-transform: uppercase; font-weight: 600; letter-spacing: 0.05em; margin-bottom: 4px;">Critical Vendors</div>
                        <div style="font-size: 2rem; font-weight: 800; color: #EF4444; line-height: 1;">{critical_count}</div>
                    </div>
                    <div>
                        <div style="font-size: 0.75rem; color: #4B5563; text-transform: uppercase; font-weight: 600; letter-spacing: 0.05em; margin-bottom: 4px;">High Risk Vendors</div>
                        <div style="font-size: 2rem; font-weight: 800; color: #F59E0B; line-height: 1;">{high_risk_count}</div>
                    </div>
                    <div>
                        <div style="font-size: 0.75rem; color: #4B5563; text-transform: uppercase; font-weight: 600; letter-spacing: 0.05em; margin-bottom: 4px;">Highest Risk Vendor</div>
                        <div style="font-size: 1.1rem; font-weight: 800; color: #111827; line-height: 1.2;">{highest_risk_vendor} <span style="font-size: 0.85rem; color: #EF4444; font-weight: 700;">({highest_risk_score})</span></div>
                    </div>
                    <div>
                        <div style="font-size: 0.75rem; color: #4B5563; text-transform: uppercase; font-weight: 600; letter-spacing: 0.05em; margin-bottom: 4px;">Total Financial Exposure</div>
                        <div style="font-size: 1.6rem; font-weight: 800; color: #06B6D4; line-height: 1;">€{total_exposure:,.0f}</div>
                    </div>
                </div>
            </div>
            <div class="alert-card" style="border-left-color: #06B6D4; margin-bottom: 0; background-color: #F8FAFC; padding: 16px;">
                <p style="margin: 0; color: #111827; font-size: 0.85rem; line-height: 1.5;">
                    <strong>Management Summary:</strong><br>
                    {immediate_review_count} vendors require immediate review. {expired_certs_count} vendors have expired certifications. Total exposure exceeds €{total_exposure/1e6:.0f}M.
                </p>
            </div>
        </div>
        """
        st.markdown(exec_summary_html.replace('\n', ' '), unsafe_allow_html=True)
        
    with col_priority:
        # Rank vendors using Severity, Risk Score, and Breach Status
        sev_map = {'CRITICAL': 5, 'HIGH': 4, 'MEDIUM': 3, 'LOW': 2, 'NONE': 1}
        breach_map = {'BREACHED_RECENT': 4, 'BREACHED_LAST_12_MONTHS': 3, 'UNDER_INVESTIGATION': 2, 'NONE': 1}
        
        temp_df = df.copy()
        temp_df['sev_rank'] = temp_df['severity'].map(sev_map).fillna(0)
        temp_df['breach_rank'] = temp_df['breach_status'].map(breach_map).fillna(0)
        
        # Sort descending
        top_vendors = temp_df.sort_values(
            by=['sev_rank', 'risk_score', 'breach_rank'],
            ascending=[False, False, False]
        ).head(5)
        
        rows_html = ""
        for _, v in top_vendors.iterrows():
            if v['risk_score'] >= 80:
                score_color = '#EF4444'
            elif v['risk_score'] >= 50:
                score_color = '#F59E0B'
            else:
                score_color = '#10B981'
            
            sev_badge = severity_badge_html(v['severity'])
            anomaly_clean = v['anomaly_type'].replace('_', ' ').title() if v['anomaly_type'] != 'NONE' else 'No Anomaly'
            
            rows_html += f"""
            <tr>
                <td style="font-weight: 700; color: #06B6D4;">{v['vendor_id']}</td>
                <td>{v['type'].title()}</td>
                <td style="text-align: center; font-weight: 800; color: {score_color};">{v['risk_score']}</td>
                <td style="text-align: center;">{sev_badge}</td>
                <td style="text-align: right; font-size: 0.75rem; color: #4B5563;">{anomaly_clean}</td>
            </tr>
            """
            
        priority_table_html = f"""
        <div class="kpi-card" style="padding: 24px; min-height: 380px;">
            <h3 style="color: #F97316; margin-top: 0; margin-bottom: 16px; font-size: 1.15rem; letter-spacing: -0.02em;">Top 5 Vendors Requiring Immediate Attention</h3>
            <table class="priority-table">
                <thead>
                    <tr>
                        <th>Vendor ID</th>
                        <th>Type</th>
                        <th style="text-align: center;">Risk Score</th>
                        <th style="text-align: center;">Severity</th>
                        <th style="text-align: right;">Anomaly Type</th>
                    </tr>
                </thead>
                <tbody>
                    {rows_html}
                </tbody>
            </table>
        </div>
        """
        st.markdown(priority_table_html.replace('\n', ' '), unsafe_allow_html=True)
        
    # ----------------------------------------------------
    # Compliance Coverage Center
    # ----------------------------------------------------
    # GDPR Coverage %
    gdpr_count = df['certifications'].astype(str).str.contains('GDPR', case=False).sum()
    gdpr_pct = gdpr_count / total_vendors if total_vendors > 0 else 0.0
    
    # SOC2 Coverage %
    soc2_count = df[df['certifications'].astype(str).str.contains('SOC2', case=False) & ~df['is_cert_expired']].shape[0]
    soc2_pct = soc2_count / total_vendors if total_vendors > 0 else 0.0
    
    # Active Contract Coverage %
    active_contract_count = (df['contract_end'] > ANCHOR_DATE).sum()
    contract_pct = active_contract_count / total_vendors if total_vendors > 0 else 0.0
    
    # Expired Certifications Count
    expired_certs_count = df['is_cert_expired'].sum()
    
    # Expired Contracts Count
    expired_contracts_count = df['is_contract_expired'].sum()
    
    # GRC styling helper
    def get_grc_class_and_color(val, is_percentage=True):
        if is_percentage:
            if val >= 0.75:
                return "grc-green", "#10B981"
            elif val >= 0.50:
                return "grc-yellow", "#F59E0B"
            else:
                return "grc-red", "#EF4444"
        else:
            if val == 0:
                return "grc-green", "#10B981"
            elif val <= 5:
                return "grc-yellow", "#F59E0B"
            else:
                return "grc-red", "#EF4444"
                
    st.markdown("<h3 style='color: #0F172A; margin-top: 32px; margin-bottom: 8px; font-weight: 700; letter-spacing: -0.02em;'>Compliance Coverage Center</h3><p style='color: #4B5563; font-size: 0.875rem; margin-bottom: 24px; margin-top: -4px;'>Real-time compliance status, active credentials tracking, and contract validity metrics.</p>", unsafe_allow_html=True)
    
    col_grc1, col_grc2, col_grc3, col_grc4, col_grc5 = st.columns(5)
    
    # 1. GDPR Coverage %
    gdpr_class, gdpr_color = get_grc_class_and_color(gdpr_pct, is_percentage=True)
    with col_grc1:
        st.markdown(
            f'<div class="kpi-card {gdpr_class}" title="Proportion of vendors with an active GDPR Data Processing Agreement (DPA).">'
            f'<div class="kpi-title">GDPR Coverage</div>'
            f'<div class="kpi-value" style="color: {gdpr_color};">{gdpr_pct * 100:.1f}%</div>'
            f'<div class="kpi-subtitle">{gdpr_count} of {total_vendors} vendors</div>'
            f'</div>',
            unsafe_allow_html=True
        )
        
    # 2. SOC2 Coverage %
    soc2_class, soc2_color = get_grc_class_and_color(soc2_pct, is_percentage=True)
    with col_grc2:
        st.markdown(
            f'<div class="kpi-card {soc2_class}" title="Proportion of vendors with active, non-expired SOC2 certification.">'
            f'<div class="kpi-title">SOC2 Coverage</div>'
            f'<div class="kpi-value" style="color: {soc2_color};">{soc2_pct * 100:.1f}%</div>'
            f'<div class="kpi-subtitle">{soc2_count} of {total_vendors} vendors</div>'
            f'</div>',
            unsafe_allow_html=True
        )
        
    # 3. Active Contract Coverage %
    contract_class, contract_color = get_grc_class_and_color(contract_pct, is_percentage=True)
    with col_grc3:
        st.markdown(
            f'<div class="kpi-card {contract_class}" title="Proportion of vendors with active contracts extending past the audit reference date of June 20, 2026.">'
            f'<div class="kpi-title">Active Contract Coverage</div>'
            f'<div class="kpi-value" style="color: {contract_color};">{contract_pct * 100:.1f}%</div>'
            f'<div class="kpi-subtitle">{active_contract_count} of {total_vendors} vendors</div>'
            f'</div>',
            unsafe_allow_html=True
        )
        
    # 4. Expired Certifications Count
    expired_certs_class, expired_certs_color = get_grc_class_and_color(expired_certs_count, is_percentage=False)
    with col_grc4:
        st.markdown(
            f'<div class="kpi-card {expired_certs_class}" title="Total number of vendors whose security certifications have expired.">'
            f'<div class="kpi-title">Expired Certifications</div>'
            f'<div class="kpi-value" style="color: {expired_certs_color};">{expired_certs_count}</div>'
            f'<div class="kpi-subtitle">Out of compliance</div>'
            f'</div>',
            unsafe_allow_html=True
        )
        
    # 5. Expired Contracts Count
    expired_contracts_class, expired_contracts_color = get_grc_class_and_color(expired_contracts_count, is_percentage=False)
    with col_grc5:
        st.markdown(
            f'<div class="kpi-card {expired_contracts_class}" title="Total number of vendors with expired contracts that remain active in the system.">'
            f'<div class="kpi-title">Expired Contracts</div>'
            f'<div class="kpi-value" style="color: {expired_contracts_color};">{expired_contracts_count}</div>'
            f'<div class="kpi-subtitle">Requiring renewal</div>'
            f'</div>',
            unsafe_allow_html=True
        )
        
    st.write("")
    st.write("")
    
    # Dashboard Visualizations
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        st.markdown("### Risk Score Distribution")
        # Histogram colored by custom category tiers
        fig_risk = px.histogram(
            df,
            x="risk_score",
            color="risk_tier",
            nbins=25,
            labels={"risk_score": "Risk Score (0 - 100)", "risk_tier": "Risk Category"},
            color_discrete_map={
                'Low (<50)': '#10B981',
                'Medium (50-79)': '#F59E0B',
                'High (>=80)': '#EF4444'
            },
            title="Distribution of Vendor Risk Metrics"
        )
        fig_risk.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#111827",
            margin=dict(l=40, r=20, t=40, b=40),
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=False),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_risk, use_container_width=True)
        
    with chart_col2:
        st.markdown("### Severity Distribution")
        # Donut Chart for Anomaly severity levels
        severity_counts = df['severity'].value_counts().reset_index()
        severity_counts.columns = ['severity', 'count']
        
        # Sort custom order
        order = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'NONE']
        severity_counts['severity'] = pd.Categorical(severity_counts['severity'], categories=order, ordered=True)
        severity_counts = severity_counts.sort_values('severity')
        
        fig_sev = px.pie(
            severity_counts,
            values='count',
            names='severity',
            hole=0.6,
            color='severity',
            color_discrete_map={
                'CRITICAL': '#991B1B',
                'HIGH': '#EF4444',
                'MEDIUM': '#F59E0B',
                'LOW': '#10B981',
                'NONE': '#6B7280'
            },
            title="Registry breakdown by Severity Alerts"
        )
        fig_sev.update_traces(textposition='outside', textinfo='percent+label')
        fig_sev.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#111827",
            showlegend=False,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig_sev, use_container_width=True)
        
    # Vendor Type Chart (Full Width)
    st.markdown("### Vendor Type Distribution & Average Risk Profile")
    type_stats = df.groupby('type').agg(
        total_vendors=('vendor_id', 'count'),
        avg_risk=('risk_score', 'mean')
    ).reset_index()
    
    fig_type = px.bar(
        type_stats,
        x='total_vendors',
        y='type',
        orientation='h',
        color='avg_risk',
        color_continuous_scale=['#10B981', '#F59E0B', '#EF4444', '#991B1B'],
        labels={
            'total_vendors': 'Number of Vendors',
            'type': 'Vendor Type',
            'avg_risk': 'Average Risk Score'
        },
        title="Vendor Volume by Category (Colored by Average Risk Score)"
    )
    fig_type.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#111827",
        height=380,
        margin=dict(l=160, r=20, t=50, b=40),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=False)
    )
    st.plotly_chart(fig_type, use_container_width=True)
    
    # ----------------------------------------------------
    # Executive Risk Heatmap
    # ----------------------------------------------------
    st.markdown("### Executive Risk Heatmap")
    st.caption("Quantitative visual grid mapping vendor categories to their severity profiles.")
    
    # Create crosstab matrix of vendor counts by type and severity
    heatmap_df = pd.crosstab(df['type'], df['severity'])
    
    # Ensure logical sorting order for columns
    severity_order = ['NONE', 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
    for sev in severity_order:
        if sev not in heatmap_df.columns:
            heatmap_df[sev] = 0
    heatmap_df = heatmap_df[severity_order]
    
    # Create 2D heatmap with Reds color scale
    fig_heatmap = go.Figure(data=go.Heatmap(
        z=heatmap_df.values,
        y=heatmap_df.index.values,
        x=heatmap_df.columns.values,
        colorscale='Reds',
        showscale=True,
        text=heatmap_df.values,
        texttemplate="%{text}",
        textfont={"size": 11, "family": "Inter", "weight": "bold"}
    ))
    
    fig_heatmap.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_family="Inter",
        height=350,
        margin=dict(l=160, r=20, t=40, b=20),
        xaxis=dict(
            visible=True,
            showgrid=False,
            side="top",
            tickfont={"size": 11, "family": "Inter"}
        ),
        yaxis=dict(
            visible=True,
            showgrid=False,
            tickfont={"size": 11, "family": "Inter"}
        )
    )
    
    st.plotly_chart(fig_heatmap, use_container_width=True)

# ----------------------------------------------------
# 5. VIEW - VENDOR REGISTRY
# ----------------------------------------------------
elif menu == "Vendor Registry":
    st.markdown("<div class='main-header'><h1>Vendor Registry Directory</h1><p style='color:#4B5563; margin-top:-10px;'>Search, filter, and inspect third-party vendors cataloged in the GRC database.</p></div>", unsafe_allow_html=True)
    
    # Filter Layout Panel
    with st.expander("Filters & Search Controls", expanded=True):
        col_search, col_sev, col_anomaly, col_sort = st.columns([2, 1, 1, 1])
        
        with col_search:
            search_query = st.text_input("Search Vendor ID or Category Type", placeholder="e.g. VEND_001 or Cloud Provider")
            
        with col_sev:
            sev_options = ["All"] + sorted(df['severity'].unique().tolist())
            selected_sev = st.selectbox("Severity Classification", options=sev_options)
            
        with col_anomaly:
            anomaly_options = ["All"] + sorted(df['anomaly_type'].unique().tolist())
            selected_anomaly = st.selectbox("Anomaly Type", options=anomaly_options)
            
        with col_sort:
            sort_order = st.selectbox("Sort by Risk Score", options=["Highest First", "Lowest First"])
            
    # Apply Filtering
    filtered_df = df.copy()
    
    if search_query:
        search_query_lower = search_query.lower()
        filtered_df = filtered_df[
            filtered_df['vendor_id'].str.lower().str.contains(search_query_lower) |
            filtered_df['type'].str.lower().str.contains(search_query_lower)
        ]
        
    if selected_sev != "All":
        filtered_df = filtered_df[filtered_df['severity'] == selected_sev]
        
    if selected_anomaly != "All":
        filtered_df = filtered_df[filtered_df['anomaly_type'] == selected_anomaly]
        
    if sort_order == "Highest First":
        filtered_df = filtered_df.sort_values(by="risk_score", ascending=False)
    else:
        filtered_df = filtered_df.sort_values(by="risk_score", ascending=True)
        
    st.markdown(f"**Results:** Showing {len(filtered_df)} vendors matching criteria")
    
    # Format table data
    display_df = filtered_df[[
        'vendor_id', 'type', 'risk_score', 'severity', 'anomaly_type', 'annual_spend', 
        'certifications', 'cert_expiry', 'contract_end'
    ]].copy()
    
    # Render with Streamlit's new column configs for dynamic graphics!
    st.dataframe(
        display_df,
        column_config={
            "vendor_id": st.column_config.TextColumn("Vendor ID", width="medium"),
            "type": st.column_config.TextColumn("Vendor Category"),
            "risk_score": st.column_config.ProgressColumn(
                "Risk Score",
                help="Quantitative Risk Score (0-100)",
                format="%d",
                min_value=0,
                max_value=100,
            ),
            "severity": st.column_config.TextColumn("Alert Severity"),
            "anomaly_type": st.column_config.TextColumn("Anomaly Alert Type"),
            "annual_spend": st.column_config.NumberColumn(
                "Annual Spend (€)",
                format="€%,.0f"
            ),
            "certifications": st.column_config.TextColumn("Active Credentials"),
            "cert_expiry": st.column_config.DateColumn(
                "Cert Expiration",
                format="YYYY-MM-DD"
            ),
            "contract_end": st.column_config.DateColumn(
                "Contract End Date",
                format="YYYY-MM-DD"
            )
        },
        hide_index=True,
        use_container_width=True
    )
    
    # Direct selection integration
    st.write("")
    select_col1, select_col2 = st.columns([2, 3])
    with select_col1:
        inspect_vendor = st.selectbox(
            "Select a vendor to load details in the Inspector tab:",
            options=filtered_df['vendor_id'].tolist() if len(filtered_df) > 0 else df['vendor_id'].tolist()
        )
        if st.button("Inspect Selected Vendor Details"):
            st.session_state['selected_vendor_id'] = inspect_vendor
            st.success(f"Vendor {inspect_vendor} loaded! Please select the 'Vendor Details' tab on the navigation menu to view.")

# ----------------------------------------------------
# 6. VIEW - VENDOR DETAILS
# ----------------------------------------------------
elif menu == "Vendor Details":
    st.markdown("<div class='main-header'><h1>Vendor Risk Profile Inspector</h1><p style='color:#4B5563; margin-top:-10px;'>Granular details, compliance metrics, and risk evaluations for a chosen vendor.</p></div>", unsafe_allow_html=True)
    
    # Selection box
    vendor_list = sorted(df['vendor_id'].unique().tolist())
    default_idx = vendor_list.index(st.session_state['selected_vendor_id']) if st.session_state['selected_vendor_id'] in vendor_list else 0
    
    target_vendor = st.selectbox(
        "Select Vendor Profile to Inspect",
        options=vendor_list,
        index=default_idx
    )
    
    # Update local state
    st.session_state['selected_vendor_id'] = target_vendor
    
    # Extract records
    v_data = df[df['vendor_id'] == target_vendor].iloc[0]
    
    # Layout detail cards
    d_col1, d_col2 = st.columns([1, 2])
    
    with d_col1:
        # Scorecard
        scorecard_html = (
            f'<div style="background-color: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 12px; padding: 24px; text-align: center;">'
            f'<p style="color: #4B5563; font-size: 0.8rem; text-transform: uppercase; font-weight: 600; margin-bottom: 2px;">Vendor ID</p>'
            f'<h2 style="color: #06B6D4; margin-top: 0; margin-bottom: 12px;">{v_data["vendor_id"]}</h2>'
            f'<p style="color: #4B5563; font-size: 0.8rem; text-transform: uppercase; font-weight: 600; margin-bottom: 4px;">Audited Risk Score</p>'
            f'<h1 style="font-size: 4rem; margin-top: 0; margin-bottom: 0; font-weight: 800; line-height: 1; color: #111827;">{v_data["risk_score"]}</h1>'
            f'<div style="margin-top: 16px; margin-bottom: 20px;">{risk_badge_html(v_data["risk_score"])}</div>'
            f'<hr style="border-color: #E5E7EB; margin: 16px 0;" />'
            f'<p style="color: #4B5563; font-size: 0.8rem; text-transform: uppercase; font-weight: 600; margin-bottom: 4px;">Alert Severity Rating</p>'
            f'<div style="margin-bottom: 12px;">{severity_badge_html(v_data["severity"])}</div>'
            f'<p style="color: #4B5563; font-size: 0.8rem; text-transform: uppercase; font-weight: 600; margin-bottom: 2px;">Breach History Status</p>'
            f'<p style="font-weight: 600; color: {"#EF4444" if "BREACHED" in v_data["breach_status"] else "#10B981" if v_data["breach_status"] == "NONE" else "#F59E0B"}; margin-bottom: 0;">'
            f'{v_data["breach_status"].replace("_", " ")}'
            f'</p>'
            f'</div>'
        )
        st.markdown(scorecard_html, unsafe_allow_html=True)
        
        # Calculate breakdown
        base_scores = {
            "payment processor": 40,
            "cloud provider": 35,
            "integration partner": 30,
            "software vendor": 20,
            "consultancy": 15
        }
        breach_modifiers = {
            "none": 0,
            "breached_recent": 35,
            "breached_last_12_months": 20,
            "under_investigation": 25
        }
        
        v_type_normalized = v_data['type'].strip().lower()
        v_breach_normalized = v_data['breach_status'].strip().lower()
        
        base_val = base_scores.get(v_type_normalized, 15)
        breach_val = breach_modifiers.get(v_breach_normalized, 0)
        cert_val = 20 if v_data['is_cert_expired'] else 0
        contract_val = 15 if v_data['is_contract_expired'] else 0
        
        calculated_base_sum = base_val + breach_val + cert_val + contract_val
        diff = v_data['risk_score'] - calculated_base_sum
        
        # Build list of factors
        factors = []
        factors.append((f"+{base_val} → {v_data['type'].title()} Base Risk Factor", "#EF4444"))
        
        if breach_val > 0:
            breach_text = v_data['breach_status'].replace('_', ' ').title()
            factors.append((f"+{breach_val} → Security Breach History ({breach_text})", "#EF4444"))
        else:
            factors.append(("+0 → No Security Breach Incidents", "#10B981"))
            
        if cert_val > 0:
            factors.append(("+20 → Expired Security Certification", "#EF4444"))
        else:
            factors.append(("+0 → Active compliance credentials", "#10B981"))
            
        if contract_val > 0:
            factors.append(("+15 → Expired Contract with Active Access", "#EF4444"))
        else:
            factors.append(("+0 → Active Contract Standing", "#10B981"))
            
        if diff > 0:
            factors.append((f"+{diff} → Elevated GRC/Operational Risk Adjustment", "#EF4444"))
        elif diff < 0:
            factors.append((f"-{abs(diff)} → Active Security Mitigation Controls Offset", "#10B981"))
            
        # Format HTML
        factors_list_html = ""
        for text, color in factors:
            parts = text.split(" → ")
            factors_list_html += f'<div style="display: flex; align-items: center; margin-bottom: 8px; font-size: 0.85rem; color: #111827;"><span style="color: {color}; font-weight: 700; margin-right: 8px; min-width: 40px; display: inline-block;">{parts[0]}</span> <span style="color: #4B5563; margin-right: 8px;">→</span> <span style="color: #1F2937;">{parts[1]}</span></div>'
            
        breakdown_html = (
            f'<div style="background-color: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 12px; padding: 20px; margin-top: 16px;">'
            f'<h4 style="color: #06B6D4; margin-top: 0; margin-bottom: 16px; text-transform: uppercase; font-size: 0.75rem; letter-spacing: 0.05em; text-align: center; font-weight: 700;">Why Is This Vendor Risky?</h4>'
            f'<div style="display: flex; flex-direction: column;">'
            f'{factors_list_html}'
            f'</div>'
            f'</div>'
        )
        st.markdown(breakdown_html, unsafe_allow_html=True)
        
    with d_col2:
        # Detailed lists
        st.markdown("### Vendor Information")
        info_col1, info_col2 = st.columns(2)
        with info_col1:
            st.write(f"**Vendor Classification:** {v_data['type']}")
            st.write(f"**Annual Account Spend:** €{v_data['annual_spend']:,.2f}")
            st.write(f"**Active Credentials:** {v_data['certifications']}")
        with info_col2:
            st.write(f"**Contract Commencement:** {v_data['contract_start'].strftime('%Y-%m-%d')}")
            st.write(f"**Contract Terminus:** {v_data['contract_end'].strftime('%Y-%m-%d')}")
            st.write(f"**Required Credentials:** {v_data['expired_certifications'] if v_data['expired_certifications'] != 'NONE' else 'Fully Certified'}")
            
        st.markdown("---")
        
        st.markdown("### Compliance & Contract Status")
        comp_col1, comp_col2 = st.columns(2)
        
        with comp_col1:
            st.markdown("**Certification Validity:**")
            st.markdown(cert_badge_html(v_data['is_cert_expired'], v_data['cert_expiry']), unsafe_allow_html=True)
            st.caption("Active certification prevents data leakage risks.")
            
        with comp_col2:
            st.markdown("**Contract Validity:**")
            st.markdown(contract_badge_html(v_data['is_contract_expired'], v_data['contract_end']), unsafe_allow_html=True)
            st.caption("Expired active contract creates orphaned access risks.")
            
        st.markdown("---")
        
        st.markdown("### Flags & Anomaly Investigations")
        if v_data['is_anomaly'] == 1:
            anomaly_html = (
                f'<div class="alert-card" style="border-color: #EF4444;">'
                f'<h4 style="color: #EF4444; margin-top: 0; margin-bottom: 6px;">Anomaly Detected: {v_data["anomaly_type"].replace("_", " ")}</h4>'
                f'<p style="margin-bottom: 0; color: #1F2937; font-size: 0.9rem;"><strong>Audit Rationale:</strong> {v_data["explanation"]}</p>'
                f'</div>'
            )
            st.markdown(anomaly_html, unsafe_allow_html=True)
        else:
            st.success("Compliant Profile: This vendor shows no GRC compliance anomalies or flags.")
            
        # Business Impact & Action Recommendations
        st.markdown("---")
        st.markdown("### Risk & Action Analysis")
        analysis_col1, analysis_col2 = st.columns(2)
        
        with analysis_col1:
            # 1. Potential Business Impact
            if v_data['is_cert_expired'] and not v_data['is_contract_expired']:
                desc = "This vendor has an expired certification while maintaining active contracts."
                bullets = [
                    "Regulatory non-compliance with industry GRC frameworks",
                    "Immediate audit findings and audit remediation penalties",
                    "Increased third-party risk exposure to corporate assets"
                ]
                color = "#EF4444"
            elif v_data['breach_status'] != 'NONE' and v_data['type'] in ['Payment Processor', 'Cloud Provider', 'Integration Partner']:
                desc = "This vendor experienced a breach or is under investigation and maintains elevated access."
                bullets = [
                    "Unauthorized customer data exposure and privacy leakage",
                    "Significant direct and indirect financial recovery loss",
                    "Severe brand reputation and trust degradation"
                ]
                color = "#EF4444"
            elif v_data['is_contract_expired']:
                desc = "This vendor has an expired contract while operational system integrations remain active."
                bullets = [
                    "Orphaned access vulnerabilities and threat vectors",
                    "Non-compliance with corporate GRC data governance mandates",
                    "Unmonitored data ingress and egress flow risks"
                ]
                color = "#F59E0B"
            else:
                desc = "This vendor maintains active certifications, contracts, and displays no breach indicators."
                bullets = [
                    "Negligible security exposure to corporate client networks",
                    "Full compliance with corporate procurement standards",
                    "Regular audit review cycle holds at standard frequency"
                ]
                color = "#10B981"
                
            bullets_html = "".join([f"<li style='margin-bottom: 4px;'>{b}</li>" for b in bullets])
            impact_html = f"""
            <div class="alert-card" style="border-left: 4px solid {color}; background-color: #F8FAFC; padding: 16px; min-height: 180px;">
                <h4 style="color: {color}; margin-top: 0; margin-bottom: 8px; font-weight: 700;">Potential Business Impact</h4>
                <p style="margin-bottom: 12px; color: #111827; font-size: 0.85rem; font-weight: 600;">{desc}</p>
                <ul style="margin: 0; padding-left: 18px; color: #4B5563; font-size: 0.8rem; line-height: 1.4;">
                    {bullets_html}
                </ul>
            </div>
            """
            st.markdown(impact_html, unsafe_allow_html=True)
            
        with analysis_col2:
            # 2. Recommended Actions
            anomaly_type = v_data['anomaly_type']
            is_cert_expired = v_data['is_cert_expired']
            is_contract_expired = v_data['is_contract_expired']
            breach_status = v_data['breach_status']
            
            if anomaly_type == 'EXPIRED_CERTIFICATION' or is_cert_expired:
                recs = [
                    "Renew certification immediately with vendor compliance",
                    "Schedule formal internal compliance and risk review",
                    "Restrict sensitive system access until compliance is fully restored"
                ]
                rec_color = "#F97316"
            elif anomaly_type == 'BREACHED_VENDOR_HIGH_ACCESS' or (breach_status != 'NONE' and breach_status != 'UNDER_INVESTIGATION'):
                recs = [
                    "Launch vendor security assessment and audit protocols",
                    "Perform immediate review and consolidation of privileged access keys",
                    "Escalate vendor GRC status to senior security leadership"
                ]
                rec_color = "#EF4444"
            elif anomaly_type == 'CONTRACT_EXPIRED_ACTIVE_ACCESS' or is_contract_expired:
                recs = [
                    "Revoke system credentials and access keys immediately",
                    "Review contract ownership and check for legacy renewals",
                    "Conduct orphaned access audit across internal directories"
                ]
                rec_color = "#EF4444"
            elif anomaly_type == 'VENDOR_UNDER_INVESTIGATION' or breach_status == 'UNDER_INVESTIGATION':
                recs = [
                    "Temporarily suspend non-essential data and API integrations",
                    "Initiate activity log auditing and real-time credential monitoring",
                    "Establish active communication line with vendor GRC audit lead"
                ]
                rec_color = "#F59E0B"
            else:
                recs = [
                    "Maintain continuous GRC audit monitoring schedule",
                    "Conduct GRC standard annual review checks",
                    "Verify contact information records remain up to date"
                ]
                rec_color = "#10B981"
                
            recs_html = "".join([f"<li style='margin-bottom: 4px;'>{r}</li>" for r in recs])
            actions_html = f"""
            <div class="alert-card" style="border-left: 4px solid {rec_color}; background-color: #F8FAFC; padding: 16px; min-height: 180px;">
                <h4 style="color: {rec_color}; margin-top: 0; margin-bottom: 8px; font-weight: 700;">Recommended Actions</h4>
                <ul style="margin: 0; padding-left: 18px; color: #1F2937; font-size: 0.8rem; line-height: 1.4;">
                    {recs_html}
                </ul>
            </div>
            """
            st.markdown(actions_html, unsafe_allow_html=True)
            
    # Risk Reduction Simulator standalone widget below the main columns
    st.markdown("---")
    st.markdown("### Risk Reduction Simulator")
    st.caption("Evaluate the quantitative risk score improvements achieved by applying specific GRC remediation actions.")
    
    sim_col1, sim_col2 = st.columns([1, 1.2])
    
    with sim_col1:
        st.markdown("**Simulate actions**")
        renew_cert = st.checkbox("Renew Expired Certification (-25 pts)")
        complete_audit = st.checkbox("Complete Security Audit (-15 pts)")
        remove_access = st.checkbox("Remove Privileged Access (-18 pts)")
        close_investigation = st.checkbox("Close Security Investigation (-16 pts)")
        review_contract = st.checkbox("Review Contract and Access Rights (-15 pts)")
        
    with sim_col2:
        current_risk = int(v_data['risk_score'])
        points_reduction = 0
        actions_taken = []
        
        if renew_cert:
            points_reduction += 25
            actions_taken.append("renewing certifications")
        if complete_audit:
            points_reduction += 15
            actions_taken.append("completing security audits")
        if remove_access:
            points_reduction += 18
            actions_taken.append("removing privileged access")
        if close_investigation:
            points_reduction += 16
            actions_taken.append("closing security investigations")
        if review_contract:
            points_reduction += 15
            actions_taken.append("reviewing contract and access rights")
            
        new_risk = max(0, current_risk - points_reduction)
        pct_improvement = (points_reduction / current_risk * 100) if current_risk > 0 else 0.0
        
        def sim_badge_html(score):
            if score <= 30:
                color = '#10B981'
                level = 'LOW'
            elif score <= 60:
                color = '#F59E0B'
                level = 'MEDIUM'
            elif score <= 80:
                color = '#F97316'
                level = 'HIGH'
            else:
                color = '#EF4444'
                level = 'CRITICAL'
            return f'<span class="badge" style="background-color: {color}15; color: {color}; border: 1px solid {color}30; font-weight: 700;">{level}</span>'
            
        def get_score_color(score):
            if score <= 30:
                return '#10B981'
            elif score <= 60:
                return '#F59E0B'
            elif score <= 80:
                return '#F97316'
            else:
                return '#EF4444'
                
        before_color = get_score_color(current_risk)
        after_color = get_score_color(new_risk)
        
        # 4 Metrics tiles (concatenated parenthesized single line strings to prevent parser bugs)
        metrics_html = (
            f'<div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 20px;">'
            f'<div style="background-color: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 8px; padding: 12px; text-align: center;">'
            f'<div style="font-size: 0.7rem; color: #4B5563; text-transform: uppercase; font-weight: 600;">Current Risk</div>'
            f'<div style="font-size: 1.5rem; font-weight: 800; color: #111827; margin-top: 4px;">{current_risk}</div>'
            f'</div>'
            f'<div style="background-color: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 8px; padding: 12px; text-align: center;">'
            f'<div style="font-size: 0.7rem; color: #4B5563; text-transform: uppercase; font-weight: 600;">New Risk</div>'
            f'<div style="font-size: 1.5rem; font-weight: 800; color: {after_color}; margin-top: 4px;">{new_risk}</div>'
            f'</div>'
            f'<div style="background-color: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 8px; padding: 12px; text-align: center;">'
            f'<div style="font-size: 0.7rem; color: #4B5563; text-transform: uppercase; font-weight: 600;">Reduction</div>'
            f'<div style="font-size: 1.5rem; font-weight: 800; color: #10B981; margin-top: 4px;">-{points_reduction}</div>'
            f'</div>'
            f'<div style="background-color: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 8px; padding: 12px; text-align: center;">'
            f'<div style="font-size: 0.7rem; color: #4B5563; text-transform: uppercase; font-weight: 600;">Improvement</div>'
            f'<div style="font-size: 1.5rem; font-weight: 800; color: #06B6D4; margin-top: 4px;">{pct_improvement:.1f}%</div>'
            f'</div>'
            f'</div>'
        )
        st.markdown(metrics_html, unsafe_allow_html=True)
        
        # Progress Bars and Badges
        def make_progress_bar_html(score, color):
            return (
                f'<div style="background-color: #E5E7EB; border-radius: 6px; height: 12px; width: 100%; margin-bottom: 12px; overflow: hidden; position: relative;">'
                f'<div style="background-color: {color}; width: {score}%; height: 100%; border-radius: 6px 0 0 6px;"></div>'
                f'</div>'
            )
            
        before_badge = sim_badge_html(current_risk)
        after_badge = sim_badge_html(new_risk)
        
        progress_bars_html = (
            f'<div style="margin-bottom: 20px;">'
            f'<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">'
            f'<span style="font-size: 0.8rem; font-weight: 600; color: #111827;">Before Risk Score: {current_risk}</span>'
            f'{before_badge}'
            f'</div>'
            f'{make_progress_bar_html(current_risk, before_color)}'
            f'<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px; margin-top: 12px;">'
            f'<span style="font-size: 0.8rem; font-weight: 600; color: #111827;">After Risk Score: {new_risk}</span>'
            f'{after_badge}'
            f'</div>'
            f'{make_progress_bar_html(new_risk, after_color)}'
            f'</div>'
        )
        st.markdown(progress_bars_html, unsafe_allow_html=True)
        
        # Business explanation string
        level_before = get_level_str = lambda s: 'LOW' if s <= 30 else 'MEDIUM' if s <= 60 else 'HIGH' if s <= 80 else 'CRITICAL'
        lbl_before = level_before(current_risk)
        lbl_after = level_before(new_risk)
        
        if points_reduction > 0:
            actions_str = ", ".join(actions_taken[:-1]) + (" and " + actions_taken[-1] if len(actions_taken) > 1 else actions_taken[0])
            explanation = f"By {actions_str}, the vendor risk level decreases from {lbl_before} to {lbl_after}. This significantly reduces compliance and breach exposure."
        else:
            explanation = "Select remediation simulator options to evaluate risk reduction pathways."
            
        explanation_html = (
            f'<div class="alert-card" style="border-left-color: #06B6D4; background-color: #F8FAFC; padding: 16px; margin-bottom: 0;">'
            f'<p style="margin: 0; color: #111827; font-size: 0.85rem; line-height: 1.5;">'
            f'{explanation}'
            f'</p>'
            f'</div>'
        )
        st.markdown(explanation_html, unsafe_allow_html=True)

# ----------------------------------------------------
# 6.5. VIEW - RISK SIMULATOR
# ----------------------------------------------------
elif menu == "Risk Simulator":
    st.markdown("<div class='main-header'><h1>Vendor Risk Simulator</h1><p style='color:#4B5563; margin-top:-10px;'>Simulate the reduction of vendor risk scores by applying specific security and compliance remediation actions.</p></div>", unsafe_allow_html=True)
    
    # Selection box
    vendor_list = sorted(df['vendor_id'].unique().tolist())
    default_idx = vendor_list.index(st.session_state['selected_vendor_id']) if st.session_state['selected_vendor_id'] in vendor_list else 0
    
    target_vendor = st.selectbox(
        "Select Vendor Profile to Simulate",
        options=vendor_list,
        index=default_idx
    )
    
    # Update global state so tabs stay synchronized
    st.session_state['selected_vendor_id'] = target_vendor
    
    # Extract vendor data
    v_data = df[df['vendor_id'] == target_vendor].iloc[0]
    
    # Initialize session state variables for this vendor simulator to prevent resetting on other interactions
    if 'last_sim_vendor' not in st.session_state or st.session_state['last_sim_vendor'] != target_vendor:
        st.session_state['last_sim_vendor'] = target_vendor
        st.session_state['sim_recalculated'] = False
        st.session_state['sim_soc2'] = False
        st.session_state['sim_gdpr'] = False
        st.session_state['sim_breach'] = False
        st.session_state['sim_contract'] = False
        st.session_state['sim_remediation'] = False

    sim_col1, sim_col2 = st.columns([1, 1.2])
    
    with sim_col1:
        st.markdown("<h3 style='color: #0F172A; font-weight: 700; margin-top: 0; margin-bottom: 12px;'>Vendor Information</h3>", unsafe_allow_html=True)
        
        # Risk level determination based on score
        def get_risk_level_info(score):
            if score <= 30:
                return "Low", "#10B981"
            elif score <= 60:
                return "Medium", "#F59E0B"
            elif score <= 80:
                return "High", "#F97316"
            else:
                return "Critical", "#EF4444"
                
        current_risk_score = int(v_data['risk_score'])
        current_level, current_color = get_risk_level_info(current_risk_score)
        
        info_html = f"""
        <div style="background-color: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 12px; padding: 24px; min-height: 290px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                <span style="font-weight: 700; color: #4B5563; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em;">Vendor ID:</span>
                <span style="font-weight: 800; color: #06B6D4; font-size: 1.1rem;">{v_data['vendor_id']}</span>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                <span style="font-weight: 700; color: #4B5563; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em;">Vendor Type:</span>
                <span style="font-weight: 600; color: #1F2937; font-size: 0.9rem;">{v_data['type'].title()}</span>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                <span style="font-weight: 700; color: #4B5563; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em;">Current Risk Score:</span>
                <span style="font-weight: 800; color: #111827; font-size: 1.5rem;">{current_risk_score}</span>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                <span style="font-weight: 700; color: #4B5563; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em;">Current Risk Level:</span>
                <span class="badge" style="background-color: {current_color}15; color: {current_color}; border: 1px solid {current_color}30; font-weight: 700; font-size: 0.8rem;">{current_level.upper()}</span>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0;">
                <span style="font-weight: 700; color: #4B5563; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em;">Current Severity:</span>
                {severity_badge_html(v_data['severity'])}
            </div>
        </div>
        """
        st.markdown(info_html, unsafe_allow_html=True)
        
    with sim_col2:
        st.markdown("<h3 style='color: #0F172A; font-weight: 700; margin-top: 0; margin-bottom: 12px;'>Simulation Controls</h3>", unsafe_allow_html=True)
        
        # Checkboxes are interactive, we store their selection in session state or just read them directly
        renew_soc2 = st.checkbox("Renew SOC2 Certification (-15 pts)", value=st.session_state['sim_soc2'])
        add_gdpr = st.checkbox("Add GDPR DPA Agreement (-10 pts)", value=st.session_state['sim_gdpr'])
        remove_breach = st.checkbox("Remove Breach History (-20 pts)", value=st.session_state['sim_breach'])
        renew_contract = st.checkbox("Renew Expired Contract (-8 pts)", value=st.session_state['sim_contract'])
        complete_remediation = st.checkbox("Complete Remediation Actions (-12 pts)", value=st.session_state['sim_remediation'])
        
        # Save check states to session state
        st.session_state['sim_soc2'] = renew_soc2
        st.session_state['sim_gdpr'] = add_gdpr
        st.session_state['sim_breach'] = remove_breach
        st.session_state['sim_contract'] = renew_contract
        st.session_state['sim_remediation'] = complete_remediation
        
        st.write("")
        if st.button("Recalculate Risk", use_container_width=True):
            st.session_state['sim_recalculated'] = True
            
    # Show simulation details only if Recalculate Risk button has been clicked
    if st.session_state['sim_recalculated']:
        # Perform calculations
        points_reduction = 0
        if renew_soc2:
            points_reduction += 15
        if add_gdpr:
            points_reduction += 10
        if remove_breach:
            points_reduction += 20
        if renew_contract:
            points_reduction += 8
        if complete_remediation:
            points_reduction += 12
            
        new_risk_score = max(0, current_risk_score - points_reduction)
        pct_improvement = (points_reduction / current_risk_score * 100) if current_risk_score > 0 else 0.0
        
        new_level, new_color = get_risk_level_info(new_risk_score)
        
        st.markdown("---")
        st.markdown("<h3 style='color: #0F172A; font-weight: 700; margin-top: 0; margin-bottom: 16px;'>Simulation Results</h3>", unsafe_allow_html=True)
        
        # Row of 5 key metrics
        metrics_html = f"""
        <div style="display: grid; grid-template-columns: repeat(5, 1fr); gap: 12px; margin-bottom: 24px;">
            <div style="background-color: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 10px; padding: 16px; text-align: center; box-shadow: 0 1px 2px rgba(0,0,0,0.02);">
                <div style="font-size: 0.72rem; color: #4B5563; text-transform: uppercase; font-weight: 600; letter-spacing: 0.02em;">Current Risk</div>
                <div style="font-size: 1.8rem; font-weight: 800; color: #111827; margin-top: 6px;">{current_risk_score}</div>
            </div>
            <div style="background-color: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 10px; padding: 16px; text-align: center; box-shadow: 0 1px 2px rgba(0,0,0,0.02);">
                <div style="font-size: 0.72rem; color: #4B5563; text-transform: uppercase; font-weight: 600; letter-spacing: 0.02em;">Simulated Risk</div>
                <div style="font-size: 1.8rem; font-weight: 800; color: {new_color}; margin-top: 6px;">{new_risk_score}</div>
            </div>
            <div style="background-color: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 10px; padding: 16px; text-align: center; box-shadow: 0 1px 2px rgba(0,0,0,0.02);">
                <div style="font-size: 0.72rem; color: #4B5563; text-transform: uppercase; font-weight: 600; letter-spacing: 0.02em;">Points Reduced</div>
                <div style="font-size: 1.8rem; font-weight: 800; color: #10B981; margin-top: 6px;">-{points_reduction}</div>
            </div>
            <div style="background-color: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 10px; padding: 16px; text-align: center; box-shadow: 0 1px 2px rgba(0,0,0,0.02);">
                <div style="font-size: 0.72rem; color: #4B5563; text-transform: uppercase; font-weight: 600; letter-spacing: 0.02em;">Reduction %</div>
                <div style="font-size: 1.8rem; font-weight: 800; color: #06B6D4; margin-top: 6px;">{pct_improvement:.1f}%</div>
            </div>
            <div style="background-color: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 10px; padding: 16px; text-align: center; box-shadow: 0 1px 2px rgba(0,0,0,0.02);">
                <div style="font-size: 0.72rem; color: #4B5563; text-transform: uppercase; font-weight: 600; letter-spacing: 0.02em;">Category Shift</div>
                <div style="margin-top: 6px; display: flex; align-items: center; justify-content: center; gap: 4px; font-weight: 700; font-size: 0.75rem;">
                    <span style="color: {current_color};">{current_level}</span>
                    <span style="color: #6B7280;">&rarr;</span>
                    <span style="color: {new_color};">{new_level}</span>
                </div>
            </div>
        </div>
        """
        st.markdown(metrics_html, unsafe_allow_html=True)
        
        # Plotly visual comparison and business impact section
        res_col1, res_col2 = st.columns([1.2, 1])
        
        with res_col1:
            st.markdown("<h4 style='color: #0F172A; font-weight: 700; margin-top: 0;'>Risk Score Comparison</h4>", unsafe_allow_html=True)
            # Create plotly bar chart
            fig_sim = go.Figure()
            fig_sim.add_trace(go.Bar(
                x=['Before Risk', 'After Risk'],
                y=[current_risk_score, new_risk_score],
                marker_color=[current_color, new_color],
                text=[current_risk_score, new_risk_score],
                textposition='auto',
                width=0.35
            ))
            fig_sim.update_layout(
                yaxis=dict(range=[0, 100], gridcolor="#E5E7EB"),
                paper_bgcolor="#FFFFFF",
                plot_bgcolor="#FFFFFF",
                font_family="Inter",
                font_color="#111827",
                height=260,
                margin=dict(l=40, r=40, t=20, b=20)
            )
            st.plotly_chart(fig_sim, use_container_width=True)
            
        with res_col2:
            st.markdown("<h4 style='color: #0F172A; font-weight: 700; margin-top: 0;'>Business Impact Analysis</h4>", unsafe_allow_html=True)
            
            # 1. Estimated Risk Reduction callout
            reduction_text = f"Simulated security controls reduced vendor risk by <b>{points_reduction} points</b>, achieving a <b>{pct_improvement:.1f}%</b> relative improvement."
            reduction_html = f"""
            <div class="alert-card" style="border-left: 4px solid #06B6D4; background-color: #F8FAFC; padding: 16px; margin-bottom: 16px;">
                <h5 style="color: #06B6D4; margin-top: 0; margin-bottom: 6px; font-weight: 700; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em;">Estimated Risk Reduction</h5>
                <p style="margin: 0; color: #1F2937; font-size: 0.85rem; line-height: 1.4;">{reduction_text}</p>
            </div>
            """
            st.markdown(reduction_html, unsafe_allow_html=True)
            
            # 2. Recommended Business Outcome logic
            if new_risk_score > 60: # remains High or Critical
                outcome = "Escalate to Risk Committee."
                outcome_desc = "Despite simulated mitigations, the vendor's risk profile remains high or critical. Professional escalation and review by the Risk Committee is required before access is continued."
                outcome_color = "#EF4444" # Red
            elif points_reduction > 30:
                outcome = "Vendor can move to standard monitoring."
                outcome_desc = "Significant risk reduction achieved. The vendor can be safely transitioned to standard GRC audit cycles and monitoring frequencies."
                outcome_color = "#10B981" # Green
            elif 15 <= points_reduction <= 30:
                outcome = "Vendor requires periodic review."
                outcome_desc = "Moderate risk reduction achieved. Maintain quarterly or semi-annual periodic reviews to verify compliance continues to hold."
                outcome_color = "#F59E0B" # Amber
            else:
                # low reduction and score is Low or Medium
                if new_risk_score <= 30:
                    outcome = "Vendor can move to standard monitoring."
                    outcome_desc = "The vendor's risk score is very low, allowing transition to standard monitoring protocols."
                    outcome_color = "#10B981" # Green
                else:
                    outcome = "Vendor requires periodic review."
                    outcome_desc = "Minimal reduction achieved and risk profile is medium. Vendor requires periodic review to maintain continuous security baseline."
                    outcome_color = "#F59E0B" # Amber
                    
            outcome_html = f"""
            <div class="alert-card" style="border-left: 4px solid {outcome_color}; background-color: #F8FAFC; padding: 16px; margin-bottom: 0;">
                <h5 style="color: {outcome_color}; margin-top: 0; margin-bottom: 6px; font-weight: 700; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em;">Recommended Business Outcome</h5>
                <p style="margin: 0; color: #111827; font-weight: 700; font-size: 0.9rem; margin-bottom: 4px;">{outcome}</p>
                <p style="margin: 0; color: #4B5563; font-size: 0.8rem; line-height: 1.4;">{outcome_desc}</p>
            </div>
            """
            st.markdown(outcome_html, unsafe_allow_html=True)

# ----------------------------------------------------
# 6.6. VIEW - FUTURE VENDOR RISK PREDICTOR
# ----------------------------------------------------
elif menu == "Future Risk Predictor":
    st.markdown("<div class='main-header'><h1>Future Vendor Risk Predictor</h1><p style='color:#4B5563; margin-top:-10px;'>Predict future vendor risk levels based on upcoming compliance and contract events.</p></div>", unsafe_allow_html=True)
    
    # Selection box
    vendor_list = sorted(df['vendor_id'].unique().tolist())
    default_idx = vendor_list.index(st.session_state['selected_vendor_id']) if st.session_state['selected_vendor_id'] in vendor_list else 0
    
    target_vendor = st.selectbox(
        "Select Vendor Profile to Predict Future Risk",
        options=vendor_list,
        index=default_idx
    )
    
    # Update global state so tabs stay synchronized
    st.session_state['selected_vendor_id'] = target_vendor
    
    # Extract vendor data
    v_data = df[df['vendor_id'] == target_vendor].iloc[0]
    
    # Expiry calculations
    days_to_cert = (v_data['cert_expiry'] - ANCHOR_DATE).days
    days_to_contract = (v_data['contract_end'] - ANCHOR_DATE).days
    has_breach = v_data['breach_status'] != 'NONE'
    current_risk = int(v_data['risk_score'])
    
    # Predict future risk score progressions
    projections = {}
    for t in [0, 30, 60, 90]:
        score = current_risk
        
        # Breach history rule
        if has_breach:
            score += 10
            
        # Certification expiry rules
        if 0 < days_to_cert <= 30:
            if t == 30:
                score += 10
            elif t >= 60:
                score += 15
        elif 30 < days_to_cert <= 60:
            if t >= 60:
                score += 15
                
        # Contract expiry rules
        if 0 < days_to_contract <= 90:
            if days_to_contract <= 30:
                if t >= 30:
                    score += 8
            elif days_to_contract <= 60:
                if t >= 60:
                    score += 8
            else: # 60 < days_to_contract <= 90
                if t >= 90:
                    score += 8
                    
        projections[t] = min(100, score)

    # Risk level determination based on score
    def get_risk_level_info(score):
        if score <= 30:
            return "Low", "#10B981"
        elif score <= 60:
            return "Medium", "#F59E0B"
        elif score <= 80:
            return "High", "#F97316"
        else:
            return "Critical", "#EF4444"

    p_col1, p_col2 = st.columns([1, 1.2])
    
    with p_col1:
        st.markdown("<h3 style='color: #0F172A; font-weight: 700; margin-top: 0; margin-bottom: 12px;'>Vendor Context</h3>", unsafe_allow_html=True)
        
        cert_status_str = f"Expiring in {days_to_cert} days" if days_to_cert > 0 else (f"Expired ({v_data['cert_expiry'].strftime('%Y-%m-%d')})" if v_data['is_cert_expired'] else "Active")
        contract_status_str = f"Expiring in {days_to_contract} days" if days_to_contract > 0 else (f"Expired ({v_data['contract_end'].strftime('%Y-%m-%d')})" if v_data['is_contract_expired'] else "Active")
        breach_status_str = v_data['breach_status'].replace('_', ' ').title()
        
        info_html = f"""
        <div style="background-color: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 12px; padding: 24px; min-height: 310px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px;">
                <span style="font-weight: 700; color: #4B5563; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em;">Vendor ID:</span>
                <span style="font-weight: 800; color: #06B6D4; font-size: 1.1rem;">{v_data['vendor_id']}</span>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px;">
                <span style="font-weight: 700; color: #4B5563; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em;">Vendor Type:</span>
                <span style="font-weight: 600; color: #1F2937; font-size: 0.9rem;">{v_data['type'].title()}</span>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px;">
                <span style="font-weight: 700; color: #4B5563; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em;">Current Risk Score:</span>
                <span style="font-weight: 800; color: #111827; font-size: 1.3rem;">{current_risk}</span>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px;">
                <span style="font-weight: 700; color: #4B5563; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em;">Breach History:</span>
                <span style="font-weight: 600; color: {'#EF4444' if has_breach else '#10B981'}; font-size: 0.9rem;">{breach_status_str}</span>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px;">
                <span style="font-weight: 700; color: #4B5563; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em;">Certifications:</span>
                <span style="font-weight: 600; color: {'#F59E0B' if days_to_cert > 0 and days_to_cert <= 60 else '#EF4444' if v_data['is_cert_expired'] else '#10B981'}; font-size: 0.9rem;">{cert_status_str}</span>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0;">
                <span style="font-weight: 700; color: #4B5563; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em;">Contract Expiry:</span>
                <span style="font-weight: 600; color: {'#F59E0B' if days_to_contract > 0 and days_to_contract <= 90 else '#EF4444' if v_data['is_contract_expired'] else '#10B981'}; font-size: 0.9rem;">{contract_status_str}</span>
            </div>
        </div>
        """
        st.markdown(info_html, unsafe_allow_html=True)
        
    with p_col2:
        st.markdown("<h3 style='color: #0F172A; font-weight: 700; margin-top: 0; margin-bottom: 12px;'>Timeline Risk Projections</h3>", unsafe_allow_html=True)
        
        col_c1, col_c2, col_c3, col_c4 = st.columns(4)
        
        def card_html(title, score, level, color):
            return f"""
            <div style="background-color: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 12px; padding: 20px; text-align: center; box-shadow: 0 1px 2px rgba(0,0,0,0.02); min-height: 140px; display: flex; flex-direction: column; justify-content: space-between;">
                <div style="font-size: 0.72rem; color: #4B5563; text-transform: uppercase; font-weight: 600; letter-spacing: 0.05em;">{title}</div>
                <div style="font-size: 2.1rem; font-weight: 800; color: #111827; line-height: 1.1; margin: 8px 0;">{score}</div>
                <span class="badge" style="background-color: {color}15; color: {color}; border: 1px solid {color}30; font-weight: 700; font-size: 0.7rem; justify-content: center; display: inline-flex;">{level.upper()}</span>
            </div>
            """
            
        with col_c1:
            l, c = get_risk_level_info(projections[0])
            st.markdown(card_html("Today", projections[0], l, c), unsafe_allow_html=True)
        with col_c2:
            l, c = get_risk_level_info(projections[30])
            st.markdown(card_html("30 Days", projections[30], l, c), unsafe_allow_html=True)
        with col_c3:
            l, c = get_risk_level_info(projections[60])
            st.markdown(card_html("60 Days", projections[60], l, c), unsafe_allow_html=True)
        with col_c4:
            l, c = get_risk_level_info(projections[90])
            st.markdown(card_html("90 Days", projections[90], l, c), unsafe_allow_html=True)

    st.markdown("---")
    res_p1, res_p2 = st.columns([1.2, 1])
    
    with res_p1:
        st.markdown("<h4 style='color: #0F172A; font-weight: 700; margin-top: 0;'>90-Day Projected Risk Curve</h4>", unsafe_allow_html=True)
        # Create line chart
        fig_proj = go.Figure()
        fig_proj.add_trace(go.Scatter(
            x=['Today', '30 Days', '60 Days', '90 Days'],
            y=[projections[0], projections[30], projections[60], projections[90]],
            mode='lines+markers+text',
            line=dict(color='#06B6D4', width=3),
            marker=dict(size=10, color='#0F172A'),
            text=[projections[0], projections[30], projections[60], projections[90]],
            textposition='top center',
            textfont=dict(family='Inter', size=11, color='#1F2937')
        ))
        fig_proj.update_layout(
            yaxis=dict(range=[0, 110], gridcolor="#E5E7EB"),
            xaxis=dict(gridcolor="#E5E7EB"),
            paper_bgcolor="#FFFFFF",
            plot_bgcolor="#FFFFFF",
            font_family="Inter",
            font_color="#111827",
            height=260,
            margin=dict(l=40, r=40, t=20, b=20)
        )
        st.plotly_chart(fig_proj, use_container_width=True)
        
    with res_p2:
        st.markdown("<h4 style='color: #0F172A; font-weight: 700; margin-top: 0;'>Analysis & Preventive Guidance</h4>", unsafe_allow_html=True)
        
        # Predicted Risk Narrative
        reasons = []
        if has_breach:
            reasons.append("historical security breaches")
        if 0 < days_to_cert <= 60:
            reasons.append(f"upcoming certification expiry (in {days_to_cert} days)")
        if 0 < days_to_contract <= 90:
            reasons.append(f"impending contract expiration (in {days_to_contract} days)")
            
        if len(reasons) > 0:
            reasons_str = ", ".join(reasons[:-1]) + (" and " + reasons[-1] if len(reasons) > 1 else reasons[0])
            narrative_text = f"Vendor risk is expected to increase from {projections[0]} to {projections[90]} due to {reasons_str}."
        else:
            narrative_text = f"Vendor risk is expected to remain stable at {projections[0]} over the next 90 days. No critical upcoming compliance or contract events detected."
            
        narrative_html = f"""
        <div class="alert-card" style="border-left: 4px solid #F59E0B; background-color: #F8FAFC; padding: 16px; margin-bottom: 16px;">
            <h5 style="color: #F59E0B; margin-top: 0; margin-bottom: 6px; font-weight: 700; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em;">Predicted Risk Narrative</h5>
            <p style="margin: 0; color: #1F2937; font-size: 0.85rem; line-height: 1.4;">{narrative_text}</p>
        </div>
        """
        st.markdown(narrative_html, unsafe_allow_html=True)
        
        # Recommended Preventive Actions
        actions = []
        if 0 < days_to_cert <= 60:
            actions.append(f"Renew SOC2 Certification (expiry within {days_to_cert} days)")
        if 0 < days_to_contract <= 90:
            actions.append(f"Review Contract Terms (expiry within {days_to_contract} days)")
        if has_breach:
            actions.append("Schedule Security Assessment (due to historical breach indicators)")
            actions.append("Perform Access Review (privileges audit for high-risk flags)")
            
        if len(actions) == 0:
            actions.append("No immediate actions required. Maintain standard GRC monitoring cycle.")
            
        actions_li_html = "".join([f"<li style='margin-bottom: 4px; font-size: 0.8rem;'>{a}</li>" for a in actions])
        
        actions_html = f"""
        <div class="alert-card" style="border-left: 4px solid #10B981; background-color: #F8FAFC; padding: 16px; margin-bottom: 0;">
            <h5 style="color: #10B981; margin-top: 0; margin-bottom: 6px; font-weight: 700; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em;">Recommended Preventive Actions</h5>
            <ul style="margin: 0; padding-left: 18px; color: #1F2937; line-height: 1.4;">
                {actions_li_html}
            </ul>
        </div>
        """
        st.markdown(actions_html, unsafe_allow_html=True)

# ----------------------------------------------------
# 6.7. VIEW - AI VENDOR RISK ADVISOR
# ----------------------------------------------------
elif menu == "AI Vendor Risk Advisor":
    st.markdown("<div class='main-header'><h1>AI Vendor Risk Advisor</h1><p style='color:#4B5563; margin-top:-10px;'>Executive-grade vendor intelligence, risk explanation, and remediation guidance.</p></div>", unsafe_allow_html=True)
    
    # Selection box
    vendor_list = sorted(df['vendor_id'].unique().tolist())
    default_idx = vendor_list.index(st.session_state['selected_vendor_id']) if st.session_state['selected_vendor_id'] in vendor_list else 0
    
    target_vendor = st.selectbox(
        "Select Vendor Profile to Analyze",
        options=vendor_list,
        index=default_idx
    )
    
    # Update global state so tabs stay synchronized
    st.session_state['selected_vendor_id'] = target_vendor
    
    # Extract vendor data
    v_data = df[df['vendor_id'] == target_vendor].iloc[0]
    
    # Manage button and analysis state
    if 'last_advisor_vendor' not in st.session_state or st.session_state['last_advisor_vendor'] != target_vendor:
        st.session_state['last_advisor_vendor'] = target_vendor
        st.session_state['advisor_analyzed'] = False
        
    st.write("")
    if st.button("Analyze Vendor", use_container_width=True):
        st.session_state['advisor_analyzed'] = True
        
    if st.session_state['advisor_analyzed']:
        with st.spinner("Analyzing GRC telemetry and generating risk brief..."):
            # Expiry and core variables
            days_to_cert = (v_data['cert_expiry'] - ANCHOR_DATE).days
            days_to_contract = (v_data['contract_end'] - ANCHOR_DATE).days
            current_risk = int(v_data['risk_score'])
            
            # Determine Risk Level
            if current_risk >= 80:
                risk_level = "HIGH"
            elif current_risk >= 50:
                risk_level = "MEDIUM"
            else:
                risk_level = "LOW"
                
            # Verdict brackets
            if current_risk <= 39:
                verdict = "APPROVED"
                verdict_color = "#10B981"
                verdict_bg = "#ECFDF5"
                verdict_border = "#A7F3D0"
            elif current_risk <= 64:
                verdict = "WATCHLIST"
                verdict_color = "#D97706"
                verdict_bg = "#FEF3C7"
                verdict_border = "#FDE68A"
            elif current_risk <= 84:
                verdict = "HIGH RISK"
                verdict_color = "#EA580C"
                verdict_bg = "#FFEDD5"
                verdict_border = "#FED7AA"
            else:
                verdict = "CRITICAL REVIEW"
                verdict_color = "#DC2626"
                verdict_bg = "#FEF2F2"
                verdict_border = "#FCA5A5"
                
            # 2. Executive Summary text
            if verdict == "APPROVED":
                summary_text = "This vendor currently presents a low-to-medium risk profile and maintains acceptable governance, compliance, and operational controls. No immediate remediation actions are required."
            elif verdict == "WATCHLIST":
                summary_text = "This vendor presents moderate risk exposure due to compliance gaps and elevated operational risk indicators. Increased monitoring is recommended."
            elif verdict == "HIGH RISK":
                summary_text = "This vendor presents significant risk exposure requiring immediate management attention due to unresolved compliance and security concerns."
            else:  # CRITICAL REVIEW
                summary_text = "This vendor represents a critical third-party risk and requires immediate executive review, remediation planning, and access validation."
                
            # 3. Key Risk Drivers
            drivers = []
            if v_data['is_cert_expired']:
                cert_type = v_data['certifications'] if pd.notna(v_data['certifications']) else "Security"
                drivers.append(f"Expired compliance certification ({cert_type} expired on {v_data['cert_expiry'].strftime('%Y-%m-%d')})")
            elif v_data['certifications'] == 'NONE' or pd.isna(v_data['certifications']):
                drivers.append("Missing core security certifications (no active SOC2 or ISO27001 registered)")

            if v_data['certifications'] not in ['GDPR_COMPLIANT', 'SOC2 & ISO27001'] and 'GDPR' not in str(v_data['certifications']):
                drivers.append("Missing GDPR Data Processing Agreement (DPA) status")

            if v_data['breach_status'] in ['BREACHED_RECENT', 'BREACHED_LAST_12_MONTHS']:
                drivers.append(f"Recorded security breach history ({v_data['breach_status'].replace('_', ' ').title()})")

            if v_data['breach_status'] == 'UNDER_INVESTIGATION' or v_data['anomaly_type'] == 'VENDOR_UNDER_INVESTIGATION':
                drivers.append("Vendor currently under active GRC investigation")

            if v_data['is_contract_expired']:
                drivers.append(f"Expired contract with active access (ended on {v_data['contract_end'].strftime('%Y-%m-%d')})")
            elif 0 <= days_to_contract <= 90:
                drivers.append(f"Contract expiring soon (expires in {days_to_contract} days)")

            if v_data['type'] in ['Payment Processor', 'Cloud Provider', 'Integration Partner']:
                drivers.append(f"High data access privileges (operates as a critical {v_data['type']})")

            if current_risk >= 85:
                drivers.append(f"Critical risk score tier ({current_risk}/100)")
            elif current_risk >= 65:
                drivers.append(f"Elevated risk score tier ({current_risk}/100)")

            if v_data['annual_spend'] >= 500000:
                drivers.append(f"Elevated financial exposure (annual spend of €{v_data['annual_spend']:,.0f})")

            if v_data['is_anomaly'] == 1:
                drivers.append(f"GRC Telemetry Anomaly detected ({v_data['anomaly_type'].replace('_', ' ').title()})")

            if not drivers:
                drivers.append("No active compliance or risk drivers detected in GRC database.")
                
            # 4. Business Impact
            impacts = []
            if v_data['is_cert_expired'] or v_data['certifications'] == 'NONE':
                impacts.append("GDPR Compliance Exposure: Processing personal data without valid certifications introduces regulatory non-compliance.")
                impacts.append("Increased Audit Findings: Internal and external audit teams will flag missing or expired security credentials.")

            if v_data['breach_status'] == 'UNDER_INVESTIGATION' or v_data['anomaly_type'] == 'VENDOR_UNDER_INVESTIGATION':
                impacts.append("Regulatory Reporting Obligations: Active compliance investigations could trigger mandatory disclosure timelines under GDPR/DORA.")

            if v_data['breach_status'] in ['BREACHED_RECENT', 'BREACHED_LAST_12_MONTHS']:
                impacts.append("Supply Chain Trust Damage: Recorded security incidents create client-facing reputational and supply chain trust exposure.")

            if v_data['is_contract_expired'] or (0 <= days_to_contract <= 90):
                impacts.append("Third-Party Legal Risk: Operational integration operates without a valid or current underlying contract agreement.")

            if v_data['type'] in ['Payment Processor', 'Cloud Provider', 'Integration Partner']:
                impacts.append("Elevated Operational Risk: Systemic infrastructure dependency exposes internal processes to supply chain compromise.")

            if v_data['annual_spend'] >= 500000:
                impacts.append("Financial Loss Exposure: Failure or compromise of this vendor carries high business interruption costs.")

            if not impacts:
                impacts.append("Negligible operational impact. Vendor operates within standard security baseline guidelines.")
                
            # 5. Recommended Actions
            actions = []
            if v_data['is_cert_expired'] or v_data['certifications'] == 'NONE':
                actions.append("Renew Security Certifications: Engage vendor compliance officer to request updated SOC2 / ISO27001 credentials.")

            if v_data['breach_status'] in ['BREACHED_RECENT', 'BREACHED_LAST_12_MONTHS', 'UNDER_INVESTIGATION'] or v_data['is_anomaly'] == 1:
                actions.append("Conduct Technical Security Review: Trigger a comprehensive audit of vendor data access logs and network integrations.")

            if v_data['is_contract_expired'] or (0 <= days_to_contract <= 90):
                actions.append("Contract Terms Re-negotiation: Formally initiate contract renewal or draft legal extensions to prevent orphaned service terms.")

            if v_data['type'] in ['Payment Processor', 'Cloud Provider', 'Integration Partner']:
                actions.append("Perform Privilege Access Audit: Verify Least Privilege policy on database and API credentials associated with this vendor.")

            if current_risk >= 65:
                actions.append("Escalate to GRC Committee: Place this vendor profile on the next executive risk committee meeting agenda for oversight review.")

            if not actions:
                actions.append("Maintain standard GRC monitoring and schedule annual compliance reviews.")
                
            # 6. Confidence Score
            total_fields = len(v_data)
            filled_fields = v_data.notna().sum()
            completeness_pct = (filled_fields / total_fields) * 100

            confidence_pct = completeness_pct
            if v_data['breach_status'] == 'UNDER_INVESTIGATION' or v_data['anomaly_type'] == 'VENDOR_UNDER_INVESTIGATION':
                confidence_pct -= 20
            if v_data['is_anomaly'] == 1:
                confidence_pct -= 15
            if v_data['breach_status'] in ['BREACHED_RECENT', 'BREACHED_LAST_12_MONTHS']:
                confidence_pct -= 10

            confidence_pct = max(10, min(100, confidence_pct))

            if confidence_pct >= 85:
                confidence_level = "HIGH"
                confidence_color = "#10B981"
            elif confidence_pct >= 60:
                confidence_level = "MEDIUM"
                confidence_color = "#F59E0B"
            else:
                confidence_level = "LOW"
                confidence_color = "#EF4444"
                
            # 7. Risk Trend Outlook
            if current_risk >= 85 or v_data['breach_status'] == 'UNDER_INVESTIGATION' or v_data['anomaly_type'] == 'VENDOR_UNDER_INVESTIGATION':
                trend = "CRITICAL ESCALATION RISK"
                trend_color = "#DC2626"
                trend_bg = "#FEF2F2"
                trend_border = "#FCA5A5"
                trend_text = "Risk is projected to escalate rapidly due to active compliance investigations or severe security findings. Immediate access containment is advised."
            elif v_data['is_cert_expired'] or v_data['is_contract_expired'] or (0 <= days_to_contract <= 90) or v_data['breach_status'] != 'NONE':
                trend = "INCREASING"
                trend_color = "#EA580C"
                trend_bg = "#FFEDD5"
                trend_border = "#FED7AA"
                trend_text = "Risk exposure is trending upward due to unresolved compliance expiries, contract standing, or incident history. Active remediation is required to stabilize."
            else:
                trend = "STABLE"
                trend_color = "#10B981"
                trend_bg = "#ECFDF5"
                trend_border = "#A7F3D0"
                trend_text = "Risk profile is stable. Vendor controls are functioning within acceptable tolerances with no near-term compliance milestones or incidents."
                
            # 8. Executive Decision Panel
            if verdict == "APPROVED":
                decision = "AUTHORIZED FOR CONTINUED ENGAGEMENT"
                decision_color = "#10B981"
                decision_bg = "#ECFDF5"
                decision_border = "#A7F3D0"
                decision_rationale = f"Vendor complies with core GRC metrics. Risk score is {current_risk} (Low), and security certifications are active. No remediation is necessary."
            elif verdict == "WATCHLIST":
                decision = "APPROVED WITH MONITORING"
                decision_color = "#D97706"
                decision_bg = "#FEF3C7"
                decision_border = "#FDE68A"
                decision_rationale = f"Vendor is approved but placed on active watch. Compliance gaps (risk score: {current_risk}) require quarterly verification and validation."
            elif verdict == "HIGH RISK":
                decision = "REQUIRES REMEDIATION"
                decision_color = "#EA580C"
                decision_bg = "#FFEDD5"
                decision_border = "#FED7AA"
                decision_rationale = f"Vendor presents elevated risk (score: {current_risk}). Continued engagement is subject to completing the recommended security reviews and renewing certifications."
            else:  # CRITICAL REVIEW
                decision = "EXECUTIVE ESCALATION REQUIRED"
                decision_color = "#DC2626"
                decision_bg = "#FEF2F2"
                decision_border = "#FCA5A5"
                decision_rationale = f"Vendor represents critical risk to the organization (score: {current_risk}). Immediate escalation to the Chief Information Security Officer (CISO) is required to review system integrations."
            # 9. Generate PDF Report
            try:
                pdf_buf = create_advisor_pdf(
                    v_data, current_risk, risk_level, verdict,
                    confidence_level, confidence_pct, trend, trend_text,
                    summary_text, drivers, impacts, actions,
                    decision, decision_rationale
                )
                pdf_bytes = pdf_buf.getvalue()
            except Exception as e:
                pdf_bytes = None
                st.error(f"Error generating PDF report: {str(e)}")

            # Rendering Verdict Card (Section 1)
            verdict_card_html = f"""
            <div style="background-color: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 12px; padding: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); margin-bottom: 24px;">
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 16px;">
                    <div>
                        <div style="font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; color: #6B7280; font-weight: 600;">AI GRC RISK VERDICT</div>
                        <div style="font-size: 1.8rem; font-weight: 800; color: #111827; margin-top: 4px;">{v_data['vendor_id']}</div>
                        <div style="font-size: 0.875rem; color: #4B5563; margin-top: 2px;">Type: <strong>{v_data['type'].title()}</strong></div>
                    </div>
                    <div style="display: flex; gap: 16px; align-items: center; flex-wrap: wrap;">
                        <div style="text-align: center; border-right: 1px solid #E5E7EB; padding-right: 16px;">
                            <div style="font-size: 0.7rem; color: #6B7280; font-weight: 600; text-transform: uppercase;">Risk Score</div>
                            <div style="font-size: 1.5rem; font-weight: 800; color: #111827;">{current_risk}</div>
                        </div>
                        <div style="text-align: center; border-right: 1px solid #E5E7EB; padding-right: 16px;">
                            <div style="font-size: 0.7rem; color: #6B7280; font-weight: 600; text-transform: uppercase;">Risk Level</div>
                            <div style="font-size: 1.25rem; font-weight: 700; color: #111827;">{risk_level}</div>
                        </div>
                        <div style="text-align: center; border-right: 1px solid #E5E7EB; padding-right: 16px;">
                            <div style="font-size: 0.7rem; color: #6B7280; font-weight: 600; text-transform: uppercase;">Severity</div>
                            <div style="font-size: 1.25rem; font-weight: 700; color: #111827;">{v_data['severity']}</div>
                        </div>
                        <div style="background-color: {verdict_bg}; color: {verdict_color}; border: 1px solid {verdict_border}; padding: 12px 24px; border-radius: 8px; font-weight: 800; font-size: 1.25rem; text-align: center; letter-spacing: 0.05em; box-shadow: 0 1px 2px rgba(0,0,0,0.02);">
                            {verdict}
                        </div>
                    </div>
                </div>
            </div>
            """
            st.markdown(verdict_card_html, unsafe_allow_html=True)
            
            # Rendering Grid Layout for other sections
            col_summary, col_confidence = st.columns([2, 1])
            with col_summary:
                # Render Executive Summary as a card (Section 2)
                st.markdown(f"""
                <div style="background-color: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 12px; padding: 24px; height: 100%;">
                    <h3 style="color: #111827; font-size: 1.15rem; margin-top: 0; margin-bottom: 12px; border-bottom: 2px solid #E5E7EB; padding-bottom: 8px;">Executive Summary</h3>
                    <p style="color: #374151; font-size: 0.95rem; line-height: 1.6; margin: 0;">{summary_text}</p>
                </div>
                """, unsafe_allow_html=True)
            with col_confidence:
                # Render Confidence Badge as a card (Section 6)
                st.markdown(f"""
                <div style="background-color: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 12px; padding: 24px; height: 100%;">
                    <h3 style="color: #111827; font-size: 1.15rem; margin-top: 0; margin-bottom: 12px; border-bottom: 2px solid #E5E7EB; padding-bottom: 8px;">GRC Confidence Score</h3>
                    <div style="display: flex; align-items: center; gap: 12px; margin-top: 12px;">
                        <div style="background-color: {confidence_color}15; color: {confidence_color}; border: 1px solid {confidence_color}30; padding: 8px 16px; border-radius: 8px; font-weight: 800; font-size: 1.1rem; text-align: center;">
                            {confidence_level}
                        </div>
                        <div style="font-size: 1.8rem; font-weight: 800; color: #111827;">{confidence_pct:.0f}%</div>
                    </div>
                    <p style="color: #6B7280; font-size: 0.8rem; margin-top: 12px; margin-bottom: 0; line-height: 1.4;">Based on data completeness ({completeness_pct:.0f}% populated fields) and active compliance investigations.</p>
                </div>
                """, unsafe_allow_html=True)

            st.write("")

            col_drivers, col_impact = st.columns(2)
            with col_drivers:
                # Render Key Risk Drivers (Section 3)
                drivers_li_html = "".join([f"<li style='margin-bottom: 10px; font-size: 0.9rem; color: #374151;'>{d}</li>" for d in drivers])
                st.markdown(f"""
                <div style="background-color: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 12px; padding: 24px; height: 100%;">
                    <h3 style="color: #111827; font-size: 1.15rem; margin-top: 0; margin-bottom: 12px; border-bottom: 2px solid #E5E7EB; padding-bottom: 8px;">Key Risk Drivers</h3>
                    <ul style="padding-left: 20px; margin: 0;">
                        {drivers_li_html}
                    </ul>
                </div>
                """, unsafe_allow_html=True)
            with col_impact:
                # Render Business Impact (Section 4)
                impacts_li_html = "".join([f"<li style='margin-bottom: 10px; font-size: 0.9rem; color: #374151;'>{i}</li>" for i in impacts])
                st.markdown(f"""
                <div style="background-color: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 12px; padding: 24px; height: 100%;">
                    <h3 style="color: #111827; font-size: 1.15rem; margin-top: 0; margin-bottom: 12px; border-bottom: 2px solid #E5E7EB; padding-bottom: 8px;">Business Impact Analysis</h3>
                    <ul style="padding-left: 20px; margin: 0;">
                        {impacts_li_html}
                    </ul>
                </div>
                """, unsafe_allow_html=True)

            st.write("")

            col_actions, col_trend = st.columns([2, 1])
            with col_actions:
                # Render Recommended Actions (Section 5)
                actions_li_html = "".join([f"<li style='margin-bottom: 10px; font-size: 0.9rem; color: #111827; font-weight: 500;'>{a}</li>" for a in actions])
                st.markdown(f"""
                <div style="background-color: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 12px; padding: 24px; height: 100%;">
                    <h3 style="color: #111827; font-size: 1.15rem; margin-top: 0; margin-bottom: 12px; border-bottom: 2px solid #E5E7EB; padding-bottom: 8px;">Recommended GRC Mitigation Actions</h3>
                    <ul style="padding-left: 20px; margin: 0;">
                        {actions_li_html}
                    </ul>
                </div>
                """, unsafe_allow_html=True)
            with col_trend:
                # Render Risk Trend Outlook (Section 7)
                st.markdown(f"""
                <div style="background-color: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 12px; padding: 24px; height: 100%;">
                    <h3 style="color: #111827; font-size: 1.15rem; margin-top: 0; margin-bottom: 12px; border-bottom: 2px solid #E5E7EB; padding-bottom: 8px;">Risk Trend Outlook</h3>
                    <div style="display: inline-block; background-color: {trend_bg}; color: {trend_color}; border: 1px solid {trend_border}; padding: 6px 14px; border-radius: 6px; font-weight: 800; font-size: 0.85rem; text-transform: uppercase; margin-top: 4px; margin-bottom: 12px;">
                        {trend}
                    </div>
                    <p style="color: #374151; font-size: 0.9rem; margin: 0; line-height: 1.5;">{trend_text}</p>
                </div>
                """, unsafe_allow_html=True)

            st.write("")

            # Render Decision panel (Section 8)
            st.markdown(f"""
            <div style="background-color: {decision_bg}; border: 1.5px solid {decision_border}; border-radius: 12px; padding: 24px; margin-bottom: 16px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.02);">
                <div style="font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; color: {decision_color}; font-weight: 700;">OFFICIAL EXECUTIVE GRC DECISION</div>
                <div style="font-size: 1.4rem; font-weight: 800; color: {decision_color}; margin-top: 4px;">{decision}</div>
                <div style="font-size: 0.9rem; color: #374151; margin-top: 8px; line-height: 1.5;"><strong>Rationale:</strong> {decision_rationale}</div>
            </div>
            """, unsafe_allow_html=True)

            st.write("")
            # Render Download Report (Section 9)
            if pdf_bytes is not None:
                st.download_button(
                    label="Download Formatted GRC Report (PDF)",
                    data=pdf_bytes,
                    file_name=f"{v_data['vendor_id']}_AI_GRC_Assessment.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

# ----------------------------------------------------
# 7. VIEW - ALERTS & INCIDENTS
# ----------------------------------------------------
elif menu == "Alerts & Incidents":
    st.markdown("<div class='main-header'><h1>Alerts & Incidents Center</h1><p style='color:#4B5563; margin-top:-10px;'>Active compliance logs and critical investigations generated by GRC validation checks.</p></div>", unsafe_allow_html=True)
    
    # Pre-calculated alerts
    expired_cert_df = df[df['is_cert_expired']].copy()
    high_risk_df = df[df['risk_score'] >= 80].copy()
    investigation_df = df[
        (df['breach_status'] == 'UNDER_INVESTIGATION') | 
        (df['anomaly_type'] == 'VENDOR_UNDER_INVESTIGATION')
    ].copy()
    expired_contract_df = df[df['is_contract_expired']].copy()
    
    alert_tab1, alert_tab2, alert_tab3, alert_tab4 = st.tabs([
        f"Expired Credentials ({len(expired_cert_df)})",
        f"High Risk Profile ({len(high_risk_df)})",
        f"Under Investigation ({len(investigation_df)})",
        f"Expired Contracts ({len(expired_contract_df)})"
    ])
    
    with alert_tab1:
        st.subheader("Expired Certifications & Credentials")
        st.warning("Action Required: The following vendors possess expired security or operational credentials. Reach out to request updated SOC2 or ISO certificates.")
        
        st.dataframe(
            expired_cert_df[[
                'vendor_id', 'type', 'certifications', 'cert_expiry', 'annual_spend', 'severity'
            ]],
            column_config={
                "vendor_id": "Vendor ID",
                "type": "Vendor Category",
                "certifications": "Expired Certificate",
                "cert_expiry": st.column_config.DateColumn("Expired Date", format="YYYY-MM-DD"),
                "annual_spend": st.column_config.NumberColumn("Annual spend", format="€%,.0f"),
                "severity": "Severity"
            },
            hide_index=True,
            use_container_width=True
        )
        
    with alert_tab2:
        st.subheader("High Risk Profile Warnings")
        st.error("Urgent Notice: The vendors listed below have risk evaluation scores exceeding 80/100. Implement additional security evaluations and network segmentation.")
        
        st.dataframe(
            high_risk_df[[
                'vendor_id', 'type', 'risk_score', 'severity', 'breach_status', 'annual_spend'
            ]].sort_values('risk_score', ascending=False),
            column_config={
                "vendor_id": "Vendor ID",
                "type": "Vendor Category",
                "risk_score": st.column_config.ProgressColumn("Risk Score", min_value=0, max_value=100, format="%d"),
                "severity": "Severity Rating",
                "breach_status": "Breach History Status",
                "annual_spend": st.column_config.NumberColumn("Annual spend", format="€%,.0f")
            },
            hide_index=True,
            use_container_width=True
        )
        
    with alert_tab3:
        st.subheader("Security Breach & Policy Investigations")
        st.markdown(
            "<div class='alert-card' style='border-color: #EF4444;'><h4 style='margin:0; color:#EF4444;'>Active Audit Investigation Protocol</h4>"
            "<p style='margin:5px 0 0 0; font-size:0.9rem; color:#1F2937;'>These third parties are currently flagged under active internal security reviews. Suspend all non-essential data access keys immediately.</p></div>", 
            unsafe_allow_html=True
        )
        
        st.dataframe(
            investigation_df[[
                'vendor_id', 'type', 'breach_status', 'anomaly_type', 'explanation', 'annual_spend'
            ]],
            column_config={
                "vendor_id": "Vendor ID",
                "type": "Vendor Category",
                "breach_status": "Status",
                "anomaly_type": "Incident Flag",
                "explanation": "Security Explanation",
                "annual_spend": st.column_config.NumberColumn("Annual spend", format="€%,.0f")
            },
            hide_index=True,
            use_container_width=True
        )
        
    with alert_tab4:
        st.subheader("Contract Expiration Alerts")
        st.info("Notice: Contracts for the following vendors have expired, but active database access or systems integrations may still be running.")
        
        st.dataframe(
            expired_contract_df[[
                'vendor_id', 'type', 'contract_end', 'annual_spend', 'severity', 'explanation'
            ]],
            column_config={
                "vendor_id": "Vendor ID",
                "type": "Vendor Category",
                "contract_end": st.column_config.DateColumn("Terminated Date", format="YYYY-MM-DD"),
                "annual_spend": st.column_config.NumberColumn("Annual Spend", format="€%,.0f"),
                "severity": "Severity",
                "explanation": "Audit Details"
            },
            hide_index=True,
            use_container_width=True
        )
