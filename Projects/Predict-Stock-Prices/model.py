# -*- coding: utf-8 -*-
"""
Created on Sun Oct  9 11:06:27 2016

@author: donaldfung
"""
         
class Model():
    
    def partition(self, df):
        # get size of train and test sets
        train_size = int(df.shape[0] * 0.8)
        test_size = int(df.shape[0] * 0.1)
        
        train = df.iloc[:train_size]
        validation = df.iloc[train_size:train_size + test_size]
        test = df.iloc[-test_size:]
    
        # target label valus
        y_train = train.loc[:, ("Adj. Close")]
        y_val = validation.loc[:, ("Adj. Close")]
        y_test = test.loc[:, ("Adj. Close")]
                          
        # feature data
        X_train = train.drop("Adj. Close", axis = 1)
        X_val = validation.drop("Adj. Close", axis = 1)
        X_test = test.drop("Adj. Close", axis = 1)
        return X_train, y_train, X_val, y_val, X_test, y_test 
        
    def feature_scale(self, X_train, X_val, X_test):
        "Normalize all columns"""
    
        from sklearn.preprocessing import MinMaxScaler
        mms = MinMaxScaler()
        
        X_train_std = mms.fit_transform(X_train)
        X_val_std = mms.fit_transform(X_val)
        X_test_std = mms.fit_transform(X_test)
        return X_train_std, X_val_std, X_test_std
        
    def predict(self, df):

        # get time frame
        time_frame = settings.time_frame
        
        # copy of data
        df_copy = df.copy()

        from sklearn.linear_model import SGDRegressor
        from sklearn.metrics import mean_absolute_error, mean_squared_error
    
        # partition data
        X_train, y_train, X_val, y_val, X_test, y_test = self.partition(df_copy)
        
        # normalize features
        X_train_std, X_val_std, X_test_std = self.feature_scale(X_train, X_val, X_test)
        
        # instance of Linear Regression classifier
        lr = SGDRegressor()
        
        # fit model
        lr.fit(X_train_std, y_train)
        
        # predictions on validation set
        predictions = lr.predict(X_val_std)
    
        # R^2 score
        score = lr.score(X_val_std, y_val)
        
        # error
        test_error = (mean_squared_error(y_val, predictions)**.5)
        print test_error
        
    def plot(self, predictions, y_true):

        import matplotlib.pyplot as plt
        fig, ax = plt.subplots()
        ax.plot(range(0, len(predictions)), predictions, label = "Predictions", color = 'green')
        ax.plot(range(0, len(y_true)), y_true, label = "Actual Price", color = 'red')
        
        ax.legend(loc = 'lower right')
        ax.set_xlabel('Time')
        ax.set_ylabel('Price/Share')
        plt.show()


    