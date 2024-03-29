"""
    This script models the most simplified version of the algorithm.
    No micro-side factor is contained (no death-and-birth).
    Only macro factors (purely stochastic equation driven).
"""

import pandas_datareader as web
import matplotlib.pyplot as plt      
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
np.random.seed(17)

def generate_parameter(original_price_list, target_adjustment):
    
    sampling_price_list = []
    for index in range(len(original_price_list)):
        price_list = []
        if len(original_price_list)-index > 10:
            for number in range(10):
                price_list.append(original_price_list[index+number])
            sampling_price_list.append(price_list)

    theta = []
    sigma = []
    mu = []

    for index in range(len(sampling_price_list)):
        X_t = np.array(sampling_price_list[index])
        y = np.diff(X_t)
        X = X_t[:-1].reshape(-1, 1)
        reg = LinearRegression(fit_intercept=True)
        reg.fit(X, y)
        alpha = -reg.coef_[0]
        gamma = reg.intercept_ / alpha
        y_hat = reg.predict(X)
        beta = np.std(y - y_hat)
        theta.append(alpha)
        mu.append(gamma)
        sigma.append(beta)


    x0 = original_price_list[10]
    simulated_price = [x0]

    for index in range(len(sampling_price_list)):
        mean = mu[index]
        theta_tmp = theta[index]
        sigm = sigma[index]
        dWt = np.random.normal(0,1)
        simulated_price.append(simulated_price[-1]+theta_tmp * (mean-simulated_price[-1]) + sigm * dWt)
    
    adjust_factor = target_adjustment/x0
    adjusted_price = [i*adjust_factor for i in simulated_price]
    adjusted_price[0] = np.round(adjusted_price[0])

    split = [adjusted_price[i:i + 10] for i in range(0, len(adjusted_price), 10)]

    # print(split[0])

    day_based_price_list = [adjusted_price[0]]
    tick_based_price_list = [adjusted_price[0]]
    second_based_price_list = [adjusted_price[0]]

    for index in range(len(split[:-1])):
        one_day = split[index]
        one_day_df = pd.DataFrame(one_day, columns = ['one_day_price'])
        drift = one_day_df.pct_change()
        drift = drift[1:]['one_day_price'].tolist()
        
        x0 = one_day[0]
        ticks_in_min = 60
        dt = 1/(60*ticks_in_min)
        T = 9
        num = int(T/dt)

        daily_price = [x0]

        for k in range(num):
            mu_tmp = drift[int(k*dt)]*0.9
            sigma = 0.1
            dBt = np.random.normal(0,np.sqrt(dt))
            next_price = daily_price[-1] + mu_tmp * daily_price[-1] * dt + sigma * np.sqrt(daily_price[-1]) * dBt
            daily_price.append(next_price)
        
        daily_price[-1] = one_day[-1]
        second_based_price_list += daily_price
        day_based_price_list.append(one_day[-1])

        daily_price_scaled = []
        adjust_num = 180

        for inx in range(len(daily_price)):
            if inx % adjust_num == 0:
                daily_price_scaled.append(daily_price[inx])

        tick_based_price_list += daily_price_scaled

    return(simulated_price, tick_based_price_list, day_based_price_list, second_based_price_list, adjusted_price)

current_tick = pd.read_csv('/Users/xiaokeai/Desktop/ast/ast_tick_price.csv')
current_day = pd.read_csv('/Users/xiaokeai/Desktop/ast/ast_day_price.csv')
current_second = pd.read_csv('/Users/xiaokeai/Desktop/ast/ast_second_price.csv')

start_date = "2021/10/1"
end_date = "2022/7/1"
symbol = ['BYDDY']
index_data = web.get_data_yahoo(symbol, start_date, end_date)
index_price_df = index_data['Adj Close']
index_price_list = index_price_df['BYDDY'].to_list()
target_adjustment = current_second["second_based"].to_list()[-1]

simulated_price, tick_based_price_list, day_based_price_list, second_based_price_list, adjusted_price = generate_parameter(index_price_list, target_adjustment)

