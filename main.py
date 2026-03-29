from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.core.window import Window
import threading
import requests
import json

class StorySimulatorApp(App):
    def build(self):
        # 设置窗口大小
        Window.size = (800, 600)
        
        # 主布局
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # 创建UI元素
        self.create_ui_elements()
        
        # 添加UI到主布局
        main_layout.add_widget(self.top_panel)
        main_layout.add_widget(self.chat_area)
        main_layout.add_widget(self.input_area)
        
        return main_layout
    
    def create_ui_elements(self):
        # 顶部控制面板
        self.top_panel = GridLayout(cols=2, size_hint_y=None, height=200, spacing=10)
        
        # 左侧控制区
        left_panel = GridLayout(cols=1, spacing=5)
        
        # API配置
        api_layout = GridLayout(cols=2, size_hint_y=None, height=40)
        api_layout.add_widget(Label(text="API URL:", size_hint_x=0.3))
        self.api_input = TextInput(text="http://localhost:8000/v1/chat/completions", multiline=False)
        api_layout.add_widget(self.api_input)
        left_panel.add_widget(api_layout)
        
        # AI选择
        ai_layout = GridLayout(cols=2, size_hint_y=None, height=40)
        ai_layout.add_widget(Label(text="选择AI:", size_hint_x=0.3))
        self.ai_selector = TextInput(text="默认AI", multiline=False, disabled=True)
        ai_layout.add_widget(self.ai_selector)
        left_panel.add_widget(ai_layout)
        
        # 获取AI按钮
        get_ai_btn = Button(text="获取AI列表", size_hint_y=None, height=40)
        get_ai_btn.bind(on_press=self.fetch_ai_models)
        left_panel.add_widget(get_ai_btn)
        
        # 右侧设定区
        right_panel = GridLayout(cols=1, spacing=5)
        
        # 设定输入
        settings_label = Label(text="故事设定:", size_hint_y=None, height=30)
        right_panel.add_widget(settings_label)
        
        self.settings_input = TextInput(multiline=True, size_hint_y=None, height=100)
        right_panel.add_widget(self.settings_input)
        
        # 添加设定按钮
        add_setting_btn = Button(text="添加设定", size_hint_y=None, height=40)
        add_setting_btn.bind(on_press=self.add_setting)
        right_panel.add_widget(add_setting_btn)
        
        self.top_panel.add_widget(left_panel)
        self.top_panel.add_widget(right_panel)
        
        # 聊天显示区域
        scroll = ScrollView(size_hint_y=0.6)
        self.chat_display = Label(text="欢迎使用AI故事模拟器！\n\n开始输入你的故事吧...", 
                                 text_size=(Window.width*0.9, None),
                                 halign='left', valign='top')
        self.chat_display.bind(texture_size=self.chat_display.setter('size'))
        scroll.add_widget(self.chat_display)
        self.chat_area = scroll
        
        # 输入区域
        self.input_area = GridLayout(cols=2, size_hint_y=None, height=100, spacing=10)
        
        self.user_input = TextInput(multiline=True)
        send_btn = Button(text="发送", size_hint_x=0.2)
        send_btn.bind(on_press=self.send_message)
        
        self.input_area.add_widget(self.user_input)
        self.input_area.add_widget(send_btn)
    
    def fetch_ai_models(self, instance):
        api_url = self.api_input.text.replace('/chat/completions', '/models')
        try:
            response = requests.get(api_url)
            if response.status_code == 200:
                data = response.json()
                models = [model.get('id', 'Unknown') for model in data.get('data', [])]
                popup_content = GridLayout(cols=1, padding=10, spacing=10)
                
                for model in models:
                    btn = Button(text=model, size_hint_y=None, height=40)
                    btn.bind(on_press=lambda x, m=model: self.select_ai(m))
                    popup_content.add_widget(btn)
                
                popup = Popup(title='选择AI模型', content=popup_content, 
                             size_hint=(0.8, 0.8))
                popup.open()
            else:
                self.show_popup("错误", f"获取AI列表失败: {response.status_code}")
        except Exception as e:
            self.show_popup("错误", f"网络请求失败: {str(e)}")
    
    def select_ai(self, model_name):
        self.ai_selector.text = model_name
        self.show_popup("提示", f"已选择AI: {model_name}")
    
    def add_setting(self, instance):
        setting = self.settings_input.text.strip()
        if setting:
            self.show_popup("设定已添加", f"设定内容:\n{setting[:50]}...")
            self.settings_input.text = ""
    
    def send_message(self, instance):
        user_msg = self.user_input.text.strip()
        if not user_msg:
            return
            
        # 显示用户消息
        self.update_chat_display(f"我: {user_msg}\n")
        self.user_input.text = ""
        
        # 在新线程中处理AI响应
        thread = threading.Thread(target=self.process_ai_response, args=(user_msg,))
        thread.daemon = True
        thread.start()
    
    def process_ai_response(self, user_msg):
        api_url = self.api_input.text
        headers = {"Content-Type": "application/json"}
        
        # 构建提示词
        prompt = f"用户: {user_msg}\nAI助手:"
        
        payload = {
            "model": self.ai_selector.text,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7
        }
        
        try:
            response = requests.post(api_url, headers=headers, json=payload, timeout=60)
            if response.status_code == 200:
                result = response.json()
                ai_response = result["choices"][0]["message"]["content"].strip()
                self.update_chat_display(f"AI: {ai_response}\n{'-'*50}\n")
            else:
                self.update_chat_display(f"错误: {response.status_code} - {response.text}\n")
        except Exception as e:
            self.update_chat_display(f"错误: 请求失败 - {str(e)}\n")
    
    def update_chat_display(self, message):
        self.chat_display.text += message
        self.chat_display.texture_update()
    
    def show_popup(self, title, content):
        popup_content = Label(text=content)
        popup = Popup(title=title, content=popup_content, 
                     size_hint=(0.8, 0.4))
        popup.open()

StorySimulatorApp().run()