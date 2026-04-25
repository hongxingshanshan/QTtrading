from tqdm import tqdm 
from backend import DataBase as db
from datetime import datetime, timedelta
from backend.tushare import token

# 初始化pro接口
pro = token.get_tushare().pro_api()

def import_daily_limit_cpt_list(start_date, end_date):
    """
    获取每天涨停股票最多最强的概念板块数据并导入daily_limit_cpt_list表
    参数:
        start_date: 开始日期 (格式: YYYYMMDD)
        end_date: 结束日期 (格式: YYYYMMDD)
    """
    # 获取数据库连接
    conn = db.get_db()
    cursor = conn.cursor()

    # 定义每次请求的最大数据量
    limit = 2000
    offset = 0

    while True:
        # 拉取最强板块数据
        df = pro.limit_cpt_list(
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            offset=offset,
            fields='ts_code,name,trade_date,days,up_stat,cons_nums,up_nums,pct_chg,rank'
        )

        # 如果没有数据，则退出循环
        if df.empty:
            break

        # 将 NaN 值替换为 None
        df = df.replace({float('nan'): None})

        # 将数据转换为字典列表
        data = df.to_dict(orient='records')

        # 插入数据到数据库，使用主键存在覆盖逻辑
        for record in tqdm(data, desc=f"Importing daily_limit_cpt_list data from {start_date} to {end_date} page {offset}", total=len(data), mininterval=0.1):
            try:
                cursor.execute('''
                    INSERT INTO daily_limit_cpt_list (
                        ts_code, name, trade_date, days, up_stat, cons_nums, up_nums, pct_chg, `rank`
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        name=VALUES(name),
                        days=VALUES(days),
                        up_stat=VALUES(up_stat),
                        cons_nums=VALUES(cons_nums),
                        up_nums=VALUES(up_nums),
                        pct_chg=VALUES(pct_chg),
                        `rank`=VALUES(`rank`)
                ''', (
                    record['ts_code'], record['name'], record['trade_date'], record['days'], record['up_stat'],
                    record['cons_nums'], record['up_nums'], record['pct_chg'], record['rank']
                ))
            except Exception as e:
                print(f"Error inserting record: {record}")
                print(f"Error details: {e}")
                continue

        # 提交事务
        conn.commit()

        # 更新offset
        offset += limit

    # 关闭数据库连接
    cursor.close()
    conn.close()

    print(f"Daily limit concept data imported from {start_date} to {end_date}.")

def import_hm_detail_data(start_date, end_date):
    """
    获取每日游资交易数据并导入hm_detail表
    参数:
        start_date: 开始日期 (格式: YYYYMMDD)
        end_date: 结束日期 (格式: YYYYMMDD)
    """
    # 获取数据库连接
    conn = db.get_db()
    cursor = conn.cursor()

    # 定义每次请求的最大数据量
    limit = 2000
    offset = 0

    while True:
        # 拉取游资交易数据
        df = pro.hm_detail(trade_date=start_date,
            limit=limit,
            offset=offset,
            fields='trade_date,ts_code,ts_name,buy_amount,sell_amount,net_amount,hm_name,hm_orgs,tag'
        )

        # 如果没有数据，则退出循环
        if df.empty:
            break

        # 将 NaN 值替换为 None
        df = df.replace({float('nan'): None})

        # 将数据转换为字典列表
        data = df.to_dict(orient='records')

        # 插入数据到数据库，使用主键存在覆盖逻辑
        for record in tqdm(data, desc=f"Importing hm_detail data from {start_date} to {end_date} page {offset}", total=len(data), mininterval=0.1):
            try:
                cursor.execute('''
                    INSERT INTO daily_hot_money_trading (
                        trade_date, ts_code, ts_name, buy_amount, sell_amount, net_amount, hm_name, hm_orgs, tag
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        ts_name=VALUES(ts_name),
                        buy_amount=VALUES(buy_amount),
                        sell_amount=VALUES(sell_amount),
                        net_amount=VALUES(net_amount),
                        hm_name=VALUES(hm_name),
                        hm_orgs=VALUES(hm_orgs),
                        tag=VALUES(tag)
                ''', (
                    record['trade_date'], record['ts_code'], record['ts_name'], record['buy_amount'],
                    record['sell_amount'], record['net_amount'], record['hm_name'], record['hm_orgs'], record.get('tag')
                ))
            except Exception as e:
                print(f"Error inserting record: {record}")
                print(f"Error details: {e}")
                continue

        # 提交事务
        conn.commit()

        # 更新offset
        offset += limit

    # 关闭数据库连接
    cursor.close()
    conn.close()

    print(f"HM detail data imported from {start_date} to {end_date}.")


