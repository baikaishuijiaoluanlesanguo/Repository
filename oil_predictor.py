import requests
from bs4 import BeautifulSoup
import re
import datetime  # 修复：导入 datetime 模块

def get_accurate_prediction():
    # 搜索链接：专门搜索包含“成品油调价”的新闻，并按时间排序
    url = "https://www.baidu.com/s?rtt=1&bsst=1&cl=2&tn=news&word=成品油调价预测"
    
    headers = {
        # 伪装成浏览器，避免被百度拦截
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            return "访问新闻搜索失败，请检查网络或稍后再试。"

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 尝试查找第一条新闻标题 (最新的预测信息通常是第一条)
        # 注意：百度的class名称会变，这里使用一个通用且靠近标题的元素
        
        # 常见的百度新闻标题选择器 (可能需要根据时间调整)
        first_title_tag = soup.find('h3', class_='news-title_1YtI1')
        
        if not first_title_tag:
             # 如果找不到特定的 class，尝试查找所有 h3 标签
             first_title_tag = soup.find('h3')
        
        if not first_title_tag:
             return "未能找到新闻标题，网站结构可能已变更。"

        title = first_title_tag.get_text(strip=True)
        
        # --- 核心预测逻辑 ---
        
        trend = "搁浅或待定"
        amount_ton = 0
        
        # 正则表达式：匹配“上调/下调”后面跟着的数字和“元/吨”
        # e.g., "预计上调120元/吨"
        money_pattern = re.compile(r'(上调|下调)(\d+)元/吨')
        
        match = money_pattern.search(title)
        
        if match:
            direction = match.group(1) # 上调 或 下调
            amount_ton = int(match.group(2))
            
            # 换算成 元/升，用于公众号文案
            amount_liter = amount_ton / 1300 if amount_ton > 0 else 0 
            
            if amount_ton >= 50: # 超过50元/吨的调价红线，才算有效调整
                if direction == "上调":
                    trend = f"🚨 大幅上涨：{amount_ton}元/吨"
                else: # direction == "下调"
                    trend = f"✅ 大幅下跌：{amount_ton}元/吨"
            else:
                trend = f"⏸️ 接近搁浅：{amount_ton}元/吨"
            
        else:
            # 如果标题里没有金额，只看关键词
            amount_liter = 0
            if "上调" in title and "搁浅" not in title:
                trend = "🚨 预计上涨 (金额待定)"
            elif "下调" in title and "搁浅" not in title:
                trend = "✅ 预计下跌 (金额待定)"

        # 结果汇总
        result_message = f"""
        --- 预测分析结果 ({datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}) ---
        
        📰 最新新闻标题: {title}
        
        🔥 公众号发文结论: {trend}
        
        💰 折合每升预计变动: 约 {amount_liter:.2f} 元/升
        
        📝 发文建议: 
        1. 调价前一天（第9/10个工作日）的上午是最佳发文时间。
        2. 如果结论是“大幅上涨”或“大幅下跌”，立即发文！
        """
        
        return result_message

    except Exception as e:
        return f"程序执行失败: {e}"

if __name__ == "__main__":
    print(get_accurate_prediction())