aspect_simulator_index_tick = pd.DataFrame(tick_based_price_list, columns=["tick_based"])
aspect_simulator_index_day = pd.DataFrame(day_based_price_list, columns=["day_based"])
aspect_simulator_index_second = pd.DataFrame(second_based_price_list, columns=["second_based"])
aspect_simulator_index_adjust = pd.DataFrame(adjusted_price, columns=["adjusted_price"])

# start_date_1 = "2020/9/1"
# end_date_1 = "2021/3/1"
# symbol_1 = ['GS']
# index_data_1 = web.get_data_yahoo(symbol_1, start_date_1, end_date_1)
# index_price_df_1 = index_data_1['Adj Close']
# index_price_list_1 = index_price_df_1['GS'].to_list()
# target_adjustment_1 = second_based_price_list[-1]


# simulated_price_1, tick_based_price_list_1, day_based_price_list_1, second_based_price_list_1, adjusted_price_1 = generate_parameter(index_price_list_1, target_adjustment_1)

# aspect_simulator_index_tick_1 = pd.DataFrame(tick_based_price_list_1, columns=["tick_based"])
# aspect_simulator_index_day_1 = pd.DataFrame(day_based_price_list_1, columns=["day_based"])
# aspect_simulator_index_second_1 = pd.DataFrame(second_based_price_list_1, columns=["second_based"])
# aspect_simulator_index_adjust_1 = pd.DataFrame(adjusted_price_1, columns=["adjusted_price"])


# start_date_2 = "2015/11/1"
# end_date_2 = "2016/1/1"
# symbol_2 = ['JPM']
# index_data_2 = web.get_data_yahoo(symbol_2, start_date_2, end_date_2)
# index_price_df_2 = index_data_2['Adj Close']
# index_price_list_2 = index_price_df_2['JPM'].to_list()
# target_adjustment_2 = second_based_price_list_1[-1]

# simulated_price_2, tick_based_price_list_2, day_based_price_list_2, second_based_price_list_2, adjusted_price_2 = generate_parameter(index_price_list_2, target_adjustment_2)

# aspect_simulator_index_tick_2 = pd.DataFrame(tick_based_price_list_2, columns=["tick_based"])
# aspect_simulator_index_day_2 = pd.DataFrame(day_based_price_list_2, columns=["day_based"])
# aspect_simulator_index_second_2 = pd.DataFrame(second_based_price_list_2, columns=["second_based"])
# aspect_simulator_index_adjust_2 = pd.DataFrame(adjusted_price_2, columns=["adjusted_price"])

# aspect_simulator_index_tick=aspect_simulator_index_tick.append(aspect_simulator_index_tick_1)
# aspect_simulator_index_day=aspect_simulator_index_day.append(aspect_simulator_index_day_1)
# aspect_simulator_index_second=aspect_simulator_index_second.append(aspect_simulator_index_second_1)
# aspect_simulator_index_adjust=aspect_simulator_index_adjust.append(aspect_simulator_index_adjust_1)

# aspect_simulator_index_tick=aspect_simulator_index_tick.append(aspect_simulator_index_tick_2)
# aspect_simulator_index_day=aspect_simulator_index_day.append(aspect_simulator_index_day_2)
# aspect_simulator_index_second=aspect_simulator_index_second.append(aspect_simulator_index_second_2)
# aspect_simulator_index_adjust=aspect_simulator_index_adjust.append(aspect_simulator_index_adjust_2)

current_second = current_second.append(aspect_simulator_index_second)
current_tick = current_tick.append(aspect_simulator_index_tick)
current_day = current_day.append(aspect_simulator_index_day)

current_tick.to_csv('/Users/xiaokeai/Desktop/price_data/ast/ast_tick_price.csv')
current_day.to_csv('/Users/xiaokeai/Desktop/price_data/ast/ast_day_price.csv')
current_second.to_csv('/Users/xiaokeai/Desktop/price_data/ast/ast_second_price.csv')
# aspect_simulator_index_adjust.to_csv('/Users/xiaokeai/Desktop/price_data/jky/jky_adjust_price.csv')