def import_daily_data_for_stock(ts_code, start_date, end_date):
    """
    根据股票ts_code和开始时间结束时间导入daily_data表
    """
    start_date = datetime.strptime(start_date, '%Y%m%d').date()
    end_date = datetime.strptime(end_date, '%Y%m%d').date()

    # 获取数据库连接
    conn = db.get_db()
    cursor = conn.cursor(dictionary=True)

    offset = 0
    limit = 6000

    while True:
        # 拉取每日数据
        start_date_str = start_date.strftime('%Y%m%d')
        end_date_str = end_date.strftime('%Y%m%d')
        df = pro.daily(ts_code=ts_code, start_date=start_date_str, end_date=end_date_str, offset=offset, limit=limit)

        # 将 NaN 值替换为 None
        df = df.replace({float('nan'): None})

        data = df.to_dict(orient='records')

        if not data:
            break

        # 插入数据到数据库，使用主键存在覆盖逻辑
        for record in data:
            cursor.execute('''
                INSERT INTO daily_data (ts_code, trade_date, open, high, low, close, pre_close, price_change, pct_chg, vol, amount)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    open=VALUES(open),
                    high=VALUES(high),
                    low=VALUES(low),
                    close=VALUES(close),
                    pre_close=VALUES(pre_close),
                    price_change=VALUES(price_change),
                    pct_chg=VALUES(pct_chg),
                    vol=VALUES(vol),
                    amount=VALUES(amount)
            ''', (
                record['ts_code'], record['trade_date'], record['open'], record['high'], record['low'], record['close'],
                record['pre_close'], record['change'], record['pct_chg'], record['vol'], record['amount']
            ))

        offset += limit

    conn.commit()
    cursor.close()
    conn.close()

def import_all_daily_data(start_date, end_date):
    """
    遍历所有股票并导入daily_data表（单线程版本）
    参数:
        start_date: 开始日期 (格式: YYYYMMDD)
        end_date: 结束日期 (格式: YYYYMMDD)
    """
    # 将输入的日期字符串转换为日期对象
    start_date = datetime.strptime(start_date, '%Y%m%d').date()
    end_date = datetime.strptime(end_date, '%Y%m%d').date()

    # 获取数据库连接
    conn = db.get_db()
    cursor = conn.cursor(dictionary=True)

    # 获取所有股票的ts_code和上市时间
    cursor.execute('SELECT ts_code, list_date FROM stock_basic_info')
    stocks = cursor.fetchall()

    # 遍历所有股票
    for index, stock in tqdm(enumerate(stocks),desc=f"Importing all_daily_data from {start_date} to {end_date}", total=len(stocks), mininterval=0.1):
        ts_code = stock['ts_code']
        list_date = stock['list_date']

        # 如果开始时间早于上市时间，则将当前股票的起始日期设置为上市时间
        current_start_date = start_date
        if current_start_date < list_date:
            current_start_date = list_date

        # 打印进度
        # print(f"begin: {index + 1}/{total_stocks} stocks processed, ts_code={ts_code}, start_date={current_start_date}, end_date={end_date}")

        # 导入每日数据
        import_daily_data_for_stock(ts_code, current_start_date.strftime('%Y%m%d'), end_date.strftime('%Y%m%d'))

        # 打印进度
        # print(f"end: {index + 1}/{total_stocks} stocks processed, ts_code={ts_code}, start_date={current_start_date}, end_date={end_date}")

    # 关闭数据库连接
    cursor.close()
    conn.close()

    print(f"All daily data imported from {start_date} to {end_date}.")

