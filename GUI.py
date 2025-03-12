from tkinter import *
from tkinter import ttk, filedialog, simpledialog, messagebox

from typing import List
from Document import Fapiao, PaperMaterial, Combined
from Reimbursement import Schema, Record, Certificate

import os
import ctypes
import yaml

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

    def _refresh_frame(self, frame):
        for widget in frame.winfo_children():
            widget.destroy()

    def _create_widget_in_grid(self, widget_func, location, widget_params, grid_params):
        widget = widget_func(location, **widget_params)
        if 'sticky' not in grid_params: grid_params['sticky'] = 'W'
        if 'padx' not in grid_params: grid_params['padx'] = 10
        if 'pady' not in grid_params: grid_params['pady'] = 2
        widget.grid(**grid_params)
        return widget

    def _label(self, location, widget_params, grid_params):
        return self._create_widget_in_grid(ttk.Label, location, widget_params, grid_params)
    
    def _button(self, location, widget_params, grid_params):
        return self._create_widget_in_grid(ttk.Button, location, widget_params, grid_params)

    def _combobox(self, location, widget_params, grid_params):
        return self._create_widget_in_grid(ttk.Combobox, location, widget_params, grid_params)

    def _entry(self, location, widget_params, grid_params):
        return self._create_widget_in_grid(ttk.Entry, location, widget_params, grid_params)

    def _add_contestant(self):
        popup = Toplevel(self.root, background='#FFFFFF', padx=10, pady=10)
        popup.title('添加选手')
        popup.lift()

        self._label(popup, widget_params={'text': '添加选手'}, grid_params={'column': 0, 'row': 0})
        entry_contestant = self._entry(popup,
                                         widget_params={'width': 15},
                                         grid_params={'column': 1, 'row': 0})

        def get_selection():
            try:
                contestant = entry_contestant.get()  # 获取选中的值
                if contestant is None or contestant == '':
                    raise ValueError('请输入选手')
                self.schema.add_contestant(contestant)
            except ValueError as e:
                messagebox.showwarning("错误：", str(e))
            popup.destroy()  # 关闭弹窗

        self._button(popup, widget_params={'text': '确定', 'command': get_selection, 'style': 'confirm.TButton'}, grid_params={'column': 3, 'row': 2})
        
        self.root.wait_window(popup)
        self.display()

    def _del_contestant(self, name: str):
        if name: self.schema.del_contestant(name)
        self.display()

    def _upd_city(self):
        popup = Toplevel(self.root, background='#FFFFFF', padx=10, pady=10)
        popup.title('修改城市')
        popup.lift()

        self._label(popup, widget_params={'text': '修改城市'}, grid_params={'column': 0, 'row': 0})
        entry_contestant = self._entry(popup,
                                         widget_params={'width': 15},
                                         grid_params={'column': 1, 'row': 0})

        def get_selection():
            try:
                contestant = entry_contestant.get()  # 获取选中的值
                if contestant is None or contestant == '':
                    raise ValueError('请输入城市')
                self.schema.upd_city(contestant)
            except ValueError as e:
                messagebox.showwarning("错误：", str(e))
            popup.destroy()  # 关闭弹窗

        self._button(popup, widget_params={'text': '确定', 'command': get_selection, 'style': 'confirm.TButton'}, grid_params={'column': 3, 'row': 2})
        
        self.root.wait_window(popup)
        self.display()

    def _add_trip(self, record: Record, home_city: str, dest_city: str, contestants: List[str]):        
        popup = Toplevel(self.root, background='#FFFFFF', padx=10, pady=10)
        popup.title('添加行程')
        popup.lift()
        options_trips = [home_city + '-' + dest_city, dest_city + '-' + home_city]
        options_contestants = contestants

        self._label(popup, widget_params={'text': '选择选手'}, grid_params={'column': 0, 'row': 0})
        box_contestants = self._combobox(popup,
                                         widget_params={'values': options_contestants, 'state': 'readonly', 'width': 15},
                                         grid_params={'column': 1, 'row': 0})
        self._label(popup, widget_params={'text': '选择行程'}, grid_params={'column': 2, 'row': 0})
        box_trips = self._combobox(popup,
                                         widget_params={'values': options_trips, 'state': 'readonly', 'width': 15},
                                         grid_params={'column': 3, 'row': 0})

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

        self._button(popup, widget_params={'text': '确定', 'command': get_selection, 'style': 'confirm.TButton'}, grid_params={'column': 3, 'row': 2, 'sticky': 'E'})

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
        popup = Toplevel(self.root, background="#FFFFFF", padx=10, pady=10)
        popup.title('➕添加纸质报销材料')
        popup.lift()

        label_amount = self._label(popup, widget_params={'text': '金额（元）'}, grid_params={'column': 0, 'row': 0})
        entry_amount = self._entry(popup, widget_params={'width': 50}, grid_params={'column': 1, 'row': 0})
        label_text = self._label(popup, widget_params={'text': '材料说明'}, grid_params={'column': 0, 'row': 1})
        entry_text = self._entry(popup, widget_params={'width': 50}, grid_params={'column': 1, 'row': 1})

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

        self._button(popup, widget_params={'text': "确定", 'command': get_entry}, grid_params={'column': 3, 'row': 2})

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

    def _store(self):
        folder_path = filedialog.askdirectory(
            title="选择存储的文件夹"  # 对话框标题
        )
        
        if folder_path:
            traffic_data = [record.to_dict() for record in self.schema.records['traffic']]
            paper_data = [record.to_dict() for record in self.schema.records['paper']]
            hostel_data = [record.to_dict() for record in self.schema.records['hostel']]
            registration_data = [record.to_dict() for record in self.schema.records['registration']]

            all_data = {
                'contestants': self.schema.contestants,
                'dest_city': self.schema.dest_city,
                'traffic': traffic_data,
                'paper': paper_data,
                'hostel': hostel_data,
                'registration': registration_data
            }

            Record.write_to_json(folder_path, all_data)
        
        self.display()

    def _read(self):
        file_path = filedialog.askopenfilename(
            title="选择一个 JSON 文件",  # 对话框标题
            filetypes=[("JSON 文件", "*.json")]  # 文件类型过滤
        )
        
        if file_path:
            all_data = Record.read_from_json(file_path)
            self.schema.__init__()
            
            for contestant in all_data['contestants']:
                self.schema.add_contestant(contestant)

            self.schema.upd_city(all_data['dest_city'])

            for r in all_data['traffic']:
                record = Record(r['fapiao'])
                for certificate in r['certificates']:
                    record.add_cert(Certificate(certificate))
                for trip in r['trips']:
                    record.add_trip(trip['city1'] + '-' + trip['city2'], trip['contestant'])
                self.schema.add_record(record_type='traffic', record=record)

            for r in all_data['hostel']:
                record = Record(r['fapiao'])
                self.schema.add_record(record_type='hostel', record=record)

            for r in all_data['paper']:
                record = Record.from_paper(PaperMaterial(total_amount=r['fapiao']['total_amount'], text=r['fapiao']['total_amount']))
                for trip in r['trips']:
                    record.add_trip(trip['city1'] + '-' + trip['city2'], trip['contestant'])
                self.schema.add_record(record_type='paper', record=record)
                
            for r in all_data['registration']:
                record = Record(r['fapiao'])
                self.schema.add_record(record_type='registration', record=record)

        self.display()

    def _display_contestants(self):
        self._label(self.schema_scrollable_frame,
                    widget_params={'text': '👥参赛队员：'},
                    grid_params={'column': 0, 'row': self.current_row})
        for index, contestant in enumerate(self.schema.contestants):
            self._button(self.schema_scrollable_frame,
                         widget_params={'text': contestant, 'style': 'del.TButton', 'command': lambda c=contestant: self._del_contestant(c)},
                         grid_params={'column': index + 1, 'row': self.current_row})
        self._button(self.schema_scrollable_frame,
                     widget_params={'text': '➕添加队员', 'command': self._add_contestant},
                     grid_params={'column': len(self.schema.contestants) + 1, 'row': self.current_row})
        self.current_row += 1

    def _display_city(self):
        self._label(self.schema_scrollable_frame,
                    widget_params={'text': '🗺举办城市：' + self.schema.dest_city},
                    grid_params={'column': 0, 'row': self.current_row})
        self._button(self.schema_scrollable_frame,
                     widget_params={'text': "✍修改", 'command': self._upd_city},
                     grid_params={'column': 1, 'row': self.current_row})
        self.current_row += 1

    def _display_record(self, record, record_type):
        styles = {'路径': 'pink.TLabel', '金额': 'teal.TLabel', '类型': 'yellow.TLabel'}
        icon = {'路径': '📁', '金额': '¥', '类型': ''}
        attri, result = record.info
        for i, t in enumerate(attri):
            self._label(self.schema_scrollable_frame,
                        widget_params={'text': icon[t] + str(result[t]), 'style': styles[t]},
                        grid_params={'column': i+2, 'row': self.current_row, 'sticky': ''})
        self.current_row += 1

        if record_type == 'traffic' or record_type == 'paper':  
            self._label(self.schema_scrollable_frame,
                        widget_params={'text': '行程'},
                        grid_params={'column': 1, 'row': self.current_row})
            for i, t in enumerate(record.trips):
                self._label(self.schema_scrollable_frame,
                            widget_params={'text': Record.trip_to_str(t)},
                            grid_params={'column': 2, 'row': self.current_row})
                self._button(self.schema_scrollable_frame,
                             widget_params={'text': '删除行程', 'style': 'del.TButton', 'command': lambda r=record, t=t: self._del_trip(r, t)}, 
                             grid_params={'column': 5, 'row': self.current_row})
                self.current_row += 1
            self.current_row += 1

            self._button(self.schema_scrollable_frame,
                         widget_params={'text': '➕添加行程', 'command': lambda r=record: self._add_trip(r, self.schema.home_city, self.schema.dest_city, self.schema.contestants)},
                         grid_params={'column': 1, 'row': self.current_row})
            self.current_row += 1
        
            

            if type(record.fapiao) == Fapiao:
                self._label(self.schema_scrollable_frame,
                            widget_params={'text': '行程单'},
                            grid_params={'column': 1, 'row': self.current_row})
                for i, t in enumerate(record.certificates):
                    attri, result = t.info
                    for j, s in enumerate(attri):
                        self._label(self.schema_scrollable_frame,
                                    widget_params={'text': icon[s] + str(result[s]), 'style': styles[s]},
                                    grid_params={'column': 2+j, 'row': self.current_row, 'sticky': ''})
                    self._button(self.schema_scrollable_frame,
                                 widget_params={'text': '删除行程单', 'style': 'del.TButton', 'command': lambda r=record, t=t: self._del_cert(r, t)},
                                 grid_params={'column': 2+len(attri), 'row': self.current_row})
                    self.current_row += 1
                self.current_row += 1   
                
                self._button(self.schema_scrollable_frame,
                             widget_params={'text': '➕添加行程单', 'command': lambda r=record: self._add_cert(r)},
                             grid_params={'column': 1, 'row': self.current_row})
                self.current_row += 1
            elif type(record.fapiao) == Combined:
                self._label(self.schema_scrollable_frame,
                            widget_params={'text': '合订单无需行程单证明'},
                            grid_params={'column': 1, 'row': self.current_row})
                self.current_row += 1

    def _display_reim_item(self, type, add_text, add_func, del_func):
        icon = {'traffic': '🛫', 'hostel': '🏠', 'registration': '✅', 'paper': '📃'}
        self._label(self.schema_scrollable_frame, widget_params={'text': icon[type] + Schema.name[type]}, grid_params={'column': 0, 'row': self.current_row})
        self.current_row += 1
        for i, record in enumerate(self.schema.records[type]):
            self._button(self.schema_scrollable_frame, widget_params={'text': str(i), 'command': lambda r=record: del_func(r), 'style': 'del.TButton'}, grid_params={'column': 0, 'row': self.current_row})
            self._display_record(record, record_type=type)
        self._button(self.schema_scrollable_frame, widget_params={'text': add_text, 'command': add_func}, grid_params={'column': 0, 'row': self.current_row})
        self.current_row += 1

    def _display_traffic(self):
        self._display_reim_item(type='traffic', add_text='➕发票/合订单', add_func=self._add_traffic, del_func=self._del_traffic)

    def _display_hostel(self):
        self._display_reim_item(type='hostel', add_text='➕添加发票', add_func=self._add_hostel, del_func=self._del_hostel)

    def _display_registration(self):
        self._display_reim_item(type='registration', add_text='➕添加发票', add_func=self._add_registration, del_func=self._del_registration)

    def _display_paper(self):
        self._display_reim_item(type='paper', add_text='➕添加纸质材料', add_func=self._add_paper, del_func=self._del_paper)

    def _display_error_message(self):
        current_row = 0
        self._label(self.valid_scrollable_frame, widget_params={'text': '❌错误', 'foreground': 'red'}, grid_params={'column': 0, 'row': current_row, 'pady': 0})
        current_row += 1
        for e in self.schema.error:
            self._label(self.valid_scrollable_frame, widget_params={'text': e, 'foreground': 'red', 'style': 'Error.TLabel'}, grid_params={'column': 0, 'row': current_row})
            current_row += 1
        self._label(self.valid_scrollable_frame, widget_params={'text': '⚠警告', 'foreground': 'orange'}, grid_params={'column': 0, 'row': current_row, 'pady': 0})
        current_row += 1
        for w in self.schema.warning:
            self._label(self.valid_scrollable_frame, widget_params={'text': w, 'foreground': 'orange', 'style': 'Warning.TLabel'}, grid_params={'column': 0, 'row': current_row})
            current_row += 1


    def _display_validation_generation(self):
        current_row = 0
        self._button(self.tools_container, widget_params={'text': '💾存储', 'style': 'purple.TButton', 'command': self._store}, grid_params={'column': 0, 'row': current_row})
        self._button(self.tools_container, widget_params={'text': '🕮读取', 'style': 'pink.TButton', 'command': self._read}, grid_params={'column': 1, 'row': current_row})
        self._button(self.tools_container, widget_params={'text': '🛠校验', 'style': 'yellow.TButton', 'command': self._validate}, grid_params={'column': 2, 'row': current_row})
        self._button(self.tools_container, widget_params={'text': '🏭生成', 'style': 'teal.TButton', 'command': self._generate}, grid_params={'column': 3, 'row': current_row})

        self.path_entry = self._entry(self.tools_container, widget_params={'width': 50}, grid_params={'column': 4, 'row': current_row})
        def select_directory():
            """打开目录选择对话框，并将选择的路径更新到 Entry 组件中"""
            directory = filedialog.askdirectory()  # 弹出目录选择对话框
            if directory:  # 如果用户选择了目录
                self.path_entry.delete(0, END)  # 清空当前内容
                self.path_entry.insert(0, directory)  # 插入新路径
        self._button(self.tools_container, widget_params={'text': '📂选择目标文件夹', 'command': select_directory}, grid_params={'column': 5, 'row': current_row})
        self._label(self.tools_container, widget_params={'text': '上次成功生成时间：{time}'.format(time=self.schema.last_gen_time), 'foreground': 'green'}, grid_params={'column': 6, 'row': current_row})

    def display(self):
        self.current_row = 0
        self._refresh_frame(self.schema_scrollable_frame)
        self._refresh_frame(self.valid_scrollable_frame)
        self._display_validation_generation()
        self._display_contestants()
        self._display_city()
        self._display_traffic()
        self._display_hostel()
        self._display_registration()
        self._display_paper()
        self._display_error_message()

    # def _create_scrollable_frame(self, **params):
    #     container = ttk.Frame(self.paned_window)
    #     self.paned_window.add(container, **params)
    #     # self.container.pack(side="top", fill="both", expand=True, padx=10, pady=10)
    #     container.pack(fill="both", expand=True)
    #     canvas = Canvas(container)
    #     # canvas.configure(height=10)

    #     scrollbar = Scrollbar(container, orient="vertical", command=canvas.yview)
    #     scrollable_frame = ttk.Frame(canvas)

    #     # 将滚动条与Canvas关联
    #     scrollable_frame.bind(
    #         "<Configure>",
    #         lambda e: canvas.configure(
    #             scrollregion=canvas.bbox("all")
    #         )
    #     )

    #     # 将Frame放入Canvas中
    #     canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    #     canvas.configure(yscrollcommand=scrollbar.set)

    #     # 布局Canvas和滚动条
    #     # scrollable_frame.pack(fill="both", expand=True)
    #     canvas.pack(side="left", fill="both", expand=True)
    #     scrollbar.pack(side="right", fill="y")
    #     return container, canvas, scrollable_frame, scrollbar

    def _create_scrollable_frame(self, **params):
        container = ttk.Frame(self.paned_window)
        self.paned_window.add(container, **params)
        
        # 确保父容器可扩展
        # container.pack(fill="both", expand=True)  # ✅ 关键修复
        
        canvas = Canvas(container, bg="#FFFFFF", height=200)  # ✅ 移除 height=10
        scrollbar = Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        # 绑定滚动区域更新事件
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-e.delta/60), "units"))

        # 将 Frame 放入 Canvas（不要额外调用 pack!）
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # 正确布局组件
        canvas.pack(side="left", fill="both", expand=True)
        # scrollable_frame.pack(fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        return container, canvas, scrollable_frame, scrollbar

    def _create_tools(self):
        self.tools_container = ttk.Frame(self.paned_window)
        self.tools_container.pack(side='left', fill='both', expand=False)
        self.paned_window.add(self.tools_container, weight=0)

    def _set_config(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')
        with open("style.yaml", "r", encoding="utf-8") as file:
            config = yaml.safe_load(file)
            for widget, properties in config['Custom'].items():
                # print(widget, properties)
                if "map" in properties:
                    self.style.map(widget, **properties["map"])
                    del properties["map"]
                self.style.configure(widget, **properties)

    def run(self):
        self.root = Tk()
        
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
        ScaleFactor=ctypes.windll.shcore.GetScaleFactorForDevice(0)
        self.root.tk.call('tk', 'scaling', ScaleFactor/75)
        
        self.root.title("Reimaton")
        self.root.iconbitmap("logo.ico")
        self.root.wm_iconbitmap("logo.ico")
        self.root.geometry('{0}x{1}'.format(self.root.winfo_screenwidth()-100, self.root.winfo_screenheight()-100))
        self.root.state('zoomed')
        
        self._set_config()

        self.paned_window = ttk.PanedWindow(self.root, orient="vertical")
        self.paned_window.pack(fill="both", expand=True)

        self.schema_container, self.schema_canvas, self.schema_scrollable_frame, self.schema_scrollbar = self._create_scrollable_frame(weight=1)
        self.valid_container, self.valid_canvas, self.valid_scrollable_frame, self.valid_scrollbar = self._create_scrollable_frame(weight=0)
        self._create_tools()

        self.display()
        self.root.mainloop()