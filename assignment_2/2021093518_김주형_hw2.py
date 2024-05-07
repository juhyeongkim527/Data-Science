import pandas as pd
import argparse
import math
import random # for randomly split to test_data_object

class Node:
    def __init__(self, data):
        self.data = data
        self.selected_feature = 'leaf'
        self.children = []
    
    def append_child(self, child):
        self.children.append(child)

    def set_selected_feature(self, feature):
        self.selected_feature = feature

def get_info(node):
    node_class = node.iloc[:,-1]

    info = 0
    for i in range(node_class.nunique()):
        p_i = node_class.value_counts().iloc[i] / len(node_class)
        info -= p_i * math.log(p_i, 2)
    
    return info

count = 0
def get_gain_ratio(node, feature):
    same_value_groups = node.groupby(feature)
    
    before_info = get_info(node)
    after_info = 0
    split_info = 0

    for same_values in same_value_groups:
        # same_values[0] : value_name, same_values[1] : dataframe
        after_info += (len(same_values[1]) / len(node.iloc[:, -1])) * get_info(same_values[1])
        split_info -= (len(same_values[1]) / len(node.iloc[:, -1])) * math.log((len(same_values[1]) / len(node.iloc[:, -1])), 2)
    
    gain_ratio = (before_info - after_info) / split_info

    # print('before_info : ' + str(before_info))
    # print('after_info : ' + str(after_info))
    # print(str(feature) + '\'s gain_ratio : ' + str(gain_ratio) + '\n')
    return gain_ratio


def select_feature(node, features):    
    highest_gain_ratio = 0
    selected_feature = ''
    for feature in features:
        gain_ratio = get_gain_ratio(node, feature)
        if(gain_ratio > highest_gain_ratio):
            highest_gain_ratio = gain_ratio
            selected_feature = feature

    # print('highest_gain_ratio : ' + str(highest_gain_ratio))
    # print('selected_feature : ' + str(selected_feature))

    return selected_feature    

def make_tree(node, available_features):
    if(len(available_features) == 0 or node.data.iloc[:,-1].nunique() == 1):
        # print(node.data)
        # print('Leaf Node\n\n')
        return
    
    # print('before : '+str(available_features))
    selected_feature = select_feature(node.data, available_features)
    node.set_selected_feature(selected_feature)
    available_features_copy = available_features.copy()
    available_features_copy.remove(selected_feature)
    # print('after : ' +str(available_features_copy)+'\n')
    
    children = node.data.groupby(selected_feature)
    
    for child in children:
        node.append_child(Node(child[1]))
    
    for child in node.children:
        make_tree(child, available_features_copy)

predicted_class_label = []
def predict_class_label(node, test_data_object, selected_feature):
    global predicted_class_label

    if(selected_feature == 'leaf' and node.data.iloc[:, -1].nunique() == 1):
        predicted_class_label.append(node.data.iloc[:, -1].iloc[0])
        return
    
    if(selected_feature == 'leaf' and node.data.iloc[:, -1].nunique() != 1):    
        majority_count = 0
        majority_class_label = ''
        class_labels = node.data.groupby(node.data.columns[-1])
        for class_label in class_labels:       
            if(majority_count < len(class_label[1])):
                majority_count = len(class_label[1])
                majority_class_label = class_label[1].iloc[:, -1].iloc[0]
        predicted_class_label.append(majority_class_label)
        return
    
    feature_value = test_data_object[selected_feature]
    is_matched = False
    for child in node.children:
        if(child.data[selected_feature].iloc[0] == feature_value):
            is_matched = True
            predict_class_label(child, test_data_object, child.selected_feature)
            break

    # below is a case that tree cannot split test_data_object 
    # because tree's children made by train_data don't have feature_value of test_data_object
    
    # solution 1. split to left child (most simple)
    # score : 313 / 346 for training by "dt_train1.txt" and testing by "dt_test1.txt"
    # if(is_matched == False): 
    #     predict_class_label(node.children[0], test_data_object, node.children[0].selected_feature)
    
    # solution 2. split to random child
    # score : when testing 10 times, approximately 312~319 / 346 for training by "dt_train1.txt" and testing by "dt_test1.txt" 
    # if(is_matched == False): 
    #     random_child = node.children[random.randrange(0, len(node.children))]
    #     predict_class_label(random_child, test_data_object, random_child.selected_feature)

    # solution 3. majority voting for present node (best score)
    # score : 323 / 346 for training by "dt_train1.txt" and testing by "dt_test1.txt"
    if(is_matched == False):
        majority_count = 0
        majority_class_label = ''
        class_labels = node.data.groupby(node.data.columns[-1])
        for class_label in class_labels:       
            if(majority_count < len(class_label[1])):
                majority_count = len(class_label[1])
                majority_class_label = class_label[1].iloc[:, -1].iloc[0]
        predicted_class_label.append(majority_class_label)
        
def main(train_file_name, test_file_name, result_file_name):
    train_data = pd.read_csv(train_file_name, delimiter = '\t')
    test_data = pd.read_csv(test_file_name, delimiter = '\t')
    
    features = list(train_data.columns[:-1])
    root = Node(train_data)

    make_tree(root, features)
    
    for i in range(len(test_data)):
        predict_class_label(root, test_data.loc[i], root.selected_feature)

    global predicted_class_label
    test_data.insert(len(test_data.columns), train_data.columns[-1], predicted_class_label)
    test_data.to_csv(result_file_name, sep = '\t', index = False)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("train_file_name", type = str)
    parser.add_argument("test_file_name", type = str)
    parser.add_argument("result_file_name", type = str)
    args = parser.parse_args()
    train_file_name = args.train_file_name
    test_file_name = args.test_file_name
    result_file_name = args.result_file_name
    main(train_file_name, test_file_name, result_file_name)