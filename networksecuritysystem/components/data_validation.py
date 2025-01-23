import os
import sys
import pandas as pd

from networksecuritysystem.entity.artifact_entity import DataIngestionArtifact,DataValidationArtifact
from networksecuritysystem.entity.config_entity import DataValidationConfig
from networksecuritysystem.exception.exception import NetworkSecuritySystemException 
from networksecuritysystem.logging.logger import logging 
from networksecuritysystem.constant.training_pipeline import SCHEMA_FILE_PATH
from networksecuritysystem.utils.main_utils.utils import read_yaml_file

from scipy.stats import ks_2samp  # for checking data-drift


class DataValidation:
    def __init__(self,data_ingestion_artifact:DataIngestionArtifact,
                 data_validation_config:DataValidationConfig):
        try:
            self.data_ingestion_artifact=data_ingestion_artifact
            self.data_validation_config=data_validation_config
            self._schema_config = read_yaml_file(SCHEMA_FILE_PATH)
        except Exception as e:
            raise NetworkSecuritySystemException(e,sys)



