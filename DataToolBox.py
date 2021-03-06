import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

#minmax normalization
def minmax_norm(X):
    return (X-np.min(X))/(np.max(X)-np.min(X))

#z-score normalization
def zscore_norm(X):
    return (X-np.mean(X))/np.std(X)

#计算acc
def get_acc(real_label,predict_label):
    return len(np.nonzero(real_label-predict_label==0)[0])/len(real_label)

#计算auc
def get_auc(real_label, scores):
    return roc_auc_score(real_label, scores)

#计算macc，返回tp,tn,macc
def get_macc(real_label, predict_label):
    n1 = len(np.nonzero(real_label == 1)[0])
    n2 = len(np.nonzero(real_label == 0)[0])
    tp_temp = sum(predict_label[np.nonzero(real_label == 1)[0]] == 1)
    tn_temp = sum(predict_label[np.nonzero(real_label == 0)[0]] == 0)
    tp = tp_temp / n1
    tn = tn_temp / n2
    m_acc = (tp + tn) / 2
    return tp,tn,m_acc

#计算f1score
#默认少数类为1
def f1score(real_label, predict_label,min_label=1):
    n1 = len(np.nonzero(real_label == min_label)[0])
    tp_temp = sum(predict_label[np.nonzero(real_label == min_label)[0]] == min_label)
    recall=tp_temp/n1
    precision=tp_temp/len(np.nonzero(predict_label==min_label)[0])
    return 2*(recall*precision)/(recall+precision)

# 二分类，返回[多数类，少数类，多数类类标，少数类类标] 可返回index
def divide_data(data, label,return_index=False):
    labels=	np.unique(label)
    n1 = len(np.nonzero(label == labels[0])[0])
    n2 = len(np.nonzero(label == labels[1])[0])
    # 判断少数类的类标号
    if n1 > n2:
        less_label = labels[1]
        much_label = labels[0]
    else:
        less_label = labels[0]
        much_label = labels[1]
    if return_index:
        data_much_index = np.nonzero(label != less_label)[0]
        data_less_index = np.nonzero(label == less_label)[0]
        return data_much_index, data_less_index, much_label, less_label

    # 分离多数类和少数类
    data_much = data[np.nonzero(label!=less_label)[0],:]
    data_less = data[np.nonzero(label==less_label)[0],:]
    return data_much,data_less,much_label,less_label

# 随机下采样Random UnderSampling
def RUS(data_much, data_less, much_label, less_label):
    less_num = data_less.shape[0]
    much_num = data_much.shape[0]
    # 保留所有少数类
    train_data_temp = data_less
    train_label_temp=np.ones((1,less_num))*less_label
    # 多数类随机下采样
    index=np.arange(much_num)
    np.random.shuffle(index)
    train_data_temp=np.vstack((train_data_temp,data_much[index[0:less_num],:]))
    train_label_temp=np.hstack((train_label_temp,np.ones((1,less_num))*much_label))

    return train_data_temp,train_label_temp

# 随机上采样Random OverSampling
def ROS(data_much, data_less, much_label, less_label):
    less_num = data_less.shape[0]
    much_num = data_much.shape[0]
    # 保留所有多数类
    train_data_temp = data_much
    train_label_temp=np.ones((1,much_num))*much_label
    # 少数类有放回复制
    index=np.array(pd.DataFrame.sample(pd.DataFrame(np.arange(less_num)),replace=True,n=much_num)).T[0]
    train_data_temp=np.vstack((train_data_temp,data_less[index,:]))
    train_label_temp=np.hstack((train_label_temp,np.ones((1,much_num))*less_label))

    return train_data_temp,train_label_temp

#PAC-Bayes bund
#2分类
def PAC_Bayes(real_label,pred,rou=0.05):
    m = pred.shape[0]
    KL = pred
    KL[:, 0] = -1 * (1 - real_label) * np.log(KL[:, 0] + 0.00001)
    KL[:, 1] = -1 * real_label * np.log(KL[:, 1] + 0.00001)
    pac = (np.sum(KL) + np.log((m + 1) / rou)) / m
    return pac

def cross_entropy_loss(real_label,pred):
    KL = pred
    KL[:, 0] = -1 * (1 - real_label) * np.log(KL[:, 0] + 0.00001)
    KL[:, 1] = -1 * real_label * np.log(KL[:, 1] + 0.00001)
    return np.sum(KL)/KL.shape[0]