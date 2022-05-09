## Linear Regression Project:  
Variables Predicting Pre-Owned Car Prices


### Abstract

Although make and model are some of the first factors that come to mind when considering the price of a second-hand car, many other features may go into pricing. I was interested in how car pricing patterns independent of make and model might provide insight into local consumer preferences. On Carfax.com, cars are listed for sale by dealers along with information about the individual vehicle history, an asking price and an estimated value. My aim was to report on factors correlated with price in a given location using linear regression. Initial results confirmed the influence of mileage, engine capacity and a number of optional features, but more data could help expand and refine the model depending on the use case.

### Design

Listings on Carfax.com contain detailed, standardized information about individual cars on the market. Making use of this data, my goal was to build a linear model to predict listed prices based on the available continuous and categorical features describing pre-owned cars. This could be taken as a pilot analysis for a scaled-up, or more complex, automatic price prediction tool for use by Carfax, car dealerships (e.g. for inventory management) or other market research. Additionally, a simplified model provides some initial findings on the key features that influence used car prices, and in future work similar results can be compared between cities.

### Data
	
Using webscraping tools, I obtained around 50 pages of search results from each of two locations: Philadelphia, PA and Brooklyn, NY. Altogether, I collected over 1000 listings from each location. 
Numerical continuous features included mileage, price and engine capacity. Many descriptive labels were also available, so I started with around 200 features after dummy-coding each label (e.g. ‘heated seats’ or ‘AWD’). After manual and algorithmic feature selection, I retained about 128 features, out of which 29 were highlighted in the final model choice. 

### Algorithms

#### Feature engineering:
I created a few variables while preprocessing the data, such as a numerical rating of damage history, and many binomial features based on descriptive text labels. I also removed any highly collinear variables. The target variable, car price, was log-transformed to approximate a normal distribution. 

#### Linear regression: 
I first looked at variations of a Lasso regularized model, to narrow down features while maintaining reasonable adjusted R2 and RMSE validation scores. I also compared results with variations of an ElasticNet model, but found the Lasso model more compelling in terms of interpretability without a large increase in bias.

#### Model selection: 
For each model, I used cross-validation to obtain robust measures of explained variance and error. I checked residuals graphically for constant variance and approximate normality, and reported final scores on held-out test data.

### Tools

Web scraping was implemented using BeautifulSoup and Selenium in Python. I filtered and navigated through search results using Selenium, and parsed the individual pages with BeautifulSoup.
