#!/usr/bin/python
# -*- coding: UTF-8 -*-
from bs4 import BeautifulSoup
import re
import json
import sqlite3
# curl https://www.javhoo.com/actresses/page/[1-212] > javhoo_actresses_212pages.html
jactress_dict ={
'html_path':'/home/curie/javhoo/javhoo/javhoo_actresses_212pages.html',
'sqlite3db_path':'/home/curie/javhooDB.db'
}
class JavHoo_Actress():
    def __init__(self,jdict):
        self.htmlpath = jdict['html_path']
        self.dbpath = jdict['sqlite3db_path']
    def get_actressName(self,article):
        return article.a['href'].replace('/star/','')
    def get_actressImgurl(self,article):
        # return article.select('img[class="iso-lazy-load preload-me"]')[0]['data-src']
        result_list = article.select('img[class="iso-lazy-load preload-me"]')
        return ((result_list[0]['data-src']) if(result_list) else None)
    def get_soup(self):
        avhtml = open(self.htmlpath,'r',encoding='utf-8')
        avsoup = BeautifulSoup(avhtml.read(),'lxml')
        return avsoup
    def process(self,article):
        info_dict = self.get_infodict(article)
        print(info_dict)
        self.save_to_sqlite3(info_dict)
        return
    def process_all(self):
        avsoup = self.get_soup()
        wdivs = avsoup.find_all("div",class_="wf-cell iso-item")
        for w in wdivs:
            article = w.article
            self.process(article)
        return
    def pfind(self,article,pstr):
        tcontent = article.select('div[class="testimonial-content"]')[0]   
        result_list = re.compile(r"<p>"+ str(pstr) +":(?P<tagName>.+?)</p>").findall(str(tcontent))
        return (result_list[0] if(result_list) else None)
        # return (result_list[0] if(result_list) else '')
    def get_infodict(self,article):
        infodict = {
            'name': self.get_actressName(article),
            'imgurl': self.get_actressImgurl(article),
            'birthday': self.pfind(article,"生日"),
            'height':self.pfind(article,"身高"),
            'cup_size':self.pfind(article,"罩杯"),
            'bust':self.pfind(article,"胸圍"),
            'waist':self.pfind(article,"腰圍"),
            'hips':self.pfind(article,"臀圍"),
            'birthplace':self.pfind(article,"出生地"),
            'hobby':self.pfind(article,"愛好")    
        }
        return infodict
    def save_to_sqlite3(self,dict_data):
        sql_insert = '''
        INSERT INTO
            actress(id,
                name,imgurl,birthday,height,cup_size,
                bust,waist,hips,birthplace,hobby)
        VALUES (null,?,?,?,?,?,?,?,?,?,?);
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
    def create_table(self):
        sql_creat = '''
        create table actress(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name text,imgurl text,
        birthday text,height text,cup_size text,
        bust text,waist text,hips text,
        birthplace text,hobby text
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
        drop table actress;
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

if __name__ == '__main__':
    actress = JavHoo_Actress(jactress_dict)
    actress.drop_table()
    actress.create_table()
    actress.process_all()




