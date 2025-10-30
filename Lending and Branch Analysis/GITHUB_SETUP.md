# GitHub Migration Guide

## Should You Move to GitHub?

**Yes, but MEASURE carefully:**

### ✅ Benefits of GitHub:
- **Version control**: Track changes, roll back mistakes
- **Collaboration**: Share code with team members
- **Backup**: Cloud backup of your code
- **Documentation**: README files, issues, discussions
- **Best practices**: Standard for software development
- **Automation**: Can use GitHub Actions for workflows

### ⚠️ Important Security Considerations:

1. **Service Account Keys** (`*.json` files) - **NEVER commit these!**
   - Your `hdma1-242116-74024e2eb88f.json` contains private keys
   - If committed, anyone with access could use your BigQuery credentials
   - **Already added to .gitignore**

2. **CSV Data Files** - **Be selective:**
   - Public crosswalks (like CBSA to County) = OK to commit
   - Analysis results with sensitive data = Should NOT commit
   - Large files (>100MB) = Use Git LFS or exclude

3. **Excel Output Files** - **Usually exclude:**
   - May contain sensitive analysis results
   - Large file sizes
   - Better stored elsewhere (SharePoint, OneDrive)

## Recommended Approach: Hybrid Strategy

### Option 1: Code on GitHub, Data on SharePoint (RECOMMENDED)
```
GitHub Repository (Public or Private):
  ├── Lending and Branch Analysis/
  │   ├── utils/
  │   ├── queries/
  │   ├── examples/
  │   └── README.md
  ├── *.py (your analysis scripts)
  └── .gitignore (excludes credentials and data)

SharePoint/OneDrive:
  ├── Service account JSON files
  ├── CSV data exports
  ├── Excel analysis outputs
  └── Large data files
```

**Benefits:**
- Code is version-controlled and shareable
- Sensitive data stays on SharePoint (org-controlled)
- Best of both worlds

### Option 2: Private GitHub Repository
- Everything on GitHub but repository is private
- Still use .gitignore for credentials
- Good for internal team collaboration
- Still need to be careful about data files

## Setup Steps

### 1. Review .gitignore
The `.gitignore` file I created excludes:
- All `.json` files (credentials)
- Large CSV exports
- Excel outputs
- Python cache files

**Customize it** based on what you want to include/exclude.

### 2. Decide What to Commit

**Safe to commit:**
- ✅ Python code (`*.py`)
- ✅ Query templates
- ✅ README and documentation
- ✅ Public reference data (if small): CBSA to County crosswalk
- ✅ Utility scripts

**Should NOT commit:**
- ❌ Service account JSON files
- ❌ Analysis results (CSV, Excel)
- ❌ Large data exports
- ❌ Sensitive crosswalk files

### 3. Create GitHub Repository

```bash
# Navigate to project directory
cd "C:\Users\edite\OneDrive - Nat'l Community Reinvestment Coaltn\Desktop\DREAM Analysis"

# Initialize git (if not already)
git init

# Add files (respecting .gitignore)
git add .

# Review what will be committed
git status

# Create initial commit
git commit -m "Initial commit: Lending and Branch Analysis utilities"

# Create repository on GitHub, then:
git remote add origin https://github.com/your-org/your-repo.git
git branch -M main
git push -u origin main
```

### 4. Handle Credentials Securely

**Option A: Environment Variables**
```python
# Instead of hardcoding key path:
import os
key_path = os.getenv('BIGQUERY_KEY_PATH', 'default/path.json')
```

**Option B: Configuration File (not in git)**
```python
# config.local.json (in .gitignore)
# Loaded by code but not committed
```

**Option C: Keep on SharePoint**
- Store credentials file on SharePoint
- Update code to point to SharePoint location
- Document location in README (without sensitive details)

### 5. Document Setup for Team Members

Add to README:
```markdown
## Setup Instructions

1. Clone repository
2. Get service account key from [SharePoint location]
3. Place key file at: `../hdma1-242116-74024e2eb88f.json`
4. Install dependencies: `pip install -r requirements.txt`
```

## Checklist Before First Push

- [ ] Review `.gitignore` - ensure credentials are excluded
- [ ] Run `git status` - verify no `.json` files are staged
- [ ] Check CSV files - decide which to exclude
- [ ] Remove any hardcoded credentials from code
- [ ] Create `requirements.txt` if you have dependencies
- [ ] Update README with setup instructions
- [ ] Test that code works without committed credentials

## My Recommendation

**Move to GitHub, but use a hybrid approach:**

1. ✅ Put code on GitHub (utilities, queries, scripts)
2. ✅ Keep credentials on SharePoint
3. ✅ Keep large data files on SharePoint
4. ✅ Maybe commit small, public reference data (like CBSA crosswalk)

This gives you version control for code while keeping sensitive data secure on SharePoint where your organization controls access.

## Need Help?

I can help you:
- Customize `.gitignore` for your needs
- Create a `requirements.txt` for dependencies
- Set up environment variable handling
- Review what files to commit
- Create setup documentation

Just ask!

