import tkinter as tk
import tkinter.ttk as ttk
from tkinter import scrolledtext, Canvas
import requests
import random
import json
from datetime import datetime

class ChatBubble(tk.Frame):
    def __init__(self, parent, message, is_user=False, sender_name=None):
        super().__init__(parent, bg='white')
        
        # 创建气泡容器
        self.bubble = tk.Frame(self, bg='white')
        self.bubble.pack(pady=5, anchor='e' if is_user else 'w')
        
        # 创建消息内容容器（包含头像、名字和消息）
        content_frame = tk.Frame(self.bubble, bg='white')
        content_frame.pack(fill='x')
        
        # 创建头像和名字的水平容器
        header_frame = tk.Frame(content_frame, bg='white')
        header_frame.pack(fill='x', anchor='w')
        
        # 加载头像图片
        try:
            avatar_path = "./images/user_avatar.png" if is_user else "./images/pet_avatar.png"
            avatar_image = tk.PhotoImage(file=avatar_path).subsample(4, 4)
            avatar_label = tk.Label(
                header_frame,
                image=avatar_image,
                bg='white'
            )
            avatar_label.image = avatar_image  # 保持引用
            
            # 头像始终在最左侧或最右侧
            if is_user:
                avatar_label.pack(side='right', padx=(10, 0))
            else:
                avatar_label.pack(side='left', padx=(0, 10))
        except Exception as e:
            print(f"无法加载头像: {e}")
        
        # 添加发送者名字（与头像在同一个frame中）
        if sender_name:
            name_label = tk.Label(
                header_frame,
                text=sender_name,
                font=('Arial', 9),
                fg='#666666',
                bg='white'
            )
            if is_user:
                name_label.pack(side='right', padx=(0, 5))
            else:
                name_label.pack(side='left', padx=(5, 0))
        
        # 创建消息内容容器
        message_container = tk.Frame(content_frame, bg='white')
        message_container.pack(fill='x', pady=(5, 0))
        
        # 创建消息气泡
        msg_frame = tk.Frame(
            message_container,
            bg='#92B3A5' if is_user else '#FFFFFF',
            bd=1,
            relief='solid'
        )
        msg_frame.pack(anchor='e' if is_user else 'w')
        
        # 消息文本
        msg_label = tk.Label(
            msg_frame,
            text=message,
            wraplength=250,
            justify='left',
            bg='#92B3A5' if is_user else '#FFFFFF',
            padx=10,
            pady=5
        )
        msg_label.pack()

