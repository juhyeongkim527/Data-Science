import pandas as pd
import argparse
# from scipy import stats
# import math
# import tqdm
from sklearn.metrics.pairwise import euclidean_distances

def range_query(point, eps, distance_matrix): # object_id를 저장하는 list를 return
    neighbors = set()
    for i in range(len(distance_matrix[point])): # 주석 친 아래 방법으로 하면 너무 느려서 미리 main() 함수에서 distance_matrix를 계산해서 argument로 넘김
        if(distance_matrix[point][i] <= eps):
            neighbors.add(i)
    return neighbors

    # 아래 방법으로 하려면 argument에 db가 필요
    # center = [point.iloc[1], point.iloc[2]]
    # neighbors = set()
    # for p in range(len(db)):
    #     if(db.loc[p, 'label'] != 'undefined' and db.loc[p, 'label'] != 'noise'):
    #         continue
    #     candidate = [db.iloc[p, 1], db.iloc[p, 2]]
    #     distance = math.sqrt(math.pow(center[0] - candidate[0], 2) + math.pow(center[1] - candidate[1], 2))
    #     # distance, _ = stats.kendalltau(center, candidate)
    #     if(distance <= eps):
    #         neighbors.add(db.iloc[p, 0])
    # return neighbors

def DBSCAN(db, eps, minPts, distance_matrix):
    label = -1
    
    for p in range(len(db)):        
        neighbors = set()
        seed_set = set()

        if(db.loc[p, 'label'] != 'undefined'):    # 이미 label이 아래에서 설정된 point의 경우 continue
            continue
        
        neighbors = range_query(p, eps, distance_matrix)

        if(len(neighbors) <  minPts):
            db.loc[p, 'label'] = 'noise'
            continue
        
        label += 1
        db.loc[p, 'label'] = label
        seed_set = neighbors
        seed_set.remove(p)
        
        while(len(seed_set) > 0):
            q = seed_set.pop()
            if(db.loc[q, 'label'] == 'noise'):
                db.loc[q, 'label'] = label
            
            if(db.loc[q, 'label'] != 'undefined'):
                continue

            db.loc[q, 'label'] = label
            neighbors = range_query(q, eps, distance_matrix)
            if(len(neighbors) < minPts):
                continue
            seed_set = seed_set.union(neighbors)

def main(input_file_path, n, eps, minPts):
    db = pd.read_csv(input_file_path, delimiter = '\t', header = None)
    db['label'] = 'undefined'
    
    coordinates = db.iloc[:, 1:3]
    distance_matrix = euclidean_distances(coordinates, coordinates)
    
    DBSCAN(db, eps, minPts, distance_matrix)

    db = db.drop(db[db['label'] == 'noise'].index)   # label이 noise인 points 제거
    clusters = db.groupby('label')
    
    # for cluster in clusters:
    #     cluster[1].iloc[:, 0].to_csv(f'input{input_file_path[5]}_cluster_{cluster[0]}.txt',  sep = '\n', index = False, header = None)
    
    # cluster의 사이즈가 큰 순서대로 n개만 출력하기 위해
    sorted_label_by_sizes = clusters.size().sort_values(ascending = False) 
    
    for i in range(n):
        for cluster in clusters:
            if(sorted_label_by_sizes.index[i] == cluster[1].iloc[0, -1]):
                cluster[1].iloc[:, 0].to_csv(f'input{input_file_path[-5]}_cluster_{i}.txt',  sep = '\n', index = False, header = None)
                continue
                

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file_path", type = str)
    parser.add_argument("n", type = int)
    parser.add_argument("eps", type = int)
    parser.add_argument("minPts", type = int)
    args = parser.parse_args()
    input_file_path = args.input_file_path
    n = args.n
    eps = args.eps
    minPts = args.minPts
    main(input_file_path, n, eps, minPts)