"""
Configuration and Taxonomy Rules for Resume Scraper
"""

import os
import re

# Directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DUMP_DIR = os.path.join(BASE_DIR, "dump_resumes_here")
# Also support input_resumes for backward compatibility
FALLBACK_INPUT_DIR = os.path.join(BASE_DIR, "input_resumes")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

# Category Taxonomy and Matching Keywords
CATEGORIES = {
    "Software_Engineering": [
        "software engineer", "developer", "backend", "frontend", "full stack", "fullstack",
        "java", "python", "c++", "c#", ".net", "react", "angular", "node.js", "nodejs",
        "javascript", "typescript", "golang", "ruby", "php", "django", "flask", "spring boot",
        "microservices", "rest api", "graphql", "devops", "docker", "kubernetes", "aws", "azure",
        "ci/cd", "git", "linux", "system architecture", "sql", "postgresql", "mongodb"
    ],
    "Data_Science_and_AI": [
        "data scientist", "machine learning", "deep learning", "nlp", "computer vision",
        "artificial intelligence", "data analyst", "data engineer", "pandas", "numpy",
        "scikit-learn", "tensorflow", "pytorch", "keras", "tableau", "power bi", "powerbi",
        "big data", "spark", "hadoop", "databricks", "llm", "genai", "prompt engineering",
        "business intelligence", "statistical analysis", "etl", "snowflake"
    ],
    "Finance_and_Accounting": [
        "finance", "accounting", "accountant", "chartered accountant", "financial analyst",
        "auditing", "taxation", "gst", "balance sheet", "p&l", "general ledger", "accounts payable",
        "accounts receivable", "reconciliation", "financial modeling", "investment banking",
        "wealth management", "portfolio management", "risk management", "quickbooks", "tally",
        "sap fico", "cpa", "cfa", "ifrs", "budgeting", "forecasting"
    ],
    "Sales_and_Marketing": [
        "sales", "business development", "lead generation", "b2b", "b2c", "account executive",
        "digital marketing", "seo", "sem", "social media marketing", "content marketing",
        "email marketing", "google ads", "brand management", "crm", "salesforce", "hubspot",
        "market research", "campaign management", "client acquisition", "closing deals",
        "revenue growth", "pipeline management", "public relations"
    ],
    "Human_Resources": [
        "human resources", "hr", "talent acquisition", "recruiter", "recruitment", "headhunting",
        "onboarding", "employee engagement", "payroll", "performance management", "hr policies",
        "labor laws", "statutory compliance", "screening", "interviewing", "sourcing",
        "workday", "bamboohr", "people operations", "hiring", "compensation and benefits"
    ],
    "Operations_and_Management": [
        "operations manager", "project manager", "program manager", "scrum master", "agile",
        "supply chain", "logistics", "procurement", "vendor management", "inventory control",
        "quality assurance", "six sigma", "lean", "process improvement", "pmp", "jira",
        "confluence", "operations excellence", "cross-functional leadership", "workflow optimization"
    ],
    "Education_and_Teaching": [
        "teacher", "teaching", "educator", "classroom", "curriculum", "instruction", "lesson plan",
        "lesson plans", "student", "pedagogy", "kindergarten", "preschool", "school", "faculty",
        "tutoring", "academic", "special education", "elementary", "substitute teacher", "reading teacher",
        "differentiated instruction", "iep", "common core", "ngss", "school district"
    ],
    "Design_and_Creative": [
        "ui/ux", "graphic designer", "product designer", "visual designer", "interaction design",
        "figma", "adobe xd", "photoshop", "illustrator", "wireframing", "prototyping",
        "user research", "design systems", "motion graphics", "typography", "indesign"
    ],
    "Legal_and_Compliance": [
        "legal", "lawyer", "advocate", "compliance", "contracts", "regulatory", "litigation",
        "intellectual property", "due diligence", "corporate law", "arbitration", "company secretary"
    ]
}

DEFAULT_CATEGORY = "General_and_Others"

