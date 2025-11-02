# Meme Images for Social Media

This directory contains work-appropriate meme images generated for social media posts.

## Usage

Memes are generated using the script: `Member Reports/scripts/generate_memes.py`

## Stable URLs

All meme images in this directory have stable GitHub URLs that can be used in Buffer CSV files:

```
https://raw.githubusercontent.com/[YOUR_REPO]/[BRANCH]/memes/[filename].png
```

## Generating Memes

### For a single meme:
```bash
python Member Reports/scripts/generate_memes.py --template this_is_fine --text "Text line 1" "Text line 2"
```

### For all posts:
```bash
python Member Reports/scripts/generate_memes.py --posts Member Reports/data/buffer_posts_all.json
```

## Committing to GitHub

After generating memes, commit and push them:

**Windows:**
```bash
scripts\commit_memes.bat
```

**Linux/Mac:**
```bash
bash scripts/commit_memes.sh
```

Or manually:
```bash
git add memes/
git commit -m "Add meme images for social media posts"
git push
```

## Meme Templates Available

- `this_is_fine` - House on fire, dog drinking coffee (exasperated)
- `side_eye` - Child looking over shoulder skeptically (suspicious)
- `distracted_boyfriend` - Person distracted by something else
- `drake_pointing` - Pointing at preferred option
- `change_my_mind` - Person at table with sign
- `expanding_brain` - Brain getting bigger with each idea

Run `python Member Reports/scripts/generate_memes.py --list-templates` for full details.

