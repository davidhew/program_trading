import streamlit as st

st.html("""
<style>
.stock-row-container {
    display: flex;
    align-items: center;
    background-color: #E6F4EA;
    border-radius: 8px;
    margin: 8px 0;
    padding: 12px 15px;
    cursor: pointer;
    transition: background 0.2s;
    border: 1px solid transparent;
}
.stock-row-container:hover {
    background-color: #D4EDDC;
    border-color: #B7E1CD;
}
</style>

<script>
// 动态绑定事件，避免 React 属性注入错误
function setupListeners() {
    const rows = window.parent.document.querySelectorAll('.stock-row-container');
    rows.forEach(row => {
        // 防止重复绑定
        if (row.getAttribute('data-bound')) return;

        const code = row.getAttribute('data-code');

        // 双击查看详情
        row.addEventListener('dblclick', () => {
            const url = new URL(window.parent.location.href);
            url.searchParams.set('v_code', code);
            alert(url.href);
            window.parent.location.href = url.href;
        });

        // 点击编辑按钮 (查找内部的编辑链接)
        const editBtn = row.querySelector('.edit-trigger');
        if (editBtn) {
            editBtn.addEventListener('click', (e) => {
                e.stopPropagation(); // 阻止触发整行的双击/单击
                const url = new URL(window.parent.location.href);
                url.searchParams.set('e_code', code);
                alert(url.href);
                window.parent.location.href = url.href;
            });
        }

        row.setAttribute('data-bound', 'true');
    });
}

// 每隔一秒检查一次是否有新行渲染出来
setInterval(setupListeners, 1000);
</script>
""")

print("query_params are:"+str(st.query_params))
st.html(f"""
   <div class="stock-row-container" data-code="TSLA">
       <div class="col-code">TSLA</div>
       <div class="col-name">TSLA</div>
       <div class="col-market">美股</div>
       <div class="col-tags">FSD,ROBOTTAXI</div>
       <div class="col-action">
           <button class="edit-trigger" style="cursor:pointer; padding:2px 8px;">编辑</button>
       </div>
   </div>
   """)