def import_daily_limit_data(start_date, end_date):
    """
    获取每日涨跌停数据并导入daily_limit_data表
    参数:
        start_date: 开始日期 (格式: YYYYMMDD)
        end_date: 结束日期 (格式: YYYYMMDD)
    """
    # 获取数据库连接
    conn = db.get_db()
    cursor = conn.cursor()

    # 定义每次请求的最大数据量
    limit = 1000
    offset = 0

    while True:
        # 拉取涨跌停数据
        df = pro.limit_list_d(
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            offset=offset,
            fields='trade_date,ts_code,industry,name,close,pct_chg,amount,limit_amount,float_mv,total_mv,turnover_ratio,fd_amount,first_time,last_time,open_times,up_stat,limit_times,limit'
        )

        # 如果没有数据，则退出循环
        if df.empty:
            break

        # 将 NaN 值替换为 None
        df = df.replace({float('nan'): None})

        # 将数据转换为字典列表
        data = df.to_dict(orient='records')

        # 插入数据到数据库，使用主键存在覆盖逻辑
        for record in tqdm(data, desc=f"Importing daily_limit_data data from {start_date} to {end_date} page {offset}", total=len(data), mininterval=0.1):
            try:
                cursor.execute('''
                    INSERT INTO daily_limit_data (
                        trade_date, ts_code, industry, name, close, pct_chg, amount, limit_amount,
                        float_mv, total_mv, turnover_ratio, fd_amount, first_time, last_time,
                        open_times, up_stat, limit_times, limit_status
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        industry=VALUES(industry),
                        name=VALUES(name),
                        close=VALUES(close),
                        pct_chg=VALUES(pct_chg),
                        amount=VALUES(amount),
                        limit_amount=VALUES(limit_amount),
                        float_mv=VALUES(float_mv),
                        total_mv=VALUES(total_mv),
                        turnover_ratio=VALUES(turnover_ratio),
                        fd_amount=VALUES(fd_amount),
                        first_time=VALUES(first_time),
                        last_time=VALUES(last_time),
                        open_times=VALUES(open_times),
                        up_stat=VALUES(up_stat),
                        limit_times=VALUES(limit_times),
                        limit_status=VALUES(limit_status)
                ''', (
                    record['trade_date'], record['ts_code'], record.get('industry'), record.get('name'),
                    record['close'], record['pct_chg'], record['amount'], record.get('limit_amount'),
                    record['float_mv'], record['total_mv'], record['turnover_ratio'], record['fd_amount'],
                    record.get('first_time'), record.get('last_time'), record['open_times'], record['up_stat'],
                    record['limit_times'], record['limit']
                ))
            except Exception as e:
                print(f"Error inserting record: {record}")
                print(f"Error details: {e}")
                continue

        # 提交事务
        conn.commit()

        # 更新offset
        offset += limit

        #睡眠等待，防止请求过于频繁
        # time.sleep(0.5)

    # 关闭数据库连接
    cursor.close()
    conn.close()

    print(f"Daily limit data imported from {start_date} to {end_date}.")

def import_daily_limit_data_by_month(start_date, end_date):
    """
    按月导入数据
    参数:
        start_date: 开始日期 (格式: YYYYMMDD)
        end_date: 结束日期 (格式: YYYYMMDD)
    """
    print(f"Importing data from {start_date} to {end_date}")

    import_daily_limit_data(start_date, end_date)

    print(f"All daily limit data imported from {start_date} to {end_date}.")


def import_daily_sector_limit_data_by_date(start_date, end_date):
    # 获取数据库连接
    conn = db.get_db()
    cursor = conn.cursor(dictionary=True)

    # 查询所有板块信息
    cursor.execute("SELECT ts_code FROM ths_index")
    sectors = cursor.fetchall()

    # 遍历每个板块和每天的时间段进行数据导入
    for sector in sectors:
        ts_code = sector['ts_code']
        print(f"Begin import data for sector {ts_code} on {start_date}~{end_date}")
        # 查询并插入数据
        import_daily_sector_limit_data_by_ts_code(ts_code, start_date, end_date)
        print(f"End import data for sector {ts_code} on {start_date}~{end_date}")

    # 关闭数据库连接
    cursor.close()
    conn.close()
    print("All daily sector limit data imported.")

