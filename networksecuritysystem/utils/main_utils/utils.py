import os
import sys
import pickle
import yaml
import numpy as np
import pandas as pd
from networksecuritysystem.exception.exception import NetworkSecuritySystemException
from networksecuritysystem.logging.logger import logging


def read_yaml_file(file_path: str) -> dict:
    try:
        with open(file_path, "rb") as yaml_file:
            return yaml.safe_load(yaml_file)
    except Exception as e:
        raise NetworkSecuritySystemException(e, sys) 
    
