# THUHelper
Automatically exported from code.google.com/p/thudownloader
清华大学网络学堂助手
----------
### 背景
很早就想有这么一个工具了，本地看公告、自动下文件等等，可惜一直处于“有空就做”的状态23333333

然后google上发现了[thudownloader](https://code.google.com/p/thudownloader/)，试着用了一下好赞啊！！！可惜年久失修（最后一次更新是2011年），现在已经不能用了。

>以下为google上的原文

身为清华学子，网络学堂是学习生活不可或缺的一部分。 但相信大部分人都对上网络学堂下课件看公告感到厌烦吧。

（以下一段是抱怨，可直接跳过 ^^） 每天，我们都得把每个课程刷一遍，看看有没有新的课件或新的公告。如果有新的课件， 我们还得一个一个点击下载，还得把名字里那一串让人看起来眼花缭乱的数字去掉； 万一碰上课件比较多的课程，还得对着本地的文件看哪个是已经下载的，哪个是新的。 公告也是如此，说不定哪天老师就发布了个新公告，但由于自己没注意，很可能就错过 一次习题课，又或者是错过某次实验的通知......

如果你对上文深有同感，那么请快试用我们的软件吧。你只需在第一次启动程序后， 设置好用户名密码，以及本地的课件根目录，之后的一切都交给程序去忙吧。 借用某大牛的话说:“它会带给你一种惊艳的感觉!”

还等什么 赶紧下载试用吧 !! (点击右侧Featured downloads区域的链接开始下载~)

--转自Free大牛Dinstein 

于是Export to GitHub，研究了一个下午让他能运行了。（问题竟然是`course_id`从5位变成了6位！）

顺便改了个名。

> 可执行文件由pyinstaller生成

### 开始使用
1. 安装运行
    * 如果你有Python和pip(Windows/OSX/Linux)
        1. 下载源码
        2. 使用`pip`等方式安装依赖(包括wxPython等)
        3. 运行MyDownloader.py
    * 如果你没有Python
        * 从release里找到可执行文件
2. 在菜单栏选择“操作”--“登录设置”；
3. 设置默认下载的文件夹，以及默认的打印文件夹，注意记得点“保存以上设置”；
4. 设置用户名和密码，强烈建议选上“自动登录”，密码以加密形式存在本地；
5. 点“登录”即可开始登录过程，这可能会持续一段时间，请耐心等待:)
6. 如果一切顺利，在“我的课程”栏里会出现你本学期的课程名，如果提示出错，请确认2-5步是否设置正确；
7. 现在可以用鼠标点击左边的课程名，在右上方的“课程公告”里会显示这门课的公告，右下方“远程文件信息”显示的是该门 课课件的信息，右键点击课件名可以取消该课件的下载标记。这样，如果不想下载诸如视频之类的大课件，可以在这里取消；
8. 把不需要下载的课件的下载标记去除后，点击快捷键的最左边一个按钮：“下载所有课件、更新公告”，这样就开始自动下载 了。这可能也需要一段时间，请耐心等待 :)

### 功能介绍
1. 登录成功后，自动下载网络学堂公告，并显示新公告；
  同时，得到课件名的列表，提示哪些是新课件，并提供一键下载功能；
2. 自动检测本地课件和网络学堂上课件是否一致，如果不一致，提示重新下载；
3. 可以屏蔽不想下载的课件，这样该课件以后都不会被下载；如果后悔了，可以打开屏蔽，课件还能照常被下载；

### TODOList
* 下载文件重命名掩码
* 新版网络学堂支持
* 作业列表与提交
* 更好看的公告栏
* 更好看的UI

### 作者和贡献者
    
    haow05@gmail.com
    dinstein@163.com
    zyeoman@163.com

### 欢迎提交issue或PR