def import_daily_sector_limit_data_by_ts_code(ts_code, start_date, end_date):
    # 获取数据库连接
    conn = db.get_db()
    cursor = conn.cursor()

    # 插入数据的 SQL 语句
    insert_data_query = """
    INSERT INTO daily_sector_limit_data (sector_code, sector_name, sector_type, trade_date, up_limit_count, down_limit_count)
    SELECT 
        ti.ts_code AS sector_code,
        ti.name AS sector_name,
        ti.type AS sector_type,
        dld.trade_date,
        SUM(CASE WHEN dld.limit_status = 'U' THEN 1 ELSE 0 END) AS up_limit_count,
        SUM(CASE WHEN dld.limit_status = 'D' THEN 1 ELSE 0 END) AS down_limit_count
    FROM 
        ths_index ti
    JOIN 
        ths_member tm ON ti.ts_code = tm.ts_code
    JOIN 
        daily_limit_data dld ON tm.con_code = dld.ts_code
    WHERE 
        dld.trade_date >= %s AND dld.trade_date <= %s 
    GROUP BY 
        ti.ts_code, ti.name, ti.type, dld.trade_date
    ON DUPLICATE KEY UPDATE
        sector_name = VALUES(sector_name),
        sector_type = VALUES(sector_type),
        up_limit_count = VALUES(up_limit_count),
        down_limit_count = VALUES(down_limit_count)
    """
    cursor.execute(insert_data_query, (start_date, end_date))
    conn.commit()

    # 关闭数据库连接
    cursor.close()
    conn.close()
    print(f"Daily sector limit data imported for sector {ts_code} from {start_date} to {end_date}.")

def import_top_list_data(start_date, end_date):
    """
    获取指定时间段内的龙虎榜每日交易明细数据并导入daily_trade_data表
    参数:
        start_date: 开始日期 (格式: YYYYMMDD)
        end_date: 结束日期 (格式: YYYYMMDD)
    """
    # 获取数据库连接
    conn = db.get_db()
    cursor = conn.cursor()

    # 定义每次请求的最大数据量
    limit = 10000
    offset = 0

    current_date = datetime.strptime(start_date, '%Y%m%d')
    end_date = datetime.strptime(end_date, '%Y%m%d')

    while current_date <= end_date:
        trade_date_str = current_date.strftime('%Y%m%d')

        while True:
            # 拉取龙虎榜每日交易明细数据
            df = pro.top_list(
                trade_date=trade_date_str,
                limit=limit,
                offset=offset,
                fields='trade_date,ts_code,name,close,pct_change,turnover_rate,amount,l_sell,l_buy,l_amount,net_amount,net_rate,amount_rate,float_values,reason'
            )

            # 如果没有数据，则退出循环
            if df.empty:
                break

            # 将 NaN 值替换为 None
            df = df.replace({float('nan'): None})

            # 将数据转换为字典列表
            data = df.to_dict(orient='records')

            # 插入数据到数据库，使用主键存在覆盖逻辑
            for record in tqdm(data, desc=f"Importing top_trade_data data for {trade_date_str} page {offset}", total=len(data), mininterval=0.1):
                try:
                    cursor.execute('''
                        INSERT INTO top_trade_data (
                            trade_date, ts_code, name, close, pct_change, turnover_rate, amount, l_sell, l_buy, l_amount, net_amount, net_rate, amount_rate, float_values, reason
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE
                            name=VALUES(name),
                            close=VALUES(close),
                            pct_change=VALUES(pct_change),
                            turnover_rate=VALUES(turnover_rate),
                            amount=VALUES(amount),
                            l_sell=VALUES(l_sell),
                            l_buy=VALUES(l_buy),
                            l_amount=VALUES(l_amount),
                            net_amount=VALUES(net_amount),
                            net_rate=VALUES(net_rate),
                            amount_rate=VALUES(amount_rate),
                            float_values=VALUES(float_values),
                            reason=VALUES(reason)
                    ''', (
                        record['trade_date'], record['ts_code'], record['name'], record['close'], record['pct_change'],
                        record['turnover_rate'], record['amount'], record['l_sell'], record['l_buy'], record['l_amount'],
                        record['net_amount'], record['net_rate'], record['amount_rate'], record['float_values'], record['reason']
                    ))
                    conn.commit()
                except Exception as e:
                    print(f"Error inserting record: {record}")
                    print(f"Error details: {e}")
                    conn.rollback()

            # 增加偏移量
            offset += limit

        # 重置偏移量并移动到下一天
        offset = 0
        current_date += timedelta(days=1)

    cursor.close()
    conn.close()
    print(f"Top list data imported from {start_date} to {end_date}.")

