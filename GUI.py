from tkinter import *
from tkinter import ttk, filedialog, simpledialog, messagebox

from typing import List
from Document import Fapiao, PaperMaterial, Combined
from Reimbursement import Schema, Record, Certificate

import os

class GUI:
    root: Tk = None

    paned_window: PanedWindow = None

    schema_container: ttk.Frame = None
    schema_canvas: Canvas = None
    schema_scrollbar: Scrollbar = None
    schema_scrollable_frame: ttk.Frame = None
    
    schema: Schema = Schema()

    valid_container: ttk.Frame = None
    valid_canvas: Canvas = None
    valid_scrollbar: Scrollbar = None
    valid_scrollable_frame: ttk.Frame = None

    tools_container: ttk.Frame = None

    style: None
    current_row = 0

    path_entry: Entry = None

    def _refresh_schema_window(self):
        for widget in self.schema_scrollable_frame.winfo_children():
            widget.destroy()

    def _refresh_valid_window(self):
        for widget in self.valid_scrollable_frame.winfo_children():
            widget.destroy()

    def _add_contestant(self):
        name = simpledialog.askstring("输入", "队员姓名:")
        if name: self.schema.add_contestant(name)
        self.display()

    def _del_contestant(self, name: str):
        if name: self.schema.del_contestant(name)
        self.display()

    def _upd_city(self):
        name = simpledialog.askstring("输入", "举办城市:")
        if name: self.schema.upd_city(name)
        self.display()

    def _add_trip(self, record: Record, home_city: str, dest_city: str, contestants: List[str]):        
        popup = Toplevel(self.root)
        popup.title('添加行程')
        popup.lift()
        options_trips = [home_city + '-' + dest_city, dest_city + '-' + home_city]
        options_contestants = contestants

        frm = ttk.Frame(popup, padding=10)
        frm.grid()
        label_trips = ttk.Label(popup, text='选择选手').grid(column=0, row=0, sticky='w')
        box_contestants = ttk.Combobox(popup, values=options_contestants, state="readonly")
        box_contestants.grid(column=1,row=0, sticky='w')
        label_trips = ttk.Label(popup, text='选择行程').grid(column=2, row=0, sticky='w')
        box_trips = ttk.Combobox(popup, values=options_trips, state="readonly")
        box_trips.grid(column=3,row=0, sticky='w')

        def get_selection():
            try:
                selected_trip = box_trips.get()  # 获取选中的值
                selected_contestant = box_contestants.get()
                if selected_trip is None or selected_trip == '':
                    raise ValueError('请选择行程')
                if selected_contestant is None or selected_contestant == '':
                    raise ValueError('请选择选手')
                record.add_trip(selected_trip, selected_contestant)
            except ValueError as e:
                messagebox.showwarning("错误：", str(e))
            popup.destroy()  # 关闭弹窗

        button = ttk.Button(popup, text="确定", command=get_selection).grid(column=3, row=2, sticky='w')

        self.root.wait_window(popup)
        self.display()

    def _del_trip(self, record: Record, trip: tuple):
        record.del_trip(trip)
        self.display()

    def _add_cert(self, record: Record):
        file_path = filedialog.askopenfilename(
            title="选择一个行程单文件",  # 对话框标题
            filetypes=[("打车行程单", "*.pdf"),
                    ("舱位截图", "*.jpg *.jpeg *.png *.gif *.bmp *.tiff *.tif *.webp *.ico *.heic *.heif")]  # 文件类型过滤
        )
        if file_path:  # 如果用户选择了文件
            record.add_cert(Certificate(file_path))
        self.display()

    def _del_cert(self, record: Record, cert: Certificate):
        record.del_cert(cert)
        self.display()

    def _add_traffic(self):
        file_path = filedialog.askopenfilename(
            title="选择一个发票/合订单文件",  # 对话框标题
            filetypes=[("发票", "*.pdf"),
                    ("合订单", "*.png")]  # 文件类型过滤
        )
        if file_path:
            self.schema.add_record(record_type='traffic', record=Record(file_path))
        self.display()

    def _del_traffic(self, record: Record):
        self.schema.del_record(record_type='traffic', record=record)
        self.display()

    def _add_hostel(self):
        file_path = filedialog.askopenfilename(
            title="选择一个发票文件",  # 对话框标题
            filetypes=[
                    ("发票", "*.pdf")]  # 文件类型过滤
        )
        if file_path:
            self.schema.add_record(record_type='hostel', record=Record(file_path))
        self.display()

    def _del_hostel(self, record: Record):
        self.schema.del_record(record_type='hostel', record=record)
        self.display()

    def _add_registration(self):
        file_path = filedialog.askopenfilename(
            title="选择一个发票文件",  # 对话框标题
            filetypes=[
                    ("发票", "*.pdf")]  # 文件类型过滤
        )
        if file_path:
            self.schema.add_record(record_type='registration', record=Record(file_path))
        self.display()

    def _del_registration(self, record: Record):
        self.schema.del_record(record_type='registration', record=record)
        self.display()

    def _add_paper(self):
        popup = Toplevel(self.root)
        popup.title('添加纸质报销材料')
        popup.lift()

        frm = ttk.Frame(popup, padding=10)
        frm.grid()
        label_amount = ttk.Label(popup, text='金额（元）').grid(column=0, row=0, sticky='w')
        entry_amount = ttk.Entry(popup, width=10)
        entry_amount.grid(column=1,row=0, sticky='w')
        label_text = ttk.Label(popup, text='材料说明').grid(column=0, row=1, sticky='w')
        entry_text = ttk.Entry(popup, width=50)
        entry_text.grid(column=1,row=1, sticky='w')

        def get_entry():
            try:
                try:
                    entered_amount = float(entry_amount.get())
                except ValueError as e:
                    raise ValueError('请保证输入的金额是合法数字')
                entered_text = entry_text.get()
                
                if entered_text is None or entered_text == '':
                    raise ValueError('请输入说明')
                record = Record.from_paper(PaperMaterial(total_amount=entered_amount, text=entered_text))
                self.schema.add_record(record_type='paper', record=record)
            except ValueError as e:
                messagebox.showwarning("错误：", str(e))
            popup.destroy()  # 关闭弹窗

        button = ttk.Button(popup, text="确定", command=get_entry).grid(column=3, row=2, sticky='w')

        self.root.wait_window(popup)
        self.display()

    def _del_paper(self, record: Record):
        self.schema.del_record(record_type='paper', record=record)
        self.display()

    def _validate(self):
        self.schema.validate()
        self.display()

    def _generate(self):
        try:
            dir_path = self.path_entry.get()
            if dir_path and os.path.isdir(dir_path):
                self.schema.generate(dir_path)
            else:
                raise FileNotFoundError('请选择合法的目标文件夹')
        except FileNotFoundError as e:
            messagebox.showwarning("错误：", str(e))
        self.display()

    def _display_contestants(self):
        # self.style.map("Contestant.TButton",
        #                 background=[("active", "red"), ("pressed", "red")],  # 鼠标悬停和按下时的背景色
        #                 foreground=[("active", "white"), ("pressed", "yellow")])  # 鼠标悬停和按下时的前景色
        # self.style.map("ContestantAdd.TButton",
        #                 background=[("active", "green"), ("pressed", "red")],  # 鼠标悬停和按下时的背景色
        #                 foreground=[("active", "white"), ("pressed", "yellow")])  # 鼠标悬停和按下时的前景色
        # self.style.configure("Contestant.TLabel",
        #                      foreground="black",
        #                      background="white")
        
        ttk.Label(self.schema_scrollable_frame, text='参赛队员：', style='Contestant.TLabel').grid(column=0, row=self.current_row, sticky='w')
        for index, contestant in enumerate(self.schema.contestants):
            ttk.Button(self.schema_scrollable_frame, text=contestant,
                       command=lambda c=contestant: self._del_contestant(c),
                       style='Contestant.TButton').grid(column=index + 1,row=self.current_row, sticky='w')
        
        ttk.Button(self.schema_scrollable_frame, text='添加队员', command=self._add_contestant, style='ContestantAdd.TButton').grid(column=len(self.schema.contestants) + 1, row=self.current_row, sticky='w')
        
        self.current_row += 1

    def _display_city(self):
        ttk.Label(self.schema_scrollable_frame, text='举办城市：' + self.schema.dest_city).grid(column=0, row=self.current_row, sticky='w')
        ttk.Button(self.schema_scrollable_frame, text="修改", command=self._upd_city).grid(column=1, row=self.current_row, sticky='w')
        self.current_row += 1

    def _display_record(self, record, record_type):
        attri, result = record.info
        
        for i, t in enumerate(attri):
            ttk.Label(self.schema_scrollable_frame, text = t + '：' + str(result[t])).grid(column=i+1, row=self.current_row, sticky='w')
        self.current_row += 1

        if record_type == 'traffic' or record_type == 'paper':  
            ttk.Label(self.schema_scrollable_frame, text='行程').grid(column=1, row=self.current_row, sticky='w')
            for i, t in enumerate(record.trips):
                ttk.Label(self.schema_scrollable_frame, text=Record.trip_to_str(t)).grid(column=2, row=self.current_row, sticky='w')
                ttk.Button(self.schema_scrollable_frame, text='删除行程', command=lambda r=record, t=t: self._del_trip(r, t)).grid(column=3, row=self.current_row, sticky='w')
                self.current_row += 1
            self.current_row += 1

            ttk.Button(self.schema_scrollable_frame, text='添加行程', command=lambda r=record: self._add_trip(r, self.schema.home_city, self.schema.dest_city, self.schema.contestants)).grid(column=1, row=self.current_row, sticky='w')
            self.current_row += 1
        
            if type(record.fapiao) == Fapiao:
                ttk.Label(self.schema_scrollable_frame, text='行程单').grid(column=1, row=self.current_row, sticky='w')
                for i, t in enumerate(record.certificates):
                    ttk.Label(self.schema_scrollable_frame, text=t.to_str()).grid(column=2, row=self.current_row, sticky='w')
                    ttk.Button(self.schema_scrollable_frame, text='删除行程单', command=lambda r=record, t=t: self._del_cert(r, t)).grid(column=3, row=self.current_row, sticky='w')
                    self.current_row += 1
                self.current_row += 1
                
                ttk.Button(self.schema_scrollable_frame, text='添加行程单', command=lambda r=record: self._add_cert(r)).grid(column=1, row=self.current_row, sticky='w')
                self.current_row += 1
            elif type(record.fapiao) == Combined:
                ttk.Label(self.schema_scrollable_frame, text='合订单无需行程单证明').grid(column=1, row=self.current_row, sticky='w')
                self.current_row += 1

    def _display_traffic(self):
        ttk.Label(self.schema_scrollable_frame, text='交通').grid(column=0, row=self.current_row, sticky='w')
        self.current_row += 1
        for i, record in enumerate(self.schema.records['traffic']):
            ttk.Button(self.schema_scrollable_frame, text=str(i), command=lambda r=record: self._del_traffic(r)).grid(column=0, row=self.current_row, sticky='w')
            self._display_record(record, record_type='traffic')
        ttk.Button(self.schema_scrollable_frame, text='添加发票/合订单', command=self._add_traffic).grid(column=0, row=self.current_row, sticky='w')
        self.current_row += 1

    def _display_hostel(self):
        ttk.Label(self.schema_scrollable_frame, text='住宿').grid(column=0, row=self.current_row, sticky='w')
        self.current_row += 1
        for i, record in enumerate(self.schema.records['hostel']):
            ttk.Button(self.schema_scrollable_frame, text=str(i), command=self._del_hostel).grid(column=0, row=self.current_row, sticky='w')
            self._display_record(record, record_type='hostel')
        ttk.Button(self.schema_scrollable_frame, text='添加发票', command=self._add_hostel).grid(column=0, row=self.current_row, sticky='w')
        self.current_row += 1

    def _display_registration(self):
        ttk.Label(self.schema_scrollable_frame, text='报名费').grid(column=0, row=self.current_row, sticky='w')
        self.current_row += 1
        for i, record in enumerate(self.schema.records['registration']):
            ttk.Button(self.schema_scrollable_frame, text=str(i), command=self._del_registration).grid(column=0, row=self.current_row, sticky='w')
            self._display_record(record, record_type='registration')
        ttk.Button(self.schema_scrollable_frame, text='添加发票', command=self._add_registration).grid(column=0, row=self.current_row, sticky='w')
        self.current_row += 1

    def _display_paper(self):
        ttk.Label(self.schema_scrollable_frame, text='纸质材料').grid(column=0, row=self.current_row, sticky='w')
        self.current_row += 1
        for i, record in enumerate(self.schema.records['paper']):
            ttk.Button(self.schema_scrollable_frame, text=str(i), command=lambda r=record: self._del_paper(r)).grid(column=0, row=self.current_row, sticky='w')
            self._display_record(record, record_type='paper')
        ttk.Button(self.schema_scrollable_frame, text='添加纸质材料', command=self._add_paper).grid(column=0, row=self.current_row, sticky='w')
        self.current_row += 1

    def _display_error_message(self):
        current_row = 0
        ttk.Label(self.valid_scrollable_frame, text='错误', foreground='red').grid(column=0,row=current_row, sticky='w')
        current_row += 1
        for e in self.schema.error:
            ttk.Label(self.valid_scrollable_frame, text=e, foreground='red').grid(column=0,row=current_row, sticky='w')
            current_row += 1
        ttk.Label(self.valid_scrollable_frame, text='警告', foreground='orange').grid(column=0,row=current_row, sticky='w')
        current_row += 1
        for w in self.schema.warning:
            ttk.Label(self.valid_scrollable_frame, text=w, foreground='orange').grid(column=0,row=current_row, sticky='w')
            current_row += 1


    def _display_validation_generation(self):
        current_row = 0
        ttk.Button(self.tools_container, text='校验', command=self._validate).grid(column=0, row=current_row, sticky='w')
        ttk.Button(self.tools_container, text='生成', command=self._generate).grid(column=1, row=current_row, sticky='w')
        self.path_entry = ttk.Entry(self.tools_container, width=50)
        self.path_entry.grid(column=2,row=current_row, sticky='w')
        def select_directory():
            """打开目录选择对话框，并将选择的路径更新到 Entry 组件中"""
            directory = filedialog.askdirectory()  # 弹出目录选择对话框
            if directory:  # 如果用户选择了目录
                self.path_entry.delete(0, END)  # 清空当前内容
                self.path_entry.insert(0, directory)  # 插入新路径
        ttk.Button(self.tools_container, text="选择目标文件夹", command=select_directory).grid(column=3, row=current_row, sticky='w')
        ttk.Label(self.tools_container, text='上次成功生成时间：{time}'.format(time=self.schema.last_gen_time), foreground='green').grid(column=4, row=current_row, sticky='w')

    def display(self):
        self.current_row = 0
        self._refresh_schema_window()
        self._refresh_valid_window()
        self._display_validation_generation()
        self._display_contestants()
        self._display_city()
        self._display_traffic()
        self._display_hostel()
        self._display_registration()
        self._display_paper()
        self._display_error_message()

    def _create_scrollable_frame(self, **params):
        container = ttk.Frame(self.paned_window)
        self.paned_window.add(container, **params)
        # self.container.pack(side="top", fill="both", expand=True, padx=10, pady=10)
        
        canvas = Canvas(container)
        canvas.configure(height=80)

        scrollbar = Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        # 将滚动条与Canvas关联
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        # 将Frame放入Canvas中
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # 布局Canvas和滚动条
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        return container, canvas, scrollable_frame, scrollbar

    def _create_tools(self):
        self.tools_container = ttk.Frame(self.paned_window)
        self.paned_window.add(self.tools_container, weight=0)

    def run(self):
        self.root = Tk()
        self.root.title("Reimaton")
        self.root.geometry("960x640")
        self.style = ttk.Style()
        self.style.configure("Vertical.TPanedwindow", background="silver", width=1)

        self.paned_window = ttk.PanedWindow(self.root, orient="vertical")
        self.paned_window.pack(fill="both", expand=True)
        self.paned_window.configure(style="Vertical.TPanedwindow")  # 使用默认样式
        # self.style.theme_use("alt")

        self.schema_container, self.schema_canvas, self.schema_scrollable_frame, self.schema_scrollbar = self._create_scrollable_frame(weight=1)
        self.valid_container, self.valid_canvas, self.valid_scrollable_frame, self.valid_scrollbar = self._create_scrollable_frame(weight=0)
        self._create_tools()


        # self.scrollable_frame.grid()

        # self.root.grid_columnconfigure(0, pad=10)
        # self.root.grid_columnconfigure(1, pad=10)
        self.display()
        self.root.mainloop()