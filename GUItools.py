#!/usr/bin/env python
# -*- coding: utf-8 -*-


#为GUI提供必要的类和函数
import global_var,download,Dialogs
import wx,os,sys,threading
import cPickle as pickle
from shutil import copyfile
import aeslib
#刷新所有文件列表，获取并创建公告网页内容
def Refresh():
    global_var.app_stat='refresh'
    try:
    #if(1):
        global_var.statusBar.SetStatusText(u"状态：忙碌",2)
        global_var.statusBar.SetStatusText(u"正在获取网络学堂文件列表......",1)
        download.getCourse()
        download.refreshFiles()
        download.refreshNotes()
        ShowCourse()
        ShowFile(global_var.current_courseindex)
        a=os.path.join(global_var.setting['download_path'],u'notes')
        b=global_var.list[global_var.current_courseindex][1]+u'.htm'
        notename=os.path.join(a,b)
        
        if os.path.exists(notename):
            global_var.html.LoadFile(notename )
        
    except:
    #else:
        global_var.statusBar.SetStatusText(u"由于网络或其他原因，列表刷新失败",1)
        global_var.statusBar.SetStatusText(u"状态：空闲",2)
        return
    global_var.statusBar.SetStatusText(u"列表刷新成功",1)
    global_var.statusBar.SetStatusText(u"状态：空闲",2)
    saveList()
    global_var.app_stat='Idle'
    return True

#此函数显示制定课程的文件列表
def ShowFile(courseindex=0):
    '''当要显示更新内容（courseindex=-1）时显示更新的课件html'''
    if courseindex==-1:
        a=os.path.join(global_var.setting['download_path'],u'notes')
        b=u'newinfo.htm'
        notename=os.path.join(a,b)
        if(os.path.exists(notename)):
            global_var.html.LoadFile(notename)
            return
    a= os.path.join(global_var.setting['download_path'],u'notes')
    b= global_var.list[courseindex][1]+u'.htm'
    notename=os.path.join(a,b)
    if(os.path.exists(notename)):
        global_var.html.LoadFile(notename)
        
    global_var.current_markfile=[]
    lstControl = global_var.lstRemoteFile
    lstControl.DeleteAllItems()
    for itemindex in range(len(global_var.list[courseindex][2])):  
        item=global_var.list[courseindex][2][itemindex]
        index = lstControl.InsertStringItem(itemindex,item['file_realname'] )
        ##########################################################################
        if(item['file_realsize'] < 1024*1024):
            str_realsize = str(round(item['file_realsize']/1024.0,1))+u'K'
        else:
            str_realsize = str(round((item['file_realsize']/(1024*1024.0)),1))+u'M'
        lstControl.SetStringItem(index, 1,str_realsize)
        ##########################################################################
        lstControl.SetStringItem(index, 2, item['file_date'])
        type=download.FileType(courseindex,index)
        lstControl.SetItemImage(index,type)
        if type==0:
            global_var.current_markfile.append(index)

#此函数显示课程列表
def ShowCourse():
    lstControl = global_var.lstRemoteCourse
    lstControl.DeleteAllItems()
    lstControl.InsertStringItem(0,u"What's New?")
    for itemindex in range(len(global_var.list)):  
        item=global_var.list[itemindex]
        lstControl.InsertStringItem(itemindex+1,item[1])

#此函数检查是否自动登录
def check():
    #对于自动登录，直接把上次的list调用
    if global_var.setting['autologin']:
        global_var.userid=aeslib.decode(global_var.setting['userinfo'][0])
        global_var.userpass=aeslib.decode(global_var.setting['userinfo'][1])
        #global_var.userid= global_var.setting['userinfo'][0] 
        #global_var.userpass= global_var.setting['userinfo'][1] 
        #print u'正在为您自动登录，请稍侯......'
        try:
            global_var.conn.login()
        except:
            global_var.log_stat='no'
            return
        global_var.log_stat='yes'
        ShowCourse()
        if len(global_var.list)>0:
            ShowFile(global_var.current_courseindex)
    return
    

