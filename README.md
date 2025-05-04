# Social Media Automation Script

A Python script that automates following and interacting with social media accounts across multiple platforms.

## Supported Platforms
- GitHub (follow user and star repositories)
- SoundCloud (follow user)
- LinkedIn (follow profile)
- TikTok (follow account)
- YouTube (like video and subscribe to channel)

## Prerequisites
- Python 3.x
- Chrome browser installed
- Required Python packages (see Installation)

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd follow
```

2. Create and activate a virtual environment:
```bash
python3 -m venv myenv
source myenv/bin/activate  # On Windows use: myenv\Scripts\activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root with your credentials:
```env
# GitHub
GITHUB_TOKEN=your_github_token_here

# LinkedIn
LINKEDIN_USERNAME=your_linkedin_email
LINKEDIN_PASSWORD=your_linkedin_password

# TikTok
TIKTOK_USERNAME=your_tiktok_username
TIKTOK_PASSWORD=your_tiktok_password

# YouTube
YOUTUBE_USERNAME=your_youtube_email
YOUTUBE_PASSWORD=your_youtube_password
```

### GitHub Token Setup
1. Go to https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Select these scopes:
   - `repo` (Full control of private repositories)
   - `user:follow` (Follow and unfollow users)
   - `read:user` (Read user profile data)
4. Copy the generated token to your `.env` file

## Usage

Run the script with:
```bash
python follow.py
```

### Optional Arguments
Skip specific platforms:
```bash
python follow.py --skip github soundcloud linkedin
```

## Features
- Automated following and interaction across multiple platforms
- Retry mechanism for failed operations
- Rate limiting to avoid being blocked
- Detailed logging to `follow.log`
- Progress tracking and status messages
- Error handling and cleanup

## Troubleshooting

### Common Issues

1. **GitHub 403 Errors**
   - Verify your token has the correct scopes
   - Check token format in `.env` file
   - Ensure token hasn't expired

2. **Browser Automation Issues**
   - Make sure Chrome is installed
   - Check Chrome version compatibility
   - Ensure no other Chrome instances are running

3. **Image Not Opening**
   - Verify `beg.png` exists in the project directory
   - Check file permissions

### Logs
Detailed logs are saved to `follow.log` in the project directory. Check this file for specific error messages and debugging information.

## Security Notes
- Never commit your `.env` file to version control
- Keep your tokens and passwords secure
- Regularly rotate your tokens and passwords

## License
[Add your license information here]

## Contributing
[Add contribution guidelines here] 