from selenium import webdriver
import requests,re,threading,os
from tkinter import *
from tkinter import Scrollbar,messagebox,ttk
import tkinter.font as tf


class AnswerGUI(Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        #self.master.bind("<Button-3>", lambda event: self.buttonTest(event))
        self.ft = tf.Font(family='微软雅黑', size=12)  # 设置输出文本框字体
        self.grid()

        #self.t1 = threading.Thread(target=self.createWiget, name="GUI_start")
        self.t2 = threading.Thread(target=self.selenium_funtion_ready, name="chrome_start")
        self.t2.start()
        self.createWiget()  # 运行主程序
        #self.selenium_funtion_ready()
        if not root.mainloop():
            self.browser.quit()


    def createWiget(self):

        #整体框架
        top_frame = LabelFrame(self.master)
        top_frame.grid(row=0, column=1, rowspan=2, columnspan=5, sticky=NSEW, padx=8, pady=5)

        #输入框架
        input_frame = LabelFrame(top_frame)
        input_frame.grid(row=0, column=1, rowspan=2, columnspan=5, sticky=NSEW, padx=8, pady=5)

        #输出框架
        output_frame = LabelFrame(top_frame)
        output_frame.grid(row=3, column=1, rowspan=2, columnspan=5, sticky=NSEW, padx=8, pady=5)

        self.select = ttk.Combobox(input_frame,width=10,font=self.ft)
        self.select.grid(row=1,column=1,sticky=NSEW, padx=8, pady=5)

        self.select['value'] = ('网易云音乐', 'QQ音乐', '虾米音乐' )
        self.select.current(0)
        print(self.select.get())

        """输入文本框"""
        v1 = StringVar()
        self.eny1 = Entry(input_frame, textvariable=v1, width=50,font=self.ft)
        self.eny1.grid(row=1, column=2,columnspan=5, sticky=NSEW, padx=8, pady=5)
        self.eny1.bind("<Return>",lambda event:self.selenium_function())

        """确定按键"""
        btn1 = Button(input_frame, text='确定', width=16,command=self.selenium_function)
        btn1.grid(row=1, column=7, sticky=NSEW, pady=5, padx=8)

        """列表框"""
        self.lb = Listbox(output_frame, selectmode=EXTENDED, font=self.ft, height=29,width=78)
        self.lb.bind('<Double-Button-1>', self.player)
        self.lb.grid(row=0, column=1, columnspan=5, pady=5, padx=8, sticky=NSEW)

        """退出按钮"""
        btn2 = Button(output_frame, text="退出",width=10, command=self.quit_sys)
        btn2.grid(row=1, column=1, sticky=NS, pady=5, padx=8)

        """上一页"""
        btn3 = Button(output_frame, text="上一页",width=10, command=self.last_page)
        btn3.grid(row=1, column=2, sticky=NS, pady=5, padx=8)

        """下一页"""
        btn4 = Button(output_frame,text="下一页",width=10,command=self.next_page)
        btn4.grid(row=1,column=3,sticky=NS,pady=5,padx=8)

        """下载按钮"""
        btn1 = Button(output_frame, text="下载",width=10, command=self.download_music)
        btn1.grid(row=1, column=4, sticky=NS, pady=5, padx=8)

        """添加纵向滚动条"""
        scroll = Scrollbar(output_frame)
        scroll.grid(row=0, column=7, sticky='ns', )
        self.lb.configure(yscrollcommand=scroll.set)
        scroll.configure(command=self.lb.yview)

    def selenium_funtion_ready(self):

        # 初始化selenium(隐藏模式）
        # chrome_options = webdriver.chrome.options.Options()
        # chrome_options.add_argument('--headless')
        # self.browser = webdriver.Chrome(executable_path=r'C:\chromedriver_win32\chromedriver.exe',options=chrome_options)  # 初始化浏览器
        self.browser = webdriver.Chrome(r'C:\chromedriver_win32\chromedriver.exe')
        self.browser.implicitly_wait(10)                    #隐式等待10s
        self.browser.get(f"https://music.163.com/#/search/m/?s={self.eny1.get()}&type=1")
        self.browser.switch_to.frame("contentFrame")

    def selenium_function(self,*args):

        self.t2.join()
        search_box = self.browser.find_element_by_id("m-search-input")
        search_box.clear()
        search_box.send_keys(self.eny1.get(),"\n")
        self.selenium_outputlist()      #获取歌曲列表

    def selenium_outputlist(self):
        res_lists = self.browser.find_elements_by_css_selector('body  .srchsongst .item')
        self.lb.delete(0,END)
        self.id_dict = {}
        self.downloadid = {}
        for res_list in res_lists:
            download_id = res_list.find_element_by_css_selector("div a").get_attribute("id")
            data_res_copyright = res_list.find_element_by_css_selector("div a").get_attribute('data-res-copyright')

            if data_res_copyright == 0:
                pass
            else:
                res_words = res_list.text.split("\n")
                res_word = "---".join(res_words)
                ids = re.findall(r"\d+\.?\d*", download_id)
                for id in ids:

                    self.downloadid[res_word] = id
                self.lb.insert(END, res_word)
                self.id_dict[res_word] = download_id

    def player(self, *args):

        self.browser.find_element_by_id(self.id_dict[self.lb.get(self.lb.curselection())]).click()

    def download_music(self,*args):

        res_word = self.lb.get(self.lb.curselection())
        rename = res_word.split("---")
        rename = rename[0] + ".mp3"
        finename = os.path.join("download",rename)
        id = int(self.downloadid[res_word])

        url = f"http://music.163.com/song/media/outer/url?id={id}.MP3"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36"}

        response = requests.get(url,headers = headers)
        with open(finename,"wb+") as f:
            f.write(response.content)
        f.close()
        self.message()

    def message(self):
        messagebox.showinfo(title="提示",message="下载成功！")

    def quit_sys(self):
        self.browser.quit()
        root.destroy()

    def next_page(self):

        js = "var q=document.documentElement.scrollTop=10000"
        self.browser.execute_script(js)
        self.browser.find_element_by_css_selector(".u-page .znxt").click()
        self.selenium_outputlist()

    def last_page(self):

        js = "var q=document.documentElement.scrollTop=10000"
        self.browser.execute_script(js)
        self.browser.find_element_by_css_selector(".u-page .zprv").click()
        self.selenium_outputlist()


"""主函数"""
if __name__ == '__main__':
    path = "download"
    if not os.path.exists(path):
        os.mkdir(path)
    root = Tk()
    root.iconbitmap("start.ico")
    root.geometry("795x775+100+10")
    root.title('music163')
    app = AnswerGUI(master=root)
    root.mainloop()