#对课程列表框的响应
def courseSelected_cmd(event):
    '''注意此处的实际课程index是m_itemIndex-1，因为课程第一项显示的是更新'''
    index=event.m_itemIndex
    global_var.current_courseindex=index-1
    global_var.current_fileindex=[]
    global_var.localsel=[]
    ShowFile(index-1)

#刷新指定课程的文件列表和公告
def refreshCourse():
    #if(1):
    try:
        global_var.app_stat='refreshcourse'
        global_var.statusBar.SetStatusText(u"状态：忙碌",2)
        global_var.statusBar.SetStatusText(u"正在更新本课程的课件列表和公告......",1)
        download.RefreshCourse(global_var.current_courseindex)
        ShowFile()
        global_var.statusBar.SetStatusText(u"状态：空闲",2)
        global_var.current_fileindex=[]
        #此句为了防止选定的出错
        global_var.localsel=[]
        global_var.statusBar.SetStatusText(u"更新完毕",1)
        global_var.app_stat='Idle'
    #else:
    except:
        global_var.statusBar.SetStatusText(u"状态：空闲",2)
        global_var.statusBar.SetStatusText(u"由于网络或其他原因，更新失败",1)


def loadSetting():
    path=os.path.join(os.path.split( os.path.realpath( sys.argv[0] ) )[0].decode('gbk'),u'setting')
    if os.path.exists(path):
        f=open(path,'rb')
        global_var.setting=pickle.load(f)
        f.close()
    else:
        saveSetting()


#把程序中的设置信息保存至本地
def saveSetting():
    path=os.path.join(os.path.split( os.path.realpath( sys.argv[0] ) )[0].decode('gbk'),u'setting')
    f=open(path,'wb')
    pickle.dump(global_var.setting,f,True)
    f.close()


#从本地读入设置信息

#从本地读入设置信息
def loadList(first_use = 1):
    rt = 0
    path=os.path.join(global_var.setting['download_path'],u'.MyDownloader_history')
    if(os.path.exists(path)):
        rt=0
        f=open(path,'rb')
        global_var.list=pickle.load(f)
        f.close()
    else:
        rt = 1
    return rt

def saveList():
    path=os.path.join(global_var.setting['download_path'],u'.MyDownloader_history')
    try:
        f=open(path,'wb')
        pickle.dump(global_var.list,f,True)
        f.close()
    except:
        pass

################################################################################################################
#对文件列表的一系列响应
################################################################################################################
def fileSelected_cmd(event):
    global_var.current_fileindex.append(event.GetIndex())
    #print str(global_var.current_fileindex)

def fileDeSelected_cmd(event):
    if(event.GetIndex() in global_var.current_fileindex):
        global_var.current_fileindex.remove(event.GetIndex())
        #print str(global_var.current_fileindex)

def markFile(event):
    for i in global_var.current_fileindex:
        global_var.lstRemoteFile.SetItemImage(i,0)
        #下面一句if判断如果选中的文件序号已经被标记了，就不用加入current_markfile，之前的一些选择标记出错的bug来源于此
        #2008.3.25  By venture
        #print u"当前："
        #print global_var.current_markfile
        if (not i in global_var.current_markfile):
            global_var.current_markfile.append(i)
        if (global_var.current_courseindex,i) in global_var.setting['filter']:
            global_var.setting['filter'].remove((global_var.current_courseindex,i))
            saveSetting()

def demarkFile(event):
    for i in global_var.current_fileindex:
        if not ((global_var.current_courseindex,i) in global_var.setting['filter']):
            if (i in global_var.current_markfile):
                global_var.current_markfile.remove(i)
                global_var.lstRemoteFile.SetItemImage(i,1)

