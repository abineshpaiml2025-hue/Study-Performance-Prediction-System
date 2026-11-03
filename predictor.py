import numpy as np
from sklearn.ensemble import RandomForestRegressor

def train_model():
    np.random.seed(42)

    study_hours = np.random.uniform(0, 8, 500)
    attendance = np.random.uniform(40, 100, 500)
    previous_marks = np.random.uniform(30, 100, 500)
    assignments = np.random.uniform(20, 100, 500)

    performance = (
        0.28 * previous_marks
        + 2.7 * study_hours
        + 0.20 * attendance
        + 0.12 * assignments
        + np.random.normal(0, 5, 500)
    )

    performance = np.clip(performance, 0, 100)

    X = np.column_stack((
        study_hours,
        attendance,
        previous_marks,
        assignments
    ))

    model = RandomForestRegressor(
        n_estimators=100,
        random_state=42
    )

    model.fit(X, performance)
    return model


model = train_model()


def predict_performance(hours, attendance, marks, assignments):
    data = np.array([[
        hours, attendance, marks, assignments
    ]])

    prediction = model.predict(data)[0]
    return round(float(np.clip(prediction, 0, 100)), 2)


def recommend_study(hours, attendance, marks, assignments):

    recommendations = []

    if marks < 60:
        recommendations.append(
            "Focus more on weak subjects and practise daily."
        )

    if hours < 2:
        recommendations.append(
            "Increase daily study time gradually."
        )

    if attendance < 75:
        recommendations.append(
            "Improve your class attendance."
        )

    if assignments < 80:
        recommendations.append(
            "Complete pending assignments on time."
        )

    if not recommendations:
        recommendations.append(
            "Excellent! Maintain your current study routine."
        )

    return " ".join(recommendations)
