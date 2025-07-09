import os
import sys
import yfinance as yf
import pandas as pd
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta

# Try to import get_env_variable, fallback to sys.path hack if needed
try:
    from stock_idss.utils.env_loader import get_env_variable
except ModuleNotFoundError:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../utils')))
    from utils.env_loader import get_env_variable

def fetch_fundamental_data(ticker: str, save_dir: str = '../data/fundamentals/') -> Dict[str, any]:
    """
    Fetch comprehensive fundamental data for a stock ticker.
    
    Args:
        ticker (str): Stock ticker symbol (e.g., 'AAPL')
        save_dir (str): Directory to save the fundamental data
        
    Returns:
        Dict[str, pd.DataFrame]: Dictionary containing different types of fundamental data
    """
    os.makedirs(save_dir, exist_ok=True)
    
    # Initialize yfinance ticker object
    stock = yf.Ticker(ticker)
    
    fundamental_data = {}
    
    try:
        # 1. Financial Statements
        fundamental_data['income_stmt'] = stock.income_stmt
        fundamental_data['balance_sheet'] = stock.balance_sheet
        fundamental_data['cash_flow'] = stock.cashflow
        
        # 2. Key Statistics and Ratios
        fundamental_data['info'] = stock.info
        
        # 3. Earnings Data (handle deprecated methods)
        try:
            fundamental_data['earnings'] = stock.earnings
        except:
            fundamental_data['earnings'] = None
        
        try:
            fundamental_data['quarterly_earnings'] = stock.quarterly_earnings
        except:
            fundamental_data['quarterly_earnings'] = None
        
        # 4. Financial Data
        fundamental_data['financials'] = stock.financials
        fundamental_data['quarterly_financials'] = stock.quarterly_financials
        
        # 5. Balance Sheet Data
        fundamental_data['balance_sheet_quarterly'] = stock.quarterly_balance_sheet
        
        # Save each dataset
        for data_type, data in fundamental_data.items():
            if data is not None:
                # Handle different data types
                if data_type == 'info':
                    # info is a dictionary, save as JSON or skip
                    continue
                elif hasattr(data, 'empty') and not data.empty:
                    # DataFrame with data
                    file_path = os.path.join(save_dir, f"{ticker}_{data_type}.csv")
                    data.to_csv(file_path)
                    print(f"Saved {data_type} data to {file_path}")
                elif isinstance(data, dict) and data:
                    # Dictionary with data
                    file_path = os.path.join(save_dir, f"{ticker}_{data_type}.csv")
                    pd.DataFrame([data]).to_csv(file_path, index=False)
                    print(f"Saved {data_type} data to {file_path}")
        
        return fundamental_data
        
    except Exception as e:
        print(f"Error fetching fundamental data for {ticker}: {e}")
        return {}

def extract_key_ratios(ticker: str, fundamental_data: Dict[str, any]) -> pd.DataFrame:
    """
    Extract key financial ratios from fundamental data.
    
    Args:
        ticker (str): Stock ticker symbol
        fundamental_data (Dict): Dictionary of fundamental data
        
    Returns:
        pd.DataFrame: DataFrame with calculated ratios
    """
    ratios = {}
    
    try:
        info = fundamental_data.get('info', {})
        
        # Basic ratios from yfinance info
        ratios['pe_ratio'] = info.get('trailingPE', None)
        ratios['pb_ratio'] = info.get('priceToBook', None)
        ratios['debt_to_equity'] = info.get('debtToEquity', None)
        ratios['current_ratio'] = info.get('currentRatio', None)
        ratios['roe'] = info.get('returnOnEquity', None)
        ratios['roa'] = info.get('returnOnAssets', None)
        ratios['market_cap'] = info.get('marketCap', None)
        ratios['enterprise_value'] = info.get('enterpriseValue', None)
        ratios['sector'] = info.get('sector', None)
        ratios['industry'] = info.get('industry', None)
        
        # Calculate additional ratios from financial statements
        if 'balance_sheet' in fundamental_data and fundamental_data['balance_sheet'] is not None:
            bs = fundamental_data['balance_sheet']
            if hasattr(bs, 'empty') and not bs.empty and len(bs.columns) > 0:
                try:
                    # Get most recent data (first column)
                    latest_date = bs.columns[0]
                    
                    # Current Ratio = Current Assets / Current Liabilities
                    if 'Total Current Assets' in bs.index and 'Total Current Liabilities' in bs.index:
                        current_assets = bs.loc['Total Current Assets', latest_date]
                        current_liabilities = bs.loc['Total Current Liabilities', latest_date]
                        if current_liabilities and current_liabilities != 0:
                            ratios['calculated_current_ratio'] = current_assets / current_liabilities
                    
                    # Debt-to-Equity = Total Debt / Total Stockholder Equity
                    if 'Total Debt' in bs.index and 'Total Stockholder Equity' in bs.index:
                        total_debt = bs.loc['Total Debt', latest_date]
                        total_equity = bs.loc['Total Stockholder Equity', latest_date]
                        if total_equity and total_equity != 0:
                            ratios['calculated_debt_to_equity'] = total_debt / total_equity
                except Exception as e:
                    print(f"Warning: Error calculating balance sheet ratios: {e}")
        
        # Calculate growth metrics from income statement
        if 'income_stmt' in fundamental_data and fundamental_data['income_stmt'] is not None:
            income = fundamental_data['income_stmt']
            if hasattr(income, 'empty') and not income.empty and len(income.columns) >= 2:
                try:
                    # Revenue growth (YoY)
                    if 'Total Revenue' in income.index:
                        current_revenue = income.loc['Total Revenue', income.columns[0]]
                        prev_revenue = income.loc['Total Revenue', income.columns[1]]
                        if prev_revenue and prev_revenue != 0:
                            ratios['revenue_growth_yoy'] = (current_revenue - prev_revenue) / prev_revenue
                    
                    # Earnings growth (YoY)
                    if 'Net Income' in income.index:
                        current_earnings = income.loc['Net Income', income.columns[0]]
                        prev_earnings = income.loc['Net Income', income.columns[1]]
                        if prev_earnings and prev_earnings != 0:
                            ratios['earnings_growth_yoy'] = (current_earnings - prev_earnings) / prev_earnings
                except Exception as e:
                    print(f"Warning: Error calculating income statement ratios: {e}")
        
        # Create DataFrame with ratios
        ratios_df = pd.DataFrame([ratios])
        ratios_df['ticker'] = ticker
        ratios_df['date'] = datetime.now().strftime('%Y-%m-%d')
        
        return ratios_df
        
    except Exception as e:
        print(f"Error calculating ratios for {ticker}: {e}")
        return pd.DataFrame()