def btnMarkAll_handle(event):
    for i in range(len(global_var.list[global_var.current_courseindex][2])):
        global_var.lstRemoteFile.SetItemImage(i,0)
        global_var.current_markfile.append(i)
        if (global_var.current_courseindex,i) in global_var.setting['filter']:
            global_var.setting['filter'].remove((global_var.current_courseindex,i))
            saveSetting()

def btnDemarkAll_handle(event):
    for i in range(len(global_var.list[global_var.current_courseindex][2])):
        if not ((global_var.current_courseindex,i) in global_var.setting['filter']):
            if (i in global_var.current_markfile):
                global_var.current_markfile.remove(i)
                global_var.lstRemoteFile.SetItemImage(i,1)

def filterFile(event):
    for i in global_var.current_fileindex:
        global_var.setting['filter'].append((global_var.current_courseindex,i))
        if (i in global_var.current_markfile):
            global_var.current_markfile.remove(i)
        global_var.lstRemoteFile.SetItemImage(i,3)
    saveSetting()

def defilterFile(event):
    for i in global_var.current_fileindex:
        if ((global_var.current_courseindex,i) in global_var.setting['filter']):
            global_var.setting['filter'].remove((global_var.current_courseindex,i))
            global_var.lstRemoteFile.SetItemImage(i,1)
    saveSetting()

def lstRemoteFile_RightClick(event):
    lstControl = global_var.lstRemoteFile
    
    #生成弹出菜单
    if global_var.current_fileindex:
        popmenu = wx.Menu()
        menu_id_mark = wx.NewId()
        popmenu.Append(menu_id_mark, u"设置下载标记")
        menu_id_demark=wx.NewId()
        popmenu.Append(menu_id_demark, u"取消下载标记")

        menu_id_filter=wx.NewId()
        popmenu.Append(menu_id_filter, u"屏蔽此课件")
        
        menu_id_defilter=wx.NewId()
        popmenu.Append(menu_id_defilter, u"取消对课件的屏蔽")
        menu_id_refresh = wx.NewId()
        popmenu.Append(menu_id_refresh, u"刷新本课程列表")
        
        global_var.main_frame.Bind(wx.EVT_MENU,markFile, id=menu_id_mark)
        global_var.main_frame.Bind(wx.EVT_MENU,demarkFile, id=menu_id_demark)
        global_var.main_frame.Bind(wx.EVT_MENU,filterFile, id=menu_id_filter)
        global_var.main_frame.Bind(wx.EVT_MENU,defilterFile, id=menu_id_defilter)
        #menu_id_refresh和btnRefresh按钮绑定在同一个事件
        global_var.main_frame.Bind(wx.EVT_MENU,btnRefresh_handle, id=menu_id_refresh)
        lstControl.PopupMenu(popmenu)
        popmenu.Destroy()
    return
#############################################################################################################
#文件列表的一系列响应事件结束
##############################################################################################################

##############################################################################################################
#本次下载列表框的响应事件
################################################
#注意print_file列表中只有索引没有其他信息
#local_files中是课程索引和文件索引的元组
#localsel同样只有索引信息


def localSelected_cmd(event):
    global_var.localsel.append(event.GetIndex())
    #print 'local'+str(global_var.localsel)

def localDeSelected_cmd(event):
    if event.GetIndex() in global_var.localsel:
        global_var.localsel.remove(event.GetIndex())
        #print 'local'+str(global_var.localsel)

def printFile(event):
    for i in global_var.localsel:
        global_var.lstLocalFile.SetItemImage(i,0)
        #此处同上（文件列表的选择函数中）venture
        if (not i in global_var.print_files):
            global_var.print_files.append(i)

def noprintFile(event):
    for i in global_var.localsel:
        global_var.print_files.remove(i)
        global_var.lstLocalFile.SetItemImage(i,1)

