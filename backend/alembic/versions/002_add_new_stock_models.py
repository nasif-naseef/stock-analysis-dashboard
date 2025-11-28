"""Add new stock models matching notebook API structure

Revision ID: 002_add_new_models
Revises: 001_add_configuration_tables
Create Date: 2024-11-28

This migration adds new tables to match the Jupyter notebook response models:
- analyst_consensus: Analyst consensus data
- historical_analyst_consensus: Historical consensus data
- insider_scores: Insider confidence scores
- crowd_stats: Crowd wisdom statistics
- article_distribution: Article distribution across sources
- article_sentiment: Article sentiment analysis
- support_resistance: Support/resistance price levels
- stop_loss: Stop loss recommendations
- chart_events: Technical chart events
- technical_summaries: Technical analysis summaries

Also updates existing tables with new columns for notebook API fields.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002_add_new_models'
down_revision = '001_add_configuration_tables'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create analyst_consensus table
    op.create_table(
        'analyst_consensus',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ticker', sa.String(length=10), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('total_ratings', sa.Integer(), nullable=True),
        sa.Column('buy_ratings', sa.Integer(), nullable=True),
        sa.Column('hold_ratings', sa.Integer(), nullable=True),
        sa.Column('sell_ratings', sa.Integer(), nullable=True),
        sa.Column('consensus_recommendation', sa.String(length=50), nullable=True),
        sa.Column('consensus_rating_score', sa.Float(), nullable=True),
        sa.Column('price_target_high', sa.Float(), nullable=True),
        sa.Column('price_target_low', sa.Float(), nullable=True),
        sa.Column('price_target_average', sa.Float(), nullable=True),
        sa.Column('source', sa.String(length=100), nullable=True),
        sa.Column('raw_data', sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_analyst_consensus_id', 'analyst_consensus', ['id'], unique=False)
    op.create_index('ix_analyst_consensus_ticker', 'analyst_consensus', ['ticker'], unique=False)
    op.create_index('ix_analyst_consensus_timestamp', 'analyst_consensus', ['timestamp'], unique=False)
    op.create_index('ix_analyst_consensus_ticker_timestamp', 'analyst_consensus', ['ticker', 'timestamp'], unique=False)

    # Create historical_analyst_consensus table
    op.create_table(
        'historical_analyst_consensus',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ticker', sa.String(length=10), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('date', sa.String(length=50), nullable=True),
        sa.Column('buy', sa.Integer(), nullable=True),
        sa.Column('hold', sa.Integer(), nullable=True),
        sa.Column('sell', sa.Integer(), nullable=True),
        sa.Column('consensus', sa.String(length=50), nullable=True),
        sa.Column('price_target', sa.Float(), nullable=True),
        sa.Column('raw_data', sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_historical_analyst_consensus_id', 'historical_analyst_consensus', ['id'], unique=False)
    op.create_index('ix_historical_analyst_consensus_ticker', 'historical_analyst_consensus', ['ticker'], unique=False)
    op.create_index('ix_historical_analyst_consensus_timestamp', 'historical_analyst_consensus', ['timestamp'], unique=False)
    op.create_index('ix_historical_analyst_consensus_ticker_timestamp', 'historical_analyst_consensus', ['ticker', 'timestamp'], unique=False)

    # Create insider_scores table
    op.create_table(
        'insider_scores',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ticker', sa.String(length=10), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('stock_score', sa.Float(), nullable=True),
        sa.Column('sector_score', sa.Float(), nullable=True),
        sa.Column('score', sa.Float(), nullable=True),
        sa.Column('source', sa.String(length=100), nullable=True),
        sa.Column('raw_data', sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_insider_scores_id', 'insider_scores', ['id'], unique=False)
    op.create_index('ix_insider_scores_ticker', 'insider_scores', ['ticker'], unique=False)
    op.create_index('ix_insider_scores_timestamp', 'insider_scores', ['timestamp'], unique=False)
    op.create_index('ix_insider_scores_ticker_timestamp', 'insider_scores', ['ticker', 'timestamp'], unique=False)

    # Create crowd_stats table
    op.create_table(
        'crowd_stats',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ticker', sa.String(length=10), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('stats_type', sa.String(length=20), nullable=True),
        sa.Column('portfolio_holding', sa.Integer(), server_default='0'),
        sa.Column('amount_of_portfolios', sa.Integer(), server_default='0'),
        sa.Column('amount_of_public_portfolios', sa.Integer(), server_default='0'),
        sa.Column('percent_allocated', sa.Float(), server_default='0.0'),
        sa.Column('based_on_portfolios', sa.Integer(), server_default='0'),
        sa.Column('percent_over_last_7d', sa.Float(), server_default='0.0'),
        sa.Column('percent_over_last_30d', sa.Float(), server_default='0.0'),
        sa.Column('score', sa.Float(), server_default='0.0'),
        sa.Column('individual_sector_average', sa.Float(), server_default='0.0'),
        sa.Column('frequency', sa.Float(), server_default='0.0'),
        sa.Column('source', sa.String(length=100), nullable=True),
        sa.Column('raw_data', sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_crowd_stats_id', 'crowd_stats', ['id'], unique=False)
    op.create_index('ix_crowd_stats_ticker', 'crowd_stats', ['ticker'], unique=False)
    op.create_index('ix_crowd_stats_timestamp', 'crowd_stats', ['timestamp'], unique=False)
    op.create_index('ix_crowd_stats_ticker_timestamp', 'crowd_stats', ['ticker', 'timestamp'], unique=False)

    # Create article_distribution table
    op.create_table(
        'article_distribution',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ticker', sa.String(length=10), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('total_articles', sa.Integer(), server_default='0'),
        sa.Column('news_count', sa.Integer(), server_default='0'),
        sa.Column('news_percentage', sa.Float(), server_default='0.0'),
        sa.Column('social_count', sa.Integer(), server_default='0'),
        sa.Column('social_percentage', sa.Float(), server_default='0.0'),
        sa.Column('web_count', sa.Integer(), server_default='0'),
        sa.Column('web_percentage', sa.Float(), server_default='0.0'),
        sa.Column('source', sa.String(length=100), nullable=True),
        sa.Column('raw_data', sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_article_distribution_id', 'article_distribution', ['id'], unique=False)
    op.create_index('ix_article_distribution_ticker', 'article_distribution', ['ticker'], unique=False)
    op.create_index('ix_article_distribution_timestamp', 'article_distribution', ['timestamp'], unique=False)
    op.create_index('ix_article_distribution_ticker_timestamp', 'article_distribution', ['ticker', 'timestamp'], unique=False)

    # Create article_sentiment table
    op.create_table(
        'article_sentiment',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ticker', sa.String(length=10), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('sentiment_id', sa.String(length=50), nullable=True),
        sa.Column('sentiment_label', sa.String(length=50), nullable=True),
        sa.Column('sentiment_value', sa.Integer(), nullable=True),
        sa.Column('subjectivity_id', sa.String(length=50), nullable=True),
        sa.Column('subjectivity_label', sa.String(length=50), nullable=True),
        sa.Column('subjectivity_value', sa.Integer(), nullable=True),
        sa.Column('confidence_id', sa.String(length=50), nullable=True),
        sa.Column('confidence_name', sa.String(length=50), nullable=True),
        sa.Column('source', sa.String(length=100), nullable=True),
        sa.Column('raw_data', sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_article_sentiment_id', 'article_sentiment', ['id'], unique=False)
    op.create_index('ix_article_sentiment_ticker', 'article_sentiment', ['ticker'], unique=False)
    op.create_index('ix_article_sentiment_timestamp', 'article_sentiment', ['timestamp'], unique=False)
    op.create_index('ix_article_sentiment_ticker_timestamp', 'article_sentiment', ['ticker', 'timestamp'], unique=False)

    # Create support_resistance table
    op.create_table(
        'support_resistance',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('symbol', sa.String(length=10), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('date', sa.String(length=50), nullable=True),
        sa.Column('exchange', sa.String(length=50), nullable=True),
        sa.Column('support_10', sa.Float(), nullable=True),
        sa.Column('resistance_10', sa.Float(), nullable=True),
        sa.Column('support_20', sa.Float(), nullable=True),
        sa.Column('resistance_20', sa.Float(), nullable=True),
        sa.Column('support_40', sa.Float(), nullable=True),
        sa.Column('resistance_40', sa.Float(), nullable=True),
        sa.Column('support_100', sa.Float(), nullable=True),
        sa.Column('resistance_100', sa.Float(), nullable=True),
        sa.Column('support_250', sa.Float(), nullable=True),
        sa.Column('resistance_250', sa.Float(), nullable=True),
        sa.Column('support_500', sa.Float(), nullable=True),
        sa.Column('resistance_500', sa.Float(), nullable=True),
        sa.Column('source', sa.String(length=100), nullable=True),
        sa.Column('raw_data', sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_support_resistance_id', 'support_resistance', ['id'], unique=False)
    op.create_index('ix_support_resistance_symbol', 'support_resistance', ['symbol'], unique=False)
    op.create_index('ix_support_resistance_timestamp', 'support_resistance', ['timestamp'], unique=False)
    op.create_index('ix_support_resistance_symbol_timestamp', 'support_resistance', ['symbol', 'timestamp'], unique=False)

    # Create stop_loss table
    op.create_table(
        'stop_loss',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ticker', sa.String(length=10), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('recommended_stop_price', sa.Float(), nullable=True),
        sa.Column('calculation_timestamp', sa.String(length=100), nullable=True),
        sa.Column('stop_type', sa.String(length=50), server_default='Volatility-Based'),
        sa.Column('direction', sa.String(length=50), server_default='Below (Long Position)'),
        sa.Column('tightness', sa.String(length=50), server_default='Medium'),
        sa.Column('source', sa.String(length=100), nullable=True),
        sa.Column('raw_data', sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_stop_loss_id', 'stop_loss', ['id'], unique=False)
    op.create_index('ix_stop_loss_ticker', 'stop_loss', ['ticker'], unique=False)
    op.create_index('ix_stop_loss_timestamp', 'stop_loss', ['timestamp'], unique=False)
    op.create_index('ix_stop_loss_ticker_timestamp', 'stop_loss', ['ticker', 'timestamp'], unique=False)

    # Create chart_events table
    op.create_table(
        'chart_events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ticker', sa.String(length=10), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('event_id', sa.String(length=100), nullable=True),
        sa.Column('event_type', sa.String(length=100), nullable=True),
        sa.Column('event_name', sa.String(length=200), nullable=True),
        sa.Column('price_period', sa.String(length=50), nullable=True),
        sa.Column('start_date', sa.String(length=100), nullable=True),
        sa.Column('end_date', sa.String(length=100), nullable=True),
        sa.Column('target_price', sa.Float(), nullable=True),
        sa.Column('start_price', sa.Float(), nullable=True),
        sa.Column('end_price', sa.Float(), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('source', sa.String(length=100), nullable=True),
        sa.Column('raw_data', sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_chart_events_id', 'chart_events', ['id'], unique=False)
    op.create_index('ix_chart_events_ticker', 'chart_events', ['ticker'], unique=False)
    op.create_index('ix_chart_events_timestamp', 'chart_events', ['timestamp'], unique=False)
    op.create_index('ix_chart_events_ticker_timestamp', 'chart_events', ['ticker', 'timestamp'], unique=False)
    op.create_index('ix_chart_events_is_active', 'chart_events', ['is_active'], unique=False)

    # Create technical_summaries table
    op.create_table(
        'technical_summaries',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('symbol', sa.String(length=10), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=True),
        sa.Column('exchange', sa.String(length=50), nullable=True),
        sa.Column('isin', sa.String(length=50), nullable=True),
        sa.Column('instrument_id', sa.String(length=100), nullable=True),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('recommendation', sa.String(length=100), nullable=True),
        sa.Column('signal_strength', sa.Float(), nullable=True),
        sa.Column('source', sa.String(length=100), nullable=True),
        sa.Column('raw_data', sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_technical_summaries_id', 'technical_summaries', ['id'], unique=False)
    op.create_index('ix_technical_summaries_symbol', 'technical_summaries', ['symbol'], unique=False)
    op.create_index('ix_technical_summaries_timestamp', 'technical_summaries', ['timestamp'], unique=False)
    op.create_index('ix_technical_summaries_symbol_timestamp', 'technical_summaries', ['symbol', 'timestamp'], unique=False)

    # Add new columns to existing tables
    # news_sentiment - add notebook API fields
    op.add_column('news_sentiment', sa.Column('stock_bullish_score', sa.Float(), nullable=True))
    op.add_column('news_sentiment', sa.Column('stock_bearish_score', sa.Float(), nullable=True))
    op.add_column('news_sentiment', sa.Column('sector_bullish_score', sa.Float(), nullable=True))
    op.add_column('news_sentiment', sa.Column('sector_bearish_score', sa.Float(), nullable=True))

    # hedge_fund_data - add notebook API fields
    op.add_column('hedge_fund_data', sa.Column('sentiment', sa.Float(), nullable=True))
    op.add_column('hedge_fund_data', sa.Column('trend_action', sa.Integer(), nullable=True))
    op.add_column('hedge_fund_data', sa.Column('trend_value', sa.Integer(), nullable=True))

    # blogger_sentiment - add notebook API fields
    op.add_column('blogger_sentiment', sa.Column('bearish', sa.Integer(), server_default='0'))
    op.add_column('blogger_sentiment', sa.Column('neutral', sa.Integer(), server_default='0'))
    op.add_column('blogger_sentiment', sa.Column('bullish', sa.Integer(), server_default='0'))
    op.add_column('blogger_sentiment', sa.Column('bearish_count', sa.Integer(), server_default='0'))
    op.add_column('blogger_sentiment', sa.Column('neutral_count', sa.Integer(), server_default='0'))
    op.add_column('blogger_sentiment', sa.Column('bullish_count', sa.Integer(), server_default='0'))
    op.add_column('blogger_sentiment', sa.Column('score', sa.Float(), server_default='0.0'))
    op.add_column('blogger_sentiment', sa.Column('avg', sa.Float(), server_default='0.0'))

    # quantamental_scores - add notebook API fields
    op.add_column('quantamental_scores', sa.Column('overall', sa.Integer(), nullable=True))
    op.add_column('quantamental_scores', sa.Column('growth', sa.Integer(), nullable=True))
    op.add_column('quantamental_scores', sa.Column('value', sa.Integer(), nullable=True))
    op.add_column('quantamental_scores', sa.Column('income', sa.Integer(), nullable=True))
    op.add_column('quantamental_scores', sa.Column('quality', sa.Integer(), nullable=True))
    op.add_column('quantamental_scores', sa.Column('momentum', sa.Integer(), nullable=True))

    # target_prices - add notebook API fields
    op.add_column('target_prices', sa.Column('close_price', sa.Float(), nullable=True))
    op.add_column('target_prices', sa.Column('target_date', sa.String(length=100), nullable=True))
    op.add_column('target_prices', sa.Column('last_updated', sa.String(length=100), nullable=True))


def downgrade() -> None:
    # Remove added columns from existing tables
    op.drop_column('target_prices', 'last_updated')
    op.drop_column('target_prices', 'target_date')
    op.drop_column('target_prices', 'close_price')

    op.drop_column('quantamental_scores', 'momentum')
    op.drop_column('quantamental_scores', 'quality')
    op.drop_column('quantamental_scores', 'income')
    op.drop_column('quantamental_scores', 'value')
    op.drop_column('quantamental_scores', 'growth')
    op.drop_column('quantamental_scores', 'overall')

    op.drop_column('blogger_sentiment', 'avg')
    op.drop_column('blogger_sentiment', 'score')
    op.drop_column('blogger_sentiment', 'bullish_count')
    op.drop_column('blogger_sentiment', 'neutral_count')
    op.drop_column('blogger_sentiment', 'bearish_count')
    op.drop_column('blogger_sentiment', 'bullish')
    op.drop_column('blogger_sentiment', 'neutral')
    op.drop_column('blogger_sentiment', 'bearish')

    op.drop_column('hedge_fund_data', 'trend_value')
    op.drop_column('hedge_fund_data', 'trend_action')
    op.drop_column('hedge_fund_data', 'sentiment')

    op.drop_column('news_sentiment', 'sector_bearish_score')
    op.drop_column('news_sentiment', 'sector_bullish_score')
    op.drop_column('news_sentiment', 'stock_bearish_score')
    op.drop_column('news_sentiment', 'stock_bullish_score')

    # Drop new tables
    op.drop_index('ix_technical_summaries_symbol_timestamp', table_name='technical_summaries')
    op.drop_index('ix_technical_summaries_timestamp', table_name='technical_summaries')
    op.drop_index('ix_technical_summaries_symbol', table_name='technical_summaries')
    op.drop_index('ix_technical_summaries_id', table_name='technical_summaries')
    op.drop_table('technical_summaries')

    op.drop_index('ix_chart_events_is_active', table_name='chart_events')
    op.drop_index('ix_chart_events_ticker_timestamp', table_name='chart_events')
    op.drop_index('ix_chart_events_timestamp', table_name='chart_events')
    op.drop_index('ix_chart_events_ticker', table_name='chart_events')
    op.drop_index('ix_chart_events_id', table_name='chart_events')
    op.drop_table('chart_events')

    op.drop_index('ix_stop_loss_ticker_timestamp', table_name='stop_loss')
    op.drop_index('ix_stop_loss_timestamp', table_name='stop_loss')
    op.drop_index('ix_stop_loss_ticker', table_name='stop_loss')
    op.drop_index('ix_stop_loss_id', table_name='stop_loss')
    op.drop_table('stop_loss')

    op.drop_index('ix_support_resistance_symbol_timestamp', table_name='support_resistance')
    op.drop_index('ix_support_resistance_timestamp', table_name='support_resistance')
    op.drop_index('ix_support_resistance_symbol', table_name='support_resistance')
    op.drop_index('ix_support_resistance_id', table_name='support_resistance')
    op.drop_table('support_resistance')

    op.drop_index('ix_article_sentiment_ticker_timestamp', table_name='article_sentiment')
    op.drop_index('ix_article_sentiment_timestamp', table_name='article_sentiment')
    op.drop_index('ix_article_sentiment_ticker', table_name='article_sentiment')
    op.drop_index('ix_article_sentiment_id', table_name='article_sentiment')
    op.drop_table('article_sentiment')

    op.drop_index('ix_article_distribution_ticker_timestamp', table_name='article_distribution')
    op.drop_index('ix_article_distribution_timestamp', table_name='article_distribution')
    op.drop_index('ix_article_distribution_ticker', table_name='article_distribution')
    op.drop_index('ix_article_distribution_id', table_name='article_distribution')
    op.drop_table('article_distribution')

    op.drop_index('ix_crowd_stats_ticker_timestamp', table_name='crowd_stats')
    op.drop_index('ix_crowd_stats_timestamp', table_name='crowd_stats')
    op.drop_index('ix_crowd_stats_ticker', table_name='crowd_stats')
    op.drop_index('ix_crowd_stats_id', table_name='crowd_stats')
    op.drop_table('crowd_stats')

    op.drop_index('ix_insider_scores_ticker_timestamp', table_name='insider_scores')
    op.drop_index('ix_insider_scores_timestamp', table_name='insider_scores')
    op.drop_index('ix_insider_scores_ticker', table_name='insider_scores')
    op.drop_index('ix_insider_scores_id', table_name='insider_scores')
    op.drop_table('insider_scores')

    op.drop_index('ix_historical_analyst_consensus_ticker_timestamp', table_name='historical_analyst_consensus')
    op.drop_index('ix_historical_analyst_consensus_timestamp', table_name='historical_analyst_consensus')
    op.drop_index('ix_historical_analyst_consensus_ticker', table_name='historical_analyst_consensus')
    op.drop_index('ix_historical_analyst_consensus_id', table_name='historical_analyst_consensus')
    op.drop_table('historical_analyst_consensus')

    op.drop_index('ix_analyst_consensus_ticker_timestamp', table_name='analyst_consensus')
    op.drop_index('ix_analyst_consensus_timestamp', table_name='analyst_consensus')
    op.drop_index('ix_analyst_consensus_ticker', table_name='analyst_consensus')
    op.drop_index('ix_analyst_consensus_id', table_name='analyst_consensus')
    op.drop_table('analyst_consensus')
