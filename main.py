import sys
from networksecuritysystem.exception.exception import NetworkSecuritySystemException
from networksecuritysystem.logging.logger import logging
from networksecuritysystem.entity.config_entity import TrainingPipelineConfig,DataIngestionConfig
from networksecuritysystem.components.data_ingestion import DataIngestion

if __name__=='__main__':
    try:
        trainingpipelineconfig=TrainingPipelineConfig()
        dataingestionconfig=DataIngestionConfig(trainingpipelineconfig)
        data_ingestion=DataIngestion(dataingestionconfig)
        logging.info("Initiate the data ingestion")
        dataingestionartifact=data_ingestion.initiate_data_ingestion()
        logging.info("Data Initiation Completed")
        print(dataingestionartifact)
        
    except Exception as e:
           raise NetworkSecuritySystemException(e,sys)