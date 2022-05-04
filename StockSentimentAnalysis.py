import requests, json, os, six, io, sys
import google.auth
from google.cloud import language_v1 as language
from google.cloud import translate_v2 as translate
from google.cloud import storage
from google.cloud import speech
from tkinter import *
from tkinter import ttk, filedialog, simpledialog
from tkinter.messagebox import showinfo, showwarning
import requests
import pandas as pd
import matplotlib.pyplot as plt
from PIL import ImageTk, Image as IMIM # https://programmerah.com/attributeerror-type-object-image-has-no-attribute-open-41937/

"""
@ Description: Closing Stock Price using Quote Endpoint from Alpha Vantage
@ API Documentation: https://www.alphavantage.co/documentation/
"""


class StockSentimentGroup6:
    def __init__(self, windowsGui, api_key, client):
        self.windowsGui_ = windowsGui
        self.windowsGui_.title('Stock Sentiment Analysis')
        #self.windowsGui_.geometry("780x440")
        self.api_key = api_key
    
    # RUN FUNCITONS HERE:
        self.create_frames()
        self.create_widgets()
        self.get_series()


    def create_frames(self):
        # Base Frame - one Frame for all
        # Honestly, I don't know if this makes sense. I need more coffee...
        self.mainframe = ttk.Frame(self.windowsGui_
            ,style = 'mainFrameColor.TFrame')
        self.mainframe.grid(column=0, row=0, sticky=(N, W, E, S))

        # Stock Information -Top Left Corner
        self.stockInformationFrame = ttk.Frame(self.mainframe
            ,padding = '5 15 15 5')
            #,style = '')
        self.stockInformationFrame.grid(column=0, row=0, sticky=(N, W, E, S))

        # Stock Checkboxes - Top Right Corner. 
        self.checkboxStockFrame = ttk.Frame(self.mainframe
            ,padding='5 15 15 5')
            #,style = '')
        self.checkboxStockFrame.grid(column=1, row=0, sticky=(N, W, E, S))

        # Stock Sentiment Analysis and Historical Pricing - Middle
        # one row THICC
        self.sentiment_and_historic_pricing_frame = ttk.Frame(self.mainframe
            ,padding='5 15 15 5'
            ,relief='sunken')
        self.sentiment_and_historic_pricing_frame.grid(column=0, row=2, columnspan=2, sticky=(N, W, E, S))

        # Stock Charts and Sentiment Analysis
        self.chart_sentiment_frame = ttk.Frame(self.mainframe
            ,padding='5 15 15 5'
            ,relief='sunken')
        self.chart_sentiment_frame.grid(column=0, row=4, columnspan=2, sticky=(N, W, E, S))

    
    def create_widgets(self):

        self.stock_labels = ['Symbol','Close Price: USD', 
            'Previous Close', 'Percent Change', 'Volume']

        self.stocks_of_interest = ['IBM', 'APPLE', 'MICROSOFT', 
            'MODERNA', 'PFIZER']

        self.tckr_stocks = ['IBM', 'AAPL', 'MSFT', 'MRNA', 'PFE', 'NVAX', 'AZN']
        
        self.last_100_day_bbtns = ['Description', 'Closing Price', 'Volume']

        ############################
        #  FRAME:                  # 
        # stockInformationFrame    #              
        ############################

        # # Creating Stock Labels inside stockInformationFrame
        # stock_label = ttk.Label(self.stockInformationFrame
        #     ,text='Symbol')
        # stock_label.grid(column=0, row=0, sticky=W)

        for i in range(len(self.stock_labels)):
            lbl = ttk.Label(self.stockInformationFrame
                ,text =self.stock_labels[i])
                #Style=
            lbl.grid(column=0, row=i,sticky=W)
        
        #self.symbol_string_var = StringVar()
        self.str_var = [StringVar(), StringVar(),StringVar(), StringVar(), StringVar()]
        for i in range(len(self.stock_labels)):
            entry = ttk.Entry(self.stockInformationFrame
                ,textvariable=self.str_var[i])
            entry.grid(column=1, row=i, sticky=W)
            

        # #The Price Button Which Will Retrieve the Data:
        price_bttn = ttk.Button(self.stockInformationFrame
            ,text='Get Price'
            ,command=self.get_closing_price)
        price_bttn.grid(column=1, row=i+2, pady=3)

        ############################
        #  FRAME:                  # 
        #  checkboxStockFrame      #              
        ############################

        # Creating CheckButton for Easy Access to Stocks of Interest:
        self.stock_selection_int = IntVar()
        for self.stock in range(len(self.stocks_of_interest)):
            chck_bttn = ttk.Checkbutton(self.checkboxStockFrame
                ,text=self.stocks_of_interest[self.stock]
                ,variable=self.stock_selection_int
                ,onvalue=self.stock+1
                ,command=self.check_stock)
            chck_bttn.grid(column=0, row=self.stock)
            chck_bttn["width"]=30
        
        ############################
        #  FRAME:                  # 
        #  sentiment_and_ \        #
        # historic_pricing_bttns   #              
        ############################

        self.last_100_day_label = ttk.Label(self.sentiment_and_historic_pricing_frame
            ,text='Last 100 Days: ')
        self.last_100_day_label.grid(column=0, row=0, sticky=W)

        self.stock_price_optn = IntVar()
        #self.stock_price_optn = [IntVar(), IntVar(), IntVar()]
        for itm in range(len(self.last_100_day_bbtns)):
            stock_info = ttk.Checkbutton(self.sentiment_and_historic_pricing_frame
                ,text=self.last_100_day_bbtns[itm]
                ,variable=self.stock_price_optn
                ,onvalue=itm+1
                ,command=self.choice_value)
            stock_info.grid(column=1+itm, row=0, sticky=E)

    def get_closing_price(self):
        if self.str_var[0].get() == "":
            showinfo(title='Warning', message='Missign ticker symbol')
            return
        ticker_smbl = self.str_var[0].get().upper()
        stock_name = self.str_var[0].get().upper()
        self.str_var[0].set(ticker_smbl)

        base_url = r"https://www.alphavantage.co/query?function=GLOBAL_QUOTE"
        # Additional URL stuff
        main_url = base_url + '&symbol=' + ticker_smbl + \
            "&apikey=" + self.api_key

        res_obj = requests.get(main_url, verify=False)
        self.result = res_obj.json()

        print(self.result)

        try:
            self.c_price = self.result["Global Quote"]['05. price']
            f_price = round(float(self.c_price), 2)
            self.c_price = str(f_price)
            print(self.c_price)
            self.str_var[1].set('$'+self.c_price)

            # Get and Display Previous Closing Price
            self.pc_price = self.result['Global Quote']['08. previous close']
            f_price = round(float(self.pc_price), 2)
            self.pc_price = str(f_price)
            self.str_var[2].set('$'+self.pc_price)

            # Get and Display Percent Change
            self.p_change = self.result['Global Quote']['10. change percent']
            self.str_var[3].set(self.p_change)

            # Get and Display Volume Movement. 
            self.volume = self.result['Global Quote']['06. volume']
            v = int(self.volume) # converts the string sel.volume to integer
            v = "{:,}".format(v) # Converts int to string with commas
            self.str_var[4].set(v)

        except Exception as e:
            warn_msg = "Symbol " +  ticker_smbl + " Not Found"
            showwarning(title='Warning', message=warn_msg)
            #self.clear_entries()
        
                
    def check_stock(self):
        self.str_var[0].set(self.tckr_stocks[self.stock_selection_int.get()-1])
        

    def get_series(self):
        if self.str_var[0] == "":
            showinfo(title="Warning", message="No proper stock selected")
            return
        ticker_smbl = self.str_var[0].get()
        
        #Base URL to get historical data:
        base_url = r"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED"
        main_url = base_url + '&symbol='+ ticker_smbl +  '&apikey=' + api_key

        #Get JSON Request
        res_obj = requests.get(main_url)
        results = res_obj.json()
        try:
            timeSeries = results['Time Series (Daily)']

            map_of_values = {
                1: ["closing_price", "4. close"],
                3: ["volume", "6. volume"]
            }

            name_of_col = map_of_values[self.choice][0] # will use the self.choice_values function
            content_of_col = map_of_values[self.choice][1]

            dictionary = {"date_range": [], name_of_col: []}

            x='date_range'
            y= name_of_col

            for key, value in timeSeries.items():
                dictionary["date_range"].append(key)
                dictionary[name_of_col].append(value[content_of_col])

            df = pd.DataFrame(dictionary)
            df["date_range"] = df["date_range"].astype('datetime64', copy=False)
            df[name_of_col] = df[name_of_col].astype('float64', copy=False)

            plot = df.plot(x=x, y=y, title=ticker_smbl, colormap='jet', marker='.', markersize=5)
            plot.set_xlabel("Date")
            plot.set_ylabel(name_of_col)
            plt.grid(True)
            plt.savefig('ts_plot_hw.png')
 
            
            self.imgobj = ImageTk.PhotoImage(IMIM.open('ts_plot_hw.png'))
            self.imgwin = ttk.Label(self.chart_sentiment_frame, image=self.imgobj)
            self.imgwin.grid(column=0, row=3, sticky=W)

        except Exception as e:
            print(str(e))

    def stock_data_sentiment_and_Description(self):
        text = Text(self.chart_sentiment_frame)
        text.grid(column=0, row=2, columnspan=2,  sticky=W)

        if self.str_var[0] == "":
            showinfo(title="Warning", message="No proper stock selected")
            return
        ticker_smbl = self.str_var[0].get()

        # replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
        url = 'https://www.alphavantage.co/query?function=OVERVIEW&symbol=' + \
             ticker_smbl + '&apikey='+api_key
        r = requests.get(url)   
        data = r.json()
        #print(data)

        analyst_tp = data["PERatio"]
        fiftytwo_high = data["52WeekHigh"]
        fiftytwo_low = data["52WeekLow"]
        company_description = data["Description"]

        stock_website = self.stocks_of_interest[self.stock_selection_int.get()-1]
        print(stock_website)

        html_file = 'WebPages/'+ stock_website +'.html' # checkbutton
        print("Classifying HTML inf File: ", html_file)

        try:
            with open(html_file, "r") as file_contents:
                contents = file_contents.read()
                if len(contents)>1000000:
                    print(html_file, 'size= ', len(contents), 'too large to process locally')
                    sys.exit()
        except:
            print('Unable to process', html_file)
            sys.exit()

        sentiment, magnitude = \
        self.get_sentiment( contents, file_type="html") 
        # print(u"=" * 20)
        # print("Sentiment: {:>6.3f}".format(sentiment))
        # print("Magnitude: {:>6.3f}".format(magnitude)) 
        # print(u"=" * 80, "\n")

        text_box_details = "PE Ratio: " + analyst_tp \
            + '\n'+ "52WeekHigh: " + fiftytwo_high \
            + '\n'+ "52WeekLow: " + fiftytwo_low \
            + '\n'+'====================================' \
            + '\n' + "Sentiment: " + str(sentiment) \
            + '\n' + "Magnitude: " + str(magnitude)\
            + '\n'+'====================================' \
            + '\n' + "\nDescription:\n" + company_description 

        text.insert('end', text_box_details)

    def choice_value(self):
        self.choice = 0
        if self.last_100_day_bbtns[self.stock_price_optn.get()-1] == 'Description':
            self.choice = 2
        if self.last_100_day_bbtns[self.stock_price_optn.get()-1] == 'Closing Price':
            self.choice = 1
        if self.last_100_day_bbtns[self.stock_price_optn.get()-1] == 'Volume':
            self.choice = 3
        self.get_series()
        self.stock_data_sentiment_and_Description()
    
    def get_sentiment(self, contents, file_type="html"):

        if file_type == 'html':
            document = language.Document(content= contents, language='en',
            type_=language.Document.Type.HTML)
        
        response = client.analyze_sentiment(document=document, encoding_type= 'UTF32')
        sentiment =response.document_sentiment
        return sentiment.score, sentiment.magnitude



google_project_file = "GoogleTranslateCredentials.json"
credentials, project_id = google.auth.\
                        load_credentials_from_file(google_project_file)
client = language.LanguageServiceClient(credentials=credentials)
api_key  = "demo"
root   = Tk()
my_app = StockSentimentGroup6(root, api_key, client)
# Display GUI
root.mainloop()