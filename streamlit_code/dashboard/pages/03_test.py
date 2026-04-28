import streamlit as st

# 建议将数据定义和 HTML 构造逻辑放在一起
html_content = f"""
<div class="stock-row-container" data-code="TSLA">
   <div class="col-code">TSLA</div>
   <div class="col-name">TSLA</div>
   <div class="col-action">
       <button class="edit-trigger">编辑</button>
   </div>
</div>

<style>
    .stock-row-container {{ background-color: #E6F4EA; cursor: pointer; padding: 10px; border-radius: 8px; }}
    .stock-row-container:hover {{ background-color: #D4EDDC; }}
</style>

<script>
(function() {{
    const bindEvents = () => {{
        // 直接使用 document 查找当前作用域下的元素
        const rows = document.querySelectorAll('.stock-row-container:not([data-bound])');
        rows.forEach(row => {{
            const code = row.getAttribute('data-code');

            row.addEventListener('dblclick', () => {{
                // 使用 top.location 确保改变的是最外层的 URL
                const url = new URL(window.top.location.href);
                url.searchParams.set('v_code', code);
                alert(url)
                window.top.location.href = url.href;
            }});

            row.setAttribute('data-bound', 'true');
            console.log('Successfully bound dblclick to:', code);
        }});
    }};

    // 初始执行一次，并开启监听
    bindEvents();
    setInterval(bindEvents, 1000);
}})();
</script>
"""

st.html(html_content)