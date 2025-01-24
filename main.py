import sys
from networksecuritysystem.exception.exception import NetworkSecuritySystemException
from networksecuritysystem.logging.logger import logging
from networksecuritysystem.entity.config_entity import TrainingPipelineConfig,DataIngestionConfig,DataValidationConfig
from networksecuritysystem.components.data_ingestion import DataIngestion
from networksecuritysystem.components.data_validation import DataValidation

if __name__=='__main__':
    try:
        trainingpipelineconfig=TrainingPipelineConfig()
        dataingestionconfig=DataIngestionConfig(trainingpipelineconfig)
        data_ingestion=DataIngestion(dataingestionconfig)
        logging.info("Initiate the data ingestion")
        dataingestionartifact=data_ingestion.initiate_data_ingestion()
        logging.info("Data Initiation Completed")
        print(dataingestionartifact)

        datavalidationconfig=DataValidationConfig(trainingpipelineconfig)
        data_validation=DataValidation(dataingestionartifact,datavalidationconfig)
        logging.info("Initiate the data validation")
        datavalidationartifact=data_validation.initiate_data_validation()
        logging.info("Data Validation Completed")
        print(datavalidationartifact)
        
    except Exception as e:
           raise NetworkSecuritySystemException(e,sys)