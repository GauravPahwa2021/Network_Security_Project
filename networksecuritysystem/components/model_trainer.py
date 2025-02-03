import os
import sys

from networksecuritysystem.exception.exception import NetworkSecuritySystemException 
from networksecuritysystem.logging.logger import logging

from networksecuritysystem.entity.artifact_entity import DataTransformationArtifact,ModelTrainerArtifact
from networksecuritysystem.entity.config_entity import ModelTrainerConfig


from networksecuritysystem.utils.main_utils.utils import save_preprocessor_object,load_preprocessor_object,load_numpy_array_data
from networksecuritysystem.utils.main_utils.utils import evaluate_models
from networksecuritysystem.utils.ml_utils.metric.classification_metric import get_classification_score
from networksecuritysystem.utils.ml_utils.model.estimator import NetworkModel

from sklearn.metrics import r2_score
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import (
    AdaBoostClassifier,
    GradientBoostingClassifier,
    RandomForestClassifier,
)

from urllib.parse import urlparse
import mlflow
import dagshub
# Initialize DagsHub
dagshub.init(repo_owner='GauravPahwa2021', repo_name='Network_Security_Project', mlflow=True)

# Set the MLflow tracking URI to DagsHub
mlflow.set_tracking_uri("https://dagshub.com/GauravPahwa2021/Network_Security_Project.mlflow")

from dotenv import load_dotenv
load_dotenv()

# Set DagsHub credentials as environment variables
os.environ['MLFLOW_TRACKING_USERNAME'] = os.getenv("MLFLOW_TRACKING_USERNAME")
os.environ['MLFLOW_TRACKING_PASSWORD'] = os.getenv("MLFLOW_TRACKING_PASSWORD")


