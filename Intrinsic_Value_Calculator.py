#imports yfinance to collect data from the yahoo finance website
import yfinance as yf

#imports pandas necessary for the data gathered from yfinance as they come in the form of Data Frames
import pandas as pd

#Imports matplotlib.pyplot necessary for creating graphs
import matplotlib.pyplot as plt

#used hide the future warnings
import warnings
warnings.filterwarnings("ignore")

#used during testing to see all rows of the data frames
pd.set_option('max_colwidth', None)

#imports fredapi which allows me to collect data from fred, is needed to get the AAA corporate bond yeild, which is necessary for calculating the intrinsic value
from fredapi import Fred

#fred key needed to use the fred api,
fred = Fred(api_key='(******ENTER OWN KEY******)')

#used for graphing the current price and Intrinsic value
import numpy as np

#to remove complex
from math import nan

#values used in loop that needed defining
threeGrowthPeriod = 0
pE = 0
intVal = 0
idx = 0

#lists needed for graphs and during the loop
tickers = []
tickersWInt = []
IntrinsicValue = []
names = []
IntL = []
low = []

#needed for conditional statements
pESmall = False
eData = False
epsData = False
search = False
error = False

tickerSearch = input('Do you want to Search for a stock or use the file: ')
tickerSearch = tickerSearch.lower()
while tickerSearch == 'search' or tickerSearch == 'yes' or tickerSearch == 'search for stock':
    tickerSearch = input('Enter a ticker: ')
    search = True
    while tickerSearch == 'use the file' or tickerSearch == 'use file' or tickerSearch == 'file':
        search = False

    
#opens the .csv file where the tickers are coming from, this allows the user to end many tickers at one time
if search == False:
    infile = open('tickers.csv','r')
    fileDataString = infile.read()
    allRows = fileDataString.split('\n')
    infile.close()

#collects the data from fred
dfAAA = fred.get_series_latest_release('AAA')
AAA = dfAAA.iloc[-1]

