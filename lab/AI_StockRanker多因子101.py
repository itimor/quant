# 本代码由可视化策略环境自动生成 2019年11月13日 21:36
# 本代码单元只能在可视化模式下编辑。您也可以拷贝代码，粘贴到新建的代码单元或者策略，然后修改。


# 回测引擎：初始化函数，只执行一次
def m4_initialize_bigquant_run(context):
    # 加载预测数据
    context.ranker_prediction = context.options['data'].read_df()

    # 系统已经设置了默认的交易手续费和滑点，要修改手续费可使用如下函数
    context.set_commission(PerOrder(buy_cost=0.0003, sell_cost=0.0013, min_cost=5))
    # 预测数据，通过options传入进来，使用 read_df 函数，加载到内存 (DataFrame)
    # 设置买入的股票数量，这里买入预测股票列表排名靠前的5只
    stock_count = 5
    # 每只的股票的权重，如下的权重分配会使得靠前的股票分配多一点的资金，[0.339160, 0.213986, 0.169580, ..]
    #context.stock_weights = T.norm([1 / math.log(i + 2) for i in range(0, stock_count)])
    #改为等权重配置
    context.stock_weights = [1 / stock_count for i in range(0, stock_count)]
    # 设置每只股票占用的最大资金比例
    context.max_cash_per_instrument = 0.2
    context.options['hold_days'] = 3

# 回测引擎：每日数据处理函数，每天执行一次
def m4_handle_data_bigquant_run(context, data):
    #获取当日日期
    today = data.current_dt
    today_date = data.current_dt.strftime('%Y-%m-%d')
    
    current_stock = [] # 当前持仓  
    current_stopdays_stock = [] # 固定天数卖出列表    
    current_stopwin_stock = []  # 止盈列表
    current_stoploss_stock = [] # 止损列表
    cash_for_sell = 0 # 当日卖出现金

    equities = {e.symbol: p for e, p in context.portfolio.positions.items() if p.amount>0}    
    if len(equities)>0:
        for sid in equities:            
            symbol = context.symbol(sid)            
            position = equities[sid]
            stock_market_price=data.current(symbol,'price')  #当前市场价
            stock_cost=position.cost_basis  #持仓成本价

            # 固定天数卖出
            if today-position.last_sale_date>=datetime.timedelta(2) and data.can_trade(symbol) and not context.has_unfinished_sell_order(equities[sid]):
                context.order_target_percent(symbol, 0)
                current_stopdays_stock.append(sid)
                cash_for_sell += position.amount * stock_market_price
                continue            

            # 止盈 赚20% 且为可交易状态
            if stock_market_price/stock_cost-1 >= 0.15  and data.can_trade(symbol) and not context.has_unfinished_sell_order(equities[sid]):
                context.order_target_percent(symbol,0)
                current_stopwin_stock.append(sid)
                cash_for_sell += position.amount * stock_market_price
                continue

            # 止损 亏5% 且为可交易状态
            if stock_market_price/stock_cost-1 <= -0.08 and data.can_trade(symbol) and not context.has_unfinished_sell_order(equities[sid]):   
                context.order_target_percent(symbol,0)     
                current_stoploss_stock.append(sid)
                cash_for_sell += position.amount * stock_market_price
                continue
            
            current_stock.append(sid)

    if len(current_stopdays_stock)>0:
        print(today_date,'固定天数卖出列表',current_stopdays_stock)
    if len(current_stopwin_stock)>0:
        print(today_date,'止盈股票列表',current_stopwin_stock)
    if len(current_stoploss_stock)>0:
        print(today_date,'止损股票列表',current_stoploss_stock)

    cash_for_buy = context.portfolio.cash + cash_for_sell -100 #买入股票 可用现金    
    #单只股标最大仓位金额
    max_cash_per_instrument = context.portfolio.portfolio_value * context.max_cash_per_instrument

    # 按日期过滤得到今日的预测数据
    ranker_prediction = context.ranker_prediction[context.ranker_prediction.date == today_date]

    current_buy_stock = []
    
    for index, row in ranker_prediction.iterrows():
        instrument = row['instrument']
        if instrument in current_stock:
            continue
        if instrument in current_stoploss_stock:
            continue
        if not data.can_trade(context.symbol(instrument)):
            continue
        # 评分太低，当天不买
        #if row['score']<1:
        #    break
       

        cash = max_cash_per_instrument
        breakFlag = False
        if(cash_for_buy < cash):
            cash = cash_for_buy
            breakFlag = True
        price = data.current(context.symbol(instrument), 'price')  # 最新价格
        stock_num = np.floor(cash/price/100)*100  # 向下取整
        context.order(context.symbol(instrument), stock_num) # 整百下单
        cash_for_buy = cash_for_buy - stock_num * price       
        current_buy_stock.append(instrument)
        if(breakFlag):
            break
    if len(current_buy_stock)>0:
        print(today_date,'买入股票',current_buy_stock)
