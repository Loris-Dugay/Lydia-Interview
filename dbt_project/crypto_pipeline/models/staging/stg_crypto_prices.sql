{{
    config(materialized='view')
}}

WITH source AS (
    SELECT * FROM {{ source('raw', 'raw_crypto_prices') }}
)

SELECT
    timestamp,
    price,
    coin_id,
    vs_currency,
    DATE_TRUNC('day', timestamp) AS price_date,
    CASE
        WHEN price <=0 THEN TRUE
        WHEN price is NULL THEN TRUE
        ELSE FALSE
    END AS is_invalid_price
FROM source
WHERE price > 0 OR price is NOT NULL
