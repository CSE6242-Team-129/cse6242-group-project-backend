import prediction

pred = prediction.Prediction()
classifier = pred.train_model()
input_index, input_features = pred.receive_input("sample_test_data.csv")
pred.deliver_output()
