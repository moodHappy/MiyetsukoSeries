import os
import re
import json

# ================= 配置区 =================
TARGET_DIR = "." 
OUTPUT_FILE = "index.html"
# ==========================================

def scan_html_files():
    library = {}
    total_files = 0
    print("🕵️ 图书管理员正在重构 SPA 极简折叠架构...")
    
    for root, dirs, files in os.walk(TARGET_DIR):
        # 排除 git 隐藏文件夹，防止干扰
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
                
    # 结构化排序
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

def generate_searchable_index():
    stories_tree, total_files = scan_html_files()
    
    if not stories_tree:
        print("⚠️ 未扫描到任何 HTML 文件。")
        return
        
    print(f"✅ 扫描完毕！共归档 {total_files} 篇内容。正在注入双层折叠引擎...")
    
    json_data = json.dumps(stories_tree, ensure_ascii=False)
    
    html_template = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Nexus Hub - 个人文库枢纽</title>
    <style>
        :root { 
            --bg: #f0f2f5; 
            --card: #ffffff; 
            --text: #1a1a1c; 
            --muted: #6b7280; 
            --accent: #2563eb; 
            --accent-glow: rgba(37,99,235,0.08); 
            --border: #e5e7eb; 
            --sub-bg: #f8fafc;
        }
        body { 
            font-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, "Helvetica Neue", Arial, sans-serif; 
            -webkit-font-smoothing: antialiased; 
            background: var(--bg); 
            color: var(--text); 
            margin: 0; 
            padding: 0; 
            text-align: left; 
        }
        
        /* 页面切换动画 */
        .view-section { display: none; animation: fadeIn 0.3s cubic-bezier(0.4, 0, 0.2, 1); }
        .view-section.active { display: block; }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        /* ---------------- 主视图 UI ---------------- */
        .container { max-width: 800px; margin: 0 auto; padding: 40px 20px 80px 20px; }
        .header { margin-bottom: 30px; text-align: center; }
        .header h1 { font-size: 2.4rem; font-weight: 800; margin: 0 0 10px 0; letter-spacing: -0.5px; background: linear-gradient(135deg, #1e3a8a, #3b82f6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .header p { color: var(--muted); font-size: 1.05rem; margin: 0; font-weight: 500; }
        
        /* 悬浮搜索框 */
        .search-box { position: sticky; top: 15px; z-index: 100; background: rgba(255, 255, 255, 0.7); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); padding: 12px; border-radius: 18px; box-shadow: 0 8px 32px rgba(0,0,0,0.06); border: 1px solid rgba(255,255,255,0.4); margin-bottom: 35px; transition: transform 0.3s; }
        .search-input { width: 100%; padding: 14px 20px; font-size: 1.05rem; border: none; border-radius: 12px; outline: none; background: rgba(255,255,255,0.9); box-sizing: border-box; font-family: inherit; transition: box-shadow 0.2s; }
        .search-input:focus { box-shadow: inset 0 0 0 2px var(--accent); }

        .area-title { font-size: 0.95rem; color: var(--muted); font-weight: 700; margin: 0 0 12px 10px; text-transform: uppercase; letter-spacing: 1.5px; }

        /* 外层折叠菜单 UI (书籍) */
        details.book-group { background: var(--card); border-radius: 18px; margin-bottom: 16px; box-shadow: 0 4px 15px rgba(0,0,0,0.03); overflow: hidden; border: 1px solid var(--border); transition: all 0.3s ease; }
        details.book-group:hover { box-shadow: 0 8px 25px rgba(0,0,0,0.06); border-color: #d1d5db; }
        
        summary.book-title { padding: 22px 20px; font-size: 1.15rem; font-weight: 700; cursor: pointer; list-style: none; display: flex; justify-content: space-between; align-items: center; user-select: none; background: var(--card); transition: background 0.2s; }
        summary.book-title::-webkit-details-marker { display: none; }
        summary.book-title:active { background: #f9fafb; }
        
        /* 快捷导航特殊样式 */
        details.toc-group { border: 2px solid var(--accent); box-shadow: 0 8px 24px var(--accent-glow); }
        details.toc-group summary.book-title { background: linear-gradient(to right, #eff6ff, #ffffff); }
        details.toc-group .book-badge { background: var(--accent); color: #fff; }
        
        .book-icon-wrapper { display: flex; align-items: center; gap: 12px; }
        .book-icon { font-size: 1.3rem; }
        .book-badge { background: #f3f4f6; color: var(--muted); font-size: 0.8rem; padding: 4px 12px; border-radius: 20px; font-weight: 700; }
        
        .book-content { padding: 5px 20px 20px 20px; background: var(--card); border-top: 1px dashed var(--border); }

        /* 内层折叠菜单 UI (季/卷/子文件夹) - 永远折叠 */
        details.sub-group { background: var(--sub-bg); border-radius: 12px; margin-bottom: 12px; border: 1px solid var(--border); overflow: hidden; }
        details.sub-group:last-child { margin-bottom: 0; }
        summary.sub-title { padding: 15px 18px; font-size: 0.95rem; font-weight: 700; color: var(--accent); cursor: pointer; display: flex; justify-content: space-between; align-items: center; text-transform: uppercase; letter-spacing: 0.5px; list-style: none; user-select: none; }
        summary.sub-title::-webkit-details-marker { display: none; }
        summary.sub-title:active { background: #f1f5f9; }
        .sub-content { padding: 0 15px 15px 15px; }

        /* 统一条目 UI (章节) */
        .story-item { display: flex; justify-content: space-between; align-items: center; padding: 16px 18px; border-radius: 12px; text-decoration: none; color: var(--text); background: #ffffff; border: 1px solid var(--border); margin-bottom: 8px; transition: all 0.2s ease; cursor: pointer; }
        .story-item:last-child { margin-bottom: 0; }
        .story-item:hover, .story-item:active { border-color: var(--accent); box-shadow: 0 4px 12px var(--accent-glow); transform: translateX(4px); }
        
        /* 聚合目录的大卡片 */
        .toc-item { padding: 20px 18px; border: 1px solid rgba(37,99,235,0.2); background: linear-gradient(to right, #ffffff, #f8fafc); }
        .toc-item .story-title { font-size: 1.15rem; color: var(--accent); }
        
        .story-info { display: flex; flex-direction: column; gap: 6px; }
        .story-title { font-size: 1.05rem; font-weight: 600; line-height: 1.4; }
        .story-path { font-size: 0.8rem; color: var(--muted); font-weight: 500; }
        .story-arrow { color: var(--muted); font-size: 1.2rem; flex-shrink: 0; margin-left: 15px; transition: transform 0.2s; }
        .story-item:hover .story-arrow { transform: translateX(4px); color: var(--accent); }
        
        /* ---------------- 独立目录页 (SPA) UI ---------------- */
        .nav-bar { position: sticky; top: 0; z-index: 100; background: rgba(255, 255, 255, 0.85); backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px); border-bottom: 1px solid rgba(229, 231, 235, 0.5); padding: 15px 20px; display: flex; align-items: center; justify-content: flex-start; cursor: pointer; transition: background 0.2s; }
        .nav-bar:active { background: #f3f4f6; }
        .nav-bar span { color: var(--accent); font-weight: 700; font-size: 1.05rem; display: flex; align-items: center; gap: 6px; }
        
        .no-result { text-align: center; padding: 50px 20px; color: var(--muted); display: none; font-size: 1.1rem; font-weight: 500; }
    </style>
</head>
<body>

    <div id="mainView" class="view-section active">
        <div class="container">
            <div class="header">
                <h1>Nexus Hub</h1>
                <p>已接入 <b>TOTAL_COUNT_PLACEHOLDER</b> 个机密区块</p>
            </div>
            
            <div class="search-box">
                <input type="text" id="searchInput" class="search-input" placeholder="输入关键字，瞬间接驳目标区块...">
            </div>
            
            <div id="treeContainer"></div>
            <div id="searchContainer" style="display: none; flex-direction: column; gap: 8px;"></div>
            <div class="no-result" id="noResult">🕸️ 信号丢失：未找到匹配的区块内容...</div>
        </div>
    </div>

    <div id="tocView" class="view-section">
        <div class="nav-bar" onclick="switchView('main')">
            <span>← 返回主枢纽</span>
        </div>
        <div class="container" style="padding-top: 20px;">
            <div class="header" id="dynamicTocHeader" style="text-align: left; margin-bottom: 20px;">
                </div>
            <div id="dynamicTocContent">
                </div>
        </div>
    </div>

    <script>
        const libraryData = DATA_PLACEHOLDER;
        
        const searchInput = document.getElementById('searchInput');
        const treeContainer = document.getElementById('treeContainer');
        const searchContainer = document.getElementById('searchContainer');
        const noResult = document.getElementById('noResult');
        
        const mainView = document.getElementById('mainView');
        const tocView = document.getElementById('tocView');

        // ==== 视图切换核心逻辑 ====
        function switchView(viewName) {
            if (viewName === 'main') {
                tocView.classList.remove('active');
                mainView.classList.add('active');
            } else {
                mainView.classList.remove('active');
                tocView.classList.add('active');
            }
            window.scrollTo(0, 0); 
        }

        // ==== 渲染特定书籍的独立目录 (内部完全折叠) ====
        function openBookToc(bookName) {
            const book = libraryData.find(b => b.book_name === bookName);
            if(!book) return;
            
            let totalChaps = 0;
            book.sections.forEach(s => totalChaps += s.chapters.length);
            
            // 渲染头部
            document.getElementById('dynamicTocHeader').innerHTML = `
                <h1 style="font-size: 2rem;">《${book.book_name}》</h1>
                <p>全卷共收录 ${totalChaps} 个源文件</p>
            `;
            
            // 渲染内部折叠列表
            let htmlStr = '';
            book.sections.forEach(sec => {
                let secNameDisplay = sec.section_name === "正文" ? "📄 正文" : `📂 ${sec.section_name}`;
                
                // 强制关闭标签 details (open=false)，实现“永远折叠”
                htmlStr += `
                <details class="sub-group">
                    <summary class="sub-title">
                        <span>${secNameDisplay}</span>
                        <span style="font-size:0.8rem; color:var(--muted); font-weight:normal;">${sec.chapters.length} 篇</span>
                    </summary>
                    <div class="sub-content">
                `;
                
                sec.chapters.forEach(chap => {
                    htmlStr += `
                    <a href="${chap.url}" class="story-item">
                        <div class="story-info"><span class="story-title">${chap.title}</span></div>
                        <span class="story-arrow">→</span>
                    </a>`;
                });
                
                htmlStr += `</div></details>`;
            });
            document.getElementById('dynamicTocContent').innerHTML = htmlStr;
            
            switchView('toc');
        }

        // ==== 渲染主控台树状结构 ====
        function renderTree() {
            treeContainer.innerHTML = '';
            
            // 1. 动态生成【快捷聚合导航】
            if(libraryData.length > 0) {
                const tocGroup = document.createElement('details');
                tocGroup.className = 'book-group toc-group';
                tocGroup.open = true; // 外层导航默认展开
                
                const summary = document.createElement('summary');
                summary.className = 'book-title';
                summary.innerHTML = '<div class="book-icon-wrapper"><span class="book-icon">🧭</span> <span>快捷聚合导航</span></div> <span class="book-badge">' + libraryData.length + ' 册</span>';
                tocGroup.appendChild(summary);
                
                const content = document.createElement('div');
                content.className = 'book-content';
                content.style.paddingTop = '15px';
                
                libraryData.forEach(book => {
                    let chapCount = 0;
                    book.sections.forEach(s => chapCount += s.chapters.length);
                    
                    const div = document.createElement('div');
                    div.className = 'story-item toc-item';
                    div.innerHTML = '<div class="story-info"><span class="story-title">《' + book.book_name + '》 总目录</span><span class="story-path">包含 ' + chapCount + ' 个源文件</span></div><span class="story-arrow">→</span>';
                    // 点击进入第二层
                    div.onclick = () => openBookToc(book.book_name);
                    content.appendChild(div);
                });
                
                tocGroup.appendChild(content);
                treeContainer.appendChild(tocGroup);
            }
            
            // 分界线
            const divLabel = document.createElement('div');
            divLabel.className = 'area-title';
            divLabel.innerText = "详细区块卷宗";
            divLabel.style.marginTop = "35px";
            treeContainer.appendChild(divLabel);

            // 2. 生成所有【折叠卷宗】(内外双重折叠)
            libraryData.forEach((book) => {
                const details = document.createElement('details');
                details.className = 'book-group';
                details.open = false; // 外层书籍默认折叠
                
                let chapterCount = 0;
                book.sections.forEach(sec => chapterCount += sec.chapters.length);

                const summary = document.createElement('summary');
                summary.className = 'book-title';
                summary.innerHTML = '<div class="book-icon-wrapper"><span class="book-icon">📁</span> <span>' + book.book_name + '</span></div> <span class="book-badge">' + chapterCount + ' 篇</span>';
                details.appendChild(summary);

                const content = document.createElement('div');
                content.className = 'book-content';
                content.style.paddingTop = '15px';

                book.sections.forEach(sec => {
                    let secNameDisplay = sec.section_name === "正文" ? "📄 正文" : `✦ ${sec.section_name}`;
                    
                    // 内层季/卷也做成折叠
                    const subDetails = document.createElement('details');
                    subDetails.className = 'sub-group';
                    subDetails.open = false; // 永远折叠
                    
                    const subSummary = document.createElement('summary');
                    subSummary.className = 'sub-title';
                    subSummary.innerHTML = `<span>${secNameDisplay}</span><span style="font-size:0.8rem; color:var(--muted); font-weight:normal;">${sec.chapters.length} 篇</span>`;
                    subDetails.appendChild(subSummary);
                    
                    const subContent = document.createElement('div');
                    subContent.className = 'sub-content';
                    
                    sec.chapters.forEach(chap => {
                        const a = document.createElement('a');
                        a.href = chap.url;
                        a.className = 'story-item';
                        a.innerHTML = '<div class="story-info"><span class="story-title">' + chap.title + '</span></div><span class="story-arrow">→</span>';
                        subContent.appendChild(a);
                    });
                    
                    subDetails.appendChild(subContent);
                    content.appendChild(subDetails);
                });
                
                details.appendChild(content);
                treeContainer.appendChild(details);
            });
        }

        // ==== 渲染搜索结果 ====
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

        // ==== 搜索监听 ====
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

        // 启动渲染
        renderTree();
    </script>
</body>
</html>"""

    final_html = html_template.replace("DATA_PLACEHOLDER", json_data).replace("TOTAL_COUNT_PLACEHOLDER", str(total_files))

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(final_html)
    print(f"🎉 SPA 单页应用枢纽 {OUTPUT_FILE} 编译完毕！")

if __name__ == "__main__":
    generate_searchable_index()
