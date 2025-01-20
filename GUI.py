from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import simpledialog
from tkinter import messagebox

from typing import List
from Document import Fapiao
from Reimbursement import Schema, Record, Certificate

class GUI:
    root: Tk = None

    paned_window: PanedWindow = None

    schema_canvas: Canvas = None
    schema_scroll_bar: Scrollbar = None
    schema_scrollable_frame: ttk.Frame = None
    
    schema: Schema = Schema()

    valid_canvas: Canvas = None
    valid_scroll_bar: Scrollbar = None
    valid_scrollable_frame: ttk.Frame = None

    style: None
    current_row = 0

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
        self.schema.del_contestant(name)
        self.display()

    def _upd_city(self):
        name = simpledialog.askstring("输入", "举办城市:")
        self.schema.upd_city(name)
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
            self.schema.add_traffic(Record(file_path))
        self.display()

    def _del_traffic(self, record: Record):
        self.schema.del_traffic(record)
        self.display()

    def _add_hostel(self):
        file_path = filedialog.askopenfilename(
            title="选择一个发票文件",  # 对话框标题
            filetypes=[
                    ("发票", "*.pdf")]  # 文件类型过滤
        )
        if file_path:
            self.schema.add_hostel(Record(file_path))
        self.display()

    def _del_hostel(self, record: Record):
        self.schema.del_hostel(record)
        self.display()

    def _add_registration(self):
        file_path = filedialog.askopenfilename(
            title="选择一个发票文件",  # 对话框标题
            filetypes=[
                    ("发票", "*.pdf")]  # 文件类型过滤
        )
        if file_path:
            self.schema.add_registration(Record(file_path))
        self.display()

    def _validate(self):
        self.schema.validate()
        self.display()

    def _del_registration(self, record: Record):
        self.schema.del_registration(record)
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
        
        ttk.Label(self.schema_scrollable_frame, text='参赛队员（点击删除）', style='Contestant.TLabel').grid(column=0, row=self.current_row, sticky='w')
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

        if record_type == 'traffic':  
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
            else:
                ttk.Label(self.schema_scrollable_frame, text='合订单无需行程单证明').grid(column=1, row=self.current_row, sticky='w')
                self.current_row += 1

    def _display_traffic(self):
        ttk.Label(self.schema_scrollable_frame, text='交通').grid(column=0, row=self.current_row, sticky='w')
        self.current_row += 1
        for i, record in enumerate(self.schema.traffic):
            ttk.Button(self.schema_scrollable_frame, text=str(i), command=lambda r=record: self._del_traffic(r)).grid(column=0, row=self.current_row, sticky='w')
            self._display_record(record, record_type='traffic')
        ttk.Button(self.schema_scrollable_frame, text='添加发票/合订单', command=self._add_traffic).grid(column=0, row=self.current_row, sticky='w')
        self.current_row += 1

    def _display_hostel(self):
        ttk.Label(self.schema_scrollable_frame, text='住宿').grid(column=0, row=self.current_row, sticky='w')
        self.current_row += 1
        for i, record in enumerate(self.schema.hostel):
            ttk.Label(self.schema_scrollable_frame, text=str(i)).grid(column=0, row=self.current_row, sticky='w')
            self._display_record(record, record_type='hostel')
        ttk.Button(self.schema_scrollable_frame, text='添加发票', command=self._add_hostel).grid(column=0, row=self.current_row, sticky='w')
        self.current_row += 1

    def _display_registration(self):
        ttk.Label(self.schema_scrollable_frame, text='报名费').grid(column=0, row=self.current_row, sticky='w')
        self.current_row += 1
        for i, record in enumerate(self.schema.registration):
            ttk.Label(self.schema_scrollable_frame, text=str(i)).grid(column=0, row=self.current_row, sticky='w')
            self._display_record(record, record_type='registration')
        ttk.Button(self.schema_scrollable_frame, text='添加发票', command=self._add_registration).grid(column=0, row=self.current_row, sticky='w')
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
            print(current_row)
            ttk.Label(self.valid_scrollable_frame, text=w, foreground='orange').grid(column=0,row=current_row, sticky='w')
            current_row += 1


    def _display_validation_generation(self):
        ttk.Button(self.schema_scrollable_frame, text='校验', command=self._validate).grid(column=0, row=self.current_row, sticky='w')
        ttk.Button(self.schema_scrollable_frame, text='生成').grid(column=1, row=self.current_row, sticky='w')
        self.current_row += 1

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
        self._display_error_message()

    def _create_scrollable(self):
        self.schema_container = ttk.Frame(self.paned_window)
        self.paned_window.add(self.schema_container, weight=1)
        # self.schema_container.pack(side="top", fill="both", expand=True, padx=10, pady=10)
        
        self.schema_canvas = Canvas(self.schema_container)

        self.schema_scrollbar = Scrollbar(self.schema_container, orient="vertical", command=self.schema_canvas.yview)
        self.schema_scrollable_frame = ttk.Frame(self.schema_canvas)

        # 将滚动条与Canvas关联
        self.schema_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.schema_canvas.configure(
                scrollregion=self.schema_canvas.bbox("all")
            )
        )

        # 将Frame放入Canvas中
        self.schema_canvas.create_window((0, 0), window=self.schema_scrollable_frame, anchor="nw")
        self.schema_canvas.configure(yscrollcommand=self.schema_scrollbar.set)

        # 布局Canvas和滚动条
        self.schema_canvas.pack(side="left", fill="both", expand=True)
        self.schema_scrollbar.pack(side="right", fill="y")

    def _create_error_display(self):
        self.valid_container = ttk.Frame(self.paned_window)
        self.paned_window.add(self.valid_container, weight=1)
        # self.valid_container.pack(side="bottom", fill="both", expand=True, padx=10, pady=10)
        
        self.valid_canvas = Canvas(self.valid_container)

        self.valid_scrollbar = Scrollbar(self.valid_container, orient="vertical", command=self.valid_canvas.yview)
        self.valid_scrollable_frame = ttk.Frame(self.valid_canvas)

        # 将滚动条与Canvas关联
        self.valid_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.valid_canvas.configure(
                scrollregion=self.valid_canvas.bbox("all")
            )
        )

        # 将Frame放入Canvas中
        self.valid_canvas.create_window((0, 0), window=self.valid_scrollable_frame, anchor="nw")
        self.valid_canvas.configure(yscrollcommand=self.valid_scrollbar.set)

        # 布局Canvas和滚动条
        self.valid_canvas.pack(side="left", fill="both", expand=True)
        self.valid_scrollbar.pack(side="right", fill="y")

    def run(self):
        self.root = Tk()
        self.root.title("Reimbursement Automaton")
        self.root.geometry("960x640")
        self.style = ttk.Style()
        self.style.configure("Vertical.TPanedwindow", background="silver", width=1)

        self.paned_window = ttk.PanedWindow(self.root, orient="vertical")
        self.paned_window.pack(fill="both", expand=True)
        self.paned_window.configure(style="Vertical.TPanedwindow")  # 使用默认样式
        # self.style.theme_use("alt")

        self._create_scrollable()
        self._create_error_display()


        # self.scrollable_frame.grid()

        # self.root.grid_columnconfigure(0, pad=10)
        # self.root.grid_columnconfigure(1, pad=10)
        self.display()
        self.root.mainloop()