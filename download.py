#!C://pytho25//python.exe
# -*- coding: gbk -*-
import re,os,sys,httplib,threading,urllib,wx
import global_var,GUItools
from HTMLParser import HTMLParser
from copy import deepcopy

#a class to setup http link to the server
class MyCon:  
    def __init__(self,host='learn.tsinghua.edu.cn'):
        self.conn=httplib.HTTPConnection(host,80)
        self.precookie=''
        self.thu=' '
        self.logstat=0
        
    def open(self,uri,body=None,method="GET"):
        self.conn.close()
        if(self.logstat==1):
            headers={'Cookie':self.precookie+self.thu}
        else:
            headers={}
        if method=="POST":
            headers['Content-Type']="application/x-www-form-urlencoded"
        else:
            pass
        self.conn.request(method,uri,body,headers)
        r=self.conn.getresponse()
        rescookie=r.getheader('set-cookie')
        if(self.logstat==0):
            try:
                JSESSIONID = re.findall(r'JSESSIONID=.*?;',rescookie)[0][11:-1]
                thuwebcookie=re.findall(r'THNSV2COOKIE=.*?;',rescookie)[0][13:-1]
                self.precookie+=('JSESSIONID=' + JSESSIONID + '; THNSV2COOKIE=' + thuwebcookie + '; ')
            except:
                global_var.statusBar.SetStatusText('�Բ����޷�Ϊ����½',1)
                print('�Բ����޷���½�������˳�\n')
                raise 'err'
                return
        try:
            THNSV2COOKIE=re.findall(r'THNSV2COOKIE=.*?;',rescookie)[0][13:-1]
            self.thu = ' THNSV2COOKIE=' + THNSV2COOKIE + ' '
        except:
            global_var.statusBar.SetStatusText('�޷����������ȷ��',1)
            print('�޷��������ȷ�ϣ��˳�\n')
            raise 'err'
        return r

    def login(self):
        params = urllib.urlencode({'userid': global_var.userid, 'userpass': global_var.userpass, 'submit1': '��¼'})
        #print 'Begin 1st open'
        #params = urllib.urlencode({'userid': 'haow09', 'userpass': 'haowei1987', 'submit1': '��¼'})
        self.open('/use_go.jsp',body=params,method="POST")
        self.logstat=1

    def logout(self):
        self.logstat=0
        self.precookie=''
        self.thu=''

