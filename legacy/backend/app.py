from flask import Flask, jsonify, request
from backend.query.DailyData import get_daily_data
from backend.query.HotMoneyData import get_hotmoney_data
from backend.query.DailyLimitData import get_daily_limit_data
from backend.query.StockBasicInfo import get_stock_basic_info
from backend.query.DailyHotMoneyTradeData import get_daily_hotmoney_trade_data
from backend.query.DailySectorLimitData import get_daily_sector_limit_data
from backend.query.ThsIndex import get_all_ths_index
from backend.task.ScheduledTasks import start_scheduled_tasks
import threading

app = Flask(__name__)

@app.route('/api/get_hotmoney_data', methods=['GET'])
def hotmoney_data():
    name = request.args.get('name', '')
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('pageSize', 10))
    
    data, total = get_hotmoney_data(name, page, page_size)
    return jsonify({'data': data, 'total': total})

@app.route('/api/get_daily_hotmoney_trade_data', methods=['GET'])
def daily_hotmoney_trade_data():
    hmName = request.args.get('hmName', '')
    tradeDate = request.args.get('tradeDate', '')
    tsName = request.args.get('tsName', '')
    tsCode = request.args.get('tsCode', '')
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('pageSize', 10))
    
    data, total = get_daily_hotmoney_trade_data(hmName, tradeDate, tsName, tsCode, page, page_size)
    return jsonify({'data': data, 'total': total})

@app.route('/api/get_stock_basic_info', methods=['GET'])
def stock_basic_info():
    symbol = request.args.get('symbol', '')
    name = request.args.get('name', '')
    industry = request.args.get('industry', '')
    start_date = request.args.get('startDate', '')
    end_date = request.args.get('endDate', '')
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('pageSize', 10))
    
    data, total = get_stock_basic_info(symbol, name, industry, start_date, end_date, page, page_size)
    return jsonify({'data': data, 'total': total})

@app.route('/api/get_daily_data', methods=['GET'])
def daily_data():
    ts_code = request.args.get('ts_code', '')

    data = get_daily_data(ts_code)
    return jsonify({'data': data})

@app.route('/api/get_daily_limit_data')
def daily_limit_data():
    data = get_daily_limit_data()
    return jsonify({'data': data})

@app.route('/api/get_daily_sector_limit_data', methods=['GET'])
def daily_sector_limit_data():
    sector_code = request.args.get('sector_code', '')
    sector_name = request.args.get('sector_name', '')
    sector_type = request.args.get('sector_type', '')
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    
    data = get_daily_sector_limit_data(sector_code, sector_name, sector_type, start_date, end_date)
    return jsonify(data)

@app.route('/api/get_all_ths_index', methods=['GET'])
def all_ths_index():
    data = get_all_ths_index()
    return jsonify(data)

if __name__ == '__main__':
    
    # 启动定时任务的线程
    scheduler_thread = threading.Thread(target=start_scheduled_tasks)
    scheduler_thread.daemon = True
    scheduler_thread.start()

    # 启动Flask应用
    app.run(debug=True)