import os
import logging
import asyncio
import pandas as pd
import kagglehub
from pathlib import Path

logger = logging.getLogger(__name__)

# Global variables to store loaded data
ipl_data = None
telugu_nlp_data = None

async def load_ipl_data():
    """
    Load IPL dataset from Kaggle
    """
    global ipl_data
    
    try:
        # Create data directory if it doesn't exist
        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)
        
        # Check if data is already downloaded
        ipl_data_path = data_dir / "ipl_data.csv"
        
        if not ipl_data_path.exists():
            logger.info("Downloading IPL dataset from Kaggle...")
            
            # Download from GitHub repository
            github_url = "https://raw.githubusercontent.com/12345k/IPL-Dataset/master/IPL/data.csv"
            
            # Use pandas to download and save the data
            df = pd.read_csv(github_url)
            df.to_csv(ipl_data_path, index=False)
            logger.info(f"IPL data saved to {ipl_data_path}")
            
            # Also try to download from Kaggle
            try:
                kaggle_path = kagglehub.dataset_download("patrickb1912/ipl-complete-dataset-20082020")
                logger.info(f"Additional IPL data downloaded from Kaggle to {kaggle_path}")
                
                # Merge datasets if needed
                # This would require additional processing based on the structure of the datasets
            except Exception as e:
                logger.warning(f"Could not download from Kaggle: {e}")
        
        # Load the data
        ipl_data = pd.read_csv(ipl_data_path)
        logger.info(f"Loaded IPL dataset with {len(ipl_data)} records")
        
        return ipl_data
    
    except Exception as e:
        logger.error(f"Error loading IPL data: {e}")
        return None

async def load_telugu_nlp_data():
    """
    Load Telugu NLP dataset from Kaggle
    """
    global telugu_nlp_data
    
    try:
        # Create data directory if it doesn't exist
        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)
        
        # Check if data is already downloaded
        telugu_data_path = data_dir / "telugu_nlp"
        
        if not telugu_data_path.exists():
            logger.info("Downloading Telugu NLP dataset from Kaggle...")
            
            try:
                # Download from Kaggle
                kaggle_path = kagglehub.dataset_download("sudalairajkumar/telugu-nlp")
                logger.info(f"Telugu NLP data downloaded from Kaggle to {kaggle_path}")
                
                # Create the directory
                telugu_data_path.mkdir(exist_ok=True)
                
                # Process and move the files if needed
                # This would require additional processing based on the structure of the dataset
            except Exception as e:
                logger.warning(f"Could not download Telugu NLP data from Kaggle: {e}")
                telugu_data_path.mkdir(exist_ok=True)
        
        logger.info(f"Telugu NLP data directory: {telugu_data_path}")
        
        # Here you would load the Telugu NLP data
        # Since the structure is unknown, we'll just log that it's available
        telugu_nlp_data = True
        
        return telugu_nlp_data
    
    except Exception as e:
        logger.error(f"Error loading Telugu NLP data: {e}")
        return None

def get_ipl_data():
    """
    Get the loaded IPL data
    """
    global ipl_data
    return ipl_data

def get_telugu_nlp_data():
    """
    Get the loaded Telugu NLP data
    """
    global telugu_nlp_data
    return telugu_nlp_data
