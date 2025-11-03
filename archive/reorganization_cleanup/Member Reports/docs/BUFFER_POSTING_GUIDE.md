# Buffer Posting Guide

Since Buffer doesn't have a public API, this guide shows how to schedule posts using Buffer's bulk CSV upload feature.

**Official Buffer Documentation**: https://support.buffer.com/article/926-how-to-upload-posts-in-bulk-to-buffer

## Quick Start

### Option 1: From JSON File

1. **Create a posts file** (see `data/posts_template.json` for format):

```json
[
    {
        "text": "Your first post content here",
        "image_url": "",
        "tags": "housing,lending",
        "posting_time": "2025-01-15 10:00"
    },
    {
        "text": "Your second post with an image",
        "image_url": "https://drive.google.com/uc?export=view&id=1AbCdEfGhIjKlMn",
        "tags": "report"
    }
]
```

2. **Generate the CSV**:

```bash
python scripts/schedule_buffer_posts.py --input data/posts.json --output buffer_posts.csv
```

3. **Upload to Buffer**:
   - Log in to Buffer.com
   - Go to the **Publish** tab
   - Select the channel you want to post to (left sidebar)
   - Click the gear icon (⚙️) next to the channel name
   - Click the **General** tab
   - Click **Bulk Upload** button
   - Click **Upload File** and select your CSV
   - Review the preview and click **Add Posts to Queue** or **Save as Drafts**

### Option 2: From Command Line

```bash
python scripts/schedule_buffer_posts.py \
    --text "First post" "Second post" "Third post" \
    --output buffer_posts.csv \
    --schedule-start "2025-01-15 09:00" \
    --interval-hours 2
```

This will schedule 3 posts starting at 9:00 AM, with 2-hour intervals between them.

## Buffer CSV Format

Buffer requires these **case-sensitive** columns:

| Column | Required | Description |
|--------|----------|-------------|
| **Text** | Yes* | Post content (required if Image URL is empty) |
| **Image URL** | Yes* | Direct image URL (required if Text is empty, must end in .jpg, .png, etc.) |
| **Tags** | No | Comma-separated tags (must exist in your Buffer account) |
| **Posting Time** | No | Format: `YYYY-MM-DD HH:mm` (e.g., "2025-07-29 13:29") |
| **Board Name** | No | Only for Pinterest posts |

\* At least one of Text or Image URL must be filled.

## Post Format (JSON)

Each post in your JSON file can include:

```json
{
    "text": "Post content here",           // Required if image_url is empty
    "image_url": "https://...",            // Required if text is empty (must be direct URL)
    "tags": "tag1,tag2",                   // Optional, comma-separated
    "posting_time": "2025-07-29 13:29",    // Optional, Buffer format
    "board_name": "My Board"                // Optional, Pinterest only
}
```

### Important Notes

- **Text or Image URL required**: Each post must have at least one
- **Column names are case-sensitive**: Must match exactly (`Text`, `Image URL`, etc.)
- **Tags must exist**: Tags in your CSV must already exist in your Buffer account
- **Image URLs must be direct**: Must end in `.jpg`, `.png`, etc. and be publicly accessible
- **Posting Time format**: `YYYY-MM-DD HH:mm` (24-hour format)
- **Channel-specific**: Upload CSV files to the specific channel they're intended for

## Image URLs

Buffer requires **direct image URLs** that:
- End in a file extension (`.jpg`, `.jpeg`, `.png`, etc.)
- Are publicly accessible (anyone with link can view)
- Display the image directly when opened (not embedded in a webpage)

### Getting Direct URLs

#### Google Drive
1. Upload image to Google Drive
2. Right-click → **Get link**
3. Set access to **Anyone with the link**
4. Use format: `https://drive.google.com/uc?export=view&id=FILE_ID`

#### Dropbox
1. Upload to Dropbox
2. Right-click → **Share**
3. Confirm **Anyone with the link can view**
4. Change `dl=0` to `raw=1` in URL

#### Imgur
1. Upload to imgur.com
2. Right-click image → **Open image in new tab**
3. Copy the URL from the new tab

## Scheduling

### Single Scheduled Time

```json
{
    "text": "My post",
    "posting_time": "2025-01-15 14:30"
}
```

### Automatic Interval Scheduling (Command Line)

```bash
python scripts/schedule_buffer_posts.py \
    --text "Post 1" "Post 2" "Post 3" \
    --schedule-start "2025-01-15 09:00" \
    --interval-hours 3 \
    --output posts.csv
```

This creates:
- Post 1 at 9:00 AM
- Post 2 at 12:00 PM (3 hours later)
- Post 3 at 3:00 PM (3 hours later)

### No Scheduling

