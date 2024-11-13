import requests
from bs4 import BeautifulSoup as bs
import time
import sqlite3
cookies={'JSESSIONID':'80A16646208F195A352D619CF18DBDA6'}
sleeptime=0

def self_inspection():
    conn = sqlite3.connect('testing.db')
    testing = conn.cursor()
    try:
        testing.execute('''
            CREATE TABLE testing
        (   Question   TEXT    NOT NULL,
            a1         TEXT    NOT NULL,
            a2         TEXT            ,
            a3         TEXT            ,
            a4         TEXT             );
                                         ''')
        conn.commit()
        conn.close()
    except:
        conn.commit()
        conn.close()

def re(s,n):
    import re
    if n==0:
        return re.sub(r'\D', "",s)
    if n==1:
        return re.sub(r"\s", "", s)

def 考试选择():
    url='https://eol.qztc.edu.cn/meol/welcomepage/student/course_list_v8.jsp'
    r=requests.get(url,cookies=cookies)
    soup=bs(r.text,'lxml')
    #print(soup)
    # try:
    list_clearfix=soup.find(class_="list clearfix").find_all('li')
    title,curriculum=[],[]
    chioes=0
    for content in list_clearfix:
        #title=content.find(class_="link").a["onclick"]
        content_t=re(content.find(class_="link").a["onclick"],0)
        content_c=re(content.find(class_="title").a.text,1)
        title.append(content_t)
        curriculum.append(content_c)
        print(chioes,content_c,content_t)
        chioes=chioes+1
    chioes=int(input("选择课程"))
    # chioes=0
    title=title[chioes]
    url="https://eol.qztc.edu.cn/meol/dwr/call/plaincall/__System.generateId.dwr"
    data={
        'callCount' : 1,
        'c0-scriptName' : '__System',
        'c0-methodName' : 'generateId',
        'c0-id': '0',
        'batchId' : '0',
        'instanceId' : '0',
        'page':f'%2Fmeol%2Fjpk%2Fcourse%2Flayout%2Fnewpage%2Findex.jsp%3FcourseId%3D{title}',
        'scriptSessionId':'',
        'windowName' : 'manage_course'
    }
    r =requests.post(url,cookies=cookies,data=data)
    begin=len(r.text)-r.text[::-1].find('","')
    end=r.text.find('");\n})();')
    cookies["DWRSESSIONID"]=r.text[begin:end]
    url=f"https://eol.qztc.edu.cn/meol/common/question/test/student/list.jsp?tagbug=client&cateId={title}&status=1&strStyle=new06"
    r=requests.get(url,cookies=cookies)
    exam_ch=bs(r.text,'lxml')
    examid=[]
    chioes = 0
    for i in exam_ch.find(class_="wrap").find_all('tr')[1:-3]:
        # print(i)
        l=i.find_all("td")
        # print(l)
        # print(l[5])
        try:
            examid.append(l[5].span['id'][8:])
            print(chioes,re(l[0].text,1),examid[-1])
            chioes = chioes + 1
        except:
            print('*ERROR*',re(l[0].text,1),'（课程无法获取，请勿选择）')
    chioes=int(input("选择课程"))
    # chioes = 4
    examid = examid[chioes]
    return title,examid
    # except:
    #     print('登陆失败')
    #     sys.exit()

def 试卷(examid):
    #开始考试
    url=f"https://eol.qztc.edu.cn//meol/test/testExplain.do?testId={examid}"
    r=requests.get(url,cookies=cookies)
    url=f"https://eol.qztc.edu.cn/meol/common/question/test/student/stu_qtest_pre.jsp?testId={examid}"
    r=requests.get(url,cookies=cookies)
    #获取题目列表
    url=f"https://eol.qztc.edu.cn/meol/common/question/test/student/stu_qtest_main.jsp?testId={examid}"
    test=requests.get(url,cookies=cookies)
    soup=bs(test.text,'lxml')
    #print(soup)
    answerId=soup.find(class_="content").table.input['value']
    for white in soup.find_all(class_="white"):
        Questionid=re(white.td.a['onclick'],0)
        url=f"https://eol.qztc.edu.cn/meol/common/question/test/student/stu_qtest_question.jsp?testId={examid}"
        data={
            'currentSubmitQuestionid': Questionid,
            'actionType': 'saveAnswer',
            'testId':examid,
            'eqId': Questionid,
            'nextquestion': 'named',}
        time.sleep(1)
        r=requests.post(url,cookies=cookies,data=data)
        r=bs(r.text,'lxml')
        title=r.find(class_="testcontent").find("input")['value']
        name=r.find(class_="testcontent").find("input")['name']
        content=[]
        for i in r.find_all(class_="optionContent"):
            l=i.find_all("td")
            content.append([l[0].input['value'],re(l[1].text,1)])
        answer=回答(title,content)
        # time.sleep(8)
        #提交答案
        url=f"https://eol.qztc.edu.cn/meol/common/question/test/student/stu_qtest_question.jsp?testId={examid}"
        data=f'&currentSubmitQuestionid={Questionid}&actionType=saveAnswer&testId={examid}&eqId=&nextquestion=next'
        for xuanxiang in answer:
            data+=f'&answer={xuanxiang}'
        time.sleep(4)
        url+=data
        # url=f"http://eol.qztc.edu.cn/meol/common/question/test/student/stu_qtest_question.jsp?testId={examid}"
        # data=f'{"{"}"currentSubmitQuestionid":"{Questionid}","actionType":"saveAnswer","testId":"{examid}","eqId":"","nextquestion":"next"'
        # for xuanxiang in answer:
        #     data+=f',"answer":"{xuanxiang}"'
        # data+="}"
        # data=eval(data)
        # print(data)
        time.sleep(sleeptime)
        r=requests.post(url,cookies=cookies,data=data)
        if "请不要过于频繁答题！"in r.text:
            print("laji")
            time.sleep(3)
        url=f"https://eol.qztc.edu.cn/meol/common/ueditor/content.html?name={re(name,0)}"
        r=requests.post(url,cookies=cookies)
    #交卷
    url=f"https://eol.qztc.edu.cn/meol/test/stuLeakSubmitQuestion.do?answerId={answerId}"
    r=requests.post(url,cookies=cookies,data={'answerId':answerId})
    url=f"https://eol.qztc.edu.cn/meol/common/question/test/student/stu_qtest_submit.jsp?testId={examid}"
    requests.get(url,cookies=cookies)
    print(r.text,answerId)

