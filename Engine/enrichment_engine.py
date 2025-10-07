import pandas as pd
import numpy as np
import os

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Input file is in the same directory as the script (Mock Dataset folder)
FILE_NAME = os.path.join(SCRIPT_DIR, 'Mock Dataset Lead Generation Tool.csv')
# Output file goes to the parent directory (Lead generator folder)
OUTPUT_FILE = os.path.join(os.path.dirname(SCRIPT_DIR), 'enriched_leads_final.csv')

# --- 2. Core Scoring Logic ---
def calculate_ai_score(df):
    """
    Calculates the simulated M&A AI Acquisition Score based on Caprae's focus.
    (Proprietary Business Logic)
    """
    df['AI_Acquisition_Score'] = 50  # Starting neutral base score

    # Rule 1: Age Penalty/Bonus (Older = more likely to need modernization)
    df.loc[df['Years in Business'] >= 20, 'AI_Acquisition_Score'] += 20
    df.loc[(df['Years in Business'] >= 10) & (df['Years in Business'] < 20), 'AI_Acquisition_Score'] += 10
    df.loc[df['Years in Business'] < 5, 'AI_Acquisition_Score'] -= 10

    # Rule 2: Revenue Sweet Spot (Caprae's target range: $3M - $10M)
    # Robust cleaning of currency symbols, commas, and quotes before conversion
    df['Annual Revenue (USD)'] = df['Annual Revenue (USD)'].astype(str).str.replace(r'[$,"]', '', regex=True)
    # Convert to numeric, handling any remaining non-numeric values
    df['Annual Revenue (USD)'] = pd.to_numeric(df['Annual Revenue (USD)'], errors='coerce')
    
    df.loc[(df['Annual Revenue (USD)'] >= 3000000) & 
           (df['Annual Revenue (USD)'] <= 10000000), 'AI_Acquisition_Score'] += 15
    df.loc[(df['Annual Revenue (USD)'] > 10000000) | 
           (df['Annual Revenue (USD)'] < 3000000), 'AI_Acquisition_Score'] -= 5

    # Rule 3: Industry Focus (Traditional industries are prime for AI transformation)
    # Expanded list of traditional industries found in the 25-entry dataset
    df.loc[df['Industry'].isin(['Manufacturing', 'Retail', 'Consulting', 'Agency', 'Traditional Consulting', 'Logistics', 'Accounting', 'Insurance', 'Environmental']), 'AI_Acquisition_Score'] += 10

    return df

# --- 3. Technical Enrichment (Legacy Tech Flag Simulation) ---
def add_tech_flag(df):
    """
    Simulates detection of legacy tech stack, indicating a high-value
    AI-Readiness opportunity. (Technical Sophistication)
    """
    
    # Expanded Mock Tech Data for all 25 entries (using only the Company Name as key)
    tech_data = {
        'OldSchool Mfg. Co.': 'Legacy (ColdFusion, On-Premise DB)',
        'Coastal Retail Group': 'Legacy (Old E-Comm Platform)',
        'Central Distribution LLC': 'Legacy (AS400 ERP, Desktop App)',
        'Harbor Consulting Inc.': 'Legacy (SharePoint 2010, Local Servers)',
        'Midwest Machining Corp': 'Legacy (Proprietary CAD/CAM, Old OS)',
        'Alpha Digital Inc.': 'Modern (React, Python)',
        'Prime HR Solutions': 'Modern (Cloud-native SaaS)',
        'Secure Vault Storage': 'Hybrid (Custom PHP, Modern DB)',
        'Global Transport Co.': 'Legacy (Custom Cobol Backend)',
        'Elite Finance Group': 'Modern (AWS Serverless)',
        'TechForward Corp': 'Modern (Next.js, Go)',
        'Beta Solutions LLC': 'Modern (PHP, Cloud)',
        'Apex AI Systems': 'Modern (Python, TensorFlow)',
        'Future Health SaaS': 'Modern (Azure, Microservices)',
        'Green Energy Installers': 'Hybrid (Off-the-shelf CRM)',
        'Regional Accounting PLC': 'Legacy (Quickbooks Desktop, Windows Server)',
        'Metro Web Design': 'Modern (WordPress, Cloudflare)',
        'North Star Logistics': 'Legacy (Custom FoxPro System)',
        'South Side Retailer': 'Legacy (Magento 1.x)',
        'Data Analytics Hub': 'Modern (Python, Tableau)',
        'Zenith Labs Corp': 'Modern (R Studio, Jupyter)',
        'Coastline Agencies': 'Legacy (Access DB, Custom Forms)',
        'Pioneer Tools Ltd': 'Legacy (DOS-based Inventory)',
        'River Valley Services': 'Hybrid (Salesforce, Custom Legacy Billing)',
        'Blue Sky Software': 'Modern (Ruby on Rails)',
    }

    # Ensure 'Company Name' is the column used for mapping
    df['simulated_tech_stack'] = df['Company Name'].map(tech_data)

    # Flag targets with 'Legacy' or 'Old' keywords
    df['Legacy_Tech_Flag'] = df['simulated_tech_stack'].apply(
        # Check if the value is a string before checking for keywords
        lambda x: True if isinstance(x, str) and ('Legacy' in x or 'Old' in x or 'Cobol' in x or 'AS400' in x or 'DOS' in x or 'FoxPro' in x or 'Access DB' in x) else False
    )

    # Final Adjustment: Prioritize leads with Legacy Tech
    df.loc[df['Legacy_Tech_Flag'] == True, 'AI_Acquisition_Score'] += 15

    # --- Final Cleanup ---
    df['AI_Acquisition_Score'] = np.clip(df['AI_Acquisition_Score'], 0, 100).round().astype(int)

    return df

