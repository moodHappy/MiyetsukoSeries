import os
import re
import json

# ================= 配置区 =================
# 你存放 HTML 文件的根目录。'.' 代表当前脚本所在的整个目录及其所有子文件夹。
# 如果你的小说都放在特定文件夹（比如 'Fresh_Mart'），可以改成 'Fresh_Mart'
TARGET_DIR = "." 
# 生成的总导航页文件名
OUTPUT_FILE = "index.html"
# ==========================================

def scan_html_files():
    story_list = []
    print("🕵️ 图书管理员已出发，正在扫描文章...")
    
    # 遍历目录及子目录下的所有文件
    for root, dirs, files in os.walk(TARGET_DIR):
        for file in files:
            if file.endswith(".html") and file != OUTPUT_FILE:
                file_path = os.path.join(root, file)
                
                # 计算相对路径，确保在网页中点击链接能正确跳转
                rel_path = os.path.relpath(file_path, TARGET_DIR).replace('\\', '/')
                
                title = file.replace(".html", "") # 默认标题为文件名
                try:
                    # 只读取文件头部前 2048 个字符，提取 <title> 标签，速度极快
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read(2048)
                        title_match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE)
                        if title_match:
                            clean_title = title_match.group(1).strip()
                            if clean_title:
                                title = clean_title
                except Exception as e:
                    pass
                
                story_list.append({
                    "title": title,
                    "url": rel_path
                })
                
    # 按照文件路径/名称进行字母顺序排序，确保章节不会乱序
    story_list.sort(key=lambda x: x['url'])
    return story_list

def generate_searchable_index():
    stories = scan_html_files()
    
    if not stories:
        print("⚠️ 未扫描到任何 HTML 文件。")
        return
        
    print(f"✅ 扫描完毕！共找到 {len(stories)} 篇文章，正在生成索引页...")
    
    # 将列表转化为 JSON 数据注入到前端
    json_data = json.dumps(stories, ensure_ascii=False)
    
    # 极简、左对齐、Mac 字体渲染风格的 WebApp 模板
    html_template = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>全站故事索引</title>
    <style>
        :root {{ --bg: #f5f5f7; --card: #ffffff; --text: #1d1d1f; --muted: #86868b; --accent: #0066cc; --border: #e5e5ea; }}
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Helvetica Neue", Arial, sans-serif; 
            -webkit-font-smoothing: antialiased; 
            background: var(--bg); 
            color: var(--text); 
            margin: 0; 
            padding: 0; 
            text-align: left; /* 严格左对齐 */
        }}
        .container {{ max-width: 800px; margin: 0 auto; padding: 30px 20px; }}
        
        .header {{ margin-bottom: 25px; }}
        .header h1 {{ font-size: 2rem; font-weight: 700; margin: 0 0 10px 0; letter-spacing: -0.5px; }}
        .header p {{ color: var(--muted); font-size: 1rem; margin: 0; line-height: 1.5; }}
        
        /* 搜索框 UI */
        .search-box {{ 
            position: sticky; 
            top: 15px; 
            z-index: 100;
            background: rgba(255, 255, 255, 0.85); 
            backdrop-filter: blur(12px); 
            -webkit-backdrop-filter: blur(12px);
            padding: 15px; 
            border-radius: 16px; 
            box-shadow: 0 4px 20px rgba(0,0,0,0.05); 
            margin-bottom: 30px;
        }}
        .search-input {{ 
            width: 100%; 
            padding: 12px 15px; 
            font-size: 1.1rem; 
            border: 1px solid var(--border); 
            border-radius: 10px; 
            outline: none; 
            box-sizing: border-box; 
            font-family: inherit;
            transition: border-color 0.2s, box-shadow 0.2s;
        }}
        .search-input:focus {{ 
            border-color: var(--accent); 
            box-shadow: 0 0 0 3px rgba(0, 102, 204, 0.1); 
        }}
        
        /* 列表 UI */
        .list-container {{ display: flex; flex-direction: column; gap: 10px; }}
        .story-item {{ 
            display: flex; 
            justify-content: space-between; 
            align-items: center; 
            background: var(--card); 
            padding: 16px 20px; 
            border-radius: 12px; 
            text-decoration: none; 
            color: var(--text); 
            border: 1px solid transparent;
            transition: all 0.2s ease; 
        }}
        .story-item:hover, .story-item:active {{ 
            border-color: var(--border); 
            box-shadow: 0 4px 15px rgba(0,0,0,0.03); 
            transform: translateY(-1px);
        }}
        .story-title {{ font-size: 1.1rem; font-weight: 500; line-height: 1.4; }}
        .story-arrow {{ color: var(--muted); font-size: 1.2rem; flex-shrink: 0; margin-left: 15px; }}
        
        .no-result {{ text-align: left; padding: 20px 5px; color: var(--muted); display: none; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📚 个人文库索引</h1>
            <p>已收录 <b>{len(stories)}</b> 个文件，输入关键字瞬间检索。</p>
        </div>
        
        <div class="search-box">
            <input type="text" id="searchInput" class="search-input" placeholder="输入章节名或角色名搜索...">
        </div>
        
        <div class="list-container" id="listContainer">
            </div>
        <div class="no-result" id="noResult">没有找到相关的章节内容...</div>
    </div>

    <script>
        const storyData = {json_data};
        const searchInput = document.getElementById('searchInput');
        const listContainer = document.getElementById('listContainer');
        const noResult = document.getElementById('noResult');

        // 渲染列表的函数
        function renderList(data) {{
            listContainer.innerHTML = '';
            if (data.length === 0) {{
                noResult.style.display = 'block';
                return;
            }}
            noResult.style.display = 'none';
            
            data.forEach(item => {{
                const a = document.createElement('a');
                a.href = item.url;
                a.className = 'story-item';
                a.innerHTML = `<span class="story-title">${{item.title}}</span><span class="story-arrow">→</span>`;
                listContainer.appendChild(a);
            }});
        }}

        // 初始渲染完整列表
        renderList(storyData);

        // 实时模糊搜索监听
        searchInput.addEventListener('input', (e) => {{
            const keyword = e.target.value.toLowerCase().trim();
            if (!keyword) {{
                renderList(storyData);
                return;
            }}
            
            // 匹配标题或 URL 路径中包含关键字的项
            const filteredData = storyData.filter(item => 
                item.title.toLowerCase().includes(keyword) || 
                item.url.toLowerCase().includes(keyword)
            );
            renderList(filteredData);
        }});
    </script>
</body>
</html>"""

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html_template)
    print(f"🎉 索引页生成完毕！请打开 {OUTPUT_FILE} 查看。")

if __name__ == "__main__":
    generate_searchable_index()