class ModelTrainer:
    def __init__(self,model_trainer_config:ModelTrainerConfig,data_transformation_artifact:DataTransformationArtifact):
        try:
            self.model_trainer_config=model_trainer_config
            self.data_transformation_artifact=data_transformation_artifact
        except Exception as e:
            raise NetworkSecuritySystemException(e,sys)

    def track_mlflow(self,best_model,classificationmetric,input_example):
        mlflow.set_registry_uri("https://dagshub.com/GauravPahwa2021/Network_Security_Project.mlflow")
        tracking_url_type_store = urlparse(mlflow.get_tracking_uri()).scheme

        with mlflow.start_run():
            f1_score=classificationmetric.f1_score
            precision_score=classificationmetric.precision_score
            recall_score=classificationmetric.recall_score

            mlflow.log_param("model_name",best_model.__class__.__name__)
            mlflow.log_metric("f1_score",f1_score)
            mlflow.log_metric("precision",precision_score)
            mlflow.log_metric("recall_score",recall_score)
            mlflow.sklearn.log_model(best_model,"model",input_example=input_example)  
            # Model registry does not work with file store
            if tracking_url_type_store != "file":

                # Register the model
                # There are other ways to use the Model Registry, which depends on the use case,
                # please refer to the doc for more information:
                # https://mlflow.org/docs/latest/model-registry.html#api-workflow
                mlflow.sklearn.log_model(best_model, "model", registered_model_name=best_model.__class__.__name__,input_example=input_example)
            else:
                mlflow.sklearn.log_model(best_model, "model",input_example=input_example)  
    
    def train_model(self,X_train,y_train,x_test,y_test):
        models = {
                "Random Forest": RandomForestClassifier(verbose=1),
                "Decision Tree": DecisionTreeClassifier(),
                "Gradient Boosting": GradientBoostingClassifier(verbose=1),
                "Logistic Regression": LogisticRegression(verbose=1),
                "AdaBoost": AdaBoostClassifier(),
                "KNN": KNeighborsClassifier(),
            }
        params={
            "Decision Tree": {
                'criterion':['gini', 'entropy', 'log_loss'],
                # 'splitter':['best','random'],
                # 'max_features':['sqrt','log2'],
            },
            "Random Forest":{
                'n_estimators': [8,16,32,128,256],
                # 'criterion':['gini', 'entropy', 'log_loss'],
                # 'max_features':['sqrt','log2',None],
            },
            "Gradient Boosting":{
                'learning_rate':[.1,.01,.05,.001],
                'subsample':[0.6,0.7,0.75,0.85,0.9],
                'n_estimators': [8,16,32,64,128,256],
                # 'loss':['log_loss', 'exponential'],
                # 'criterion':['squared_error', 'friedman_mse'],
                # 'max_features':['auto','sqrt','log2'],
            },
            "AdaBoost":{
                'learning_rate':[.1,.01,.001],
                'n_estimators': [8,16,32,64,128,256]
            },
            "Logistic Regression":{
                'C':[0.1,1,10,100],
                # 'penalty':['l1','l2','elasticnet','none'],
                # 'solver':['newton-cg', 'lbfgs', 'liblinear', 'sag', 'saga'],
                # 'max_iter':[100,200,300,400,500]
            },
            "KNN":{
                'n_neighbors':[3,5,7,9],
                #'weights':['uniform','distance'],
                # 'algorithm':['auto','ball_tree','kd_tree','brute']
            },
        }
        model_report:dict=evaluate_models(X_train=X_train,y_train=y_train,X_test=x_test,y_test=y_test,
                                          models=models,param=params)
        
        # To get best model score from dict
        best_model_score = max(sorted(model_report.values()))

        # To get best model name from dict

        best_model_name = list(model_report.keys())[
            list(model_report.values()).index(best_model_score)
        ]
        best_model = models[best_model_name]
        y_train_pred = best_model.predict(X_train)

        classification_train_metric = get_classification_score(y_true=y_train,y_pred=y_train_pred)

        # Prepare an input example
        input_example1 = X_train[:1].reshape(1, -1)  # Ensure it is 2D
        # Use the first sample from the training data as an example
        
        # Track the experiements with mlflow
        self.track_mlflow(best_model,classification_train_metric,input_example1)


        y_test_pred=best_model.predict(x_test)
        classification_test_metric=get_classification_score(y_true=y_test,y_pred=y_test_pred)

        # Prepare an input example
        input_example2 = x_test[:1].reshape(1, -1)  # Ensure it is 2D  
        # Use the first sample from the test data as an example

        self.track_mlflow(best_model,classification_test_metric,input_example2)

        preprocessor = load_preprocessor_object(file_path=self.data_transformation_artifact.transformed_object_file_path)
            
        model_dir_path = os.path.dirname(self.model_trainer_config.trained_model_file_path)
        os.makedirs(model_dir_path,exist_ok=True)

        Network_Model=NetworkModel(preprocessor=preprocessor,model=best_model)
        save_preprocessor_object(self.model_trainer_config.trained_model_file_path,obj=Network_Model)

        # model pusher
        save_preprocessor_object("final_model/model.pkl",best_model)
        

        # Model Trainer Artifact
        model_trainer_artifact=ModelTrainerArtifact(trained_model_file_path=self.model_trainer_config.trained_model_file_path,
                             train_metric_artifact=classification_train_metric,
                             test_metric_artifact=classification_test_metric
                             )
        logging.info(f"Model trainer artifact: {model_trainer_artifact}")
        return model_trainer_artifact
    


    def initiate_model_trainer(self)->ModelTrainerArtifact:
        try:
            train_file_path = self.data_transformation_artifact.transformed_train_file_path
            test_file_path = self.data_transformation_artifact.transformed_test_file_path

            #loading training array and testing array
            train_arr = load_numpy_array_data(train_file_path)
            test_arr = load_numpy_array_data(test_file_path)

            x_train, y_train, X_test, y_test = (
                train_arr[:, :-1],
                train_arr[:, -1],
                test_arr[:, :-1],
                test_arr[:, -1],
            )

            model_trainer_artifact=self.train_model(x_train,y_train,X_test,y_test)
            return model_trainer_artifact

        except Exception as e:
            raise NetworkSecuritySystemException(e,sys)