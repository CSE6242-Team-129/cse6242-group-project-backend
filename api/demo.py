from models import Classifier, InputData, TrainingData


tdata = TrainingData("api/la_final_data.csv")
idata = InputData("api/sample_test_data.csv")
classifier = Classifier(tdata, idata)
classifier.fit()
prediction = classifier.predict()
classifier.to_csv("results.csv")