def lstLocalFile_RightClick(event):
    lstControl = global_var.lstLocalFile
    
    #生成弹出菜单
    if global_var.localsel:
        popmenu = wx.Menu()
        menu_id_print = wx.NewId()
        popmenu.Append(menu_id_print, u"设置复制标记")
        menu_id_noprint=wx.NewId()
        popmenu.Append(menu_id_noprint, u"取消复制标记")
        
        global_var.main_frame.Bind(wx.EVT_MENU,printFile, id=menu_id_print)
        global_var.main_frame.Bind(wx.EVT_MENU,noprintFile, id=menu_id_noprint)
        lstControl.PopupMenu(popmenu)
        popmenu.Destroy()
    return
#结束
#########################################################################################################




########################################################################################
#菜单项、工具栏、众按钮的处理函数
########################################################################################
def logItem_handle(event): # wxGlade: MainFrame.<event_handler>
    ret = global_var.logDialog.ShowModal()
    if ret==wx.ID_OK:
        global_var.lstLocalFile.DeleteAllItems()
        global_var.local_files=[]
        global_var.print_files=[]
        global_var.userid=global_var.logDialog.info[0]
        global_var.userpass=global_var.logDialog.info[1]
        if not global_var.theThread.isAlive():
            global_var.theThread=MyThread(Refresh,'name')
            global_var.theThread.start()
        else:
            global_var.warnDialog.html.SetPage(u'''
            <html>
            <body bgcolor="#FFEFD5">
            <centre><font size=4><strong>对不起，程序忙碌中...</font></centre>
            
            </body>
            </html>
            ''')
            global_var.warnDialog.SetSize((300,200))
            global_var.warnDialog.SetTitle(u"后台运行警告")
            global_var.warnDialog.ShowModal()


def hlpItem_handle(event):
    f=open(os.path.join(global_var.app_path.decode('gbk'),u'extra/help.txt'))
    global_var.warnDialog.html.SetPage(f.read())
    f.close()
    global_var.warnDialog.SetSize((950,660))
    global_var.warnDialog.SetTitle(u"帮助")
    global_var.warnDialog.ShowModal()

def aboutItem_handle(event):
    ret = global_var.aboutDialog.ShowModal()
    #    "Event handler `aboutItem_handle' not implemented!"






#此处需要多线程处理
def downAllTool_handle(event):
    if not global_var.theThread.isAlive():
        global_var.theThread=MyThread(_downAll,'name')
        global_var.theThread.start()
    else:
        global_var.warnDialog.html.SetPage(u'''
        <html>
        <body bgcolor="#FFEFD5">
        <centre><font size=4><strong>对不起，程序忙碌中...</font></centre>
        
        </body>
        </html>
        ''')
        global_var.warnDialog.SetSize((300,200))
        global_var.warnDialog.SetTitle(u"后台运行警告")
        global_var.warnDialog.ShowModal()
        
def _downAll():
    global_var.statusBar.SetStatusText(u"状态：忙碌",2)
    download.refreshFiles()
    #if(1):
    try:
        download.DownAll()
    #else:
    except:
        global_var.statusBar.SetStatusText(u"由于网络或其他原因，下载被中断",1)
        global_var.statusBar.SetStatusText(u"状态：空闲",2)
        return
    try:
        download.refreshNotes()
    except:
        global_var.statusBar.SetStatusText(u"由于网络或其他原因，更新文件列表被中断",1)
        global_var.statusBar.SetStatusText(u"状态：空闲",2)
        return
    saveList()
    global_var.statusBar.SetStatusText(u"所有的课件已经成功下载，所有课程公告已经更新",1)
    global_var.statusBar.SetStatusText(u"状态：空闲",2)


def downAllFilesTool_handle(event): # wxGlade: MainFrame.<event_handler>
    if not global_var.theThread.isAlive():
        global_var.theThread=MyThread(download.DownAll,'name')
        global_var.theThread.start()
    else:
        global_var.warnDialog.html.SetPage(u'''
        <html>
        <body bgcolor="#FFEFD5">
        <centre><font size=4><strong>对不起，程序忙碌中...</font></centre>
        
        </body>
        </html>
        ''')
        global_var.warnDialog.SetSize((300,200))
        global_var.warnDialog.SetTitle(u"后台运行警告")
        global_var.warnDialog.ShowModal()
        