# Common Technical & Professional Skills
SKILLS_LIST = [
    # Teaching & Education
    "Curriculum Development", "Lesson Planning", "Classroom Management", "Differentiated Instruction",
    "Special Education", "Common Core", "IEP", "STEM", "Educational Technology", "Student Assessment",
    "Instructional Design", "Literacy", "ESL", "Tutoring",
    # Programming & Tech
    "Python", "Java", "C++", "C#", "C", "JavaScript", "TypeScript", "PHP", "Ruby", "Swift", "Kotlin", "Go", "Rust", "R",
    "SQL", "MySQL", "PostgreSQL", "MongoDB", "Redis", "SQLite", "Oracle", "Cassandra", "DynamoDB",
    "HTML", "HTML5", "CSS", "CSS3", "Sass", "Bootstrap", "Tailwind CSS",
    "React", "React.js", "Angular", "Vue.js", "Node.js", "Express.js", "Next.js", "Django", "Flask", "FastAPI", "Spring", "Spring Boot", ".NET", "ASP.NET",
    "AWS", "Amazon Web Services", "Azure", "GCP", "Google Cloud", "Docker", "Kubernetes", "Terraform", "Ansible", "Jenkins", "Git", "GitHub", "GitLab", "CI/CD",
    "REST API", "GraphQL", "Microservices", "Kafka", "RabbitMQ", "Celery",
    # Data & AI
    "Machine Learning", "Deep Learning", "Data Analysis", "Data Science", "Artificial Intelligence", "NLP", "Computer Vision",
    "Pandas", "NumPy", "Scikit-Learn", "TensorFlow", "PyTorch", "Keras", "OpenCV", "Tableau", "Power BI", "Spark", "Hadoop", "Snowflake", "Databricks",
    # Business & Management
    "Project Management", "Agile", "Scrum", "Jira", "Confluence", "PMP", "Six Sigma", "Lean", "SDLC", "Product Management",
    "Business Analysis", "Requirements Gathering", "Stakeholder Management", "Vendor Management",
    # Finance & Accounting
    "Financial Analysis", "Financial Modeling", "Accounting", "Auditing", "Taxation", "GST", "Tally", "QuickBooks", "SAP", "SAP FICO", "Payroll", "Budgeting", "Forecasting",
    # Marketing & Sales
    "Digital Marketing", "SEO", "SEM", "Google Analytics", "Google Ads", "Content Marketing", "Email Marketing", "Social Media Marketing", "CRM", "Salesforce", "HubSpot", "B2B Sales", "Lead Generation",
    # HR & Operations
    "Talent Acquisition", "Recruitment", "HR Policies", "Employee Relations", "Onboarding", "Screening", "Operations Management", "Supply Chain", "Logistics", "Procurement",
    # Design
    "Figma", "Adobe XD", "Photoshop", "Illustrator", "InDesign", "UI/UX Design", "Wireframing", "Prototyping"
]

# Standard Degree Patterns (Require exact word boundaries or periods to prevent matching english words like 'be', 'me')
DEGREES = [
    r"\bPh\.?D\.?\b", r"\bDoctorate\b",
    r"\bM\.?Tech\.?\b", r"\bM\.E\.\b", r"\bMaster of Science\b", r"\bMaster of Technology\b", r"\bMaster of Engineering\b",
    r"\bB\.?Tech\.?\b", r"\bB\.E\.\b", r"\bBachelor of Technology\b", r"\bBachelor of Engineering\b", r"\bBachelor of Science\b",
    r"\bB\.?Ed\.?\b", r"\bM\.?Ed\.?\b", r"\bBachelor of Education\b", r"\bMaster of Education\b", r"\bTeaching Certification\b",
    r"\bM\.?B\.?A\.?\b", r"\bMaster of Business Administration\b", r"\bPGDM\b",
    r"\bB\.?B\.?A\.?\b", r"\bBachelor of Business Administration\b",
    r"\bM\.?C\.?A\.?\b", r"\bMaster of Computer Applications\b",
    r"\bB\.?C\.?A\.?\b", r"\bBachelor of Computer Applications\b",
    r"\bB\.?Sc\.?\b", r"\bM\.?Sc\.?\b",
    r"\bB\.?Com\.?\b", r"\bM\.?Com\.?\b", r"\bBachelor of Commerce\b", r"\bMaster of Commerce\b",
    r"\bChartered Accountant\b", r"\bCFA\b", r"\bCPA\b",
    r"\bBachelor of Arts\b", r"\bMaster of Arts\b",
    r"\bLL\.?B\.?\b", r"\bLL\.?M\.?\b", r"\bBachelor of Laws\b",
    r"\bDiploma\b", r"\bHigh School Diploma\b"
]

