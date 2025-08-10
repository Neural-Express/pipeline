<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Weekly AI Digest – {{ date }}</title>
  <style>
    body { font-family: Arial, sans-serif; background:#f4f4f4; margin:0; padding:0; }
    .container { max-width:600px; margin:auto; padding:20px; background:#fff; }
    h1 { text-align:center; color:#333; }
    .card { border:1px solid #e1e1e1; border-radius:6px; padding:15px; margin-bottom:20px; }
    .card h2 { margin:0 0 8px; font-size:18px; }
    .meta { font-size:12px; color:#777; margin-bottom:10px; }
    .summary { font-size:14px; color:#555; line-height:1.4; }
    .footer { text-align:center; font-size:12px; color:#aaa; margin-top:30px; }
    a.read-more { display:inline-block; margin-top:12px; padding:8px 12px;
                  background:#2563eb; color:#fff; text-decoration:none;
                  border-radius:4px; font-size:13px; }
  </style>
</head>
<body>
  <div class="container">
    <h1>📰 Weekly AI Digest – {{ date }}</h1>
    {% for art in articles %}
    <div class="card">
      <h2><a href="{{ art.url }}" target="_blank">{{ art.title }}</a></h2>
      <div class="meta">{{ art.source_platform }}  |  {{ art.published_date[:10] }}</div>
      <div class="summary">{{ art.summary }}</div>
      <a class="read-more" href="{{ art.url }}" target="_blank">Read full article →</a>
    </div>
    {% endfor %}
    <div class="footer">
      You’re receiving this because you subscribed to Neural Express.<br>
      <a href="https://your-unsubscribe-link">Unsubscribe</a> | 
      <a href="https://neuralexpress.in">Visit Website</a>
    </div>
  </div>
</body>
</html>
