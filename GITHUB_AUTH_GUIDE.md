# GitHub Authentication Guide

## Finding Your GitHub Username

1. **Log into GitHub**: Go to https://github.com and sign in
2. **Check your profile**: Click your profile picture (top right) → Your profile
3. **Your username** is in the URL: `https://github.com/YOUR_USERNAME`
   - Or look at the top of your profile page

**Note**: If your organization has a GitHub organization account, you might use:
- Your personal GitHub account
- Your organization's account name
- Or both (personal account with org access)

## Authentication Options

GitHub **does NOT use passwords** for git operations anymore. You need one of these:

### Option 1: Personal Access Token (Recommended for command line)

1. **Generate a token**:
   - Go to: https://github.com/settings/tokens
   - Click "Generate new token" → "Generate new token (classic)"
   - Name it: "DREAM Analysis Project"
   - Select scopes: ✅ `repo` (Full control of private repositories)
   - Click "Generate token"
   - **COPY THE TOKEN** (you won't see it again!)

2. **Use the token**:
   - When you run `git push`, it will ask for:
     - Username: Your GitHub username
     - Password: **Paste your Personal Access Token** (not your password)

### Option 2: GitHub Desktop (Easiest for Windows)

1. **Download**: https://desktop.github.com/
2. **Install and open GitHub Desktop**
3. **Sign in** with your GitHub account (uses browser login)
4. **Add your repository**:
   - File → Add Local Repository
   - Select: `C:\Users\edite\OneDrive - Nat'l Community Reinvestment Coaltn\Desktop\DREAM Analysis`
5. **Publish to GitHub**:
   - Click "Publish repository" button
   - Choose repository name and privacy
   - Click "Publish repository"

No command line needed! GitHub Desktop handles authentication.

### Option 3: GitHub CLI (`gh`)

1. **Install**: https://cli.github.com/
2. **Authenticate**:
   ```bash
   gh auth login
   ```
   - Follow prompts (it will open browser for authentication)
3. **Push**:
   ```bash
   git push -u origin main
   ```

## Which Method Should You Use?

- **GitHub Desktop**: If you're not comfortable with command line → Easiest!
- **Personal Access Token**: If you want to use command line → Quick setup
- **GitHub CLI**: If you want command line with easy auth → Most modern

## Common Issues

**"Authentication failed"**:
- Make sure you're using a Personal Access Token, not your password
- Check that token has `repo` permissions

**"Repository not found"**:
- Verify repository name is correct
- Check that you created the repository on GitHub first
- Make sure you have access to the repository

## Still Not Sure?

1. Check with your IT/tech team - they might have org GitHub setup
2. Ask if your organization has a shared GitHub account
3. Create a personal GitHub account if you don't have one (free)

