from models import Classifier, InputData, TrainingData


tdata = TrainingData("la_final_data.csv")
idata = InputData("sample_test_data.csv")
classifier = Classifier(
    tdata.features,
    tdata.target,
    n_estimators=100,
    max_depth=7,
    min_child_weight=1,
    colsample_bytree=0.75,
)
classifier.fit()
prediction = classifier.predict(idata.data_ohe, idata.index)
classifier.to_csv("results.csv")
