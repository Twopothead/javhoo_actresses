#!/usr/bin/python
# -*- coding: UTF-8 -*-
from bs4 import BeautifulSoup
import re
import json
import sqlite3
jvr_dict ={
'html_path':'/home/curie/0py/sample_vr.html',
'sqlite3db_path':'/home/curie/vr.db'
}
class JavHoo_Uncensored():
    vr_total = 0
    process_num_at_a_time = 1
    def __init__(self,jdict):
        self.htmlpath = jdict['html_path']
        self.dbpath = jdict['sqlite3db_path']
        self.vr_total = 0
        self.process_num_at_a_time = 30
    def get_soup(self):
        avhtml = open(self.htmlpath,'r',encoding='utf-8')
        avsoup = BeautifulSoup(avhtml.read(),'lxml')
        return avsoup
    def process_all(self):
        avsoup = self.get_soup()
        wdivs = avsoup.find_all("div",class_="wf-cell iso-item")
        self.vr_total = len(wdivs)
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
        while i < int(self.vr_total/self.process_num_at_a_time)+1:
            sql_insert = '''
            INSERT INTO
                vr(id,
                    vfanhao,vtitle,vimgurl,vdate)
            VALUES (null,?,?,?,?);
            '''
            data = []
            j = 0
            while j < min(self.process_num_at_a_time,self.vr_total):
                w = wdivs[av_index]
                info_dict = self.get_infodict(w.article)
                data.append(tuple(info_dict.values()))
                av_index += 1
                j = j+1
                if(av_index>=self.vr_total):
                    reach_total = True
                    break
            i = i+1
    # https://stackoverflow.com/questions/15513854/       sqlite3-warning-you-can-only-execute-one-statement-at-a-time
            sql_insert = sql_insert[:-1]
            try:
                cursor.executemany(sql_insert,data)
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
            'vfanhao': self.get_vfanhao(article),
            'vtitle': self.get_vtitle(article),
            'vimgurl': self.get_uImgurl(article),
            'vdate': self.get_vdate(article),
        }
        return infodict
    def get_vfanhao(self,article):
        return article.a['href'].replace('https://www.javhoo.com/av/','')
    def get_vtitle(self,article):
        return article.a['title']
    def get_uImgurl(self,article):
        # return article.select('img[class="iso-lazy-load preload-me"]')[0]['data-src']
        result_list = article.select('img[class="iso-lazy-load preload-me"]')
        return ((result_list[0]['data-src']) if(result_list) else None)
    def get_vdate(self,article):
        return article.find("div",{"class":"entry-meta portfolio-categories"}).date.text
    def create_table(self):
        sql_creat = '''
        create table vr(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vfanhao text,vtitle text,
        vimgurl text,
        vdate text
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
        drop table vr;
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
            vr(id,
                vfanhao,vtitle,vimgurl,vdate)
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
if __name__ == '__main__':
    print("Reading ",jvr_dict['html_path'],"...")
    vr  =  JavHoo_Uncensored(jvr_dict)
    vr.drop_table()
    vr.create_table()
    vr.process_all()
    print("see ",jvr_dict['sqlite3db_path'])