#多线程处理
def refreshNotesTool_handle(event): # wxGlade: MainFrame.<event_handler>
    if not global_var.theThread.isAlive():
        global_var.theThread=MyThread(_refreshNotes,'name')
        global_var.theThread.start()
    else:
        global_var.warnDialog.html.SetPage(u'''
        <html>
        <body bgcolor="#FFEFD5">
        <centre><font size=4><strong>对不起，程序忙碌中...</font></centre>
        
        </body>
        </html>
        ''')
        global_var.warnDialog.SetSize((300,200))
        global_var.warnDialog.SetTitle(u"后台运行警告")
        global_var.warnDialog.ShowModal()
        
    
def _refreshNotes():
    global_var.statusBar.SetStatusText(u"正在更新课程公告......",1)
    global_var.statusBar.SetStatusText(u"状态：忙碌",2)
    try:
        download.refreshNotes()
    except:
        global_var.statusBar.SetStatusText(u"由于网络或其他原因，更新文件列表被中断",1)
        global_var.statusBar.SetStatusText(u"状态：空闲",2)
        return
    saveList()
    ShowCourse()
    ShowFile(-1)
    global_var.statusBar.SetStatusText(u"公告更新完毕",1)
    global_var.statusBar.SetStatusText(u"状态：空闲",2)


def stopTool_handle(event): # wxGlade: MainFrame.<event_handler>
    if global_var.app_stat in ['downcourse','downmark']:
        global_var.app_stat='breakdown'
    elif global_var.app_stat=='getcourse':
        pass
    else:
        pass

def _refreshAll():
    global_var.statusBar.SetStatusText(u"状态：忙碌",2)
    global_var.statusBar.SetStatusText(u"正在更新课件列表......",1)
    download.refreshFiles()
    saveList()
    ShowCourse()
    ShowFile(-1)
    global_var.statusBar.SetStatusText(u"课件列表更新完毕",1)
    global_var.statusBar.SetStatusText(u"状态：空闲",2)


def refreshAllTool_handle(event): # wxGlade: MainFrame.<event_handler>
    if not global_var.theThread.isAlive():
        global_var.theThread=MyThread(_refreshAll,'name')
        global_var.theThread.start()
    else:
        global_var.warnDialog.html.SetPage(u'''
        <html>
        <body bgcolor="#FFEFD5">
        <centre><font size=4><strong>对不起，程序忙碌中...</font></centre>
        
        </body>
        </html>
        ''')
        global_var.warnDialog.SetSize((300,200))
        global_var.warnDialog.SetTitle(u"后台运行警告")
        global_var.warnDialog.ShowModal()
        


def DownMarked():
    filelist=global_var.current_markfile
    filelist.sort()
    courseindex=global_var.current_courseindex
    global_var.app_stat='downmark'
    global_var.statusBar.SetStatusText(u"状态：忙碌",2)
    for fileindex in filelist:
        if global_var.app_stat=='breakdown':
            global_var.statusBar.SetStatusText(u"下载被中断",1)
            global_var.statusBar.SetStatusText(u"状态：空闲",2)
            return
        #本地若存在完全一样的文件进行提示
        exists=download.IsExist(courseindex,fileindex) and (download.IsNew(courseindex,fileindex))
        if exists:
            #可能由于进程间的竞争，此对话框屡次出错，不用对话框
            #warninfo=u"提示：文件"+global_var.list[courseindex][2][fileindex]['file_realname'].decode('gbk')+u"与本地的"+download.IsExist(courseindex,fileindex)+u"大小不一样，将覆盖原文件"
            #global_var.warnDialog.txtInfo.SetValue(warninfo)
            #global_var.warnDialog.ShowModal()
            if True:
                download.DownSingle(courseindex,fileindex)
                #下载完成后把本次下载列表更新
                if not((courseindex,fileindex) in global_var.local_files):
                    global_var.lstLocalFile.InsertStringItem(len(global_var.local_files),global_var.list[courseindex][2][fileindex]['file_realname'])
                    global_var.lstLocalFile.SetItemImage(len(global_var.local_files),0)
                    global_var.print_files.append(len(global_var.local_files))
                    global_var.local_files.append((courseindex,fileindex))
            else:
                global_var.statusBar.SetStatusText(u"下载已取消",1)
        else:
            download.DownSingle(courseindex,fileindex)
            global_var.lstLocalFile.InsertStringItem(len(global_var.local_files),global_var.list[courseindex][2][fileindex]['file_realname'])
            global_var.lstLocalFile.SetItemImage(len(global_var.local_files),0)
            global_var.print_files.append(len(global_var.local_files))
            global_var.local_files.append((courseindex,fileindex))
    ShowFile(courseindex)
    global_var.statusBar.SetStatusText(u"状态：空闲",2)
    global_var.current_fileindex=[]

