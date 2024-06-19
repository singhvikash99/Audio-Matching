from celery import Celery
from celery_worker import app  
from utils import send_email_result
from clipprocessor import ClipProcessor
import logging
import os

celery = app

logging.basicConfig(level=logging.INFO)  
logger = logging.getLogger(__name__) 

@celery.task(bind=True)
def process_song_task(self, song_path):
    pass

@celery.task(bind=True)
def process_clips_task(self, clip_path, songs_dir):
    try:
        clip_processor = ClipProcessor(clip_path, songs_dir)
        result = clip_processor.process_clips()
        send_email_result(result) 
        os.remove(clip_path)
    except Exception as e:
        logger.error(f"Error processing clips at {clip_path}: {str(e)}")
        raise


