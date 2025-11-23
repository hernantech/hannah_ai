"""
FAL.AI Image Editing Service
Handles image uploads and AI-powered image editing using fal.ai
"""

import os
import fal_client
import tempfile
import logging
from typing import Dict, Optional, Union

logger = logging.getLogger(__name__)


class FalImageService:
    """Service for interacting with fal.ai image editing API"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the FAL service

        Args:
            api_key: FAL API key (if not provided, will use FAL_API_KEY env var)
        """
        self.api_key = api_key or os.getenv('FAL_API_KEY')
        if not self.api_key:
            raise ValueError("FAL_API_KEY not found in environment variables")

        # Set the FAL_KEY for fal_client
        os.environ['FAL_KEY'] = self.api_key
        logger.info("FAL Image Service initialized")

    def upload_image_from_bytes(self, image_data: bytes, filename: str = "image.jpg") -> str:
        """
        Upload image data to fal.ai storage

        Args:
            image_data: Raw image bytes
            filename: Original filename (for extension detection)

        Returns:
            str: URL of the uploaded image
        """
        logger.info(f"Uploading image: {filename} ({len(image_data)} bytes)")

        # Create a temporary file to upload
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as tmp_file:
            tmp_file.write(image_data)
            tmp_path = tmp_file.name

        try:
            # Upload using fal_client
            url = fal_client.upload_file(tmp_path)
            logger.info(f"Image uploaded successfully: {url}")
            return url
        finally:
            # Clean up temp file
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def edit_image(
        self,
        prompt: str,
        image_data: Union[bytes, str],
        filename: str = "image.jpg",
        image_size: str = "auto",
        output_format: str = "png",
        enable_prompt_expansion: bool = False,
        seed: Optional[int] = None
    ) -> Dict:
        """
        Edit an image using AI based on a text prompt

        Args:
            prompt: Text description of desired edits
            image_data: Either raw image bytes or an image URL
            filename: Original filename (used if image_data is bytes)
            image_size: Size preset (auto, square_hd, landscape_16_9, etc.)
            output_format: Output format (jpeg, png, webp)
            enable_prompt_expansion: Whether to expand the prompt
            seed: Random seed for reproducibility

        Returns:
            dict: Result containing edited images and metadata
        """
        logger.info(f"Editing image with prompt: '{prompt}'")

        # Determine if we have bytes or a URL
        if isinstance(image_data, bytes):
            image_url = self.upload_image_from_bytes(image_data, filename)
        elif isinstance(image_data, str) and image_data.startswith(('http://', 'https://')):
            image_url = image_data
            logger.info(f"Using provided image URL: {image_url}")
        else:
            raise ValueError("image_data must be either bytes or a valid HTTP(S) URL")

        # Build arguments
        arguments = {
            'prompt': prompt,
            'image_urls': [image_url],
            'image_size': image_size,
            'output_format': output_format,
            'enable_prompt_expansion': enable_prompt_expansion
        }

        if seed is not None:
            arguments['seed'] = seed

        logger.info(f"Submitting edit request to fal-ai/alpha-image-232/edit-image")

        try:
            # Subscribe and wait for result
            result = fal_client.subscribe(
                "fal-ai/alpha-image-232/edit-image",
                arguments=arguments,
                with_logs=True,
                on_queue_update=self._log_queue_update,
            )

            logger.info(f"Edit completed successfully. Generated {len(result.get('images', []))} image(s)")
            return result

        except Exception as e:
            logger.error(f"Failed to edit image: {str(e)}")
            raise

    def _log_queue_update(self, update):
        """Log queue updates during processing"""
        if isinstance(update, fal_client.InProgress):
            if update.logs:
                for log in update.logs:
                    logger.info(f"[FAL] {log['message']}")


# Singleton instance
_fal_service = None


def get_fal_service() -> FalImageService:
    """Get or create the FAL service singleton"""
    global _fal_service
    if _fal_service is None:
        _fal_service = FalImageService()
    return _fal_service