def btnDownMarked_handle(event):
    if not global_var.theThread.isAlive():
        global_var.theThread=MyThread(DownMarked,'name')
        global_var.theThread.start()
    else:
        global_var.warnDialog.html.SetPage(u'''
        <html>
        <body bgcolor="#FFEFD5">
        <centre><font size=4><strong>对不起，程序忙碌中...</font></centre>
        </body>
        </html>
        ''')
        global_var.warnDialog.SetSize((300,200))
        global_var.warnDialog.SetTitle(u"后台运行警告")
        global_var.warnDialog.ShowModal()
        
    

    

def btnRefresh_handle(event): # wxGlade: MainFrame.<event_handler>
    if not global_var.theThread.isAlive():
        global_var.theThread=MyThread(refreshCourse,'name')
    else:
        global_var.warnDialog.html.SetPage(u'''
        <html>
        <body bgcolor="#FFEFD5">
        <centre><font size=4><strong>对不起，程序忙碌中...</font></centre>
        </body>
        </html>
        ''')
        global_var.warnDialog.SetSize((300,200))
        global_var.warnDialog.SetTitle(u"后台运行警告")
        global_var.warnDialog.ShowModal()
        

def _Copy():
    global_var.statusBar.SetStatusText(u"状态：忙碌",2)
    #print global_var.print_files
    for i in global_var.print_files:
        (courseindex,fileindex)=global_var.local_files[i]
        coursename=global_var.list[courseindex][1]
        filename=global_var.list[courseindex][2][fileindex]['file_realname']
        a=os.path.join(global_var.setting['download_path'],coursename)
        soursepath=os.path.join(a,filename)
        targetpath=os.path.join(global_var.setting['print_path'],filename)
        print soursepath+'->'+targetpath
        if os.path.exists(soursepath) :
            if os.path.exists(targetpath):
                os.remove(targetpath)
            global_var.statusBar.SetStatusText(u"正在复制文件"+filename,1)
            copyfile(soursepath,targetpath)
            global_var.statusBar.SetStatusText(u"复制完成",1)
        global_var.statusBar.SetStatusText(u"状态：空闲",2)
def btnCopy_handle(event):
    if not global_var.theThread.isAlive():
        global_var.theThread=MyThread(_Copy,'name')
        global_var.theThread.start()
    else:
        global_var.warnDialog.html.SetPage(u'''
        <html>
        <body bgcolor="#FFEFD5">
        <centre><font size=4><strong>对不起，程序忙碌中...</font></centre>
        </body>
        </html>
        ''')
        global_var.warnDialog.SetSize((300,200))
        global_var.warnDialog.SetTitle(u"后台运行警告")
        global_var.warnDialog.ShowModal()


##############################################################################################





