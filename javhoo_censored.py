#!/usr/bin/python
# -*- coding: UTF-8 -*-
from bs4 import BeautifulSoup
import re
import json
import sqlite3
jcensored_dict ={
'html_path':'/home/curie/javhoo/javhoo/javhoo_censored_4436.html',
'sqlite3db_path':'/home/curie/censored.db'
}
# javhoo_censored_4436.html文件过大，内存放不下，需要拆分
# wc -l javhoo_censored_4436.html 为13308，13308/3=4436行，拆成三个文件
# 利用shell脚本对大文件进行分割 https://blog.csdn.net/suwei19870312/article/details/7352143
# $ split -l 4436 javhoo_censored_4436.html
#　分割得到xaa xab xac三个文件
split_a_jcensored_dict ={'html_path':'/home/curie/javhoo/censored/xaa','sqlite3db_path':'/home/curie/javhooDB.db'}
split_b_jcensored_dict ={'html_path':'/home/curie/javhoo/censored/xab','sqlite3db_path':'/home/curie/javhooDB.db'}
split_c_jcensored_dict ={'html_path':'/home/curie/javhoo/censored/xac','sqlite3db_path':'/home/curie/javhooDB.db'}
class JavHoo_Uncensored():
    censored_total = 0
    process_num_at_a_time = 1
    def __init__(self,jdict):
        self.htmlpath = jdict['html_path']
        self.dbpath = jdict['sqlite3db_path']
        self.censored_total = 0
        self.process_num_at_a_time = 30
    def get_soup(self):
        avhtml = open(self.htmlpath,'r',encoding='utf-8')
        avsoup = BeautifulSoup(avhtml.read(),'lxml')
        return avsoup
    def process_all(self):
        avsoup = self.get_soup()
        wdivs = avsoup.find_all("div",class_="wf-cell iso-item")
        self.censored_total = len(wdivs)
        self.quick_save_to_sqlite3(wdivs)
        # for w in wdivs:
        #     article = w.article
        #     self.process(article)
        return
    def quick_save_to_sqlite3(self,wdivs):
        i = 0
        av_index = 0
        reach_total = False
        conn = sqlite3.connect(self.dbpath)
        cursor = conn.cursor()
        while i < int(self.censored_total/self.process_num_at_a_time)+1:
            sql_insert = '''
            INSERT INTO
                censored(id,
                    cfanhao,ctitle,cimgurl,cdate)
            VALUES (null,?,?,?,?);
            '''
            data = []
            j = 0
            while j < min(self.process_num_at_a_time,self.censored_total):
                w = wdivs[av_index]
                info_dict = self.get_infodict(w.article)
                data.append(tuple(info_dict.values()))
                av_index += 1
                j = j+1
                if(av_index>=self.censored_total):
                    reach_total = True
                    break
            i = i+1
    # https://stackoverflow.com/questions/15513854/       sqlite3-warning-you-can-only-execute-one-statement-at-a-time
            sql_insert = sql_insert[:-1]
            try:
                cursor.executemany(sql_insert,data)
                # conn.commit()
                print(av_index)
            except BaseException as e:
                conn.rollback()
                print('except...', e)
            if(reach_total):
                conn.commit()
                conn.close()
                print("End.")
                return
        pass
    def process(self,article):
        info_dict = self.get_infodict(article)
        print(info_dict)
        # print(article)
        return
    def get_infodict(self,article):
        infodict = {
            'cfanhao': self.get_cfanhao(article),
            'ctitle': self.get_ctitle(article),
            'cimgurl': self.get_uImgurl(article),
            'cdate': self.get_cdate(article),
        }
        return infodict
    def get_cfanhao(self,article):
        return article.a['href'].replace('https://www.javhoo.com/av/','')
    def get_ctitle(self,article):
        return article.a.get('title')
    def get_uImgurl(self,article):
        # return article.select('img[class="iso-lazy-load preload-me"]')[0]['data-src']
        result_list = article.select('img[class="iso-lazy-load preload-me"]')
        return ((result_list[0]['data-src']) if(result_list) else None)
    def get_cdate(self,article):
        return article.find("div",{"class":"entry-meta portfolio-categories"}).date.text
    def create_table(self):
        sql_creat = '''
        create table censored(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cfanhao text,ctitle text,
        cimgurl text,
        cdate text
        );
        '''
        try:
            conn = sqlite3.connect(self.dbpath)
            cursor = conn.cursor()
            cursor.execute(sql_creat)
            conn.commit()
            conn.close()
        except BaseException as e:
            conn.rollback()
            print('except...', e)
        pass
    def drop_table(self):
        sql_drop = '''
        drop table if exists censored;
        '''
        try:
            conn = sqlite3.connect(self.dbpath)
            cursor = conn.cursor()
            cursor.execute(sql_drop)
            conn.commit()
            conn.close()
        except BaseException as e:
            conn.rollback()
            print('except...', e)
        pass
    def slow_save_to_sqlite3(self,dict_data):
        sql_insert = '''
        INSERT INTO
            censored(id,
                cfanhao,ctitle,cimgurl,cdate)
        VALUES (null,?,?,?,?);
        '''
        try:
            conn = sqlite3.connect(self.dbpath)
            cursor = conn.cursor()
            self.insert(cursor,sql_insert,dict_data)
            conn.commit()
            conn.close()
        except BaseException as e:
            conn.rollback()
            print('except...', e)
        pass
    def insert(self,cursor,sql_insert,dict_data):
        cursor.execute(sql_insert,tuple(dict_data.values()))
        pass
def process_split(jcensored_dict,is_drop,is_creat):
    print("Reading ",jcensored_dict['html_path'],"...")
    censored  =  JavHoo_Uncensored(jcensored_dict)
    if(is_drop):
        censored.drop_table()
    if(is_creat):
        censored.create_table()
    censored.process_all()
    print("see ",jcensored_dict['sqlite3db_path'])
    return    
if __name__ == '__main__':
    # print("Reading ",jcensored_dict['html_path'],"...")
    # censored  =  JavHoo_Uncensored(jcensored_dict)
    # censored.drop_table()
    # censored.create_table()
    # censored.process_all()
    # print("see ",jcensored_dict['sqlite3db_path'])
    # 内容过多，切分处理
    process_split(split_a_jcensored_dict,True,True)
    process_split(split_b_jcensored_dict,False,False)
    process_split(split_c_jcensored_dict,False,False)