If you omit `posting_time`, posts will be added to Buffer's queue and scheduled according to your Buffer posting schedule.

## Pinterest Posts

For Pinterest, include the `board_name` field and use the `--pinterest` flag:

```json
{
    "text": "Pinterest post",
    "image_url": "https://...",
    "board_name": "Housing Reports"
}
```

```bash
python scripts/schedule_buffer_posts.py \
    --input pinterest_posts.json \
    --output pinterest_posts.csv \
    --pinterest
```

## Examples

### Example 1: Simple Text Posts

```json
[
    {"text": "Check out our new report on mortgage lending patterns."},
    {"text": "Top 10 lenders in Tampa market analysis is now available."},
    {"text": "Community Benefits Agreements are making a difference."}
]
```

### Example 2: Posts with Images and Scheduling

```json
[
    {
        "text": "Our latest report reveals key lending trends.",
        "image_url": "https://drive.google.com/uc?export=view&id=1AbCdEfGhIjKlMn",
        "tags": "housing,report",
        "posting_time": "2025-01-15 10:00"
    },
    {
        "text": "Deep dive into mortgage lending patterns.",
        "image_url": "https://example.com/chart.png",
        "tags": "analysis,market",
        "posting_time": "2025-01-15 14:00"
    }
]
```

### Example 3: Image-Only Posts

```json
[
    {
        "image_url": "https://example.com/image1.png",
        "tags": "visual,data"
    }
]
```

## Generating Posts Programmatically

You can also create posts in Python:

```python
from utils.buffer_helper import create_buffer_csv, create_posts_from_list
from datetime import datetime, timedelta

# Create posts from a list
posts = create_posts_from_list(
    post_texts=[
        "Post 1 content",
        "Post 2 content",
        "Post 3 content"
    ],
    image_urls=[
        "https://example.com/image1.png",
        None,
        "https://example.com/image3.jpg"
    ],
    tags=["housing", "lending", "analysis"],
    posting_times=[
        datetime.now() + timedelta(days=1),
        datetime.now() + timedelta(days=2),
        datetime.now() + timedelta(days=3)
    ]
)

# Generate CSV
create_buffer_csv(posts, "output/buffer_posts.csv")
```

## Uploading to Buffer

1. **Generate your CSV file** using the script
2. **Log in to Buffer.com**
3. **Navigate to Publish tab**
4. **Select the channel** you want to post to (left sidebar)
5. **Click gear icon (⚙️)** next to channel name
6. **Click General tab**
7. **Click Bulk Upload button**
8. **Click Upload File** and select your CSV
9. **Review the preview** - Buffer will show you all posts
10. **Click Add Posts to Queue** or **Save as Drafts**

## Troubleshooting

### CSV Not Accepted by Buffer

- ✅ Check that column names match exactly: `Text`, `Image URL`, `Tags`, `Posting Time` (case-sensitive!)
- ✅ Ensure dates are in correct format: `YYYY-MM-DD HH:mm` (24-hour time)
- ✅ Make sure each post has either Text or Image URL (at least one required)
- ✅ Remove any empty rows
- ✅ Save as CSV UTF-8 if using emoji

### Posts Not Scheduled Correctly

- ✅ Buffer uses your account's timezone for scheduling
- ✅ Make sure your scheduled times account for timezone differences
- ✅ If you don't specify `posting_time`, posts go to your queue based on your Buffer posting schedule

### Image URLs Not Working

- ✅ Check that URL ends in file extension (`.jpg`, `.png`, etc.)
- ✅ Verify link sharing is set to **public** or **anyone with the link**
- ✅ Test the URL by opening it in a new browser tab (should show image directly)
- ✅ Image must be under 5MB
- ✅ Use direct image URLs (Google Drive, Dropbox with raw=1, Imgur, etc.)

### Tags Not Working

- ✅ Tags must already exist in your Buffer account
- ✅ Tags are case-sensitive
- ✅ Use comma-separated format: `"tag1,tag2,tag3"`

### Errors After Upload

Buffer will show a preview with any errors. If posts fail:
- Click **Download CSV with post errors** to get a corrected file
- Fix the errors in the downloaded CSV
- Re-upload the corrected file

## Limits

- **Free plan**: Up to 10 posts per channel (limited by available queue slots)
- **Paid plans**: Up to 100 posts at once
- Bulk uploads are **not available for YouTube**

## Alternatives to Buffer

If you need API access or different features, consider:

- **Hootsuite**: Has API, supports scheduling
- **Later**: Visual calendar, API available
- **SocialPilot**: Bulk scheduling, API access
- **Direct Platform APIs**: Twitter/X API, LinkedIn API, Facebook API (more complex but full control)