# 回测引擎：准备数据，只执行一次
def m4_prepare_bigquant_run(context):
    #在数据准备函数中一次性计算每日的大盘风控条件相比于在handle中每日计算风控条件可以提高回测速度
    # 多取50天的数据便于计算均值(保证回测的第一天均值不为Nan值)，其中context.start_date和context.end_date是回测指定的起始时间和终止时间
    start_date= (pd.to_datetime(context.start_date) - datetime.timedelta(days=50)).strftime('%Y-%m-%d')     
    benckmark_data=D.history_data(instruments=['000001.SZA'], start_date=start_date, end_date=context.end_date,fields=['close'])
    #计算指数5日涨幅
    benckmark_data['ret5']=benckmark_data['close']/benckmark_data['close'].shift(5)-1
    #计算大盘风控条件，如果5日涨幅小于-5%则设置风险状态risk为1，否则为0
    benckmark_data['risk'] = np.where(benckmark_data['ret5']<-0.04,1,0)
    #修改日期格式为字符串(便于在handle中使用字符串日期索引来查看每日的风险状态)
    benckmark_data['date']=benckmark_data['date'].apply(lambda x:x.strftime('%Y-%m-%d'))
    #设置日期为索引
    benckmark_data.set_index('date',inplace=True)
    #把风控序列输出给全局变量context.benckmark_risk
    context.benckmark_risk=benckmark_data[['risk']]


m1 = M.instruments.v2(
    start_date='2010-01-01',
    end_date='2015-01-01',
    market='CN_STOCK_A',
    instrument_list='',
    max_count=0
)

m2 = M.advanced_auto_labeler.v2(
    instruments=m1.data,
    label_expr="""# #号开始的表示注释
# 0. 每行一个，顺序执行，从第二个开始，可以使用label字段
# 1. 可用数据字段见 https://bigquant.com/docs/data_history_data.html
#   添加benchmark_前缀，可使用对应的benchmark数据
# 2. 可用操作符和函数见 `表达式引擎 <https://bigquant.com/docs/big_expr.html>`_

# 计算收益：3日收盘价(作为卖出价格)除以明日开盘价(作为买入价格)
shift(close, -3) / shift(open, -1)

# 极值处理：用1%和99%分位的值做clip
clip(label, all_quantile(label, 0.01), all_quantile(label, 0.99))

# 将分数映射到分类，这里使用20个分类
all_wbins(label, 20)

# 过滤掉一字涨停的情况 (设置label为NaN，在后续处理和训练中会忽略NaN的label)
where(shift(high, -1) == shift(low, -1), NaN, label)
""",
    start_date='',
    end_date='',
    benchmark='000300.SHA',
    drop_na_label=True,
    cast_label_int=True
)

m3 = M.input_features.v1(
    features="""#价格类
Alpha_6=rank((open_0-(sum(amount_0/volume_0*adjust_factor_0,10)/10)))*(-1*abs(rank((close_0-amount_0/volume_0*adjust_factor_0))))
Alpha_9=(-1*rank(((sum(open_0,5)*sum(close_0/shift(close_0,1)-1,5))-delay((sum(open_0,5)*sum(close_0/shift(close_0,1)-1,5)),10))))
Alpha_30=min(product(rank(rank(scale(log(sum(ts_min(rank(rank((-1*rank(delta((close_0-1),5))))),2),1))))),1),5)+ts_rank(delay((-1*shift(close_0,1)/close_0-1),6),5)
Alpha_34=rank((-1*((1-(open_0/close_0)))))
Alpha_35=rank(((1-rank((std(close_0/shift(close_0,1),2)/stddev(close_0/shift(close_0,1)-1,5))))+(1-rank(delta(close_0,1)))))
Alpha_39=(-1*rank(ts_rank(close_0,10)))*rank((close_0/open_0))
Alpha_42=(((high_0*low_0)**0.5)-amount_0/volume_0*adjust_factor_0)
Alpha_43=(rank((amount_0/volume_0*adjust_factor_0-close_0))/rank((amount_0/volume_0*adjust_factor_0+close_0)))
Alpha_55=((-1*((low_0-close_0)*(open_0**5)))/((low_0-high_0)*(close_0** 5)))
Alpha_57=0-1*(1*(rank((sum(close_0/shift(close_0,1)-1,10)/sum(sum(close_0/shift(close_0,1)-1,2),3)))*rank(((close_0/shift(close_0,1)-1)*market_cap_0))))
Alpha_101=(close_0-open_0)/((high_0-low_0)+0.001)
# 量价类
Alpha_3=-1*correlation(rank(delta(log(volume_0),2)),rank(((close_0-open_0)/open_0)),6)
Alpha_4=-1*correlation(rank(open_0),rank(volume_0),10)
Alpha_12=(rank(ts_max((amount_0/volume_0*adjust_factor_0-close_0),3))+rank(ts_min((amount_0/volume_0*adjust_factor_0-close_0),3)))*rank(delta(volume_0,3))
Alpha_13=sign(delta(volume_0,1))*(-1*delta(close_0,1))
Alpha_14=-1*rank(covariance(rank(close_0),rank(volume_0),5))
Alpha_15=(-1*rank(delta(close_0/shift(close_0,1)-1,3)))*correlation(open_0,volume_0,10)
Alpha_16=-1*sum(rank(correlation(rank(high_0),rank(volume_0),3)),3)
Alpha_17=-1*rank(covariance(rank(high_0),rank(volume_0),5))
Alpha_27=-1*ts_max(correlation(ts_rank(volume_0,5),ts_rank(high_0,5),5),3)
Alpha_45=(-1*correlation(high_0,rank(volume_0),5))
Alpha_48=(((rank((1/close_0))*volume_0)/mean(amount_0,20))*((high_0*rank((high_0-close_0)))/(sum(high_0,5) /5)))-rank((amount_0/volume_0*adjust_factor_0-delay(amount_0/volume_0*adjust_factor_0,5)))
Alpha_51=(-1*ts_max(rank(correlation(rank(volume_0),rank(amount_0/volume_0*adjust_factor_0),5)),5))
Alpha_83=(rank(delay(((high_0-low_0)/(sum(close_0,5)/5)),2))*rank(rank(volume_0)))/(((high_0-low_0)/(sum(close_0,5)/5))/(amount_0/volume_0*adjust_factor_0-close_0))
"""
)

