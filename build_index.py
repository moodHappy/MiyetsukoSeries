import os
import re
import json

# ================= 配置区 =================
TARGET_DIR = "." 
OUTPUT_FILE = "index.html"
CONTENTS_DIR = "Contents" # 专属的聚合目录文件夹
# ==========================================

def scan_html_files():
    library = {}
    total_files = 0
    print("🕵️ 图书管理员正在进行深度扫描，重构科技感多维宇宙...")
    
    for root, dirs, files in os.walk(TARGET_DIR):
        # 排除 Contents 文件夹和 git 隐藏文件夹，防止无限循环和干扰
        if CONTENTS_DIR in dirs:
            dirs.remove(CONTENTS_DIR)
        if '.git' in dirs:
            dirs.remove('.git')
            
        for file in files:
            if file.endswith(".html") and file != OUTPUT_FILE:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, TARGET_DIR).replace('\\', '/')
                
                parts = rel_path.split('/')
                
                if len(parts) == 1:
                    book_name = "未分类文稿"
                    section_name = "正文"
                else:
                    book_name = parts[0]
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
                
    # 排序数据
    sorted_library = []
    for book in sorted(library.keys()):
        sections = []
        for sub in sorted(library[book].keys()):
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

def generate_book_toc(book_data):
    """为每本书生成独立的现代科技感目录 HTML"""
    book_name = book_data['book_name']
    toc_filename = f"{book_name}_Contents.html"
    toc_filepath = os.path.join(CONTENTS_DIR, toc_filename)
    
    # 组装独立目录的内容
    content_html = ""
    total_chapters = 0
    for sec in book_data['sections']:
        total_chapters += len(sec['chapters'])
        if sec['section_name'] != "正文":
            content_html += f"<div class='section-title'>📂 {sec['section_name']}</div>\n"
        
        for chap in sec['chapters']:
            # 注意：从 Contents 文件夹跳转到源文件，需要加 ../ 回到根目录
            target_url = f"../{chap['url']}"
            content_html += f"""
            <a href="{target_url}" class="story-item">
                <div class="story-info"><span class="story-title">{chap['title']}</span></div>
                <span class="story-arrow">→</span>
            </a>
            """

    # 独立目录的 HTML 模板 (科技感 UI)
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>{book_name} - 专属目录</title>
    <style>
        :root {{ --bg: #f0f2f5; --card: #ffffff; --text: #1a1a1c; --muted: #6b7280; --accent: #2563eb; --accent-glow: rgba(37,99,235,0.08); --border: #e5e7eb; }}
        body {{ font-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, "Helvetica Neue", Arial, sans-serif; -webkit-font-smoothing: antialiased; background: var(--bg); color: var(--text); margin: 0; padding: 0; text-align: left; }}
        .nav-bar {{ position: sticky; top: 0; z-index: 100; background: rgba(255, 255, 255, 0.85); backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px); border-bottom: 1px solid rgba(229, 231, 235, 0.5); padding: 15px 20px; display: flex; align-items: center; justify-content: space-between; }}
        .nav-bar a {{ text-decoration: none; color: var(--accent); font-weight: 600; font-size: 1.05rem; display: flex; align-items: center; gap: 6px; }}
        .nav-bar a:active {{ opacity: 0.7; }}
        .header {{ padding: 30px 20px 10px 20px; max-width: 800px; margin: 0 auto; }}
        .header h1 {{ font-size: 2.2rem; font-weight: 800; margin: 0 0 8px 0; letter-spacing: -0.5px; background: linear-gradient(135deg, #1e3a8a, #3b82f6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
        .header p {{ color: var(--muted); font-size: 1rem; margin: 0; font-weight: 500; }}
        .container {{ max-width: 800px; margin: 0 auto; padding: 10px 20px 60px 20px; }}
        
        .section-title {{ font-size: 0.9rem; color: var(--accent); font-weight: 700; margin: 25px 0 12px 0; text-transform: uppercase; letter-spacing: 1px; display: flex; align-items: center; gap: 8px; }}
        .section-title::after {{ content: ''; flex: 1; height: 1px; background: linear-gradient(90deg, var(--border), transparent); }}
        
        .story-item {{ display: flex; justify-content: space-between; align-items: center; padding: 16px 18px; border-radius: 14px; text-decoration: none; color: var(--text); background: var(--card); border: 1px solid transparent; box-shadow: 0 2px 8px rgba(0,0,0,0.02); margin-bottom: 10px; transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1); }}
        .story-item:last-child {{ margin-bottom: 0; }}
        .story-item:hover, .story-item:active {{ border-color: var(--accent); box-shadow: 0 8px 24px var(--accent-glow); transform: translateY(-2px); }}
        .story-title {{ font-size: 1.05rem; font-weight: 600; line-height: 1.5; }}
        .story-arrow {{ color: var(--muted); font-size: 1.2rem; transition: transform 0.2s; }}
        .story-item:hover .story-arrow {{ transform: translateX(4px); color: var(--accent); }}
    </style>
</head>
<body>
    <div class="nav-bar">
        <a href="../index.html"><span>←</span> 返回主索引</a>
    </div>
    <div class="header">
        <h1>{book_name}</h1>
        <p>全卷共收录 {total_chapters} 个章节</p>
    </div>
    <div class="container">
        {content_html}
    </div>
</body>
</html>"""
    
    with open(toc_filepath, "w", encoding="utf-8") as f:
        f.write(html)
    return f"{CONTENTS_DIR}/{toc_filename}"

def generate_searchable_index():
    stories_tree, total_files = scan_html_files()
    
    if not stories_tree:
        print("⚠️ 未扫描到任何 HTML 文件。")
        return
        
    print(f"✅ 扫描完毕！共归档 {total_files} 篇内容。")
    
    # 创建 Contents 目录
    os.makedirs(CONTENTS_DIR, exist_ok=True)
    
    # 预处理：为每本书生成独立的 TOC 文件，并将链接注入到主树数据中
    toc_links = []
    for book in stories_tree:
        toc_url = generate_book_toc(book)
        # 计算该书总章节
        chap_count = sum([len(sec['chapters']) for sec in book['sections']])
        toc_links.append({
            "book_name": book['book_name'],
            "url": toc_url,
            "count": chap_count
        })
        
    print("📚 独立聚类目录 (Contents) 生成完毕！正在构建主控台...")

    json_data = json.dumps(stories_tree, ensure_ascii=False)
    toc_data = json.dumps(toc_links, ensure_ascii=False)
    
    # 主页 HTML 模板 (现代科技感 UI)
    html_template = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>全站故事索引</title>
    <style>
        :root { --bg: #f0f2f5; --card: #ffffff; --text: #1a1a1c; --muted: #6b7280; --accent: #2563eb; --accent-glow: rgba(37,99,235,0.08); --border: #e5e7eb; }
        body { font-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, "Helvetica Neue", Arial, sans-serif; -webkit-font-smoothing: antialiased; background: var(--bg); color: var(--text); margin: 0; padding: 0; text-align: left; }
        .container { max-width: 800px; margin: 0 auto; padding: 40px 20px 80px 20px; }
        
        .header { margin-bottom: 30px; text-align: center; }
        .header h1 { font-size: 2.4rem; font-weight: 800; margin: 0 0 10px 0; letter-spacing: -0.5px; background: linear-gradient(135deg, #1e3a8a, #3b82f6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .header p { color: var(--muted); font-size: 1.05rem; margin: 0; font-weight: 500; }
        
        /* 悬浮搜索框 */
        .search-box { position: sticky; top: 15px; z-index: 100; background: rgba(255, 255, 255, 0.7); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); padding: 12px; border-radius: 18px; box-shadow: 0 8px 32px rgba(0,0,0,0.06); border: 1px solid rgba(255,255,255,0.4); margin-bottom: 35px; transition: transform 0.3s; }
        .search-input { width: 100%; padding: 14px 20px; font-size: 1.05rem; border: none; border-radius: 12px; outline: none; background: rgba(255,255,255,0.9); box-sizing: border-box; font-family: inherit; transition: box-shadow 0.2s; }
        .search-input:focus { box-shadow: inset 0 0 0 2px var(--accent); }

        /* 内容区标题 */
        .area-title { font-size: 0.95rem; color: var(--muted); font-weight: 700; margin: 0 0 12px 10px; text-transform: uppercase; letter-spacing: 1.5px; }

        /* 折叠菜单 UI */
        details.book-group { background: var(--card); border-radius: 18px; margin-bottom: 16px; box-shadow: 0 4px 15px rgba(0,0,0,0.03); overflow: hidden; border: 1px solid var(--border); transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); }
        details.book-group:hover { box-shadow: 0 8px 25px rgba(0,0,0,0.06); border-color: #d1d5db; }
        
        summary.book-title { padding: 22px 20px; font-size: 1.15rem; font-weight: 700; cursor: pointer; list-style: none; display: flex; justify-content: space-between; align-items: center; user-select: none; background: var(--card); transition: background 0.2s; }
        summary.book-title::-webkit-details-marker { display: none; }
        summary.book-title:active { background: #f9fafb; }
        
        /* 针对默认展开的 Contents 区域的特殊高亮样式 */
        details.toc-group { border: 2px solid var(--accent); box-shadow: 0 8px 24px var(--accent-glow); }
        details.toc-group summary.book-title { background: linear-gradient(to right, #eff6ff, #ffffff); }
        
        .book-icon-wrapper { display: flex; align-items: center; gap: 12px; }
        .book-icon { font-size: 1.3rem; }
        .book-badge { background: #f3f4f6; color: var(--muted); font-size: 0.8rem; padding: 4px 12px; border-radius: 20px; font-weight: 700; }
        details.toc-group .book-badge { background: var(--accent); color: #fff; }
        
        .book-content { padding: 5px 20px 20px 20px; background: var(--card); border-top: 1px dashed var(--border); }
        
        .section-title { font-size: 0.85rem; color: var(--accent); font-weight: 700; margin: 20px 0 10px 0; padding-bottom: 6px; text-transform: uppercase; letter-spacing: 0.5px; display: flex; align-items: center; gap: 6px; }
        .section-title::after { content: ''; flex: 1; height: 1px; background: linear-gradient(90deg, var(--border), transparent); }

        /* 统一条目 UI */
        .story-item { display: flex; justify-content: space-between; align-items: center; padding: 16px 18px; border-radius: 12px; text-decoration: none; color: var(--text); background: #ffffff; border: 1px solid var(--border); margin-bottom: 8px; transition: all 0.2s ease; }
        .story-item:last-child { margin-bottom: 0; }
        .story-item:hover, .story-item:active { border-color: var(--accent); box-shadow: 0 4px 12px var(--accent-glow); transform: translateX(4px); }
        
        /* Contents 里的大号卡片 */
        .toc-item { padding: 20px 18px; border: 1px solid rgba(37,99,235,0.2); background: linear-gradient(to right, #ffffff, #f8fafc); }
        .toc-item .story-title { font-size: 1.15rem; color: var(--accent); }
        
        .story-info { display: flex; flex-direction: column; gap: 6px; }
        .story-title { font-size: 1.05rem; font-weight: 600; line-height: 1.4; }
        .story-path { font-size: 0.8rem; color: var(--muted); font-weight: 500; }
        .story-arrow { color: var(--muted); font-size: 1.2rem; flex-shrink: 0; margin-left: 15px; transition: transform 0.2s;}
        .story-item:hover .story-arrow { transform: translateX(4px); color: var(--accent); }

        .no-result { text-align: center; padding: 50px 20px; color: var(--muted); display: none; font-size: 1.1rem; font-weight: 500; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Nexus Hub</h1>
            <p>已接入 <b>TOTAL_COUNT_PLACEHOLDER</b> 个机密区块</p>
        </div>
        
        <div class="search-box">
            <input type="text" id="searchInput" class="search-input" placeholder="输入关键字，瞬间接驳目标区块...">
        </div>
        
        <div id="treeContainer"></div>
        
        <div id="searchContainer" style="display: none; display: flex; flex-direction: column; gap: 8px;"></div>
        
        <div class="no-result" id="noResult">🕸️ 信号丢失：未找到匹配的区块内容...</div>
    </div>

    <script>
        const libraryData = DATA_PLACEHOLDER;
        const tocData = TOC_PLACEHOLDER;
        
        const searchInput = document.getElementById('searchInput');
        const treeContainer = document.getElementById('treeContainer');
        const searchContainer = document.getElementById('searchContainer');
        const noResult = document.getElementById('noResult');

        function renderTree() {
            treeContainer.innerHTML = '';
            
            // 1. 优先渲染【Contents 聚合目录】，并默认打开！
            if(tocData.length > 0) {
                const tocGroup = document.createElement('details');
                tocGroup.className = 'book-group toc-group';
                tocGroup.open = true; // 强制默认展开
                
                const summary = document.createElement('summary');
                summary.className = 'book-title';
                summary.innerHTML = '<div class="book-icon-wrapper"><span class="book-icon">🧭</span> <span>快捷聚合导航</span></div> <span class="book-badge">' + tocData.length + ' 册</span>';
                tocGroup.appendChild(summary);
                
                const content = document.createElement('div');
                content.className = 'book-content';
                // 顶部加点间距
                content.style.paddingTop = '15px';
                
                tocData.forEach(toc => {
                    const a = document.createElement('a');
                    a.href = toc.url;
                    a.className = 'story-item toc-item';
                    a.innerHTML = '<div class="story-info"><span class="story-title">《' + toc.book_name + '》 总目录</span><span class="story-path">包含 ' + toc.count + ' 个源文件</span></div><span class="story-arrow">→</span>';
                    content.appendChild(a);
                });
                
                tocGroup.appendChild(content);
                treeContainer.appendChild(tocGroup);
            }
            
            // 增加一个小标题区分
            const divLabel = document.createElement('div');
            divLabel.className = 'area-title';
            divLabel.innerText = "详细区块卷宗";
            divLabel.style.marginTop = "35px";
            treeContainer.appendChild(divLabel);

            // 2. 渲染所有的【书籍实体目录】，全部默认折叠！
            libraryData.forEach((book) => {
                const details = document.createElement('details');
                details.className = 'book-group';
                details.open = false; // 强制作家实体目录全部折叠
                
                let chapterCount = 0;
                book.sections.forEach(sec => chapterCount += sec.chapters.length);

                const summary = document.createElement('summary');
                summary.className = 'book-title';
                summary.innerHTML = '<div class="book-icon-wrapper"><span class="book-icon">📁</span> <span>' + book.book_name + '</span></div> <span class="book-badge">' + chapterCount + ' 篇</span>';
                details.appendChild(summary);

                const content = document.createElement('div');
                content.className = 'book-content';

                book.sections.forEach(sec => {
                    if (sec.section_name !== "正文") {
                        const secTitle = document.createElement('div');
                        secTitle.className = 'section-title';
                        secTitle.innerHTML = '✦ ' + sec.section_name;
                        content.appendChild(secTitle);
                    } else {
                        content.style.paddingTop = '15px';
                    }
                    
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
                            
                            const pathContext = sec.section_name === "正文" ? book.book_name : book.book_name + ' / ' + sec.section_name;
                            
                            a.innerHTML = '<div class="story-info"><span class="story-title">' + chap.title + '</span><span class="story-path">🛰️ 归属：' + pathContext + '</span></div><span class="story-arrow">→</span>';
                            searchContainer.appendChild(a);
                        }
                    });
                });
            });
            
            noResult.style.display = found ? 'none' : 'block';
        }

        searchInput.addEventListener('input', (e) => {
            const keyword = e.target.value.toLowerCase().trim();
            if (keyword) {
                treeContainer.style.display = 'none';
                searchContainer.style.display = 'flex';
                renderFlatSearch(keyword);
            } else {
                treeContainer.style.display = 'block';
                searchContainer.style.display = 'none';
                noResult.style.display = 'none';
            }
        });

        renderTree();
    </script>
</body>
</html>"""

    final_html = html_template.replace("DATA_PLACEHOLDER", json_data).replace("TOC_PLACEHOLDER", toc_data).replace("TOTAL_COUNT_PLACEHOLDER", str(total_files))

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(final_html)
    print(f"🎉 终极主控台 {OUTPUT_FILE} 生成完毕！")

if __name__ == "__main__":
    generate_searchable_index()
