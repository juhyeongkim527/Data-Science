import pandas as pd
from itertools import combinations
import argparse

db = []
min_sup = 0
frequent_pattern = []
support_for_frequent_pattern = []
support_for_association_rule = []
confidence_for_association_rule = []

def scan_db_and_generate_L1(input_file_path : str, _min_sup: float):
    global db
    global min_sup
    global frequent_pattern
    global support_for_frequent_pattern

    # scan database(input file)
    with open(input_file_path, 'r') as f:
        for line in f:
            trans = [int(item) for item in line.strip().split()] # strip()은 '\n'만 제거한 string return, split()은 모든 공백 제거하여 list로 변경
            db.append(trans)

    # print('\n' + 'number of trans in db : ' + str(len(db)) + '\n')
    
    min_sup = len(db) * _min_sup / 100

    # print('min_sup : ' + str(_min_sup) + ' % (' + str(min_sup) +')' + '\n')

    # find item's range
    min_item = db[0][0]
    max_item = db[0][0]

    # find min_item and max_item to count 1-item_set
    for trans in db:
        for item in trans:
            if(min_item > item):
                min_item = item
            if(max_item < item):
                max_item = item
    
    # count 1-item_set
    count_1_item_set = [0 for i in range(max_item-min_item+1)]
    for trans in db:
        for item in trans:
            count_1_item_set[item-min_item] += 1

    # find L1
    L1 = []
    for index in range(len(count_1_item_set)):
        if(count_1_item_set[index] >= min_sup):
            # put list in list to union in generate_canididate
            itemset = [index + min_item]
            L1.append(itemset)
            frequent_pattern.append(set(itemset))
            # find support for each frequent-pattern
            support_for_frequent_pattern.append(count_1_item_set[index] / len(db) * 100)

    return L1

def genareate_candidate(L : list, k : int):
    # generate candidate(Ck+1)
    C = []
    for index in range(len(L)):
        for next_index in range(index+1, len(L)):
            # Step 1 : self-joining
            item_set = set(sorted(L[index]) + sorted(L[next_index]))
            if(len(item_set) == k+1 and item_set not in C):
                # Step 2 : pruning before candidate generation
                if(all(item in _itemset for item in item_set) for _itemset in L):
                    C.append(item_set)

    return C

def count_candidate_in_db(C : list):
    global db
    # count candidate
    # one-to-one correspond count_candidate's index with C(candidate)'s index
    count_candidate  = [0 for i in range(len(C))]
    for trans in db:
         for index in range(len(count_candidate)):
            if set(C[index]).issubset(set(trans)):
                count_candidate[index] += 1
    
    return count_candidate

def generate_L(C : list, count_candidate : list):
    # generate Lk+1
    global db
    global min_sup
    global frequent_pattern
    global support_for_frequent_pattern

    # Test the candidate against db
    L = []
    for index in range(len(count_candidate)):
        if(count_candidate[index] >= min_sup):
            # find support
            support_for_frequent_pattern.append(count_candidate[index] / len(db) * 100)
            # add Lk+1 to frequent-pattern 
            L.append(C[index])
            frequent_pattern.append(set(sorted(C[index])))

    return L

def generate_association_rules():
    # generate association rules
    global frequent_pattern
    global support_for_frequent_pattern
    global support_for_association_rule
    global confidence_for_association_rule

    # to duplicate support at same frequent-pattern
    support_index = 0;
    association_rules = []
    for item_set in frequent_pattern: 
        if(len(item_set) > 1):
            for r in range(1, len(item_set)):
                _combinations = list(combinations(item_set, r))
                for combinations_item_set in _combinations:
                    # find {item_set} and {associative_item_set} that are shown output.txt
                    subset = []

                    _item_set = list(combinations_item_set)
                    subset.append(_item_set)

                    _associative_item_set = list(set(item_set) - set(combinations_item_set))
                    subset.append(_associative_item_set)

                    association_rules.append(subset)
                    
                    # find support
                    support_for_association_rule.append("{:.2f}".format(support_for_frequent_pattern[support_index]))
                    
                    # find confidence
                    support_for_item_set = support_for_frequent_pattern[frequent_pattern.index(set(subset[0]))]
                    support_for_associative_set = support_for_frequent_pattern[frequent_pattern.index(set(subset[0]) | set(subset[1]))]
                    confidence = (support_for_associative_set / support_for_item_set * 100)
                    confidence_for_association_rule.append("{:.2f}".format(confidence))

        support_index += 1

    return association_rules

def main(_min_sup : float, input_file_path : str, ouput_file_path : str):
    # L == L1
    L = scan_db_and_generate_L1(_min_sup = _min_sup, input_file_path = input_file_path)
    
    k = 1
    while True:
        if(L):
            C = genareate_candidate(L = L, k = k)
            count_candidate = count_candidate_in_db(C)
            L = generate_L(C = C, count_candidate = count_candidate)
            k += 1
        else: # L == NULL
            break     

    association_rules = generate_association_rules()
    
    # make DataFrame from pandas
    data = {
        'item_set': [set(association_rules[i][0]) for i in range(len(association_rules))],
        'associative_item_set': [set(association_rules[i][1]) for i in range(len(association_rules))],
        'support(%)' : support_for_association_rule,
        'confidence(%)' : confidence_for_association_rule,
    }
    df = pd.DataFrame(data)
    # print(df)
    df.to_csv(ouput_file_path, sep = '\t', index = False, header=False)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("min_sup", type = float)
    parser.add_argument("input_file_path", type = str)
    parser.add_argument("output_file_path", type = str)
    args = parser.parse_args()
    main(_min_sup = args.min_sup, input_file_path = args.input_file_path, ouput_file_path = args.output_file_path)