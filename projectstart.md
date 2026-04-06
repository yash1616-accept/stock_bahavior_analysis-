cd stock-behavior-analysis
venv\Scripts\Activate.ps1
python app.py
cd frontend
npm run dev
testdata in > analyze>output > test_ticker_complete_analysis.csv
ml model isolation forest sclearn
The Machine Learning Model: Isolation Forest
1. What Model Are We Using? We integrated an Isolation Forest, which is an unsupervised machine learning algorithm from the scikit-learn library. "Unsupervised" means it doesn't need historical examples of "good" or "bad" behavior to learn from—it figures out what is normal purely by looking at the dataset in front of it.

2. Why Was This Model Chosen? In the stock market, abnormal trading behavior (like extreme panic selling or massive institutional accumulation) is rare compared to normal daily trading. The Isolation Forest is specifically designed for Anomaly Detection. Instead of trying to define what "normal" is, it tries to mathematically "isolate" the data points that look completely different from the rest of the herd.

3. What Features (Data) Does It Look At? For each trading day, the model is fed three key data points:

Price Change %: How much the stock moved up or down.
Volume Z-score: How unusually high or low the trading volume was compared to its recent 20-day moving average.
Volatility: The 7-day rolling standard deviation of the price (how wild the price swings are).
4. How Does It Work Conceptually? Imagine you have a big pile of regular apples and one giant blue apple. If you tried to separate them by asking questions (e.g., "Is it red? Is it small?"), the blue apple would get separated almost immediately because it's so different.

The Isolation Forest algorithm does exactly this with our stock data. It builds "trees" by randomly splitting data based on our three features.

Normal Days: Standard trading days look very similar to each other, so they get buried deep in the tree and take many splits to isolate.
Anomalous Days: High-volatility, massive-volume days are so unique that they get isolated within just a few splits.
If a trading day is very quick and easy to isolate, the model mathematically flags it as an Anomaly (-1).

5. How It Fits Into Our System While our existing Statistical Rules (Panic Selling, FOMO Buying) use hardcoded, rigid thresholds (e.g., "Volume Z-Score > 1.5"), the Isolation Forest ML Model is dynamic. It looks at the entire 6-month period and uses AI to find days where the combination of price, volume, and volatility is mathematically unnatural, catching subtle market anomalies that rigid rules might miss!

