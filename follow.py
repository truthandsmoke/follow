import os
import time
import logging
import argparse
import requests
import webbrowser
from dotenv import load_dotenv
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.safari.options import Options as SafariOptions
from selenium.common.exceptions import TimeoutException, WebDriverException

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('follow.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Configuration with validation
def validate_config():
    required_env_vars = {
        'github': ['GITHUB_TOKEN'],
        'linkedin': ['LINKEDIN_USERNAME', 'LINKEDIN_PASSWORD'],
        'tiktok': ['TIKTOK_USERNAME', 'TIKTOK_PASSWORD'],
        'youtube': ['YOUTUBE_USERNAME', 'YOUTUBE_PASSWORD']
    }
    
    missing_vars = []
    for platform, vars in required_env_vars.items():
        for var in vars:
            if not os.getenv(var):
                missing_vars.append(f"{platform}: {var}")
    
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

CONFIG = {
    'github': {
        'token': os.getenv('GITHUB_TOKEN'),
        'username': 'truthandsmoke',
        'repos': ['bullet', 'megamillions', 'compost', 'multipass', '99', 
                 '700bitsofentropypassword', 'timeleft'],
        'rate_limit': 1  # seconds between requests
    },
    'soundcloud': {
        'url': 'https://on.soundcloud.com/LLF1QWey55A7qH868',
        'rate_limit': 2
    },
    'linkedin': {
        'url': 'https://www.linkedin.com/in/nathan-assaf-681469356',
        'username': os.getenv('LINKEDIN_USERNAME'),
        'password': os.getenv('LINKEDIN_PASSWORD'),
        'rate_limit': 3
    },
    'tiktok': {
        'url': 'https://www.tiktok.com/@nathanassaf4',
        'username': os.getenv('TIKTOK_USERNAME'),
        'password': os.getenv('TIKTOK_PASSWORD'),
        'rate_limit': 2
    },
    'youtube': {
        'url': 'https://youtu.be/X0M01_dFHBA',
        'username': os.getenv('YOUTUBE_USERNAME'),
        'password': os.getenv('YOUTUBE_PASSWORD'),
        'rate_limit': 2
    }
}

def get_driver():
    """Get Chrome WebDriver"""
    try:
        from selenium.webdriver.chrome.options import Options as ChromeOptions
        options = ChromeOptions()
        options.add_argument("--start-maximized")
        driver = webdriver.Chrome(options=options)
        return driver
    except Exception as e:
        logger.error(f"Chrome WebDriver error: {str(e)}")
        return None

def show_beg_image():
    """Display the beg.png image after completion"""
    try:
        image_path = os.path.abspath('beg.png')
        if os.path.exists(image_path):
            logger.info("Showing donation request...")
            # Try different methods to open the image
            try:
                # Try using the default image viewer
                os.system(f'open "{image_path}"')
            except:
                try:
                    # Fallback to webbrowser
                    webbrowser.open(image_path)
                except:
                    logger.warning("Could not open image with default viewer or browser")
        else:
            logger.warning(f"beg.png not found at: {image_path}")
    except Exception as e:
        logger.error(f"Error opening image: {str(e)}")

def github_interactions():
    """Handle GitHub following and starring with retry mechanism"""
    if not CONFIG['github']['token']:
        logger.error("GitHub token missing")
        return

    # Log token (masked for security)
    token_length = len(CONFIG['github']['token'])
    masked_token = CONFIG['github']['token'][:4] + '*' * (token_length - 8) + CONFIG['github']['token'][-4:]
    logger.info(f"Using GitHub token: {masked_token}")

    headers = {
        'Authorization': f'token {CONFIG["github"]["token"]}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    def make_request(url, method='put'):
        max_retries = 3
        for attempt in range(max_retries):
            try:
                logger.info(f"Making {method.upper()} request to: {url}")
                response = requests.request(
                    method,
                    url,
                    headers=headers
                )
                if response.status_code == 204:
                    return True
                logger.warning(f"Attempt {attempt + 1}: Request failed with status {response.status_code}")
                logger.warning(f"Response headers: {dict(response.headers)}")
                logger.warning(f"Response body: {response.text}")
                if 'X-RateLimit-Remaining' in response.headers:
                    logger.warning(f"Rate limit remaining: {response.headers['X-RateLimit-Remaining']}")
                time.sleep(2)
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1}: Request error: {str(e)}")
                time.sleep(2)
        return False
    
    # Test token first with more detailed validation
    test_url = "https://api.github.com/user"
    try:
        logger.info("Validating GitHub token...")
        response = requests.get(test_url, headers=headers)
        if response.status_code == 200:
            user_data = response.json()
            logger.info(f"GitHub token is valid for user: {user_data.get('login', 'Unknown')}")
            logger.info(f"Token scopes: {response.headers.get('X-OAuth-Scopes', 'Unknown')}")
        else:
            logger.error(f"GitHub token validation failed with status: {response.status_code}")
            logger.error(f"Response headers: {dict(response.headers)}")
            logger.error(f"Response body: {response.text}")
            return
    except Exception as e:
        logger.error(f"Error validating GitHub token: {str(e)}")
        return
    
    # Follow user
    follow_url = f'https://api.github.com/user/following/{CONFIG["github"]["username"]}'
    logger.info(f"Attempting to follow user: {CONFIG['github']['username']}")
    if make_request(follow_url):
        logger.info("GitHub follow successful")
    else:
        logger.error("GitHub follow failed after retries")
    
    # Star repositories
    for repo in CONFIG['github']['repos']:
        star_url = f'https://api.github.com/user/starred/{CONFIG["github"]["username"]}/{repo}'
        logger.info(f"Attempting to star repository: {repo}")
        if make_request(star_url):
            logger.info(f"Starred {repo}")
        else:
            logger.error(f"Failed to star {repo} after retries")
        time.sleep(CONFIG['github']['rate_limit'])

def soundcloud_interaction():
    """Handle SoundCloud follow using Selenium with retry mechanism"""
    logger.info("Opening SoundCloud...")
    driver = get_driver()
    if not driver:
        logger.error("Could not initialize WebDriver")
        return
    
    try:
        driver.get(CONFIG['soundcloud']['url'])
        time.sleep(3)
        
        try:
            follow_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//button[contains(., 'Follow')]"))
            )
            follow_button.click()
            logger.info("SoundCloud follow successful")
            time.sleep(2)
        except TimeoutException:
            logger.error("Timeout waiting for SoundCloud follow button")
        except Exception as e:
            logger.error(f"Error clicking SoundCloud follow button: {str(e)}")
    except Exception as e:
        logger.error(f"SoundCloud error: {str(e)}")
    finally:
        try:
            driver.quit()
        except:
            pass