m15 = M.general_feature_extractor.v7(
    instruments=m1.data,
    features=m3.data,
    start_date='',
    end_date='',
    before_start_days=30
)

m16 = M.derived_feature_extractor.v3(
    input_data=m15.data,
    features=m3.data,
    date_col='date',
    instrument_col='instrument',
    drop_na=False,
    remove_extra_columns=False
)

m7 = M.join.v3(
    data1=m2.data,
    data2=m16.data,
    on='date,instrument',
    how='inner',
    sort=False
)

m13 = M.dropnan.v1(
    input_data=m7.data
)

m5 = M.chinaa_stock_filter.v1(
    input_data=m13.data,
    index_constituent_cond=['全部'],
    board_cond=[],
    industry_cond=['全部'],
    st_cond=['正常'],
    output_left_data=False
)

m9 = M.instruments.v2(
    start_date=T.live_run_param('trading_date', '2015-01-01'),
    end_date=T.live_run_param('trading_date', '2019-08-01'),
    market='CN_STOCK_A',
    instrument_list='',
    max_count=0
)

m17 = M.general_feature_extractor.v7(
    instruments=m9.data,
    features=m3.data,
    start_date='',
    end_date='',
    before_start_days=30
)

m18 = M.derived_feature_extractor.v3(
    input_data=m17.data,
    features=m3.data,
    date_col='date',
    instrument_col='instrument',
    drop_na=False,
    remove_extra_columns=False
)

m14 = M.dropnan.v1(
    input_data=m18.data
)

m10 = M.chinaa_stock_filter.v1(
    input_data=m14.data,
    index_constituent_cond=['全部'],
    board_cond=[],
    industry_cond=['全部'],
    st_cond=['正常'],
    output_left_data=False
)

m11 = M.input_features.v1(
    features="""Alpha_6
Alpha_9
Alpha_30
Alpha_35
Alpha_39
Alpha_55
Alpha_57

Alpha_3
Alpha_4
Alpha_14
Alpha_16
Alpha_17
Alpha_27
Alpha_45"""
)

m6 = M.stock_ranker_train.v5(
    training_ds=m5.data,
    features=m11.data,
    learning_algorithm='排序',
    number_of_leaves=30,
    minimum_docs_per_leaf=1000,
    number_of_trees=20,
    learning_rate=0.2,
    max_bins=500,
    feature_fraction=1,
    m_lazy_run=False
)

m8 = M.stock_ranker_predict.v5(
    model=m6.model,
    data=m10.data,
    m_lazy_run=False
)

m4 = M.trade.v4(
    instruments=m9.data,
    options_data=m8.predictions,
    start_date='',
    end_date='',
    initialize=m4_initialize_bigquant_run,
    handle_data=m4_handle_data_bigquant_run,
    prepare=m4_prepare_bigquant_run,
    volume_limit=0.025,
    order_price_field_buy='open',
    order_price_field_sell='close',
    capital_base=100000,
    auto_cancel_non_tradable_orders=True,
    data_frequency='daily',
    price_type='后复权',
    product_type='股票',
    plot_charts=True,
    backtest_only=False,
    benchmark=''
)