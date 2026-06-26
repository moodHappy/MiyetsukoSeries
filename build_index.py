import os
import re
import json

TARGET_DIR = "." 
OUTPUT_FILE = "index.html"

def scan_html_files():
    library = {}
    total_files = 0
    print("🕵️ 图书管理员已出发，正在重构你的多维宇宙体系...")
    
    for root, dirs, files in os.walk(TARGET_DIR):
        for file in files:
            if file.endswith(".html") and file != OUTPUT_FILE:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, TARGET_DIR).replace('\\', '/')
                
                # 智能解析文件夹层级结构
                parts = rel_path.split('/')
                
                if len(parts) == 1:
                    book_name = "未分类文稿"
                    section_name = "正文"
                else:
                    book_name = parts[0]
                    # 将中间的所有文件夹路径拼装成“卷/季”的名字
                    section_name = "/".join(parts[1:-1]) if len(parts) > 2 else "正文"
                
                title = file.replace(".html", "")
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read(2048)
                        title_match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE)
                        if title_match:
                            clean_title = title_match.group(1).strip()
                            if clean_title:
                                title = clean_title
                except Exception:
                    pass
                
                if book_name not in library:
                    library[book_name] = {}
                if section_name not in library[book_name]:
                    library[book_name][section_name] = []
                    
                library[book_name][section_name].append({
                    "title": title,
                    "url": rel_path
                })
                total_files += 1
                
    # 对字典进行优雅排序并转化为 List，以便前端按顺序渲染
    sorted_library = []
    for book in sorted(library.keys()):
        sections = []
        for sub in sorted(library[book].keys()):
            # 章节内部按照 URL (通常是拼音或序号) 进行排序
            chapters = sorted(library[book][sub], key=lambda x: x['url'])
            sections.append({
                "section_name": sub,
                "chapters": chapters
            })
        sorted_library.append({
            "book_name": book,
            "sections": sections
        })
        
    return sorted_library, total_files