#If search is false
if search == False:
    #for all rows
    for row in allRows:
        #all tickers are either 1-4 characters this makes it so if there is an empty line it will skip it
        if len(row) == 4 or len(row) == 3 or len(row) == 2 or len(row) == 1:
            #section for putting the data from the rows into a list
            tickers.append(row)
            ticker = yf.Ticker(tickers[idx])
            #print to allow the user to see what ticker the Data printed below is for
            print('------{:s}------'.format(tickers[idx].upper())) 
            
            #If the ticker is not real this statment will find it and skip the ticker and continue to a real ticker
            dfi = (ticker.income_stmt)
            if dfi.empty:
                print(' {:s} is not a Ticker or Ticker not accepted by program'.format(tickers[idx].upper()))
                #needed to continue idx otherwise will repeat the ubove if statment forever
                idx += 1
                #used to restart the loop
                continue
            #gets the dataframes neccessary
            else:
                df = (ticker.quarterly_income_stmt)
                df1 = (ticker.history(period='1mo'))
                df2 = (ticker.quarterly_balancesheet)
                
                currentYrDEPS = dfi.loc["Diluted EPS"][0]
                lastYrDEPS = dfi.loc["Diluted EPS"][1]
                twoAgoYrDEPS = dfi.loc['Diluted EPS'][2]
                
                #if there is enough data 
                if len(dfi.columns) >= 4:
                    threeAgoYrDEPS = dfi.loc["Diluted EPS"][3]
                    tickersWInt.append((tickers[idx]).upper())
                    eData = True
                else:
                    eData = False
                    
                #locates the data i need in the data frame, think of it as cells in an excel sheet
                dEPS = df.loc["Diluted EPS"][0]
                oneEPS = df.loc['Diluted EPS'][1]
                twoEPS = df.loc['Diluted EPS'][2]
                threeEPS = df.loc['Diluted EPS'][3]
            
                nLow = df1.iloc[-1]["Close"]
                tLia = df2.loc["Total Assets"][0]

                
                #Gets twelve Month Earnings per share
                twelveMonthEPS = dEPS+oneEPS+twoEPS+threeEPS 
                
                #calculates the price to earnings ratio
                pE = nLow/twelveMonthEPS 
                
                # calculates the Earnings per share change
                Eps = ((currentYrDEPS - lastYrDEPS)/lastYrDEPS)
                
                #conditional in line 74 that makes it so if there is not enough sta 
                if eData == True:
                    #calculates compounded annual growth rate needed for intrinsic value
                    CAGR = ((currentYrDEPS/threeAgoYrDEPS)**(1/3))-1
                    #Makes into real number if it is complex
                    CAGR = CAGR.real
                    #Switches from percent to actual necessary for calculation
                    CAGRnoPerc = (CAGR * 100) * 2
                    #append the current price to a list - needed to graph later
                    low.append(nLow)
                    
                        
                    #Most important equation of the program, calculate what the stock price should be based on the books rather than market. Or its potential to speak
                    #twelveMonthEPS is the ttm EPS; the 7 is a conservative P/E base for a no-growth company; CAGRnoPerc is a reasonably expected EPS growth rate of 6 years
                    #the 1 is a conservative growth rate multiplier, the 4.4 represents the multiple of the earnings yield to the bond yield, AAA is the current AAA corporate bond yeild

                    intValue = (twelveMonthEPS * (7 + 1*(CAGRnoPerc)) * 4.4) / AAA
                    if twelveMonthEPS < 0 and CAGRnoPerc < 0:
                        intValue = -intValue
                    
                    IntL.append(intValue)

                print('Current Price: {:.2f}'.format(nLow))
                
                #Allows me print only if there is enough data
                if eData == True:
                    print('Intrinsic Value: {:.2f}'.format(intValue))
                else:
                    print('-------Not enough data for intrinsic value-------')
                print('(TTM) diluted EPS: {:.2f}'.format(twelveMonthEPS))
                print('% change EPS (1 yr): {:.2%} '.format(Eps))
                
                #Conditional print if enough data
                if eData == True:
                    print('three year growth period: {:.2f}'.format(CAGR))

                #Prints Diluted Earnings per share; pE is P/E ratio
                print('Current Diluted Eps: {:.2f}'.format(dEPS))
                print('P/E: {:.2f}'.format(pE))
                
                #Adding to lists that way i can use them later when I graph them
                names.append(ticker)
                IntrinsicValue.append(intValue)
                
                #increased index to go though the list during the loops
                idx+=1