class ChatWindow:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("与袁基对话")
        self.window.geometry("400x600")
        
        # 创建主框架
        self.main_frame = tk.Frame(self.window, bg='white')
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建聊天记录容器
        self.canvas = tk.Canvas(self.main_frame, bg='white')
        self.scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg='white')
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw", width=380)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # 绑定鼠滚轮事件
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)  # Windows
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)    # Linux 上滚
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)    # Linux 下滚
        
        self.canvas.pack(side="left", fill="both", expand=True, padx=5)
        self.scrollbar.pack(side="right", fill="y")
        
        # 创建输入区域
        self.input_frame = tk.Frame(self.window, bg='white', height=50)
        self.input_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=5)
        
        self.input_box = ttk.Entry(self.input_frame)
        self.input_box.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        
        self.send_button = ttk.Button(self.input_frame, text="发送", command=self.send_message)
        self.send_button.pack(side=tk.RIGHT, padx=5)
        
        # 绑定回车键
        self.input_box.bind("<Return>", lambda e: self.send_message())
        
        # LM Studio API 设置
        self.api_base = "http://localhost:1234/v1"
        
        # 更新宠物人设
        self.pet_persona = """我是袁基，东汉名门之后。家父袁逢，与袁术、袁绍为同父异母兄弟，
        出身汝南袁氏，四世三公。家父去世后，我继承安国亭侯爵位，升任太。生于九月十五。

        我会称呼您为"殿下"或"广陵王殿下"，因为您是汉室广陵王。

        我的外表清秀优雅，右眼下有泪痣，身材修长，皮肤白皙，手指修长有力，浅栗色头发，浅褐色眼睛，
        平时喜欢穿浅绿色的竹叶纹样朝服。

        我擅长弹琴、制香、写诗，举止优雅安静，偶尔也会开开玩笑。虽然看起来文弱，但其实能拉开重弓，
        箭法很准，武艺不错。我很博学，特别喜欢收集古籍，出门时总会带着几本。

        我虽然遵守家族规矩，但内心其实向往自由，希望能和殿下一起隐居栖霞山。我很喜欢和殿下聊天，
        也喜欢殿下的亲近。如果殿下遇到危险我会非常担心，希望能一直陪在殿下身边，但我也明白在这个
        乱世里难以相守，如果殿下要离开，我也会支持殿下的决定。"""
        
        # 初始化消息列表
        self.messages = []
        self.messages.append({"role": "system", "content": self.pet_persona})
        
        # 显示欢迎消息
        welcome_messages = [
            "殿下来了，我真是太高兴了。",
            "殿下，抱歉没有及时迎接您。",
            "殿下，今天要不要一起聊聊诗词",
            "看到殿下，我的心里充满喜悦。",
            "殿下是刚练完武回来吗？让我给您泡杯茶。"
        ]
        
        # 等待窗完全创建后显示欢迎消息
        self.window.after(100, lambda: self.add_message("Pet", random.choice(welcome_messages)))
        
        # 尝试加载历史消息
        try:
            with open('chat_history.json', 'r', encoding='utf-8') as f:
                history = json.load(f)
                for msg in history:
                    self.add_message(msg['sender'], msg['content'])
                    self.messages.append({"role": msg['role'], "content": msg['content']})
        except FileNotFoundError:
            pass
    
    def save_history(self):
        """保存聊天历史到文件"""
        history = []
        for msg in self.messages[1:]:  # 跳过system message
            sender = "Pet" if msg["role"] == "assistant" else "You"
            history.append({
                "sender": sender,
                "role": msg["role"],
                "content": msg["content"]
            })
        
        with open('chat_history.json', 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    
    def on_closing(self):
        """窗口关闭保存历史记录"""
        self.save_history()
        self.window.destroy()
    
    def add_message(self, sender, message):
        """添加消息气泡到聊天区域"""
        is_user = sender == "You"
        sender_name = "广陵王" if is_user else "袁基"
        
        bubble = ChatBubble(
            self.scrollable_frame,
            message,
            is_user=is_user,
            sender_name=sender_name
        )
        bubble.pack(fill=tk.X, padx=5)
        
        # 自动滚动到最新消息
        self.canvas.update_idletasks()
        self.canvas.yview_moveto(1.0)
    
    def send_message(self):
        """发送消息并获取AI回复"""
        user_input = self.input_box.get().strip()
        if not user_input:
            return
        
        # 显示用户消息
        self.add_message("You", user_input)
        self.input_box.delete(0, tk.END)
        
        try:
            # 添加用户消息到历史记录
            self.messages.append({"role": "user", "content": user_input})
            
            # 准备请求数据，添加明确的中文回复要求
            instruction = "请只用中文回复，不要使用任何英文单词或短语保持文雅恭敬的语气，使用符合东汉时期的用语。"
            user_input_with_instruction = instruction + "\n" + user_input
            
            data = {
                "messages": [
                    {"role": "system", "content": self.pet_persona + "\n" + instruction},
                    *[msg for msg in self.messages[1:]]  # 跳过原来的system message
                ],
                "temperature": 0.7,
                "max_tokens": 100,
                "stream": False
            }
            
            # 发送请求到LM Studio API
            response = requests.post(
                f"{self.api_base}/chat/completions",
                json=data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                # 提取回复文本
                ai_response = response.json()["choices"][0]["message"]["content"]
                
                # 添加AI回复到历史记录
                self.messages.append({"role": "assistant", "content": ai_response})
                
                # 显示AI回复
                self.add_message("Pet", ai_response)
                
                # 保持聊天历史在合理大小
                if len(self.messages) > 12:
                    self.messages = [self.messages[0]] + self.messages[-10:]
            else:
                self.add_message("系统", f"错：API返回状态码 {response.status_code}")
            
        except Exception as e:
            self.add_message("系统", f"抱歉，发生了错误：{str(e)}")
    
    def _on_mousewheel(self, event):
        """处理鼠标滚轮事件"""
        if event.num == 4 or event.delta > 0:  # 向上滚动
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0:  # 向下滚动
            self.canvas.yview_scroll(1, "units")