def 回答(title,content):
    print(title,content)
    conn = sqlite3.connect('testing.db')   	
    cursor = conn.cursor()
    q_sql = "select * from testing where Question=?"
    values = cursor.execute(q_sql,[title])
    answer=[]
    for i in values:
        for j in i[1:]:
            for a in content:
                if j==a[1]:
                    answer.append(a[0])
        print('已存在')
        break
    else:
        print('空')
        answer=[content[0][0]]
    return answer

def 写入题目(title,answer):
    print(title,answer)
    conn = sqlite3.connect('testing.db')   	
    # print("打开数据库成功。")
    cursor = conn.cursor()
    q_sql = "select * from testing where Question=?"
    values = cursor.execute(q_sql,[title])
    flage = 1
    for j in values:
        print("ed")
        if j[0]!= '':
            flage = 0
    if flage == 1:
        a_sql = "INSERT OR IGNORE INTO testing(Question,a1,a2,a3,a4) VALUES(?,?,?,?,?)"
        Question,a1,a2,a3,a4 = title,None,None,None,None
        numb = 1
        for i in answer:
            if numb == 1:
                a1 = i
            if numb == 2:
                a2 = i
            if numb == 3:
                a3 = i
            if numb == 4:
                a4 = i
            numb += 1
        data = (Question,a1,a2,a3,a4)
        cursor.execute(a_sql,data)
        # sql = '''insert into testing(Question) values(?)'''
        # cursor.execute(sql,[title])
        print("插入数据成功。")
        conn.commit()
        cursor.close()    
        conn.close()
    # print(2)

def 获取答案(examid):
    url=f"http://eol.qztc.edu.cn/meol/common/question/test/student/stu_qtest_more_result.jsp?testId={examid}"
    soup=requests.get(url,cookies=cookies)
    soup=bs(soup.text,'lxml')
    url='http://eol.qztc.edu.cn/'+soup.find(class_="valuelist").find_all("tr")[-1].find(class_="view")['href']
    soup=requests.get(url,cookies=cookies)
    soup=bs(soup.text,'lxml')
    for question in soup.find_all(class_="test_checkq_question_qBody"):
        answer =[]
        title=question.find(class_="title").input['value']
        for i in question.find_all(text = '（答案）'):
            answer.append(i.parent.parent.span.text)
        写入题目(title, answer)

def 登录(账号,密码):
    url="https://eol.qztc.edu.cn/meol/loginCheck.do"
    data={
        'logintoken':int(time.time()*1000),
        'IPT_LOGINUSERNAME':账号,
        'IPT_LOGINPASSWORD':密码
    }
    r=requests.post(url,data=data,allow_redirects=False)
    # print(r.text)
    cookies['JSESSIONID'] = requests.utils.dict_from_cookiejar(r.cookies)['JSESSIONID']

def main():
    global sleeptime
    账号=input('账号：')
    密码=input('密码：')
    sleeptime=float(input('(s)每题时间4+：'))
    self_inspection()
    登录(账号,密码)
    title,examid=考试选择()
    n = int(input("请输入循环次数："))
    for i in range(n):
        试卷(examid)
        获取答案(examid)
        print(i+1)
    requests.get("http://eol.qztc.edu.cn/meol/homepage/V8/include/logout.jsp",cookies=cookies)#登出

if __name__ == '__main__':
   main()