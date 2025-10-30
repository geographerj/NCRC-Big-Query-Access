# GitHub Setup Commands

After creating your GitHub repository, run these commands:

## Replace these values:
- `YOUR_USERNAME` = Your GitHub username or organization name
- `REPO_NAME` = The repository name you created

## Commands to run:

```bash
# Add GitHub as remote repository
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git

# Rename branch to 'main' (GitHub's default)
git branch -M main

# Push your code to GitHub
git push -u origin main
```

## If you get authentication errors:

GitHub requires authentication. You can:

1. **Use GitHub Desktop** (easiest for Windows)
   - Download from: https://desktop.github.com/
   - Connect to GitHub account
   - Add repository, then push

2. **Use Personal Access Token** (command line)
   - Go to: GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
   - Generate new token with "repo" permissions
   - Use token as password when pushing

3. **Use GitHub CLI** (gh)
   ```bash
   gh auth login
   git push -u origin main
   ```

## Verify it worked:

Go to: `https://github.com/YOUR_USERNAME/REPO_NAME`

You should see all your files!