#For if they want to search a ticker instead of using the file
elif search == True:
    ticker = yf.Ticker(tickerSearch)
    print('------{:s}------'.format(tickerSearch.upper()))

    
    #Collects the Dataframes from yfinance
    dfi = (ticker.income_stmt)
    if dfi.empty:
        exit('Input valid ticker')
    else:
        df = (ticker.quarterly_income_stmt)
        df1 = (ticker.history(period='1mo'))
        df2 = (ticker.quarterly_balancesheet)
        
        currentYrDEPS = dfi.loc["Diluted EPS"][0]
        lastYrDEPS = dfi.loc["Diluted EPS"][1]
        twoAgoYrDEPS = dfi.loc['Diluted EPS'][2]

        if len(dfi.columns) >= 4:
            threeAgoYrDEPS = dfi.loc["Diluted EPS"][3]
            tickersWInt.append(tickerSearch.upper())
            eData = True
        else:
            eData = False
        
            
        #locates the data i need in the data frame, think of it as cells in an excel sheet
        dEPS = df.loc["Diluted EPS"][0]
        oneEPS = df.loc['Diluted EPS'][1]
        twoEPS = df.loc['Diluted EPS'][2]
        threeEPS = df.loc['Diluted EPS'][3]

        nLow = df1.iloc[-1]["Close"]
        #tLia = df2.loc["Total Assets"][0]
        
        #Gets twelve Month Earnings per share
        twelveMonthEPS = dEPS+oneEPS+twoEPS+threeEPS 

        #calculates the price to earnings ratio
        pE = nLow/twelveMonthEPS
        
        # calculates the Earnings per share change
        Eps = ((currentYrDEPS - lastYrDEPS)/lastYrDEPS)
        
        #conditional in line 74 that makes it so if there is not enough sta 
        if eData == True:
            #calculates compounded annual growth rate needed for intrinsic value
            
            CAGR = (currentYrDEPS/threeAgoYrDEPS) ** (1/3) - 1
            
            #turns it into a real number if it becomes a complex number
            CAGR = CAGR.real
            
            #Switches from percent to actual necessary for calculation
            CAGRnoPerc = (CAGR * 100) * 2

            #append the current price to a list - needed to graph later
            low.append(nLow)
                
            #Most important equation of the program, calculate what the stock price should be based on the books rather than market. Or its potential to speak
            #twelveMonthEPS is the ttm EPS; the 7 is a conservative P/E base for a no-growth company; CAGRnoPerc is a reasonably expected EPS growth rate of 6 years
            #the 1 is a conservative growth rate multiplier, the 4.4 represents the multiple of the earnings yield to the bond yield, AAA is the current AAA corporate bond yeild

            intValue = (twelveMonthEPS * (7 + 1*(CAGRnoPerc)) * 4.4) / AAA
            
            if twelveMonthEPS < 0 and CAGRnoPerc < 0:
                intValue = -intValue
                        
            IntL.append(intValue)
        print('Current Price: {:.2f}'.format(nLow))
        
        #Allows me print only if there is enough data
        if eData == True:
            print('Intrinsic Value: {:.2f}'.format(intValue))
        else:
            print('-------Not enough data for intrinsic value-------')
        print('(TTM) diluted EPS: {:.2f}'.format(twelveMonthEPS))
        print('% change EPS (1 yr): {:.2%} '.format(Eps))
        
        #Conditional print if enough data
        if eData == True:
            print('Three year growth period: {:.2%}'.format(CAGR))
        
        #Prints Diluted Earnings per share; pE is P/E ratio
        print('Current Diluted Eps: {:.2f}'.format(dEPS))
        print('P/E: {:.2f}'.format(pE))
        
        #Adding to lists that way i can use them later when I graph them
        names.append(ticker)
        IntrinsicValue.append(intValue)

#if there is data... Plot it (conditional)
if len(IntL) != 0:
    #for the different color bars, allows one to distiguish better
    COLOR_IntVal = "#69b3a2"
    COLOR_PRICE = "#3399e6"
    
    #sets the width of the bars
    bar_width = 0.35
    
    #adds tickers
    xLabels = tickersWInt
    x_positions = np.arange(len(xLabels))
    
    # Plotting the data
    plt.bar(x_positions - bar_width/2, IntL, color= COLOR_IntVal, label='Intrinsic Value (6-Year Growth Rate)', width=bar_width, edgecolor='black')
    plt.bar(x_positions + bar_width/2, low,color = COLOR_PRICE, label='Ticker Price', width=bar_width, edgecolor='black')

    # Adding labels and title
    plt.xlabel('Tickers')
    plt.ylabel('Price in Dollars')
    plt.title('Compairing Intrinsic Value to Stock Price')


    # Set x-axis ticks and labels
    plt.xticks(x_positions, xLabels)
    plt.yticks()
    
    # Adding a legend to differentiate between the datasets
    plt.legend()

    # Display the plot
    plt.show()
    

    
'''
#used during error testing
iTicker = input('What is the company you want:\n')
ticker = yf.Ticker(iTicker)
bS = ticker.balance_sheet

print(ticker.quarterly_income_stmt)
print(ticker.income_stmt)
print(bS)f
'''




