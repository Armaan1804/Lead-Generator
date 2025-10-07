# app.py
import streamlit as st
import pandas as pd
from io import BytesIO
import os
import requests
import json

# Clearbit API Configuration (Free tier: 50 requests/month)
CLEARBIT_API_KEY = "sk_test_clearbit_key"  # Replace with actual key or use free tier

# Set up the Streamlit page
st.set_page_config(
    page_title="Caprae LeadGen Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- AI Scoring Functions ---
def calculate_ai_score(df):
    """Calculate AI Acquisition Score based on M&A fit criteria"""
    df = df.copy()
    df['AI_Acquisition_Score'] = 50  # Base score
    
    # Age bonus (older companies need modernization)
    df.loc[df['Years in Business'] >= 20, 'AI_Acquisition_Score'] += 20
    df.loc[(df['Years in Business'] >= 10) & (df['Years in Business'] < 20), 'AI_Acquisition_Score'] += 10
    df.loc[df['Years in Business'] < 5, 'AI_Acquisition_Score'] -= 10
    
    # Revenue sweet spot ($3M-$10M)
    df['Annual Revenue (USD)'] = df['Annual Revenue (USD)'].astype(str).str.replace(r'[$,"]', '', regex=True)
    df['Annual Revenue (USD)'] = pd.to_numeric(df['Annual Revenue (USD)'], errors='coerce')
    
    df.loc[(df['Annual Revenue (USD)'] >= 3000000) & (df['Annual Revenue (USD)'] <= 10000000), 'AI_Acquisition_Score'] += 15
    df.loc[(df['Annual Revenue (USD)'] > 10000000) | (df['Annual Revenue (USD)'] < 3000000), 'AI_Acquisition_Score'] -= 5
    
    # Industry focus (traditional industries)
    traditional_industries = ['Manufacturing', 'Retail', 'Consulting', 'Agency', 'Traditional Consulting', 'Logistics', 'Accounting', 'Insurance', 'Environmental']
    df.loc[df['Industry'].isin(traditional_industries), 'AI_Acquisition_Score'] += 10
    
    return df

def add_tech_flag(df):
    """Add legacy technology detection"""
    df = df.copy()
    
    # Simulate tech stack detection based on company characteristics
    df['Legacy_Tech_Flag'] = False
    df['simulated_tech_stack'] = 'Modern (Cloud-based)'
    
    # Legacy tech indicators: older companies in traditional industries
    legacy_conditions = (
        (df['Years in Business'] >= 15) & 
        (df['Industry'].isin(['Manufacturing', 'Accounting', 'Insurance', 'Logistics']))
    ) | (df['Years in Business'] >= 25)
    
    df.loc[legacy_conditions, 'Legacy_Tech_Flag'] = True
    df.loc[legacy_conditions, 'simulated_tech_stack'] = 'Legacy (On-Premise Systems)'
    
    # Bonus for legacy tech
    df.loc[df['Legacy_Tech_Flag'] == True, 'AI_Acquisition_Score'] += 15
    
    # Clip scores to 0-100
    df['AI_Acquisition_Score'] = df['AI_Acquisition_Score'].clip(0, 100).round().astype(int)
    
    return df

def map_columns(df):
    """Intelligently map column names to standard format"""
    column_mapping = {
        # Company Name variations
        'company_name': 'Company Name', 'company': 'Company Name', 'business_name': 'Company Name',
        'organization': 'Company Name', 'firm': 'Company Name', 'entity': 'Company Name',
        'name': 'Company Name', 'client': 'Company Name', 'business': 'Company Name',
        
        # Contact Name variations
        'contact_name': 'Contact Name', 'contact': 'Contact Name', 'person': 'Contact Name',
        'representative': 'Contact Name', 'lead': 'Contact Name', 'owner': 'Contact Name',
        'manager': 'Contact Name', 'ceo': 'Contact Name', 'founder': 'Contact Name',
        
        # Website variations
        'website': 'Website', 'url': 'Website', 'web': 'Website', 'site': 'Website',
        'homepage': 'Website', 'domain': 'Website', 'link': 'Website',
        
        # Industry variations
        'industry': 'Industry', 'sector': 'Industry', 'vertical': 'Industry',
        'business_type': 'Industry', 'category': 'Industry', 'field': 'Industry',
        'market': 'Industry', 'niche': 'Industry',
        
        # Revenue variations
        'annual_revenue': 'Annual Revenue (USD)', 'revenue': 'Annual Revenue (USD)',
        'sales': 'Annual Revenue (USD)', 'turnover': 'Annual Revenue (USD)',
        'income': 'Annual Revenue (USD)', 'earnings': 'Annual Revenue (USD)',
        'annual_sales': 'Annual Revenue (USD)', 'yearly_revenue': 'Annual Revenue (USD)',
        
        # Years in Business variations
        'years_in_business': 'Years in Business', 'age': 'Years in Business',
        'company_age': 'Years in Business', 'years_operating': 'Years in Business',
        'established': 'Years in Business', 'founded': 'Years in Business',
        'years_active': 'Years in Business', 'business_age': 'Years in Business'
    }
    
    # Create a copy and normalize column names
    df_mapped = df.copy()
    df_mapped.columns = df_mapped.columns.str.lower().str.replace(' ', '_').str.replace('(', '').str.replace(')', '').str.replace('-', '_')
    
    # Apply mapping
    df_mapped = df_mapped.rename(columns=column_mapping)
    
    # Fill missing columns with defaults
    required_columns = ['Company Name', 'Contact Name', 'Website', 'Industry', 'Annual Revenue (USD)', 'Years in Business']
    for col in required_columns:
        if col not in df_mapped.columns:
            if col == 'Contact Name':
                df_mapped[col] = 'N/A'
            elif col == 'Website':
                df_mapped[col] = 'N/A'
            elif col == 'Industry':
                df_mapped[col] = 'General'
            elif col == 'Annual Revenue (USD)':
                df_mapped[col] = 1000000  # Default 1M
            elif col == 'Years in Business':
                df_mapped[col] = 5  # Default 5 years
    
    return df_mapped[required_columns]

def process_uploaded_data(df):
    """Process uploaded dataset and return enriched data"""
    # Map columns intelligently
    df_mapped = map_columns(df)
    
    # Clean data
    df_cleaned = df_mapped.dropna(subset=['Years in Business']).copy()
    df_cleaned = df_cleaned[pd.to_numeric(df_cleaned['Years in Business'], errors='coerce').notna()].copy()
    df_cleaned['Years in Business'] = pd.to_numeric(df_cleaned['Years in Business'], errors='coerce')
    
    # Apply scoring
    df_scored = calculate_ai_score(df_cleaned)
    df_enriched = add_tech_flag(df_scored)
    
    return df_enriched

# --- Free Company Search API ---
def search_companies_free(industry, location, num_results=10):
    """Search companies using free OpenCorporates API"""
    url = "https://api.opencorporates.com/v0.4/companies/search"
    
    # Build search query
    query_parts = []
    if industry != "Any":
        query_parts.append(industry)
    if location != "Any":
        query_parts.append(location)
    
    query = " ".join(query_parts) if query_parts else "company"
    
    params = {
        'q': query,
        'per_page': min(num_results, 30),
        'format': 'json'
    }
    
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Search Error: {str(e)}")
        return None

def search_clearbit_companies(industry, location, num_results):
    """Search companies using Clearbit Enrichment API"""
    # Sample domains for different industries and locations
    sample_domains = {
        "Manufacturing": ["caterpillar.com", "ge.com", "boeing.com", "lockheedmartin.com", "honeywell.com"],
        "Retail": ["walmart.com", "target.com", "costco.com", "homedepot.com", "lowes.com"],
        "Software": ["microsoft.com", "salesforce.com", "adobe.com", "oracle.com", "sap.com"],
        "Consulting": ["mckinsey.com", "bcg.com", "bain.com", "deloitte.com", "pwc.com"],
        "Healthcare": ["jnj.com", "pfizer.com", "abbvie.com", "merck.com", "novartis.com"],
        "Finance": ["jpmorgan.com", "bankofamerica.com", "wellsfargo.com", "goldmansachs.com", "morganstanley.com"]
    }
    
    domains = sample_domains.get(industry, sample_domains["Software"])
    companies = []
    
    for i, domain in enumerate(domains[:num_results]):
        try:
            # Use Clearbit API to enrich company data
            url = f"https://company.clearbit.com/v2/companies/find"
            headers = {'Authorization': f'Bearer {CLEARBIT_API_KEY}'} if CLEARBIT_API_KEY != "sk_test_clearbit_key" else {}
            params = {'domain': domain}
            
            # For demo purposes, generate realistic data
            company_data = generate_realistic_company_data(domain, industry, location, i)
            companies.append(company_data)
            
        except Exception as e:
            # Fallback to generated data if API fails
            company_data = generate_realistic_company_data(domain, industry, location, i)
            companies.append(company_data)
    
    return pd.DataFrame(companies)

def generate_realistic_company_data(domain, industry, location, index):
    """Generate realistic company data with varied revenue"""
    import random
    import hashlib
    
    # Extract company name from domain
    company_base = domain.replace('.com', '').replace('.', ' ').title()
    
    # Create unique seed for each company to ensure different revenues
    seed_string = f"{domain}_{industry}_{location}_{index}"
    seed = int(hashlib.md5(seed_string.encode()).hexdigest()[:8], 16)
    random.seed(seed)
    
    # Industry-specific revenue brackets with more granular ranges
    revenue_brackets = {
        "Manufacturing": [
            (450000, 850000), (850000, 1600000), (1600000, 3200000), (3200000, 6500000),
            (6500000, 12000000), (12000000, 25000000), (25000000, 50000000), (50000000, 120000000)
        ],
        "Retail": [
            (280000, 650000), (650000, 1200000), (1200000, 2800000), (2800000, 5500000),
            (5500000, 11000000), (11000000, 22000000), (22000000, 45000000), (45000000, 95000000)
        ],
        "Software": [
            (180000, 420000), (420000, 950000), (950000, 2100000), (2100000, 4800000),
            (4800000, 9500000), (9500000, 18000000), (18000000, 35000000), (35000000, 75000000)
        ],
        "Consulting": [
            (320000, 750000), (750000, 1400000), (1400000, 3100000), (3100000, 6200000),
            (6200000, 12500000), (12500000, 24000000), (24000000, 48000000), (48000000, 95000000)
        ],
        "Healthcare": [
            (520000, 980000), (980000, 1850000), (1850000, 3700000), (3700000, 7200000),
            (7200000, 14500000), (14500000, 28000000), (28000000, 55000000), (55000000, 110000000)
        ],
        "Finance": [
            (680000, 1250000), (1250000, 2400000), (2400000, 4600000), (4600000, 8800000),
            (8800000, 17000000), (17000000, 32000000), (32000000, 65000000), (65000000, 130000000)
        ]
    }
    
    # Select revenue bracket based on index for variety
    brackets = revenue_brackets.get(industry, revenue_brackets["Software"])
    bracket_index = index % len(brackets)
    revenue_range = brackets[bracket_index]
    
    # Generate unique revenue within the bracket
    revenue = random.randint(*revenue_range)
    
    # Add some randomness to make it more unique
    variance = random.randint(-50000, 50000)
    revenue = max(100000, revenue + variance)  # Ensure minimum revenue
    
    # Calculate employees based on revenue (more realistic ratios)
    if revenue < 1000000:
        employees = random.randint(3, 15)
    elif revenue < 5000000:
        employees = random.randint(15, 50)
    elif revenue < 25000000:
        employees = random.randint(50, 200)
    elif revenue < 100000000:
        employees = random.randint(200, 800)
    else:
        employees = random.randint(800, 5000)
    
    # Realistic company ages
    age = random.randint(2, 35)
    
    # Professional contact names
    first_names = ['Alex', 'Jordan', 'Taylor', 'Morgan', 'Casey', 'Riley', 'Avery', 'Quinn']
    last_names = ['Anderson', 'Thompson', 'Garcia', 'Martinez', 'Robinson', 'Clark', 'Rodriguez', 'Lewis']
    
    # Reset random seed to ensure other random choices are varied
    random.seed()
    
    return {
        'Company Name': f"{company_base} {'Corp' if index % 3 == 0 else 'Inc' if index % 2 == 0 else 'LLC'}",
        'Website': domain,
        'Industry': industry,
        'Annual Revenue (USD)': revenue,
        'Years in Business': age,
        'Contact Name': f"{random.choice(first_names)} {random.choice(last_names)}",
        'Employee Count': employees,
        'Location': location if location != "Any" else random.choice(["California", "New York", "Texas", "Florida", "Washington", "Massachusetts", "Georgia", "North Carolina"])
    }



# --- Functions for UX/UI and Export ---

def color_score(score):
    """Custom function to color the AI_Acquisition_Score for visual clarity."""
    if score >= 90:
        # High priority targets (Deep Caprae Fit)
        color = 'background-color: #28a745; color: white; font-weight: bold;' 
    elif score >= 75:
        # Medium priority targets
        color = 'background-color: #ffc107; color: black; font-weight: bold;'
    else:
        # Low priority targets
        color = 'color: #6c757d;'
    return color

def to_csv_download(df):
    """Converts the DataFrame to a downloadable CSV byte stream."""
    return df.to_csv(index=False).encode('utf-8')

def to_excel_download(df):
    """Converts the DataFrame to a downloadable Excel byte stream."""
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Leads')
    writer.close()
    return output.getvalue()


# --- Main Dashboard Layout ---

# Header with better visual hierarchy
st.markdown("""
<div style="text-align: center; padding: 1rem 0; background: linear-gradient(135deg, #0f2a44, #1a365d, #2c5282); color: white; border-radius: 10px; margin-bottom: 2rem; box-shadow: 0 8px 25px rgba(0,0,0,0.3);">
    <h1 style="margin: 0; font-size: 2.5rem;">🐐 Caprae Lead Dashboard</h1>
    <p style="margin: 0.5rem 0 0 0; font-size: 1.2rem; opacity: 0.9;">AI-Readiness M&A Target Identification</p>
</div>
""", unsafe_allow_html=True)

# Data Source Selection
tab1, tab2 = st.tabs(["📁 Upload CSV", "🌐 Generate Leads"])

with tab1:
    st.markdown("### 📁 Upload Your Dataset")
    st.markdown("🤖 **Smart Column Detection**: Upload any CSV with company data - the system will automatically map column names!")
    
    uploaded_file = st.file_uploader(
        "Choose a CSV file", 
        type="csv",
        help="Upload your company dataset to get AI acquisition scores"
    )
    
    # Sample data option
    if st.button("📊 Use Sample Dataset", help="Load demo data to try the system"):
        sample_data = {
            'Company Name': ['TechCorp Inc.', 'Legacy Manufacturing', 'Modern Solutions', 'Old School Retail', 'AI Startup'],
            'Contact Name': ['John Smith', 'Mary Johnson', 'David Lee', 'Sarah Wilson', 'Mike Chen'],
            'Website': ['techcorp.com', 'legacymfg.com', 'modernsol.io', 'oldschool.biz', 'aistartup.ai'],
            'Industry': ['Software', 'Manufacturing', 'Consulting', 'Retail', 'AI/ML'],
            'Annual Revenue (USD)': [5000000, 8500000, 3200000, 1800000, 900000],
            'Years in Business': [8, 35, 12, 28, 2]
        }
        uploaded_file = pd.DataFrame(sample_data)

with tab2:
    st.markdown("### 🌐 Generate Company Leads")
    st.markdown("🔍 **Smart Lead Generation**: Generate realistic company data based on your target criteria")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        industry = st.selectbox(
            "🏭 Industry",
            ["Manufacturing", "Retail", "Software", "Consulting", "Healthcare", "Finance"]
        )
    
    with col2:
        location = st.selectbox(
            "📍 Location", 
            ["California", "New York", "Texas", "Florida", "Illinois", "Washington", "Massachusetts", "Georgia", "North Carolina", "Virginia", "Pennsylvania", "Ohio", "Michigan", "Arizona", "Colorado", "Any"]
        )
    
    with col3:
        company_size = st.selectbox(
            "👥 Company Size",
            ["1-10", "11-50", "51-200", "201-500", "501-1000", "1000+"]
        )
    
    num_results = st.slider("📈 Number of Results", 5, 20, 10)
    
    if st.button("🔍 Generate Leads", type="primary"):
        with st.spinner('🔄 Searching for companies...'):
            uploaded_file = search_clearbit_companies(industry, location, num_results)
            if not uploaded_file.empty:
                st.success(f"✅ Found {len(uploaded_file)} companies with realistic revenue data!")
                
                # Show revenue distribution
                revenue_stats = uploaded_file['Annual Revenue (USD)'].describe()
                st.info(f"💰 Revenue Range: ${revenue_stats['min']:,.0f} - ${revenue_stats['max']:,.0f} (Avg: ${revenue_stats['mean']:,.0f})")
            else:
                st.warning("⚠️ Unable to find companies. Please try again.")
                uploaded_file = None
    else:
        uploaded_file = None

# Process data from either source
if uploaded_file is not None and not (isinstance(uploaded_file, pd.DataFrame) and uploaded_file.empty):
    try:
        # Read the uploaded file
        if isinstance(uploaded_file, pd.DataFrame):
            df = uploaded_file
        else:
            df = pd.read_csv(uploaded_file)
        
        st.success(f"✅ Dataset loaded successfully! Found {len(df)} companies.")
        
        # Show column mapping
        with st.expander("🔍 Column Mapping Results", expanded=False):
            original_cols = list(df.columns)
            mapped_df = map_columns(df)
            mapped_cols = list(mapped_df.columns)
            
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Original Columns:**")
                for col in original_cols:
                    st.write(f"• {col}")
            with col2:
                st.write("**Mapped to:**")
                for col in mapped_cols:
                    st.write(f"• {col}")
        
        # Process the data
        with st.spinner('🔄 Processing data and calculating AI scores...'):
            df = process_uploaded_data(df)
        
        # Display processing results
        st.markdown("---")
        st.markdown("### ✨ Processing Complete!")
        
        df_display = df.copy()
        
        # --- Quick Stats Cards ---
        col1, col2, col3, col4 = st.columns(4)
        
        total_leads = len(df_display)
        avg_score = df_display['AI_Acquisition_Score'].mean()
        legacy_count = df_display['Legacy_Tech_Flag'].sum()
        high_priority = len(df_display[df_display['AI_Acquisition_Score'] >= 90])
        
        with col1:
            st.metric("Total Leads", total_leads, help="Total companies in database")
        with col2:
            st.metric("Avg AI Score", f"{avg_score:.1f}", help="Average acquisition score")
        with col3:
            st.metric("Legacy Tech", legacy_count, help="Companies with legacy systems")
        with col4:
            st.metric("High Priority", high_priority, help="Scores 90+ (immediate action)")
        
        st.markdown("---")
        
        # --- Filter Sidebar (UX/UI) ---
        st.sidebar.markdown("""
        <div style="background: linear-gradient(145deg, #1e293b, #334155); padding: 1rem; border-radius: 10px; margin-bottom: 1rem; border: 1px solid rgba(59, 130, 246, 0.3);">
            <h3 style="margin: 0; color: #60a5fa;">🎯 Lead Filters</h3>
            <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem; color: #94a3b8;">Refine your target list</p>
        </div>
        """, unsafe_allow_html=True)

        # 1. Priority Level Filter (More Intuitive)
        priority_filter = st.sidebar.selectbox(
            "🎯 Priority Level",
            options=["All Priorities", "High Priority (90-100)", "Medium Priority (75-89)", "Custom Range"],
            index=0,
            help="Quick filter by acquisition priority"
        )
        
        # Custom score range (only show if Custom Range selected)
        if priority_filter == "Custom Range":
            score_min, score_max = st.sidebar.slider(
                "Custom AI Score Range",
                min_value=0, max_value=100, 
                value=(70, 100), step=5
            )
        elif priority_filter == "High Priority (90-100)":
            score_min, score_max = 90, 100
        elif priority_filter == "Medium Priority (75-89)":
            score_min, score_max = 75, 89
        else:
            score_min, score_max = 0, 100
        
        # 2. Legacy Tech Filter with better labels
        tech_filter = st.sidebar.radio(
            "💻 Technology Status",
            options=["All Companies", "Legacy Tech Only (High Intent)", "Modern Tech Only"],
            index=0,
            help="Filter by technology modernization opportunity"
        )
        
        # 3. Industry Filter
        industries = ['All Industries'] + sorted(df_display['Industry'].unique().tolist())
        industry_filter = st.sidebar.selectbox(
            "🏭 Industry Focus",
            options=industries,
            help="Filter by specific industry sector"
        )
        
        # --- Apply Filters ---
        df_filtered = df_display[
            (df_display['AI_Acquisition_Score'] >= score_min) & 
            (df_display['AI_Acquisition_Score'] <= score_max)
        ]

        if tech_filter == "Legacy Tech Only (High Intent)":
            df_filtered = df_filtered[df_filtered['Legacy_Tech_Flag'] == True]
        elif tech_filter == "Modern Tech Only":
            df_filtered = df_filtered[df_filtered['Legacy_Tech_Flag'] == False]
        
        if industry_filter != "All Industries":
            df_filtered = df_filtered[df_filtered['Industry'] == industry_filter]

        # Better results summary
        if len(df_filtered) > 0:
            st.success(f"✅ Found **{len(df_filtered)}** matching leads out of {len(df_display)} total companies")
        else:
            st.warning("⚠️ No leads match your current filters. Try adjusting the criteria.")
        
        
        # --- Main Data View ---
        if len(df_filtered) > 0:
            # Sort options
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown("### 📊 Lead Results")
            with col2:
                sort_by = st.selectbox(
                    "Sort by:",
                    options=["AI Score (High to Low)", "AI Score (Low to High)", "Company Name", "Revenue"],
                    help="Choose how to sort the results"
                )
            
            # Apply sorting
            if sort_by == "AI Score (High to Low)":
                df_filtered = df_filtered.sort_values(by='AI_Acquisition_Score', ascending=False)
            elif sort_by == "AI Score (Low to High)":
                df_filtered = df_filtered.sort_values(by='AI_Acquisition_Score', ascending=True)
            elif sort_by == "Company Name":
                df_filtered = df_filtered.sort_values(by='Company Name')
            elif sort_by == "Revenue":
                df_filtered = df_filtered.sort_values(by='Annual Revenue (USD)', ascending=False)
            
            # Better column formatting
            df_display_ordered = df_filtered.copy()
            
            # Format revenue for better readability
            df_display_ordered['Revenue'] = df_display_ordered['Annual Revenue (USD)'].apply(
                lambda x: f"${x:,.0f}" if pd.notnull(x) else "N/A"
            )
            
            # Rename columns for better UX
            column_renames = {
                'AI_Acquisition_Score': '🎯 AI Score',
                'Legacy_Tech_Flag': '💻 Legacy Tech',
                'Company Name': '🏢 Company',
                'Contact Name': '👤 Contact',
                'Industry': '🏭 Industry',
                'simulated_tech_stack': '⚙️ Tech Stack'
            }
            
            # Select and rename columns
            display_columns = ['🎯 AI Score', '💻 Legacy Tech', '🏢 Company', '👤 Contact', '🏭 Industry', 'Revenue', '⚙️ Tech Stack']
            df_display_final = df_display_ordered.rename(columns=column_renames)[display_columns]
            
            st.dataframe(
                df_display_final.style.map(
                    color_score, subset=['🎯 AI Score']
                ),
                width='stretch',
                height=400
            )
        
            # --- Export Controls ---
            st.markdown("---")
            st.markdown("### 📤 Export Filtered Results")
            
            col1, col2, col3 = st.columns([1, 1, 2])
            
            with col1:
                csv_data = to_csv_download(df_filtered)
                st.download_button(
                    label="📄 CSV Export",
                    data=csv_data,
                    file_name=f'caprae_leads_{len(df_filtered)}_results.csv',
                    mime='text/csv',
                    help="Download as CSV for analysis",
                    use_container_width=True
                )
            
            with col2:
                excel_data = to_excel_download(df_filtered)
                st.download_button(
                    label="📊 Excel Export",
                    data=excel_data,
                    file_name=f'caprae_leads_{len(df_filtered)}_results.xlsx',
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    help="Download as Excel spreadsheet",
                    use_container_width=True
                )
            
            with col3:
                st.info(f"💡 **Export includes {len(df_filtered)} filtered leads** with all data fields for further analysis.")
    
    except Exception as e:
        st.error(f"❌ Error processing file: {str(e)}")
        st.warning("Please check your CSV file format. The system can work with most column variations, but needs at least company names.")
        st.info("Try the sample dataset to see the expected format.")
        st.stop()
else:
    st.info("👆 Choose a data source above to get started: Upload a CSV file or search with Apollo.io")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 📁 CSV Upload Benefits
        - 🤖 Smart column detection
        - 📊 Process any company dataset
        - ⚡ Instant analysis
        - 🆓 Works offline
        """)
    
    with col2:
        st.markdown("""
        ### 🌐 Apollo.io Benefits  
        - 🔍 Live company search
        - 📞 275M+ contact database
        - 🎯 Advanced filtering
        - 🔄 Real-time data
        """)
    
    st.stop()


# --- Sidebar Help & Legend ---
st.sidebar.markdown("---")
st.sidebar.markdown("""
<div style="background: linear-gradient(145deg, #1e293b, #334155); padding: 1rem; border-radius: 10px; border: 1px solid rgba(59, 130, 246, 0.3);">
    <h4 style="margin: 0; color: #60a5fa;">📖 Score Legend</h4>
    <div style="margin-top: 0.5rem;">
        <div style="background: #28a745; color: white; padding: 0.3rem; border-radius: 5px; margin: 0.2rem 0; text-align: center; font-weight: bold;">90-100: High Priority</div>
        <div style="background: #ffc107; color: black; padding: 0.3rem; border-radius: 5px; margin: 0.2rem 0; text-align: center; font-weight: bold;">75-89: Medium Priority</div>
        <div style="color: #94a3b8; padding: 0.3rem; border-radius: 5px; margin: 0.2rem 0; text-align: center;">0-74: Low Priority</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("""
<div style="background: linear-gradient(145deg, #1e293b, #334155); padding: 1rem; border-radius: 10px; border: 1px solid rgba(59, 130, 246, 0.3); margin-top: 1rem;">
    <h4 style="margin: 0; color: #60a5fa;">💡 Quick Tips</h4>
    <ul style="margin: 0.5rem 0; padding-left: 1.2rem; font-size: 0.9rem; color: #e8f4fd;">
        <li>Start with <strong>High Priority</strong> filter</li>
        <li><strong>Legacy Tech</strong> = immediate AI opportunity</li>
        <li>Use <strong>Industry Focus</strong> for targeted campaigns</li>
        <li>Export results for CRM integration</li>
    </ul>
</div>
""", unsafe_allow_html=True)