def linkedin_interaction():
    """Handle LinkedIn follow using Selenium with retry mechanism"""
    logger.info("Opening LinkedIn...")
    driver = get_driver()
    if not driver:
        logger.error("Could not initialize WebDriver")
        return
    
    try:
        driver.get(CONFIG['linkedin']['url'])
        time.sleep(2)
        
        if "login" in driver.current_url:
            try:
                username_field = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "username"))
                )
                username_field.send_keys(CONFIG['linkedin']['username'])
                
                password_field = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "password"))
                )
                password_field.send_keys(CONFIG['linkedin']['password'] + Keys.RETURN)
                time.sleep(3)
            except TimeoutException:
                logger.error("Timeout during LinkedIn login")
                return
        
        try:
            follow_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//button[contains(., 'Follow')]"))
            )
            follow_button.click()
            logger.info("LinkedIn follow successful")
            time.sleep(2)
        except TimeoutException:
            logger.error("Timeout waiting for LinkedIn follow button")
        except Exception as e:
            logger.error(f"Error clicking LinkedIn follow button: {str(e)}")
    except Exception as e:
        logger.error(f"LinkedIn error: {str(e)}")
    finally:
        try:
            driver.quit()
        except:
            pass

def tiktok_interaction():
    """Handle TikTok follow using Selenium with retry mechanism"""
    logger.info("Opening TikTok...")
    driver = get_driver()
    if not driver:
        logger.error("Could not initialize WebDriver")
        return
    
    try:
        driver.get(CONFIG['tiktok']['url'])
        time.sleep(3)
        
        try:
            follow_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//button[contains(., 'Follow')]"))
            )
            follow_button.click()
            logger.info("TikTok follow successful")
        except TimeoutException:
            logger.warning("TikTok follow button not found - may need manual login")
        except Exception as e:
            logger.error(f"Error clicking TikTok follow button: {str(e)}")
        
        time.sleep(2)
    except Exception as e:
        logger.error(f"TikTok error: {str(e)}")
    finally:
        try:
            driver.quit()
        except:
            pass

def youtube_interaction():
    """Handle YouTube like and subscribe using Selenium with retry mechanism"""
    logger.info("Opening YouTube...")
    driver = get_driver()
    if not driver:
        logger.error("Could not initialize WebDriver")
        return
    
    try:
        driver.get(CONFIG['youtube']['url'])
        time.sleep(3)
        
        # Like the video
        try:
            like_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//button[contains(@aria-label, 'like this video')]"))
            )
            like_button.click()
            logger.info("YouTube like successful")
        except TimeoutException:
            logger.warning("YouTube like button not found")
        except Exception as e:
            logger.error(f"Error clicking YouTube like button: {str(e)}")
        
        # Subscribe to channel
        try:
            subscribe_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//button[contains(., 'Subscribe')]"))
            )
            if "subscribed" not in subscribe_button.text.lower():
                subscribe_button.click()
                logger.info("YouTube subscribe successful")
            else:
                logger.info("Already subscribed to YouTube channel")
        except TimeoutException:
            logger.warning("YouTube subscribe button not found")
        except Exception as e:
            logger.error(f"Error clicking YouTube subscribe button: {str(e)}")
        
        time.sleep(2)
    except Exception as e:
        logger.error(f"YouTube error: {str(e)}")
    finally:
        try:
            driver.quit()
        except:
            pass

def main():
    parser = argparse.ArgumentParser(description='Social Media Automation Tool')
    parser.add_argument('--skip', nargs='+', choices=['github', 'soundcloud', 'linkedin', 'tiktok', 'youtube'],
                      help='Platforms to skip')
    args = parser.parse_args()
    
    try:
        validate_config()
    except ValueError as e:
        logger.error(str(e))
        return
    
    logger.info("Starting Social Media Automation")
    
    platforms = {
        'github': github_interactions,
        'soundcloud': soundcloud_interaction,
        'linkedin': linkedin_interaction,
        'tiktok': tiktok_interaction,
        'youtube': youtube_interaction
    }
    
    skip_platforms = set(args.skip) if args.skip else set()
    
    for platform, func in platforms.items():
        if platform not in skip_platforms:
            logger.info(f"\nProcessing {platform}...")
            func()
            time.sleep(CONFIG[platform]['rate_limit'])
    
    show_beg_image()
    logger.info("All social media actions completed!")

if __name__ == "__main__":
    main()