import numpy as np
import pandas as pd
import os
from sklearn.decomposition import PCA


import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# from sklearn.model_selection import train_test_split
# from sklearn.preprocessing import StandardScaler
# from sklearn.metrics import confusion_matrix, precision_recall_curve, roc_auc_score, roc_curve, accuracy_score
# from sklearn.ensemble import RandomForestClassifier


import keras
from keras.models import Sequential
from keras.layers import Conv2D, MaxPooling2D, Flatten, Dense
from keras.utils.vis_utils import plot_model
from keras.optimizers import SGD
from keras import layers
from keras import activations



def genarate_model( 
    n_list : list , 
    activations_list : list ,
    input_dim : int , 
    input_activation_function : str = "relu" ,
    output_node_number : int = 1,
    output_activation_function : str = "sigmoid",
    model_visualization : bool = False, 
    model_summary : bool = False,
    optimizer_functions = "adam",
    first_hidden_layer : int = 50,
    ):
    """
    This funciton returns a model based on the configuration
    of the arguments sent to it.

    n_list: a list of integers that define the number of node
    in each layers
    activation_list: a list of string that define the activation
    function in each of the layers.
    the length of the shortest list out of those to lists will determine
    the number of layers in this model

    model_summary: if True, will print the model summary
    model_visualization: if True will show the visualization of the model

    input_dim: the lenght of the input vector for the input layer (number of columns
    in the dataset)
    input_activation_function: a string for setting the activation function for
    the input layer (default to "relu")
    output_activation_function: a string for setting the activation function for
    the output layer (default to "sigmoid")
    """

    # Define the model architecture
    model = Sequential()

    model.add(Dense(50 , input_dim=input_dim, activation=input_activation_function))

    for node , act_function in zip(n_list , activations_list):
        model.add(Dense(node, activation=act_function))
        
    
    model.add(Dense(output_node_number, activation=output_activation_function))


    if model_summary:
        print(model.summary())
    if model_visualization:
        plot_model(model, to_file='model_plot.png', show_shapes=True, show_layer_names=True)


    
    # Compile the model
    model.compile(loss='binary_crossentropy', optimizer=optimizer_functions, metrics=['accuracy'])
    model.compile(, loss='binary_crossentropy', metrics=['accuracy'])


    return model

def find_best_model_fit(model , num_of_iters : int = 1):
    """
    This funciton run the fit method on a given model
    a number of times to find the one fit with the 
    best accuracy
    """
    best_model = None
    best_acc = 0

    acc_list = []
    for _ in range(num_of_iters):
            
        # train the model (using the validation set)
        model.fit(X_train_norm , y_train , validation_data=(X_validation_norm , y_validation) , epochs = epoch_number , verbose=0)

        # making a prediction
        y_pred_prob_nn_1 = model.predict(X_test_norm)
        y_pred_class_nn_1 = np.rint(y_pred_prob_nn_1)


        cur_acc = accuracy_score(y_test,y_pred_class_nn_1)


        acc_list.append(cur_acc)
        
        if cur_acc > best_acc:
            best_acc = cur_acc
            best_model = model


    print(best_acc)
    return best_model



## features selection impl.



# converting the dataframes into list of all the rows in the dataframe


# normalizer = StandardScaler()

# X_train_norm = normalizer.fit_transform(X_train)
# X_test_norm = normalizer.transform(X_test)
# X_validation_norm = normalizer.transform(X_validation)

# y_train = np.asarray(y_train)
# y_test = np.asarray(y_test)
# y_validation = np.asarray(y_validation)


# # variables
# input_dim = len(X_train.keys())
# epoch_number = 100
# n_list = [100 , 120] # number of nodes in each hidden layer
# activations_list = ["relu" , "relu" , "relu"] # activation function in each hidden layer
# learning_rate = 0.003
# momentum = 0.3
# find_model_tries = 4 # nmber of times to run the model.fit before getting back the best one


# model = genarate_model(
#     n_list=n_list,
#     activations_list=activations_list,
#     input_dim=input_dim,
#     model_summary = False,
#     optimizer_functions=SGD(learning_rate= learning_rate, momentum=momentum)
# )

