if __name__ == '__main__':
    
    try:
        # 1. Load the data
        if not os.path.exists(FILE_NAME):
            raise FileNotFoundError(f"Data file not found: {FILE_NAME}")
            
        df = pd.read_csv(FILE_NAME)
        
        # 1b. Clean the data: Remove header rows and filter valid business data
        # Remove rows where 'Years in Business' is NaN or contains descriptive text
        df_cleaned = df.dropna(subset=['Years in Business']).copy()
        
        # Additional filtering: Remove rows where 'Years in Business' is not numeric
        df_cleaned = df_cleaned[pd.to_numeric(df_cleaned['Years in Business'], errors='coerce').notna()].copy()
        
        # Convert 'Years in Business' to numeric
        df_cleaned['Years in Business'] = pd.to_numeric(df_cleaned['Years in Business'], errors='coerce')
        
        print(f"Loaded {len(df_cleaned)} valid company records for processing.")
        
        # 2. Enrichment Pipeline
        df_scored = calculate_ai_score(df_cleaned) 
        df_enriched = add_tech_flag(df_scored)

        # 3. Save Final Artifact for Phase 3
        df_enriched.to_csv(OUTPUT_FILE, index=False)

        # 4. Console Review
        print(f"Final enriched data has been saved to '{OUTPUT_FILE}'.")
        print(f"Total companies processed: {len(df_enriched)}")
        
        # Display top 5 leads by score to showcase the prioritization
        print("\nTOP ACTIONABLE LEADS (Highest AI_Acquisition_Score):\n")
        top_leads = df_enriched.sort_values(by='AI_Acquisition_Score', ascending=False).head(5)
        display_columns = ['Company Name', 'Industry', 'Years in Business', 'Legacy_Tech_Flag', 'AI_Acquisition_Score']
        print(top_leads[display_columns].to_string(index=False))
        
        # Summary statistics
        print(f"\nSUMMARY STATISTICS:")
        print(f"Average AI Score: {df_enriched['AI_Acquisition_Score'].mean():.1f}")
        print(f"Companies with Legacy Tech: {df_enriched['Legacy_Tech_Flag'].sum()}")
        print(f"High Priority Leads (Score >= 70): {len(df_enriched[df_enriched['AI_Acquisition_Score'] >= 70])}")

    except FileNotFoundError as e:
        print(f"File error: {e}")
        print("Please ensure the CSV file is in the same directory as this script.")
    except pd.errors.EmptyDataError:
        print("Error: The CSV file is empty or corrupted.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        print(f"Error type: {type(e).__name__}")