import sys
import os
from datetime import datetime
import logging

# Add py3-pinterest to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'resources', 'py3-pinterest'))

from py3pin.Pinterest import Pinterest
from db import (
    get_pinterest_credentials,
    save_pinterest_credentials,
    update_pinterest_login_status
)

logger = logging.getLogger(__name__)


class PinterestService:
    def __init__(self, user_id, pinterest_email=None, pinterest_password=None, pinterest_username=None):
        """
        Initialize Pinterest service for a specific user

        Args:
            user_id: Your app's user ID
            pinterest_email: Pinterest email (optional if loading from DB)
            pinterest_password: Pinterest password (optional if loading from DB)
            pinterest_username: Pinterest username (optional if loading from DB)
        """
        self.user_id = user_id
        self.cred_root = f'./pinterest_creds/user_{user_id}/'
        os.makedirs(self.cred_root, exist_ok=True)

        # If credentials not provided, try to load from database
        if not all([pinterest_email, pinterest_password, pinterest_username]):
            creds = get_pinterest_credentials(user_id)
            if creds:
                pinterest_email = creds['pinterest_email']
                pinterest_password = creds['pinterest_password']
                pinterest_username = creds['pinterest_username']
            else:
                raise ValueError(f"No Pinterest credentials found for user {user_id}")

        self.pinterest = Pinterest(
            email=pinterest_email,
            password=pinterest_password,
            username=pinterest_username,
            cred_root=self.cred_root
        )

    def check_cookies_valid(self):
        """
        Check if stored cookies are still valid by making a simple API call

        Returns:
            bool: True if cookies are valid, False otherwise
        """
        try:
            # Try to get user overview - if this works, cookies are valid
            self.pinterest.get_user_overview()
            update_pinterest_login_status(self.user_id, True)
            return True
        except Exception as e:
            logger.warning(f"Cookie validation failed for user {self.user_id}: {str(e)}")
            update_pinterest_login_status(self.user_id, False)
            return False

    def login(self):
        """
        Perform Pinterest login using Selenium (requires Chrome)
        This will open a browser window to handle reCAPTCHA

        Returns:
            bool: True if login successful, False otherwise
        """
        try:
            self.pinterest.login()
            update_pinterest_login_status(self.user_id, True)
            logger.info(f"Successfully logged in to Pinterest for user {self.user_id}")
            return True
        except Exception as e:
            logger.error(f"Pinterest login failed for user {self.user_id}: {str(e)}")
            update_pinterest_login_status(self.user_id, False)
            return False

    def ensure_logged_in(self):
        """
        Ensure user is logged in by checking cookies, and logging in if needed

        Returns:
            bool: True if logged in (or successfully logged in), False otherwise
        """
        if self.check_cookies_valid():
            return True

        # Cookies expired, need to re-login
        logger.info(f"Cookies expired for user {self.user_id}, attempting re-login")
        return self.login()

    def get_boards(self):
        """
        Get all Pinterest boards (mood boards) for the user

        Returns:
            list: List of boards with id, name, description, etc.
        """
        try:
            if not self.ensure_logged_in():
                raise Exception("Failed to authenticate with Pinterest")

            # Get all boards for the user
            boards = self.pinterest.boards_all()

            # Extract relevant information
            board_list = []
            for board in boards:
                board_list.append({
                    'id': board.get('id'),
                    'name': board.get('name'),
                    'description': board.get('description'),
                    'pin_count': board.get('pin_count'),
                    'url': board.get('url'),
                    'image_thumbnail_url': board.get('image_thumbnail_url'),
                    'privacy': board.get('privacy')
                })

            return board_list
        except Exception as e:
            logger.error(f"Failed to get boards for user {self.user_id}: {str(e)}")
            raise

    def get_board_pins(self, board_id):
        """
        Get all pins from a specific board

        Args:
            board_id: Pinterest board ID

        Returns:
            list: List of pins with images, descriptions, etc.
        """
        try:
            if not self.ensure_logged_in():
                raise Exception("Failed to authenticate with Pinterest")

            pins = []
            pin_batch = self.pinterest.board_feed(board_id=board_id)

            while len(pin_batch) > 0:
                pins += pin_batch
                pin_batch = self.pinterest.board_feed(board_id=board_id)

            return pins
        except Exception as e:
            logger.error(f"Failed to get pins for board {board_id}: {str(e)}")
            raise


def get_pinterest_status(user_id):
    """
    Get the Pinterest connection status for a user

    Args:
        user_id: Your app's user ID

    Returns:
        str: 'connected', 'expired', or 'disconnected'
    """
    # Check if credentials exist in database
    creds = get_pinterest_credentials(user_id)

    if not creds:
        return 'disconnected'

    # Check if cookies are valid
    try:
        service = PinterestService(user_id)
        if service.check_cookies_valid():
            return 'connected'
        else:
            return 'expired'
    except Exception as e:
        logger.error(f"Error checking Pinterest status for user {user_id}: {str(e)}")
        return 'expired'