# start_date_comp_1 = "2016/4/1"
# end_date_comp_1 = "2017/8/1"
# symbol_comp_1 = ['NTDOY']
# stock_data_comp_1 = web.get_data_yahoo(symbol_comp_1, start_date_comp_1, end_date_comp_1)
# stock_price_comp_1 = stock_data_comp_1['Adj Close']
# stock_price_list_1 = stock_price_comp_1['NTDOY'].to_list()
# # stock_price_list_1 = stock_price_comp_1
# target_adjustment_1 = second_based_price_list_comp[-1]
# tick_based_price_list_comp_1, day_based_price_list_comp_1, second_based_price_list_comp_1 = generate_stock_parameter(stock_price_list_1, index_price, target_adjustment_1)

# aspect_simulator_wrkn_tick_1 = pd.DataFrame(tick_based_price_list_comp_1, columns=["tick_based"])
# aspect_simulator_wrkn_day_1 = pd.DataFrame(day_based_price_list_comp_1, columns=["day_based"])
# aspect_simulator_wrkn_second_1 = pd.DataFrame(second_based_price_list_comp_1, columns=["second_based"])

# aspect_simulator_wrkn_tick=aspect_simulator_wrkn_tick.append(aspect_simulator_wrkn_tick_1)
# aspect_simulator_wrkn_day=aspect_simulator_wrkn_day.append(aspect_simulator_wrkn_day_1)
# aspect_simulator_wrkn_second=aspect_simulator_wrkn_second.append(aspect_simulator_wrkn_second_1)



# start_date_comp_2 = "2021/2/1"
# end_date_comp_2 = "2022/1/1"
# symbol_comp_2 = ['BABA']
# stock_data_comp_2 = web.get_data_yahoo(symbol_comp_2, start_date_comp_2, end_date_comp_2)
# stock_price_comp_2 = stock_data_comp_2['Adj Close']
# stock_price_list_2 = stock_price_comp_2['BABA'].to_list()
# # stock_price_list_1 = stock_price_comp_1
# target_adjustment_2 = second_based_price_list_comp_1[-1]
# tick_based_price_list_comp_2, day_based_price_list_comp_2, second_based_price_list_comp_2 = generate_stock_parameter(stock_price_list_2, index_price, target_adjustment_2)

# aspect_simulator_wrkn_tick_2 = pd.DataFrame(tick_based_price_list_comp_2, columns=["tick_based"])
# aspect_simulator_wrkn_day_2 = pd.DataFrame(day_based_price_list_comp_2, columns=["day_based"])
# aspect_simulator_wrkn_second_2 = pd.DataFrame(second_based_price_list_comp_2, columns=["second_based"])

# aspect_simulator_wrkn_tick=aspect_simulator_wrkn_tick.append(aspect_simulator_wrkn_tick_2)
# aspect_simulator_wrkn_day=aspect_simulator_wrkn_day.append(aspect_simulator_wrkn_day_2)
# aspect_simulator_wrkn_second=aspect_simulator_wrkn_second.append(aspect_simulator_wrkn_second_2)


# aspect_simulator_wrkn_tick.to_csv('/Users/xiaokeai/Desktop/price_data/wrkn/wrkn_tick_price.csv')
# aspect_simulator_wrkn_day.to_csv('/Users/xiaokeai/Desktop/price_data/wrkn/wrkn_day_price.csv')
# aspect_simulator_wrkn_second.to_csv('/Users/xiaokeai/Desktop/price_data/wrkn/wrkn_second_price.csv')
















# start_date = "1980/10/1"
# end_date = "1980/12/24"
# symbol = ['^GSPC']
# index_data = web.get_data_yahoo(symbol, start_date, end_date)
# index_price_df = index_data['Adj Close']
# index_price_list = index_price_df['^GSPC'].to_list()
# target_adjustment = 3077.77

