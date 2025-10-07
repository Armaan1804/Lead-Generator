The Caprae AI-Readiness Lead Generator is a sophisticated system for identifying and prioritizing high-value M&A targets by scoring their **AI-readiness** and detecting **legacy technology**.

## Key Features

* **AI Acquisition Scoring**: A proprietary algorithm scores companies (0-100) based on M\&A fit criteria.
* **Legacy Tech Detection**: Identifies companies with outdated technology stacks prime for AI transformation.
* **Interactive Dashboard**: An enhanced Streamlitpowered web interface offers intuitive filtering and export.
* **Smart Prioritization**: A colorcoded scoring system uses visual metrics cards to highlight top acquisition targets.
* **Advanced Filtering**: Filters are available for priority level, technology status, and industryspecific focus.
* **Export Functionality**: Filtered results can be downloaded in CSV or Excel format with dynamic file naming.
* **Realtime Analytics**: Live metrics display total leads, average scores, and priority distributions.

---

## Installation and Usage

### Installation
To set up the project, you need to:

1.  Clone or download the project.
2.  Install required dependencies using the following command:
    `pip install pandas numpy streamlit xlsxwriter`

### Quick Start Commands
Assuming you are in the project's parent directory:

**Step 1: Navigate to project directory**
`cd "c:\Users\Armaa\OneDrive\Desktop\Lead generator"`

**Step 2: Generate enriched data**
`cd Engine`
`python enrichment_engine.py`
`cd ..`

**Step 3: Launch dashboard**
`streamlit run app.py`

### Access the Dashboard
The dashboard automatically opens in your default web browser at the **Local URL**: `http://localhost:8501`.

---

## Scoring Algorithm Details

The **AI Acquisition Score** (0100) is calculated based on several criteria:

* **Company Age**: Older companies (20+ years) receive bonus points for high modernization potential.
* **Revenue Range**: The sweet spot of **$3M$10M** receives the highest scores.
* **Industry Focus**: Traditional industries such as **Manufacturing, Retail, and Consulting** are prioritized.
* **Legacy Technology**: Companies with outdated tech stacks receive significant bonus points.

### Score Ranges and Priority
The system assigns a priority level based on the score:

* 🟢 **90100**: **High Priority** (Immediate Action)
* 🟡 **7589**: **Medium Priority** (Strong Candidates)
* ⚪ **074**: **Low Priority** (Monitor)

---

## Enhanced Dashboard Features

### Realtime Metrics
The dashboard displays:

* **Total Leads**: Complete database count.
* **Average AI Score**: Overall acquisition potential.
* **Legacy Tech Count**: Highintent modernization targets.
* **High Priority Leads**: Immediate action candidates (90+ score).

### Advanced Filtering
Key filtering options include:

* **Priority Level Filter**: High Priority (90100), Medium Priority (7589), or Custom Range.
* **Technology Status**: All Companies, **Legacy Tech Only** (High Intent), or Modern Tech Only.
* **Industry Focus**: Filter by specific industry sectors.

The dashboard uses **Smart Defaults** to automatically focus on highintent leads.

### Data Display and Export
The data display is enhanced with **Colorcoded Scores** (Green/Yellow/Gray), formatted columns with emoji icons, and sortable results.

For export, users have **CSV Export** (lightweight) and **Excel Export** (formatted spreadsheet), with the files including a summary of what was downloaded and dynamic naming for organization.

---

## Customization and Technical Details

### Customization Points
The project is designed for customization:

* **Adding New Scoring Rules**: Modify the `calculate_ai_score()` function in `Engine/enrichment_engine.py`.
* **Modifying Tech Detection**: Update the `tech_data` dictionary in the `add_tech_flag()` function.
* **Dashboard Styling**: Change color schemes, gradient headers, and metric card styles in `app.py`.

### Technical Details
The core dependencies are **pandas** (data manipulation), **numpy** (numerical computations), **streamlit** (web dashboard), and **xlsxwriter** (Excel file generation). The key files are `enrichment_engine.py` (core logic) and `app.py` (Streamlit dashboard).

The system currently uses **simulated tech stack data** and a scoring algorithm designed specifically for Caprae's M\&A criteria.
