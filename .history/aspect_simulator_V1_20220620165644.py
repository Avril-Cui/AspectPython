import pandas_datareader as web
import matplotlib.pyplot as plt 
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
np.random.seed(17)

def generate_parameter(original_price_list, adjust_factor):
    
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
    
    adjusted_price = [i*100 for i in simulated_price]

    split = [adjusted_price[i:i + 10] for i in range(0, len(adjusted_price), 10)]
    adjusted_price[0] = np.round(adjusted_price[0])

    day_based_price_list = [adjusted_price[0]]
    tick_based_price_list = [adjusted_price[0]]
    second_based_price_list = [adjusted_price[0]]

    for index in range(len(split[:-1])):
        one_day = split[index]
        one_day_df = pd.DataFrame(one_day, columns = ['one_day_price'])
        drift = one_day_df.pct_change()
        drift = drift[1:]['one_day_price'].tolist()
        
        x0 = one_day[0]
        ticks_in_min = 12
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
        daily_price_scaled = []
        adjust_num = 36

        for inx in range(len(daily_price)):
            if inx % adjust_num == 0:
                daily_price_scaled.append(daily_price[inx])
        tick_based_price_list += daily_price_scaled
        
        day_based_price_list.append(daily_price[-1])
        second_based_price_list += daily_price

    return(simulated_price, tick_based_price_list, day_based_price_list, second_based_price_list)


start_date = "2020/1/1"
end_date = "2021/1/1"
symbol = ['^GSPC']
index_data = web.get_data_yahoo(symbol, start_date, end_date)
index_price_df = index_data['Adj Close']
index_price_list = index_price_df['^GSPC'].to_list()
adjust_factor = 0.5

simulated_price, tick_based_price_list, day_based_price_list, second_based_price_list = generate_parameter(index_price_list, adjust_factor)

x_tick = np.arange(0, len(tick_based_price_list), 1)
x_second = range(0, len(second_based_price_list), 1)
x_a = range(0, len(day_based_price_list), 1)
x = range(0, len(simulated_price), 1)



plt.figure(figsize = (9,4))
plt.plot(x_tick,tick_based_price_list,'b',label = 'Per Day Price Trend',alpha = 0.3, linewidth = 2)

plt.figure(figsize = (9,4))
plt.plot(x,simulated_price,'green',label = 'price_simulation',alpha = 0.5, linewidth = 1)

plt.show()