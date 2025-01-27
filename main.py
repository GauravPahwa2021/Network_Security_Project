import sys
from networksecuritysystem.exception.exception import NetworkSecuritySystemException
from networksecuritysystem.logging.logger import logging
from networksecuritysystem.entity.config_entity import TrainingPipelineConfig,DataIngestionConfig,DataValidationConfig,DataTransformationConfig,ModelTrainerConfig
from networksecuritysystem.components.data_ingestion import DataIngestion
from networksecuritysystem.components.data_validation import DataValidation
from networksecuritysystem.components.data_transformation import DataTransformation
from networksecuritysystem.components.model_trainer import ModelTrainer

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

        datatransformationconfig=DataTransformationConfig(trainingpipelineconfig)
        data_transformation=DataTransformation(datavalidationartifact,datatransformationconfig)
        logging.info("Initiate the data transformation")
        datatransformationartifact=data_transformation.initiate_data_transformation()
        logging.info("Data Transformation Completed")
        print(datatransformationartifact)

        modeltrainerconfig=ModelTrainerConfig(trainingpipelineconfig)
        model_trainer=ModelTrainer(modeltrainerconfig,datatransformationartifact)
        logging.info("Initiate Model Trainer")
        modeltrainerartifact=model_trainer.initiate_model_trainer()
        logging.info("Model Trainer Completed")
        print(modeltrainerartifact)

    except Exception as e:
           raise NetworkSecuritySystemException(e,sys)