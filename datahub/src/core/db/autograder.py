#!/usr/bin/env python
# encoding: utf-8

import pandas as pd
import json
import argparse
import os
from sklearn.metrics import accuracy_score

answer_file = "/home/ubuntu/workspace/data_set_public/titanic_answer.csv"
board_file = "/home/ubuntu/workspace/data_set_public/titanic_leader_board.csv"

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--commit", help="commit id number of project", default="7232ad5db8b70f53f528bc4b1c3304433ad67041", type=str)
    parser.add_argument("--repo", help="repo name of project", default="tutorial", type=str)
    parser.add_argument("--clear", help="clear leader board or not (Y/N)", default="N", type=str)
    parser.add_argument("--file", help="result file", default="result", type=str)
    parser.add_argument("--username", help="user name of result file", default="zjsxzy", type=str)
    args = parser.parse_args()
    return args

def clear_board():
    board = pd.read_csv(board_file)
    board.drop(board.index, inplace=True)
    board.to_csv(board_file, index=False)

def grade(args):
    answer = pd.read_csv(answer_file)
#    config_name = "/home/ubuntu/workspace/Push_exp/%s/%s/config"%(args.commit, args.repo)
    dirs = [d for d in os.listdir("/home/ubuntu/workspace/Push_exp/%s"%args.commit)]
    config_name = "/home/ubuntu/workspace/Push_exp/%s/%s/config"%(args.commit, dirs[0])
    with open(config_name, 'r') as f:
        dic = json.load(f)
    username = dic["username"]
    create_data = dic["creat_data"].keys()[0]
    pred = pd.read_csv("/home/ubuntu/workspace/data_set_public/public_data/%s_%s.csv"%(args.commit, create_data))
    acc = accuracy_score(pred["Predict"], answer["Survived"])

    board = pd.read_csv(board_file)
    board.loc[board.shape[0]] = [board.shape[0], username, args.commit, format(acc, '.2%')]
    board.index = board["Accuracy"].map(lambda x: float(x[:-1]))
    board.sort_index(inplace=True, ascending=False)
    board.drop_duplicates(subset=['Commit_ID'], inplace=True)
    board["Ranking"] = range(1, board.shape[0] + 1)
    board.to_csv(board_file, index=False)

def grade_result(file, username):
    if file.endswith(".csv"):
        pred = pd.read_csv(file)
        answer = pd.read_csv(answer_file)
        acc = accuracy_score(pred["Predict"], answer["Survived"])

        print(file)
        print(username)
        print(acc)

        board = pd.read_csv(board_file)
        board.loc[board.shape[0]] = [board.shape[0], username, "%s submited result"%(username), format(acc, '.2%')]
        board.index = board["Accuracy"].map(lambda x: float(x[:-1]))
        board.sort_index(inplace=True, ascending=False)
        board.drop_duplicates(subset=['Commit_ID'], inplace=True)
        board["Ranking"] = range(1, board.shape[0] + 1)
        board.to_csv(board_file, index=False)
    else:
        print("Result file must be a .csv file")

if __name__ == "__main__":
    "Start autograding!!!!!"
    args = get_args()
    if args.file != "result":
        grade_result(args.file, args.username)
    elif args.clear == "N":
        grade(args)
    else:
        clear_board()
