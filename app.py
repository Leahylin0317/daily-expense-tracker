from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import os

app = Flask(__name__)
DATABASE = 'data/expenses.db'

# 初始化数据库
def init_db():
    os.makedirs('data', exist_ok=True)
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS expenses
                (id INTEGER PRIMARY KEY, 
                 date TEXT, 
                 category TEXT, 
                 amount REAL, 
                 note TEXT)''')
    conn.commit()
    conn.close()

# 主页：显示最近7天记录
@app.route('/')
def index():
    conn = sqlite3.connect(DATABASE)
    df = pd.read_sql('SELECT * FROM expenses ORDER BY date DESC LIMIT 7', conn)
    conn.close()
    return render_template('index.html', 
                          expenses=df.to_dict('records'),
                          today=datetime.now().strftime('%Y-%m-%d'))

# 添加记录
@app.route('/add', methods=['POST'])
def add_expense():
    data = {
        'date': request.form['date'],
        'category': request.form['category'],
        'amount': float(request.form['amount']),
        'note': request.form.get('note', '')
    }
    
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''INSERT INTO expenses (date, category, amount, note)
                VALUES (:date, :category, :amount, :note)''', data)
    conn.commit()
    conn.close()
    return redirect('/')

# 生成可视化报表
@app.route('/report')
def generate_report():
    conn = sqlite3.connect(DATABASE)
    df = pd.read_sql('SELECT * FROM expenses', conn)
    conn.close()

    # 按类别统计
    category_data = df.groupby('category')['amount'].sum().reset_index().to_dict('records')
    
    # 生成饼图（关键调整：减小尺寸并清理）
    plt.figure(figsize=(7, 3.5))  # 进一步缩小尺寸
    plt.pie([item['amount'] for item in category_data], 
            labels=[item['category'] for item in category_data], 
            autopct='%1.1f%%',
            pctdistance=0.8)  # 百分比标签位置
    plt.title('消费类别占比', y=1.05)  # 标题位置上移
    plt.tight_layout()  # 优化边距
    plt.savefig('static/category_pie.png')
    plt.close()  # 清理图形资源

    return render_template('report.html', category_data=category_data)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)