# Common Designation Keywords
DESIGNATION_KEYWORDS = [
    "Software Engineer", "Senior Software Engineer", "Software Developer", "Backend Developer", "Frontend Developer",
    "Full Stack Developer", "Data Scientist", "Data Analyst", "Data Engineer", "Machine Learning Engineer",
    "DevOps Engineer", "Cloud Engineer", "System Administrator", "Database Administrator", "QA Engineer", "Automation Tester",
    "Product Manager", "Project Manager", "Technical Project Manager", "Scrum Master", "Business Analyst",
    "Sales Executive", "Business Development Manager", "Sales Manager", "Account Executive",
    "Digital Marketing Specialist", "Marketing Executive", "Content Writer", "SEO Specialist",
    "HR Executive", "HR Manager", "Talent Acquisition Specialist", "Technical Recruiter",
    "Financial Analyst", "Accountant", "Senior Accountant", "Finance Manager", "Audit Associate",
    "Operations Manager", "Operations Executive", "Supply Chain Analyst",
    "Biology Teacher", "Substitute Teacher", "Master Teacher", "Lead Teacher", "Guest Teacher",
    "Classroom Teacher", "Assistant Teacher", "Associate Teacher", "Kindergarten Teacher",
    "Art Teacher", "Special Education Teacher", "Inclusion Teacher", "Preschool Teacher",
    "Teacher", "Educator", "Professor", "Lecturer", "Principal", "Academic Coordinator",
    "UI/UX Designer", "Graphic Designer", "Product Designer",
    "Consultant", "Senior Consultant", "Associate", "Team Lead", "Director", "Vice President", "Intern"
]

# Common Indian & Global Phone Regex Patterns
PHONE_PATTERNS = [
    re.compile(r'(?:(?:\+|00)\d{1,3}[\s-]?)?(?:\(?\d{2,5}\)?[\s-]?)?\d{3,5}[\s-]?\d{3,5}'),
]

# Email Regex
EMAIL_PATTERN = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')

# Locations / Cities (Priority to Indian Tech & Business Hubs + Global Hubs)
LOCATIONS = [
    # Indian Metros & Tier 1
    "Bangalore", "Bengaluru", "Mumbai", "Delhi NCR", "Delhi", "New Delhi", "Gurgaon", "Gurugram", "Noida",
    "Hyderabad", "Pune", "Chennai", "Kolkata", "Ahmedabad", "Jaipur", "Kochi", "Chandigarh", "Indore",
    "Coimbatore", "Surat", "Bhubaneswar", "Nagpur", "Thiruvananthapuram", "Trivandrum", "Vadodara",
    # Work Modes
    "Remote", "Hybrid",
    # Global Hubs
    "Singapore", "Dubai", "London", "New York", "San Francisco", "Seattle", "Toronto", "Sydney", "Berlin"
]

# Recruiter Workflow Statuses for ATS Dropdown
ATS_STATUSES = [
    "New",
    "Shortlisted",
    "Interview Scheduled",
    "Offer Extended",
    "Rejected",
    "On Hold"
]

# Recognizable Tech & Corporate Companies
KNOWN_COMPANIES = [
    "Google", "Microsoft", "Amazon", "Apple", "Meta", "Facebook", "Netflix", "Uber", "Salesforce",
    "TCS", "Tata Consultancy Services", "Infosys", "Wipro", "HCL Technologies", "HCL", "Tech Mahindra",
    "Cognizant", "Accenture", "Capgemini", "IBM", "Oracle", "Cisco", "Intel", "SAP",
    "Deloitte", "KPMG", "PwC", "PricewaterhouseCoopers", "EY", "Ernst & Young", "McKinsey", "BCG", "Bain",
    "Goldman Sachs", "Morgan Stanley", "J.P. Morgan", "JPMorgan Chase", "Citigroup", "HSBC", "Barclays",
    "Flipkart", "Swiggy", "Zomato", "Paytm", "PhonePe", "Razorpay", "Ola", "CRED", "Meesho", "Zerodha"
]
