import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import uuid

# Set a random seed for reproducibility
np.random.seed(42)
random.seed(42)

def generate_consumer_data(num_customers=1000, num_transactions=5000):
    """
    Generate a consumer purchasing patterns dataset.
    
    Parameters:
    -----------
    num_customers : int
        Number of unique customers to generate
    num_transactions : int
        Number of transactions to generate
    
    Returns:
    --------
    pandas.DataFrame
        DataFrame containing consumer purchasing data
    """
    
    # Generate customer data
    customer_ids = [str(uuid.uuid4())[:8] for _ in range(num_customers)]
    
    # Customer demographics
    age_groups = ['18-24', '25-34', '35-44', '45-54', '55-64', '65+']
    genders = ['Male', 'Female', 'Non-binary', 'Prefer not to say']
    income_brackets = ['0-25K', '25K-50K', '50K-75K', '75K-100K', '100K+']
    locations = ['Urban', 'Suburban', 'Rural']
    membership_levels = ['Bronze', 'Silver', 'Gold', 'Platinum', 'None']
    
    customers = {
        'customer_id': customer_ids,
        'age_group': [random.choice(age_groups) for _ in range(num_customers)],
        'gender': [random.choice(genders) for _ in range(num_customers)],
        'income_bracket': [random.choice(income_brackets) for _ in range(num_customers)],
        'location': [random.choice(locations) for _ in range(num_customers)],
        'membership_level': [random.choice(membership_levels) for _ in range(num_customers)],
        'account_age_days': [random.randint(1, 1825) for _ in range(num_customers)]  # 0-5 years
    }
    
    # Customer preferences with some correlations to demographics
    product_categories = ['Electronics', 'Clothing', 'Home Goods', 'Groceries', 'Beauty', 'Sports', 'Books', 'Toys']
    
    # Create a customer DataFrame to use for lookup
    customers_df = pd.DataFrame(customers)
    
    # Generate transaction data
    transactions = []
    
    # Define a range of dates (last 2 years)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=730)
    
    # Product information
    products = []
    for category in product_categories:
        for i in range(10):  # 10 products per category
            price_base = {
                'Electronics': random.uniform(50, 1000),
                'Clothing': random.uniform(15, 100),
                'Home Goods': random.uniform(20, 300),
                'Groceries': random.uniform(2, 50),
                'Beauty': random.uniform(10, 80),
                'Sports': random.uniform(20, 200),
                'Books': random.uniform(10, 30),
                'Toys': random.uniform(10, 70)
            }[category]
            
            products.append({
                'product_id': f"{category[:3].upper()}{i+1:03d}",
                'product_name': f"{category} Item {i+1}",
                'category': category,
                'base_price': price_base,
                'avg_rating': round(random.uniform(1, 5), 1)
            })
    
    # Create holiday/special event dates
    holidays = [
        datetime(start_date.year, 1, 1),   # New Year's
        datetime(start_date.year, 2, 14),  # Valentine's
        datetime(start_date.year, 7, 4),   # Independence Day
        datetime(start_date.year, 11, 25), # Black Friday
        datetime(start_date.year, 12, 25), # Christmas
        datetime(start_date.year + 1, 1, 1),   
        datetime(start_date.year + 1, 2, 14),  
        datetime(start_date.year + 1, 7, 4),   
        datetime(start_date.year + 1, 11, 24), 
        datetime(start_date.year + 1, 12, 25)
    ]
    
    # Generate transaction data with patterns
    for i in range(num_transactions):
        # Seasonality effects
        if i % 10 == 0:  # 10% of transactions near holidays
            days_offset = random.randint(-3, 3)
            holiday = random.choice(holidays)
            transaction_date = holiday + timedelta(days=days_offset)
            if transaction_date < start_date or transaction_date > end_date:
                transaction_date = start_date + timedelta(days=random.randint(0, 730))
        else:
            transaction_date = start_date + timedelta(days=random.randint(0, 730))
        
        # Select a customer
        customer = customers_df.iloc[random.randint(0, num_customers-1)]
        
        # Number of items in this transaction (with some correlation to income)
        income_index = income_brackets.index(customer['income_bracket'])
        items_base = max(1, int(np.random.normal(income_index + 1, 1.5)))
        items_count = min(10, max(1, items_base))
        
        # Select items for transaction
        transaction_products = random.sample(products, items_count)
        
        # Age-based product preferences
        age_index = age_groups.index(customer['age_group'])
        
        # For each product in this transaction
        for product in transaction_products:
            # Price adjustments
            if transaction_date.month in [11, 12]:  # Holiday season
                price_multiplier = random.uniform(0.7, 1.1)  # Sales and promotions
            else:
                price_multiplier = random.uniform(0.9, 1.05)
                
            # Membership discounts
            membership_discount = {
                'None': 0,
                'Bronze': 0.02,
                'Silver': 0.05,
                'Gold': 0.08,
                'Platinum': 0.12
            }[customer['membership_level']]
            
            # Calculate final price
            final_price = product['base_price'] * price_multiplier * (1 - membership_discount)
            
            # Payment methods with some age correlation
            payment_options = ['Credit Card', 'Debit Card', 'Mobile Payment', 'Cash', 'Gift Card']
            if age_index <= 2:  # Younger customers more likely to use mobile
                payment_weights = [0.3, 0.2, 0.4, 0.05, 0.05]
            else:  # Older customers more likely to use credit/debit
                payment_weights = [0.4, 0.3, 0.1, 0.15, 0.05]
            
            payment_method = random.choices(payment_options, weights=payment_weights)[0]
            
            # Purchase channel with location correlation
            channel_options = ['Online', 'In-store', 'Mobile App', 'Phone Order']
            if customer['location'] == 'Urban':
                channel_weights = [0.4, 0.3, 0.25, 0.05]
            elif customer['location'] == 'Suburban':
                channel_weights = [0.35, 0.4, 0.2, 0.05]
            else:  # Rural
                channel_weights = [0.45, 0.25, 0.15, 0.15]
            
            purchase_channel = random.choices(channel_options, weights=channel_weights)[0]
            
            # Customer satisfaction - generally correlated with product rating but with variance
            rating_base = product['avg_rating']
            satisfaction = min(5, max(1, int(np.random.normal(rating_base, 0.7))))
            
            # Calculate days since last purchase (random for now)
            days_since_last = random.randint(0, 180)
            
            # Determine if returned
            return_probability = 0.02  # 2% base return rate
            if satisfaction <= 2:
                return_probability = 0.4  # 40% return rate for low satisfaction
            was_returned = random.random() < return_probability
            
            # Add transaction to list
            transactions.append({
                'transaction_id': f"TXN{i+1:06d}-{len(transactions)+1}",
                'customer_id': customer['customer_id'],
                'product_id': product['product_id'],
                'product_name': product['product_name'],
                'category': product['category'],
                'transaction_date': transaction_date.strftime('%Y-%m-%d'),
                'day_of_week': transaction_date.strftime('%A'),
                'time_of_day': f"{random.randint(8, 23):02d}:{random.randint(0, 59):02d}",
                'quantity': random.randint(1, 3),
                'unit_price': round(final_price, 2),
                'payment_method': payment_method,
                'purchase_channel': purchase_channel,
                'customer_satisfaction': satisfaction,
                'days_since_last_purchase': days_since_last,
                'was_returned': was_returned,
                'age_group': customer['age_group'],
                'gender': customer['gender'],
                'income_bracket': customer['income_bracket'],
                'location': customer['location'],
                'membership_level': customer['membership_level'],
                'account_age_days': customer['account_age_days']
            })
    
    # Convert to DataFrame
    df = pd.DataFrame(transactions)
    
    # Calculate total price
    df['total_price'] = df['quantity'] * df['unit_price']
    
    # Return the final dataframe
    return df