#important:整个框架的初始化
def FrameInit(frame):
    
    print "-"*80
    print u"这个是程序运行期间的log窗口，可以显示程序运行的细节步骤，不想看可以关掉"
    print "-"*80
    #开始初始化全局变量,便于模块间互相访问窗口部件
    ######################################################################################################
    global_var.main_frame=frame
    global_var.lstRemoteFile=frame.lstRemoteFile
    global_var.lstRemoteCourse=frame.lstRemoteCourse
    global_var.lstLocalFile=frame.lstLocalFile
    global_var.html=frame.html
    
    #建立对话框对象
    global_var.selDirDialog=wx.DirDialog(None, u"选择默认目录",style=wx.DD_DEFAULT_STYLE | wx.DD_NEW_DIR_BUTTON)
    global_var.logDialog=Dialogs.LogDialog(frame)
    global_var.warnDialog=Dialogs.WarnDialog(frame)
    global_var.aboutDialog=Dialogs.AboutDialog(frame)
    
    #建立连接对象
    global_var.conn=download.MyCon()
    global_var.statusBar=frame.statusBar
    global_var.theThread=MyThread(justpass,'a')
    global_var.theThread.start()
    ######################################################################################################
    
    
    #保证本地的配置、历史文件存在，如果不存在，把global_var中默认生成的setting和history存入本地
    loadSetting()
    historypath=os.path.join(global_var.setting['download_path'],u'history')

    ##################################################################################################

    #把配置文件读入全局变量
    loadList()
    
    #开始对各控件的初始化
    ######################################################################################################
    
    global_var.logDialog.txtSetDownPath.SetValue(global_var.setting['download_path'])
    global_var.logDialog.txtSetPrintPath.SetValue(global_var.setting['print_path'])
    #设置登录对话框的初始值
    userid=global_var.setting['userinfo'][0]
    userpass=global_var.setting['userinfo'][1]
    if userid:
        global_var.logDialog.txtUserid.SetValue(aeslib.decode(userid))
        global_var.logDialog.txtUserpass.SetValue(aeslib.decode(userpass))
    else:
        global_var.logDialog.txtUserid.SetValue(u'网络学堂账号')
        global_var.logDialog.txtUserpass.SetValue(u'')

    #global_var.logDialog.txtUserid.SetValue(u'')
    #global_var.logDialog.txtUserpass.SetValue(u'')
    
    global_var.logDialog.autoSaved.SetValue(global_var.setting['autologin'])
    
    font1 = wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,wx.FONTWEIGHT_NORMAL, False, u"宋体")
    font2 = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,wx.FONTWEIGHT_NORMAL, False, u"宋体")
    frame.lstRemoteFile.SetFont(font1)
    frame.lstRemoteCourse.SetFont(font2)
    frame.lstLocalFile.SetFont(font1)
    
    #为课程列表设定图片列表
    il = wx.ImageList(16, 16)
    il.Add(wx.ArtProvider.GetBitmap(wx.ART_GO_DOWN,wx.ART_OTHER, (16, 16)))      #待下载标记
    il.Add(wx.ArtProvider.GetBitmap(wx.ART_NORMAL_FILE, wx.ART_OTHER, (16, 16))) #普通不下载的标记
    il.Add(wx.ArtProvider.GetBitmap(wx.ART_TIP, wx.ART_OTHER, (16, 16)))         #本地课件与网络学堂上的大小不匹配时的提示图标（也属于不下载类）
    il.Add(wx.ArtProvider.GetBitmap(wx.ART_DEL_BOOKMARK, wx.ART_OTHER, (16, 16)))  #被用户设置为屏蔽的课件图标（不下载）
    frame.lstRemoteFile.AssignImageList(il, wx.IMAGE_LIST_SMALL)    

    il2 = wx.ImageList(16, 16)
    il2.Add(wx.ArtProvider.GetBitmap(wx.ART_ADD_BOOKMARK,wx.ART_OTHER, (16, 16)))      #待复制的标记
    il2.Add(wx.ArtProvider.GetBitmap(wx.ART_DELETE, wx.ART_OTHER, (16, 16))) #不复制的标记
    frame.lstLocalFile.AssignImageList(il2, wx.IMAGE_LIST_SMALL)
    
    frame.lstLocalFile.InsertColumn(0, u"文件名",format=wx.LIST_FORMAT_LEFT, width=300)
    
    frame.lstRemoteFile.InsertColumn(0, u"文件名",format=wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT, width=200)
    frame.lstRemoteFile.InsertColumn(1, u"文件大小",format=wx.LIST_FORMAT_LEFT, width=80)
    frame.lstRemoteFile.InsertColumn(2, u"上传时间",format=wx.LIST_FORMAT_LEFT, width=100)
    
    #设置首列的格式wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
    
    frame.lstRemoteCourse.InsertColumn(0, u"课程名",format=wx.LIST_FORMAT_LEFT, width=180)

    #控件初始化完毕
    ######################################################################################################
    
    #绑定事件
    EventBind(frame)
    
    #检测是否需要自动登录
    check()
    