# simulated_price, tick_based_price_list, day_based_price_list, second_based_price_list, adjusted_price = generate_parameter(index_price_list, target_adjustment)

# aspect_simulator_index_tick = pd.DataFrame(tick_based_price_list, columns=["tick_based"])
# aspect_simulator_index_day = pd.DataFrame(day_based_price_list, columns=["day_based"])
# aspect_simulator_index_second = pd.DataFrame(second_based_price_list, columns=["second_based"])
# aspect_simulator_index_adjust = pd.DataFrame(adjusted_price, columns=["adjusted_price"])

# start_date_1 = "2020/1/1"
# end_date_1 = "2021/1/1"
# symbol_1 = ['^GSPC']
# index_data_1 = web.get_data_yahoo(symbol_1, start_date_1, end_date_1)
# index_price_df_1 = index_data_1['Adj Close']
# index_price_list_1 = index_price_df_1['^GSPC'].to_list()
# target_adjustment_1 = second_based_price_list[-1]

# simulated_price_1, tick_based_price_list_1, day_based_price_list_1, second_based_price_list_1, adjusted_price_1 = generate_parameter(index_price_list_1, target_adjustment_1)

# aspect_simulator_index_tick_1 = pd.DataFrame(tick_based_price_list_1, columns=["tick_based"])
# aspect_simulator_index_day_1 = pd.DataFrame(day_based_price_list_1, columns=["day_based"])
# aspect_simulator_index_second_1 = pd.DataFrame(second_based_price_list_1, columns=["second_based"])
# aspect_simulator_index_adjust_1 = pd.DataFrame(adjusted_price_1, columns=["adjusted_price"])


# start_date_2 = "1931/3/1"
# end_date_2 = "1932/3/1"
# symbol_2 = ['^GSPC']
# index_data_2 = web.get_data_yahoo(symbol_2, start_date_2, end_date_2)
# index_price_df_2 = index_data_2['Adj Close']
# index_price_list_2 = index_price_df_2['^GSPC'].to_list()
# target_adjustment_2 = second_based_price_list_1[-1]

# simulated_price_2, tick_based_price_list_2, day_based_price_list_2, second_based_price_list_2, adjusted_price_2 = generate_parameter(index_price_list_2, target_adjustment_2)

# aspect_simulator_index_tick_2 = pd.DataFrame(tick_based_price_list_2, columns=["tick_based"])
# aspect_simulator_index_day_2 = pd.DataFrame(day_based_price_list_2, columns=["day_based"])
# aspect_simulator_index_second_2 = pd.DataFrame(second_based_price_list_2, columns=["second_based"])
# aspect_simulator_index_adjust_2 = pd.DataFrame(adjusted_price_2, columns=["adjusted_price"])


# start_date_3 = "2008-11-1"
# end_date_3 = "2010-8-1"
# symbol_3 = ['^GSPC']
# index_data_3 = web.get_data_yahoo(symbol_3, start_date_3, end_date_3)
# index_price_df_3 = index_data_3['Adj Close']
# index_price_list_3 = index_price_df_3['^GSPC'].to_list()
# target_adjustment_3 = second_based_price_list_2[-1]

# simulated_price_3, tick_based_price_list_3, day_based_price_list_3, second_based_price_list_3, adjusted_price_3 = generate_parameter(index_price_list_3, target_adjustment_3)

# aspect_simulator_index_tick_3 = pd.DataFrame(tick_based_price_list_3, columns=["tick_based"])
# aspect_simulator_index_day_3 = pd.DataFrame(day_based_price_list_3, columns=["day_based"])
# aspect_simulator_index_second_3 = pd.DataFrame(second_based_price_list_3, columns=["second_based"])
# aspect_simulator_index_adjust_3 = pd.DataFrame(adjusted_price_3, columns=["adjusted_price"])

