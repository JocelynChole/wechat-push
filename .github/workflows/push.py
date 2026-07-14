import requests
  import json
  from datetime import datetime, timedelta
  import os

  # 获取环境变量
  PUSHPLUS_TOKEN = os.getenv("PUSHPLUS_TOKEN", "68d8a93160eb44ff9b95e596080c590d")
  NEWS_API_URL = os.getenv("NEWS_API_URL", "http://42.193.14.76/api/news")

  def fetch_news():
      """从云端获取资讯"""
      try:
          print(f"正在获取资讯: {NEWS_API_URL}")
          response = requests.get(NEWS_API_URL, timeout=30)
          response.raise_for_status()
          return response.json()
      except Exception as e:
          print(f"获取资讯失败: {e}")
          return None

  def build_html(news_data):
      """生成HTML内容"""
      news_list = news_data.get("news_list", [])
      if not news_list:
          return "<p>今日暂无资讯</p>"

      now = datetime.now() + timedelta(hours=8)  # 北京时间
      date_str = now.strftime("%Y年%m月%d日")

      # 统计
      sentiments = [n.get("sentiment", "中性") for n in news_list]
      bullish = sentiments.count("利好")
      bearish = sentiments.count("利空")

      html = f"""
      <h1>📊 盘前速览 - {date_str}</h1>
      <p>今日共 {len(news_list)} 条资讯 · 利好 {bullish} 条 · 利空 {bearish} 条</p>
      <hr>
      """

      # 按重要性排序
      sorted_news = sorted(news_list, key=lambda x: x.get("importance_score", 0), reverse=True)

      for i, news in enumerate(sorted_news[:15], 1):
          title = news.get("title", "")
          content = news.get("content", "")
          sentiment = news.get("sentiment", "中性")
          source = news.get("source", "")
          link = news.get("link", "")

          emoji = "📈" if sentiment == "利好" else "📉" if sentiment == "利空" else "➡️"

          html += f"""
          <div style="margin: 20px 0; padding: 15px; background: #f8f9fa; border-radius: 8px;">
              <h3>{emoji} {i}. {title}</h3>
              <p style="color: #666;">{content[:200]}...</p>
              <p style="font-size: 12px; color: #999;">来源: {source}</p>
              {f'<p><a href="{link}" target="_blank">查看原文</a></p>' if link else ''}
          </div>
          """

      html += """
      <hr>
      <p style="text-align: center; color: #999; font-size: 12px;">
      🤖 由 GitHub Actions 自动推送
      </p>
      """
      return html

  def push_wechat(title, content):
      """推送到PushPlus"""
      url = "http://www.pushplus.plus/send"
      data = {
          "token": PUSHPLUS_TOKEN,
          "title": title,
          "content": content,
          "template": "html"
      }

      try:
          response = requests.post(url, json=data, timeout=10)
          result = response.json()
          if result.get("code") == 200:
              print("✅ 推送成功！")
              return True
          else:
              print(f"❌ 推送失败：{result}")
              return False
      except Exception as e:
          print(f"❌ 出错：{e}")
          return False

  if __name__ == "__main__":
      now = datetime.now() + timedelta(hours=8)
      print(f"开始执行: {now.strftime('%Y-%m-%d %H:%M:%S')}")

      # 获取资讯
      news_data = fetch_news()
      if not news_data:
          exit(1)

      # 生成HTML
      html = build_html(news_data)

      # 推送
      title = f"📊 盘前速览 - {now.strftime('%m月%d日')}"
      push_wechat(title, html)