def save_dataset(df, filename='consumer_purchasing_patterns.csv'):
    """
    Save the generated dataset to a CSV file.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        Dataset to save
    filename : str
        Name of the output file
    """
    df.to_csv(filename, index=False)
    print(f"Dataset saved to {filename}")
    print(f"Dataset contains {len(df)} rows and {len(df.columns)} columns")
    print(f"Columns: {list(df.columns)}")

if __name__ == "__main__":
    # Generate dataset with 1000 customers and 5000 transactions
    consumer_data = generate_consumer_data(num_customers=1000, num_transactions=5000)
    
    # Display sample of dataset
    print("Sample of generated dataset:")
    print(consumer_data.head())
    
    # Save dataset to CSV
    save_dataset(consumer_data)
    
    # Print some basic statistics about the dataset
    print("\nDataset Statistics:")
    print(f"Unique customers: {consumer_data['customer_id'].nunique()}")
    print(f"Unique products: {consumer_data['product_id'].nunique()}")
    print(f"Date range: {consumer_data['transaction_date'].min()} to {consumer_data['transaction_date'].max()}")
    print(f"Average transaction value: ${consumer_data['total_price'].mean():.2f}")
    print(f"Return rate: {consumer_data['was_returned'].mean() * 100:.2f}%")
    
    # Print distribution of some categorical variables
    print("\nCategory Distribution:")
    print(consumer_data['category'].value_counts())
    
    print("\nMembership Level Distribution:")
    print(consumer_data['membership_level'].value_counts())
    
    print("\nLocation Distribution:")
    print(consumer_data['location'].value_counts())