# start_date_4 = "1968/1/1"
# end_date_4 = "1970/1/1"
# symbol_4 = ['^GSPC']
# index_data_4 = web.get_data_yahoo(symbol_4, start_date_4, end_date_4)
# index_price_df_4 = index_data_4['Adj Close']
# index_price_list_4 = index_price_df_4['^GSPC'].to_list()
# target_adjustment_4 = second_based_price_list_3[-1]

# simulated_price_4, tick_based_price_list_4, day_based_price_list_4, second_based_price_list_4, adjusted_price_4 = generate_parameter(index_price_list_4, target_adjustment_4)

# aspect_simulator_index_tick_4 = pd.DataFrame(tick_based_price_list_4, columns=["tick_based"])
# aspect_simulator_index_day_4 = pd.DataFrame(day_based_price_list_4, columns=["day_based"])
# aspect_simulator_index_second_4 = pd.DataFrame(second_based_price_list_4, columns=["second_based"])
# aspect_simulator_index_adjust_4 = pd.DataFrame(adjusted_price_4, columns=["adjusted_price"])




# aspect_simulator_index_tick=aspect_simulator_index_tick.append(aspect_simulator_index_tick_1)
# aspect_simulator_index_day=aspect_simulator_index_day.append(aspect_simulator_index_day_1)
# aspect_simulator_index_second=aspect_simulator_index_second.append(aspect_simulator_index_second_1)
# aspect_simulator_index_adjust=aspect_simulator_index_adjust.append(aspect_simulator_index_adjust_1)

# aspect_simulator_index_tick=aspect_simulator_index_tick.append(aspect_simulator_index_tick_2)
# aspect_simulator_index_day=aspect_simulator_index_day.append(aspect_simulator_index_day_2)
# aspect_simulator_index_second=aspect_simulator_index_second.append(aspect_simulator_index_second_2)
# aspect_simulator_index_adjust=aspect_simulator_index_adjust.append(aspect_simulator_index_adjust_2)

# aspect_simulator_index_tick=aspect_simulator_index_tick.append(aspect_simulator_index_tick_3)
# aspect_simulator_index_day=aspect_simulator_index_day.append(aspect_simulator_index_day_3)
# aspect_simulator_index_second=aspect_simulator_index_second.append(aspect_simulator_index_second_3)
# aspect_simulator_index_adjust=aspect_simulator_index_adjust.append(aspect_simulator_index_adjust_3)

# aspect_simulator_index_tick=aspect_simulator_index_tick.append(aspect_simulator_index_tick_4)
# aspect_simulator_index_day=aspect_simulator_index_day.append(aspect_simulator_index_day_4)
# aspect_simulator_index_second=aspect_simulator_index_second.append(aspect_simulator_index_second_4)
# aspect_simulator_index_adjust=aspect_simulator_index_adjust.append(aspect_simulator_index_adjust_4)

# print(tick_based_price_list_2[0], tick_based_price_list_1[-1])



# aspect_simulator_index_tick.to_csv('/Users/xiaokeai/Desktop/price_data/index/index_tick_price.csv')
# aspect_simulator_index_day.to_csv('/Users/xiaokeai/Desktop/price_data/index/index_day_price.csv')
# aspect_simulator_index_second.to_csv('/Users/xiaokeai/Desktop/price_data/index/index_second_price.csv')
# aspect_simulator_index_adjust.to_csv('/Users/xiaokeai/Desktop/price_data/index/index_adjust_price.csv')














# # x_tick = np.arange(0, len(tick_based_price_list), 1)
# # x_second = range(0, len(second_based_price_list), 1)
# # x_a = range(0, len(day_based_price_list), 1)
# # x = range(0, len(simulated_price), 1)



# # plt.figure(figsize = (9,4))
# # plt.plot(x_tick,tick_based_price_list,'b',label = 'Per Day Price Trend',alpha = 0.3, linewidth = 2)

# # plt.figure(figsize = (9,4))
# # plt.plot(x,simulated_price,'green',label = 'price_simulation',alpha = 0.5, linewidth = 1)

# # plt.show()