#�������γ�url�Ϳγ�����ע�⣺list��ʽ:[['courseURL','coursename',[][]],...etc]
class parserCourse(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.state='none'
        self.list=[]
        self.course=[]

    def handle_starttag(self,tag,attrs):
        if tag=='a' and attrs[0][0]=='href' and '/lesson/student/course_locate.jsp?course_id=' in attrs[0][1]:
            self.course.append(attrs[0][1])
            self.state='ok'
            

    def handle_data(self,data):
        if(self.state=='ok'):
            coursename=re.findall(r'\s\S.*$',data)[0][1:]
            #ȥ�������ڵ���Ϣ
            coursename=coursename.split('(')[0]
            coursename =  coursename.decode('utf8')
            global_var.statusBar.SetStatusText(u"�������γ̣� "+coursename,1)
            print u"�������γ̣� "+coursename
            self.course.append(coursename)
            self.course.append([])
            self.course.append([])
            self.list.append(self.course)
            self.course=[]
            self.state='none'

#a class to parser course files' info and related URI
class parserFile(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.state='none'
        self.files=[]
        self.file={}

    def handle_starttag(self,tag,attrs):
        if(self.state=='none'):
            for i in attrs:
                if i[0]=='href' and ('/MultiLanguage/uploadFile/downloadFile_student.jsp' in i[1]):
                    url=i[1]
                    
                    self.file['file_url']=url
                    self.state='name'
                    return
        if(self.state=='name_c'):
            self.state='desc'
            return
        if(self.state=='desc_c'):
            self.state='size'
            return
        if(self.state=='size_c'):
            self.state='date'
            return
        if(self.state=='date_c'):
            self.state='none'
            return

    def handle_endtag(self,tag): 
        if(self.state=='name'):
            self.state='name_c'
            return
        if(self.state=='desc'):
            self.state='desc_c'
            return
        if(self.state=='size'):
            self.state='size_c'
            return
        if(self.state=='date'):
            self.files.append(self.file)
            self.file={}
            self.state='none'
            return

    def handle_data(self,data):
        if(self.state=='name'):
            self.file['file_name']=data.decode('utf8')
        if(self.state=='desc'):
            self.file['file_desc']=data.decode('utf8')
        if(self.state=='size'):
            self.file['file_size']=data.decode('utf8')
        if(self.state=='date'):
            self.file['file_date']=data.decode('utf8')
            


#a class to parser notelist
class parserNote(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.state='none'
        self.notes=[]
        self.note={}

    def handle_starttag(self,tag,attrs):
        if(self.state=='none'):
            for i in attrs:
                if i[0]=='href' and ('note_reply.jsp?bbs_type=' in i[1]):
                    url=i[1]
                    self.note['note_url']='/public/bbs/'+url
                    self.state='title'
                    return
        if(self.state=='title_c'):
            self.state='author'
            return
        if(self.state=='author_c'):
            self.state='date'
            return

    def handle_endtag(self,tag): 
        if(self.state=='title'):
            self.state='title_c'
            return
        if(self.state=='author'):
            self.state='author_c'
            return
        if(self.state=='date'):
            self.notes.append(self.note)
            self.note={}
            self.state='none'
            return

    def handle_data(self,data):
        if(self.state=='title'):
            self.note['note_title']=data
        if(self.state=='author'):
            self.note['note_author']=data
        if(self.state=='date'):
            self.note['note_date']=data
            

#getCourse������global_var.list��ʼ������������Ŀγ���Ϣ
#���棺�˺���Ӧ�ý����û���¼��Ӧ�ó����ʼ��ʱ����
#һ�����ã�global_var.list�н�ʧȥ�����ļ����������Ϣ!
def getCourse():
    global_var.app_stat='getcourse'
    global_var.statusBar.SetStatusText(u"....��ʼ��ѯ��Ŀγ��б�",1)
    print u"....��ʼ��ѯ��Ŀγ��б�"
    #�����ȶ�ȡ���б��е���Ϣ
    conn=global_var.conn
    conn.login()
    ff=conn.open('/MultiLanguage/lesson/student/MyCourse.jsp?language=cn')
    coursepage=ff.read()
    ff.close()

    pc=parserCourse()
    pc.feed(coursepage)
    list=pc.list
    global_var.list=list
    global_var.app_stat='refresh'
    global_var.statusBar.SetStatusText(u"��ʼ���ݿγ��б�ˢ�¿μ���Ϣ��",1)
    print u"....��ʼ���ݿγ��б�ˢ�¿μ���Ϣ��"
    

#�˺��������пγ���Ϣ������ˢ��global_var.list�еĿμ���Ϣ
def refreshFiles():
    global_var.app_stat='refreshfile'
    global_var.newfile=[]
    oldfile=[]
    global_var.prelist=deepcopy(global_var.list)
    list=global_var.list
    prelist=global_var.prelist
    conn=global_var.conn
    conn.login()
    pf=parserFile()
    #�洢���ļ�
    for course in prelist:
            for file in course[2]:
                oldfile.append(file['file_url'])
    #�򿪿γ����ؽ��棬�����ļ���ַ
    for course in list:
        global_var.log_num+=1
        if(global_var.log_num==2):
            global_var.t2=GUItools.MyThread(count,'name')
            global_var.t2.start()
        ff=conn.open('/MultiLanguage/lesson/student/download.jsp?course_id='+course[0][-5:])
        filepage=ff.read()
        ff.close()
        pf.__init__()
        pf.feed(filepage)
        course[2]=pf.files
    
    #���µ��ļ��������ļ��б���
    for courseindex in range(len(list)):
        course=list[courseindex]
        for fileindex in range(len(course[2])):
            file=course[2][fileindex]
            if not (file['file_url'] in oldfile):
                global_var.newfile.append((courseindex,fileindex))
    
    #ȷ��ÿ���ļ��ľ�����Ϣ(�ļ�����ʵ�ʴ�С)
    for course in list:
        print u"-"*60
        global_var.statusBar.SetStatusText(u"���ڽ���<<" + course[1]  + u">>�Ŀμ���Ϣ��",1)
        print u"....��ʼ���� " + course[1]  + u"�Ŀμ���Ϣ��"
        print u"-"*60
        for file in course[2]:
            data=conn.open(file['file_url'],method="HEAD")
            uu=data.getheader('content-disposition')
            file['file_realsize']=int(data.getheader('content-length'))
            data.read()
            data.close()
            raw_name=re.findall(r'=".*"',uu)[0][2:-1]
            raw_name = raw_name.decode('gbk')
            global_var.statusBar.SetStatusText(u"�����ļ� "+ raw_name +u'  ��С��'+str(file['file_realsize']),1)
            print u"  "+ raw_name +u'  ��С��'+str(file['file_realsize'])
            #��Ѱ�����
            #try:
            #    file_random=re.findall(r'\S+_(\d{7,9}).\w+$',raw_name)[0]
            #except:
            #    file_random = ''
            
            #if file_random:
            #    file['file_realname']=raw_name.replace('_'+file_random,'')
            #else:
            #    print '�޷�����������ţ�ʹ��ԭ�ļ������뱨���������'
            #    file['file_realname']=raw_name
            file['file_realname']=raw_name
    ShowNew()

#�˺��������пγ���Ϣ�Ļ�����ˢ�¹�����Ϣ
def refreshNotes():
    global_var.app_stat="refreshnote"
    global_var.prelist=deepcopy(global_var.list)
    prelist=global_var.prelist
    list=global_var.list
    conn=global_var.conn
    conn.login()
    oldnote=[]
    global_var.newnote={}
    pn=parserNote()
    
    for course in prelist:
        for note in course[3]:
            oldnote.append(note['note_url'])


    for courseindex in range(len(list)):
        #����Ϊ������Ϣ
        course=list[courseindex]
        data=conn.open('/public/bbs/getnoteid_student.jsp?course_id='+course[0][-5:],method="HEAD")
        uu=data.getheader('Location').replace('http://learn.tsinghua.edu.cn','')
        data.read()
        data.close()
        data=conn.open(uu)
        pn.__init__()
        pn.feed(data.read())
        course[3]=pn.notes
        data.close()
        #�����ַץȡ����
        CreateHtml(courseindex,oldnote)
    ShowNew()

#�˺���ˢ��ָ���γ̵��ļ��б�͹���
def RefreshCourse(courseindex):
    global_var.app_stat="refreshcourse"
    course=global_var.list[courseindex][:2]
    print u"���ڲ�ѯ"+global_var.list[courseindex][1]+u"�Ŀμ�"
    global_var.statusBar.SetStatusText(u"���ڲ�ѯ<<"+global_var.list[courseindex][1]+u">>�Ŀμ�",1)
    conn=global_var.conn
    ff=conn.open('MultiLanguage/lesson/student/download.jsp?course_id='+course[0][-5:])
    filepage=ff.read()
    ff.close()
    pf=parserFile()
    pn=parserNote()
    pf.__init__()
    pf.feed(filepage)
    files=pf.files
    course.append(files)
    data=conn.open('/public/bbs/getnoteid_student.jsp?course_id='+course[0][-5:],method="HEAD")
    uu=data.getheader('Location').replace('http://learn.tsinghua.edu.cn','')
    data.read()
    data.close()
    data=conn.open(uu)
    pn.__init__()
    pn.feed(data.read())
    course.append(pn.notes)
    data.close()
    for file in course[2]:
        data=conn.open(file['file_url'],method="HEAD")
        uu=data.getheader('content-disposition')
        file['file_realsize']=int(data.getheader('content-length'))
        data.read()
        data.close()
        raw_name=re.findall(r'=".*"',uu)[0][2:-1]
        #��Ѱ�����
        file_random=re.findall(r'\S+_(\d{7,9}).\w+$',raw_name)[0]
        if file_random:
            file['file_realname']=raw_name.replace('_'+file_random,'')
        else:
            print '�޷�����������ţ�ʹ��ԭ�ļ������뱨���������'
            file['file_realname']=raw_name   
    global_var.list[courseindex]=course
    global_var.statusBar.SetStatusText(u"<<"+global_var.list[courseindex][1]+u">>�Ŀμ���ѯ���",1)
    print u">>"+global_var.list[courseindex][1]+u"�Ŀμ���ѯ���"
    CreateHtml(courseindex)
    

#�˺�������ָ���γ̵Ĺ�����ҳ��������
def CreateHtml(courseindex,oldnote=[]):
    list=global_var.list
    global_var.statusBar.SetStatusText(u"���ڲ�ѯ<<" +list[courseindex][1]+u">>�Ŀγ̹���...",1)
    print u"���ڲ�ѯ " +list[courseindex][1]+u" �Ŀγ̹���..."
    conn=global_var.conn
    if not os.path.isdir(os.path.join(global_var.setting['download_path'],u'notes')):
        os.mkdir(os.path.join(global_var.setting['download_path'],u'notes'))
    
    
    f=open(os.path.join(global_var.setting['download_path'],u'notes',(list[courseindex][1]+u'.htm')),'w')
    pre='''
    <html>
    <head>
    <META http-equiv="Content-Type" content="text/html; charset=utf-8">
    <title>
    '''
    pre+=list[courseindex][1].encode('gbk')
    pre+='''
    </title>
    <link rel="stylesheet" href="style.css" type="text/css" media="screen">
    </head>
    <body>
    <div id="header"><a name="-1"><h1>
    '''
    pre+=list[courseindex][1].encode('gbk')+'�Ŀγ̹���'
    pre+='''
    </h1></a></div>
    <div id="list">
    <ul>
    '''
    for noteindex in range(len(list[courseindex][3])):
        note=list[courseindex][3][noteindex]
        pre+='''<li><a href="#'''+str(noteindex)+'''">'''+note['note_title']+'  ('+note['note_date']+')</a></li>\n'
    
    pre+='''</ul></div>\n<div id="content">\n'''
    for noteindex in range(len(list[courseindex][3])):
        note=list[courseindex][3][noteindex]
        data=conn.open(note['note_url'])
        uu=data.read()
        data.close()
        uu=uu.split('''colspan="3" >''')[1]
        uu=uu.split('<td colspan="4" align="center" class="textTD">')[0]
        uu=uu[:-43]
        if not(note['note_url'] in oldnote):
            global_var.newnote[(courseindex,noteindex)]=uu
        pre+='''<div class="textbox"><a name="'''+str(noteindex)+'''"></a><div class="title"><h3>'''
        pre+=note['note_title']
        pre+='''</h3><div class="label">'''+note['note_date']+'   '+note['note_author']+'''</div></div><div class="content">'''+uu
        pre+='''
        </div>
        <div class="go-top"><a href="#-1">Top</a>
        </div>
        </div><br>'''
    pre+="</div></body></html>"
    pre=pre.decode('gbk').encode('utf-8')
    f.write(pre)
    f.close()
    print u">>" +list[courseindex][1]+u" �Ŀγ̹����ѯ���"
    global_var.statusBar.SetStatusText(u"<<" +list[courseindex][1]+u">>�Ŀγ̹����ѯ���",1)

#�˺���������ʾ������Ϣ��ҳ��

def ShowNew():
    if not os.path.isdir(os.path.join(global_var.setting['download_path'],u'notes')):
        os.mkdir(os.path.join(global_var.setting['download_path'],u'notes'))
    print u'���ڲ�ѯ�˴θ��µĹ���....'
    global_var.statusBar.SetStatusText( u'���ڲ�ѯ�˴θ��µĹ���....',1)
    list=global_var.list
    pre='''
    <html>
    <head>
    <META http-equiv="Content-Type" content="text/html; charset=utf-8">
    <title>����</title>
    <link rel="stylesheet" href="style.css" type="text/css" media="screen">
    </head>
    <body>
    <div id="header"><h1>���µ��ļ�</h1></div>
    <div id="content">
    <ul>
    '''
    for ft in global_var.newfile:
        coursename=list[ft[0]][1]
        filename=list[ft[0]][2][ft[1]]['file_realname']
        pre+='<li>'+filename.encode('gbk')+'......'+coursename.encode('gbk')+'</li>\n'
    pre+='''
    </ul>
    </div><div id="header"><h1>���µĹ���</h1></div>
    <div id="content">
    '''
    newnote=global_var.newnote
    for nt in newnote.keys():
        if(list[nt[0]][3]):
            note=list[nt[0]][3][nt[1]]
            coursename=list[nt[0]][1]
            notecontent=newnote[nt]
            pre+='''
            <div class="textbox"><a name="1"></a>
            <div class="title"><h3>
            '''
            pre+=note['note_title']
            pre+='''
            </h3><div class="label">'''
            pre+=note['note_date']+'--'+coursename.encode('gbk')
            pre+='''
            </div>
            </div>
            <div class="content">'''
            pre+=notecontent
            pre+='''
            </div>
            </div>
            </div>'''
        else:
            pass
    pre+='''
    </div>
    </body>
    </html>
    '''
    f=open(os.path.join(global_var.setting['download_path'],u'notes',u'newinfo.htm'),'w')
    f.write(pre.decode('gbk').encode('utf'))
    f.close()
    print u'>>���µĹ����ѯ���'
    global_var.statusBar.SetStatusText( u'�˴θ��µĹ����ѯ���',1)
        
        

#�˺�������ָ���γ̵��ļ�
def DownCourse(courseindex):
    global_var.app_stat='downcourse'
    conn=global_var.conn
    list=global_var.list
    download_path=global_var.setting['download_path']
    os.chdir(download_path)
    coursedir=os.path.join(download_path,list[courseindex][1])
    if not os.path.exists(coursedir):
        os.mkdir(coursedir)
    for fileindex in range(len(global_var.list[courseindex][2])):
        file=global_var.list[courseindex][2][fileindex]
        if FileType(courseindex,fileindex)!=0:
            continue
        else:
            if global_var.app_stat=='breakdown':
                global_var.statusBar.SetStatusText(u"״̬������",2)
                return
            filepath=os.path.join(download_path,list[courseindex][1],file['file_realname'])
            newfile=open(filepath,'wb')
            global_var.statusBar.SetStatusText(u'��������'+file['file_realname']+' ......',1)
            print u'��������'+file['file_realname']+u' ......'
            newfile.write(conn.open(file['file_url']).read())
            newfile.close()
            print u'=='+file['file_realname']+u'�������'
            #�˾�ˢ���ļ��б���ʾ
            GUItools.ShowFile(courseindex)
            global_var.lstLocalFile.InsertStringItem(len(global_var.local_files),global_var.list[courseindex][2][fileindex]['file_realname'])
            global_var.lstLocalFile.SetItemImage(len(global_var.local_files),0)
            #ע��print_file�б���ֻ������û��������Ϣ
            #local_files���ǿγ��������ļ�������Ԫ��
            global_var.print_files.append(len(global_var.local_files))
            global_var.local_files.append((courseindex,fileindex))
    global_var.statusBar.SetStatusText(u'<<'+list[courseindex][1]+u'>>�����пμ��������',1)
    print '-'*80
    print '>>'+list[courseindex][1]+u' �Ŀγ��ļ��������'
    

#�˺����������пγ̵��ļ�
def DownAll():
    global_var.statusBar.SetStatusText(u"״̬��æµ",2)
    list=global_var.list
    for courseindex in range(len(list)):
        if global_var.app_stat=='breakdown':
            global_var.statusBar.SetStatusText('�����Ѿ����ж�',1)
            global_var.statusBar.SetStatusText(u"״̬������",2)
            return
        global_var.current_courseindex=courseindex
        global_var.current_fileindex=[]
        DownCourse(courseindex)
    global_var.statusBar.SetStatusText(u"״̬������",2)
    global_var.statusBar.SetStatusText(u'���пγ̵Ŀμ������������',1)

#�˺�������ָ�����ļ�
def DownSingle(courseindex,fileindex):
    conn=global_var.conn
    list=global_var.list
    exsit=0
    download_path=global_var.setting['download_path']
    if courseindex < len(list):
        if fileindex < len(list[courseindex][2]):
            #os.chdir(download_path)
            coursedir=os.path.join(download_path,list[courseindex][1])
            if (not os.path.exists(coursedir)):
                os.mkdir(coursedir)
            #�˴����ַ�����ͳһ��unicode����ֹ����
            os.chdir(download_path+u'\\'+list[courseindex][1])
            filepath = os.path.join(coursedir,list[courseindex][2][fileindex]['file_realname'])
            if os.path.exists(filepath):
                exsit=1
                info=u"���ڸ����ļ�"+list[courseindex][2][fileindex]['file_realname']+u' ......'
            else:
                info=u"���������ļ�"+list[courseindex][2][fileindex]['file_realname']+u' ......'
            print info
            global_var.statusBar.SetStatusText(info,1)
            
            newfile=open(filepath,'wb')
            newfile.write(conn.open(list[courseindex][2][fileindex]['file_url']).read())
            newfile.close()
            if exsit:
                info=u"�����ļ�"+list[courseindex][2][fileindex]['file_realname']+u"�ɹ�"
            else:
                info=u"�����ļ�"+list[courseindex][2][fileindex]['file_realname']+u"�ɹ�"
            print ">>"+info
            global_var.statusBar.SetStatusText(info,1)
    #os.chdir(download_path)
    return
    

#�˺����ж��б��е��ļ��Ƿ������Ĭ���ļ�����
def IsExist(courseindex,fileindex):
    list=global_var.list
    download_path=global_var.setting['download_path']
    path=download_path+u'\\'+list[courseindex][1]+u'\\'+list[courseindex][2][fileindex]['file_realname']
    if os.path.exists(path) and os.path.isfile(path):
        return path
    else:
        return False
    

#�˺����ж��ļ���С�Ƿ�ƥ��
def IsNew(courseindex,fileindex):
    list=global_var.list
    download_path=global_var.setting['download_path']
    path=download_path+u'\\'+list[courseindex][1]+u'\\'+list[courseindex][2][fileindex]['file_realname']
    if os.path.exists(path) and os.path.isfile(path) and abs(os.path.getsize(path)-list[courseindex][2][fileindex]['file_realsize'])>2 :
        return path
    else:
        return False
    

#ȷ���ļ�����ʾ��𣺴����أ�������...etc
def FileType(courseindex,fileindex):
    if(IsExist(courseindex,fileindex) and IsNew(courseindex,fileindex)):
        return 2
    if ((courseindex,fileindex) in global_var.setting['filter']):
        return 3
    else:
        if IsExist(courseindex,fileindex):
            return 1
        else:
            return 0
def count():
    f=urllib.urlopen('http://mydownloader.3322.org/count/')
    f.read()
    f.close()