def generate_searchable_index():
    stories_tree, total_files = scan_html_files()
    
    if not stories_tree:
        print("⚠️ 未扫描到任何 HTML 文件。")
        return
        
    print(f"✅ 扫描完毕！共归档 {total_files} 篇内容，正在生成折叠目录...")
    
    json_data = json.dumps(stories_tree, ensure_ascii=False)
    
    # 采用安全模板替换法，避免 Python f-string 冲突。纯正 Apple 级 CSS 质感。
    html_template = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>全站故事索引</title>
    <style>
        :root { --bg: #f5f5f7; --card: #ffffff; --text: #1d1d1f; --muted: #86868b; --accent: #0066cc; --border: #e5e5ea; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Helvetica Neue", Arial, sans-serif; 
            -webkit-font-smoothing: antialiased; 
            background: var(--bg); 
            color: var(--text); 
            margin: 0; 
            padding: 0; 
            text-align: left; 
        }
        .container { max-width: 800px; margin: 0 auto; padding: 30px 20px 80px 20px; }
        
        .header { margin-bottom: 25px; }
        .header h1 { font-size: 2rem; font-weight: 700; margin: 0 0 10px 0; letter-spacing: -0.5px; }
        .header p { color: var(--muted); font-size: 1rem; margin: 0; line-height: 1.5; }
        
        /* 浮动搜索框 UI */
        .search-box { 
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
        }
        .search-input { 
            width: 100%; 
            padding: 12px 15px; 
            font-size: 1.05rem; 
            border: 1px solid var(--border); 
            border-radius: 10px; 
            outline: none; 
            box-sizing: border-box; 
            font-family: inherit;
            transition: border-color 0.2s, box-shadow 0.2s;
        }
        .search-input:focus { 
            border-color: var(--accent); 
            box-shadow: 0 0 0 3px rgba(0, 102, 204, 0.1); 
        }

        /* 原生手风琴折叠 UI (Apple 风格) */
        details.book-group {
            background: var(--card);
            border-radius: 16px;
            margin-bottom: 16px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.03);
            overflow: hidden;
            border: 1px solid transparent;
            transition: border-color 0.2s;
        }
        details.book-group:hover { border-color: #d1e5f9; }
        
        /* 隐藏默认三角符号 */
        summary.book-title {
            padding: 20px;
            font-size: 1.25rem;
            font-weight: 700;
            cursor: pointer;
            list-style: none;
            display: flex;
            justify-content: space-between;
            align-items: center;
            user-select: none;
            background: #fafafa;
        }
        summary.book-title::-webkit-details-marker { display: none; }
        summary.book-title:active { background: #f0f0f5; }
        
        .book-icon-wrapper { display: flex; align-items: center; gap: 10px; }
        .book-badge { background: #eef5ff; color: var(--accent); font-size: 0.85rem; padding: 4px 12px; border-radius: 20px; font-weight: 600; }
        
        .book-content { padding: 5px 20px 20px 20px; background: var(--card); }
        
        .section-title {
            font-size: 0.95rem;
            color: var(--muted);
            font-weight: 600;
            margin: 20px 0 10px 0;
            padding-bottom: 6px;
            border-bottom: 1px solid var(--border);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .section-title:first-child { margin-top: 10px; }

        /* 统一的章节条目 UI */
        .story-item { 
            display: flex; 
            justify-content: space-between; 
            align-items: center; 
            padding: 14px 16px; 
            border-radius: 12px; 
            text-decoration: none; 
            color: var(--text); 
            background: #ffffff;
            border: 1px solid var(--border);
            margin-bottom: 8px;
            transition: all 0.2s ease; 
        }
        .story-item:last-child { margin-bottom: 0; }
        .story-item:hover, .story-item:active { 
            border-color: var(--accent); 
            box-shadow: 0 4px 15px rgba(0,102,204,0.08); 
            transform: translateX(4px);
        }
        
        .story-info { display: flex; flex-direction: column; gap: 4px; }
        .story-title { font-size: 1.05rem; font-weight: 500; line-height: 1.4; }
        .story-path { font-size: 0.8rem; color: var(--muted); }
        .story-arrow { color: var(--muted); font-size: 1.1rem; flex-shrink: 0; margin-left: 15px; }

        .no-result { text-align: center; padding: 40px 20px; color: var(--muted); display: none; font-size: 1rem; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📚 宇宙档案馆</h1>
            <p>已归档 <b>TOTAL_COUNT_PLACEHOLDER</b> 篇机密卷宗，点击书名展开。</p>
        </div>
        
        <div class="search-box">
            <input type="text" id="searchInput" class="search-input" placeholder="输入章节名、角色名或书名瞬间检索...">
        </div>
        
        <div id="treeContainer"></div>
        
        <div class="list-container" id="searchContainer" style="display: none;"></div>
        
        <div class="no-result" id="noResult">没有找到相关的卷宗内容...</div>
    </div>

    <script>
        const libraryData = DATA_PLACEHOLDER;
        
        const searchInput = document.getElementById('searchInput');
        const treeContainer = document.getElementById('treeContainer');
        const searchContainer = document.getElementById('searchContainer');
        const noResult = document.getElementById('noResult');

        // 1. 渲染优雅的折叠树状目录 (默认视图)
        function renderTree() {
            treeContainer.innerHTML = '';
            libraryData.forEach((book, index) => {
                const details = document.createElement('details');
                details.className = 'book-group';
                // 默认展开第一个宇宙
                if (index === 0) details.open = true; 
                
                // 计算当前书本下的总章节数
                let chapterCount = 0;
                book.sections.forEach(sec => chapterCount += sec.chapters.length);

                const summary = document.createElement('summary');
                summary.className = 'book-title';
                summary.innerHTML = '<div class="book-icon-wrapper"><span>📖</span> <span>' + book.book_name + '</span></div> <span class="book-badge">' + chapterCount + ' 篇</span>';
                details.appendChild(summary);

                const content = document.createElement('div');
                content.className = 'book-content';

                book.sections.forEach(sec => {
                    // 如果有子文件夹，渲染子文件夹标题
                    if (sec.section_name !== "正文") {
                        const secTitle = document.createElement('div');
                        secTitle.className = 'section-title';
                        secTitle.innerHTML = '📂 ' + sec.section_name;
                        content.appendChild(secTitle);
                    }
                    
                    // 渲染章节
                    sec.chapters.forEach(chap => {
                        const a = document.createElement('a');
                        a.href = chap.url;
                        a.className = 'story-item';
                        a.innerHTML = '<div class="story-info"><span class="story-title">' + chap.title + '</span></div><span class="story-arrow">→</span>';
                        content.appendChild(a);
                    });
                });
                
                details.appendChild(content);
                treeContainer.appendChild(details);
            });
        }

        // 2. 渲染扁平化的搜索结果视图 (带面包屑路径提示)
        function renderFlatSearch(keyword) {
            searchContainer.innerHTML = '';
            let found = false;
            
            libraryData.forEach(book => {
                book.sections.forEach(sec => {
                    sec.chapters.forEach(chap => {
                        if (chap.title.toLowerCase().includes(keyword) || chap.url.toLowerCase().includes(keyword) || book.book_name.toLowerCase().includes(keyword)) {
                            found = true;
                            const a = document.createElement('a');
                            a.href = chap.url;
                            a.className = 'story-item';
                            
                            // 拼装上下文路径 (如: QueenRules / Season 1)
                            const pathContext = sec.section_name === "正文" ? book.book_name : book.book_name + ' / ' + sec.section_name;
                            
                            a.innerHTML = '<div class="story-info"><span class="story-title">' + chap.title + '</span><span class="story-path">所属：' + pathContext + '</span></div><span class="story-arrow">→</span>';
                            searchContainer.appendChild(a);
                        }
                    });
                });
            });
            
            noResult.style.display = found ? 'none' : 'block';
        }

        // 3. 监听输入框，智能切换两种视图
        searchInput.addEventListener('input', (e) => {
            const keyword = e.target.value.toLowerCase().trim();
            if (keyword) {
                treeContainer.style.display = 'none';
                searchContainer.style.display = 'block';
                renderFlatSearch(keyword);
            } else {
                treeContainer.style.display = 'block';
                searchContainer.style.display = 'none';
                noResult.style.display = 'none';
            }
        });

        // 初始化渲染
        renderTree();
    </script>
</body>
</html>"""

    # 注入数据，避免模板冲突
    final_html = html_template.replace("DATA_PLACEHOLDER", json_data).replace("TOTAL_COUNT_PLACEHOLDER", str(total_files))

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(final_html)
    print(f"🎉 沉浸式分类目录页生成完毕！请打开 {OUTPUT_FILE} 查看。")

if __name__ == "__main__":
    generate_searchable_index()
