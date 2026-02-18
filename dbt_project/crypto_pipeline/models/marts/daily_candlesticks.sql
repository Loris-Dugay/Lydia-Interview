{{
    config(
        materialized='incremental',
        unique_key=['price_date', 'coin_id', 'vs_currency']
    )
}}

WITH hourly_prices AS (
    SELECT * FROM {{ ref('stg_crypto_prices') }}
    {% if is_incremental() %}
        WHERE price_date > (SELECT MAX(price_date) FROM {{ this }})
    {% endif %}
),

compute_prices AS (
    SELECT
        price_date,
        coin_id,
        vs_currency,
        MAX(price) AS higher,
        MIN(price) AS lower,
        FIRST(price) AS open,
        LAST(price) AS close
    FROM hourly_prices
    GROUP BY price_date, coin_id, vs_currency
)

SELECT *
FROM compute_prices