def classify_market_cap(market_cap: float) -> str:
    """
    Classify stock based on market capitalization.
    
    Args:
        market_cap (float): Market capitalization in USD
        
    Returns:
        str: Market cap category ('Large', 'Mid', 'Small')
    """
    if market_cap is None:
        return 'Unknown'
    
    if market_cap >= 10e9:  # $10 billion or more
        return 'Large'
    elif market_cap >= 2e9:  # $2 billion to $10 billion
        return 'Mid'
    else:  # Less than $2 billion
        return 'Small'

def get_sector_classification(sector: str, industry: str) -> Dict[str, str]:
    """
    Get detailed sector and industry classification.
    
    Args:
        sector (str): Sector from yfinance
        industry (str): Industry from yfinance
        
    Returns:
        Dict[str, str]: Dictionary with sector and industry classifications
    """
    # Standard sector mappings
    sector_mappings = {
        'Technology': 'Technology',
        'Healthcare': 'Healthcare',
        'Financial Services': 'Financial',
        'Consumer Cyclical': 'Consumer Discretionary',
        'Consumer Defensive': 'Consumer Staples',
        'Communication Services': 'Communication Services',
        'Industrials': 'Industrials',
        'Energy': 'Energy',
        'Basic Materials': 'Materials',
        'Real Estate': 'Real Estate',
        'Utilities': 'Utilities'
    }
    
    return {
        'sector': sector_mappings.get(sector, sector),
        'industry': industry,
        'sector_code': sector[:3].upper() if sector else 'UNK'
    }

def fetch_and_save_fundamentals(ticker: str, save_dir: str = '../data/fundamentals/') -> str:
    """
    Fetch fundamental data and save key ratios to CSV.
    
    Args:
        ticker (str): Stock ticker symbol
        save_dir (str): Directory to save the data
        
    Returns:
        str: Path to the saved ratios CSV file
    """
    os.makedirs(save_dir, exist_ok=True)
    
    # Fetch all fundamental data
    fundamental_data = fetch_fundamental_data(ticker, save_dir)
    
    # Extract and calculate ratios
    ratios_df = extract_key_ratios(ticker, fundamental_data)
    
    if len(ratios_df) > 0:
        # Add market cap classification
        market_cap = ratios_df.get('market_cap', [None]).iloc[0]
        ratios_df['market_cap_category'] = classify_market_cap(market_cap)
        
        # Add sector classification
        sector = ratios_df.get('sector', [None]).iloc[0]
        industry = ratios_df.get('industry', [None]).iloc[0]
        sector_info = get_sector_classification(sector, industry)
        ratios_df['sector_classified'] = sector_info['sector']
        ratios_df['sector_code'] = sector_info['sector_code']
        
        # Save ratios
        ratios_file = os.path.join(save_dir, f"{ticker}_ratios.csv")
        ratios_df.to_csv(ratios_file, index=False)
        print(f"Saved ratios to {ratios_file}")
        
        return ratios_file
    
    return ""

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Fetch fundamental data and calculate ratios.")
    parser.add_argument("ticker", type=str, help="Stock ticker symbol (e.g., 'AAPL')")
    parser.add_argument("--save_dir", type=str, default="../data/fundamentals/", help="Directory to save data")
    args = parser.parse_args()
    
    ratios_file = fetch_and_save_fundamentals(args.ticker, args.save_dir)
    if ratios_file:
        print(f"Fundamental analysis complete. Ratios saved to {ratios_file}")
    else:
        print("Failed to fetch fundamental data.") 