#绑定函数
def EventBind(frame):
    
    #菜单项绑定事件
    frame.Bind(wx.EVT_CLOSE,frame.exitApp)
    frame.Bind(wx.EVT_MENU, logItem_handle, frame.logItem)
    frame.Bind(wx.EVT_MENU, frame.exitApp, frame.exitItem)
    frame.Bind(wx.EVT_MENU, hlpItem_handle, frame.hlpItem)
    frame.Bind(wx.EVT_MENU, aboutItem_handle, frame.aboutItem)
    frame.Bind(wx.EVT_MENU, frame.hide, frame.hideItem)
    frame.Bind(wx.EVT_TOOL, logItem_handle, frame.toolLogin)
    frame.Bind(wx.EVT_TOOL, downAllTool_handle, frame.toolDownAll)
    frame.Bind(wx.EVT_TOOL, downAllFilesTool_handle, frame.toolDownAllFiles)
    frame.Bind(wx.EVT_TOOL, refreshNotesTool_handle, frame.toolRefreshNotes)
    frame.Bind(wx.EVT_TOOL, stopTool_handle, frame.toolStop)
    frame.Bind(wx.EVT_TOOL, refreshAllTool_handle, frame.tollRefreshAll) 
    frame.Bind(wx.EVT_TOOL, frame.hide, frame.toolHide)   
    #众按钮绑定事件
    frame.Bind(wx.EVT_BUTTON, btnDownMarked_handle,frame.btnDownMarked)
    frame.Bind(wx.EVT_BUTTON, btnRefresh_handle, frame.btnRefresh)
    frame.Bind(wx.EVT_BUTTON, btnMarkAll_handle, frame.btnMarkAll)
    frame.Bind(wx.EVT_BUTTON, btnDemarkAll_handle, frame.btnDemarkAll)
    frame.Bind(wx.EVT_BUTTON, btnCopy_handle, frame.btnCopy)
    
    #列表项绑定
    frame.Bind(wx.EVT_LIST_ITEM_SELECTED,courseSelected_cmd,frame.lstRemoteCourse)
    frame.Bind(wx.EVT_LIST_ITEM_SELECTED,fileSelected_cmd,frame.lstRemoteFile)
    frame.Bind(wx.EVT_LIST_ITEM_DESELECTED,fileDeSelected_cmd,frame.lstRemoteFile)
    frame.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK,lstRemoteFile_RightClick,frame.lstRemoteFile)
    
    frame.Bind(wx.EVT_LIST_ITEM_SELECTED,localSelected_cmd,frame.lstLocalFile)
    frame.Bind(wx.EVT_LIST_ITEM_DESELECTED,localDeSelected_cmd,frame.lstLocalFile)
    frame.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK,lstLocalFile_RightClick,frame.lstLocalFile)
    

class MyThread(threading.Thread):
    def __init__(self,func,threadname,keyw=()):
        threading.Thread.__init__(self, name =threadname)
        self.func=func
        self.keyw=keyw
    def run(self):
        apply(self.func,self.keyw)

def justpass():
    pass
    

