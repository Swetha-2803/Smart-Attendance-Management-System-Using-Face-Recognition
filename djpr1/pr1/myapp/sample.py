import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, accuracy_score
df = pd.read_csv("diabetes.csv")
X_lr = df[['BMI']]
y_lr = df['Glucose']
model_lr = LinearRegression().fit(X_lr, y_lr)
print("\nLinear Regression Coefficient:", model_lr.coef_)
print("Intercept:", model_lr.intercept_)
plt.scatter(X_lr, y_lr, color='blue')
plt.plot(X_lr, model_lr.predict(X_lr), color='red')
plt.title("Linear Regression: BMI vs Glucose")
plt.xlabel("BMI")
plt.ylabel("Glucose")
plt.show()
X_log = df.drop("Outcome", axis=1)
y_log = df["Outcome"]
X_train, X_test, y_train, y_test = train_test_split(X_log, y_log, test_size=0.2, random_state=0)
model_log = LogisticRegression(max_iter=1000).fit(X_train, y_train)
y_pred = model_log.predict(X_test)
print("\nLogistic Regression Accuracy:", accuracy_score(y_test, y_pred))