def import_top_inst_data(start_date, end_date):
    """
    获取指定时间段内的龙虎榜每日机构交易明细数据并导入top_inst_trade_data表
    参数:
        start_date: 开始日期 (格式: YYYYMMDD)
        end_date: 结束日期 (格式: YYYYMMDD)
    """
    # 获取数据库连接
    conn = db.get_db()
    cursor = conn.cursor()

    # 定义每次请求的最大数据量
    limit = 10000
    offset = 0

    current_date = datetime.strptime(start_date, '%Y%m%d')
    end_date = datetime.strptime(end_date, '%Y%m%d')

    while current_date <= end_date:
        trade_date_str = current_date.strftime('%Y%m%d')

        while True:
            # 拉取龙虎榜每日机构交易明细数据
            df = pro.top_inst(
                trade_date=trade_date_str,
                limit=limit,
                offset=offset,
                fields='trade_date,ts_code,exalter,side,buy,buy_rate,sell,sell_rate,net_buy,reason'
            )

            # 如果没有数据，则退出循环
            if df.empty:
                break

            # 将 NaN 值替换为 None
            df = df.replace({float('nan'): None})

            # 将数据转换为字典列表
            data = df.to_dict(orient='records')

            # 插入数据到数据库，使用主键存在覆盖逻辑
            for record in tqdm(data, desc=f"Importing top_inst_data data for {trade_date_str}", total=len(data), mininterval=0.1):
                try:
                    cursor.execute('''
                        INSERT INTO top_inst_trade_data (
                            trade_date, ts_code, exalter, side, buy, buy_rate, sell, sell_rate, net_buy, reason
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE
                            buy=VALUES(buy),
                            buy_rate=VALUES(buy_rate),
                            sell=VALUES(sell),
                            sell_rate=VALUES(sell_rate),
                            net_buy=VALUES(net_buy),
                            reason=VALUES(reason)
                    ''', (
                        record['trade_date'], record['ts_code'], record['exalter'], record['side'], record['buy'],
                        record['buy_rate'], record['sell'], record['sell_rate'], record['net_buy'], record['reason']
                    ))
                    conn.commit()
                except Exception as e:
                    print(f"Error inserting record: {record}")
                    print(f"Error details: {e}")
                    conn.rollback()

            # 增加偏移量
            offset += limit

        # 重置偏移量并移动到下一天
        offset = 0
        current_date += timedelta(days=1)

    cursor.close()
    conn.close()
    print(f"Top inst data imported from {start_date} to {end_date}.")

#增量数据导入
# 导入每日股票交易数据
# import_daily_data_for_stock('000536.SZ', '20250217', '20250217')
# 导入每日涨跌停数据
# import_daily_limit_data_by_month('20250305', '20250305')
# 导入每日板块涨跌停数据
# import_daily_sector_limit_data_by_ts_code('','20250305', '20250305')
# 导入所有股票每日交易数据
# import_all_daily_data('20250221', '20250304')
# 导入每日游资交易数据
# import_hm_detail_data('20250307', '20250307')
# 导入每日最强概念板块数据
# import_daily_limit_cpt_list('20250307', '20250307')
# 导入每日龙虎榜股票数据
# import_top_list_data('20250307', '20250307')
# 导入每日龙虎榜机构交易明细数据
# import_top_inst_data('20250307','20250307')

def incr_job(start_date, end_date):
    
    # 导入每日最强板块数据
    try:
        import_daily_limit_cpt_list(start_date,end_date)
    except Exception as e:
        print(f"Error in import_daily_limit_cpt_list: {e}")

    # 导入每日涨跌停数据
    try:
        import_daily_limit_data(start_date, end_date)
    except Exception as e:
        print(f"Error in import_daily_limit_data_by_month: {e}")

    # 导入每日行业涨跌停数据
    try:
        import_daily_sector_limit_data_by_ts_code('', start_date, end_date)
    except Exception as e:
        print(f"Error in import_daily_sector_limit_data_by_ts_code: {e}")

    # 导入每日详细数据
    try:
        import_hm_detail_data(start_date, end_date)
    except Exception as e:
        print(f"Error in import_hm_detail_data: {e}")
    
    # 导入每日排行榜数据
    try:
        import_top_list_data(start_date,end_date)
    except Exception as e:
        print(f"Error in import_top_list_data: {e}")
    
    # 导入每日机构数据
    try:
        import_top_inst_data(start_date,end_date)
    except Exception as e:
        print(f"Error in import_top_inst_data: {e}")

    # 导入所有每日数据
    try:
        import_all_daily_data(start_date, end_date)
    except Exception as e:
        print(f"Error in import_all_daily_data: {e}")
    

# incr_job('20250321','20250405')